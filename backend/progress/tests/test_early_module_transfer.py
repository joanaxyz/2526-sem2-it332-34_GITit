"""Curated early-module eligibility, fixed study meaning and safe backfill."""

import copy
import io
import json
import os
from datetime import timedelta
from pathlib import Path

import pytest
from django.core.management import call_command
from django.utils import timezone
from rest_framework.test import APIClient

from adventures.models import AdventureLevelTierProgress
from progress.models import (
    AdventureLevelTierCompletion,
    KpiCheckpoint,
    KpiExposure,
)
from progress.objectives import EARLY_TRANSFER_LEVELS, transfer_expected
from progress.services import MetricsService
from progress.services.references import ref_hash, state_key
from progress.services.studies import create_study, freeze_study
from progress.services.transfer_policy import ALL_MODULE_TRANSFER_POLICY, study_transfer_pins
from testing.kpi_fixtures import bundle, end, start


def early_bundle(user_model, module, username):
    result = bundle(user_model, module=module, username=username, required=1)
    level = result[1].adventure_level
    level.slug = EARLY_TRANSFER_LEVELS[module]
    level.save(update_fields=["slug"])
    # Distinct level content must be genuinely unseen across the learner's
    # whole history; changing a variant ID alone must not bypass that rule.
    for variant in result[3]:
        for field in ("initial_state", "target_state"):
            value = json.dumps(getattr(variant, field))
            for name in ("note.txt", "extra.txt"):
                value = value.replace(name, f"m{module}-{name}")
            setattr(variant, field, json.loads(value))
        variant.ref_hash = ref_hash(variant)
        variant.save(update_fields=["initial_state", "target_state", "ref_hash"])
    return result


@pytest.mark.parametrize("module", [1, 2])
@pytest.mark.parametrize("passed", [True, False])
@pytest.mark.django_db
def test_selected_early_modules_assign_and_report_the_preserved_first_result(
    django_user_model, module, passed
):
    player, tier, _, _ = early_bundle(django_user_model, module, "early")
    end(start(player, tier))
    pending = MetricsService().performance_summary(player=player)
    assert pending["samples"]["transfer_pending"] == 1
    assert pending["samples"]["transfer_missing"] == 0
    assert pending["kpis"]["rta"]["value"] is None
    first = end(start(player, tier, transfer=True), passed=passed)
    point = KpiCheckpoint.objects.get(player=player, tier=tier, kind="transfer")
    end(start(player, tier, transfer=True))  # Later practice cannot replace first failure.
    point.refresh_from_db()
    assert point.run_id == first.id and point.passed is passed
    report = MetricsService().performance_summary(player=player)
    row = next(m for m in report["modules"] if m["number"] == module)
    assert row["rta"] == {
        "value": 100.0 if passed else 0.0,
        "numerator": int(passed),
        "denominator": 1,
    }
    assert report["samples"]["transfer_missing"] == report["samples"]["transfer_pending"] == 0
    assert MetricsService().admin_player_performance_summary(player=player) == report
    client = APIClient()
    client.force_authenticate(user=player.user)
    assert client.get("/api/progress/performance/").json() == report


@pytest.mark.parametrize("module", [1, 2])
@pytest.mark.django_db
def test_unselected_levels_create_no_live_or_study_transfer_expectation(
    django_user_model, monkeypatch, module
):
    player, tier, _, _ = bundle(django_user_model, module=module, required=1)
    assert not transfer_expected(module, "hard", tier.adventure_level.slug)
    cutoff = timezone.now() + timedelta(hours=1)
    study = create_study(
        slug="unselected", player_ids=[player.id], tier_ids=[tier.id], cutoff=cutoff
    )
    spec = study.manifest["tiers"][0]
    assert spec["transfer_expected"] is False and spec["transfer"] is None
    end(start(player, tier))
    live = MetricsService().performance_summary(player=player)
    assert live["samples"]["transfer_assigned"] == live["samples"]["transfer_missing"] == 0
    monkeypatch.setattr(
        "progress.services.studies.timezone.now", lambda: cutoff + timedelta(seconds=1)
    )
    frozen = freeze_study(study)
    assert frozen["kpis"]["rta"]["value"] is None
    assert frozen["coverage"]["transfer_assigned"] == frozen["coverage"]["transfer_missing"] == 0


def study_cohort(user_model):
    player, first, _, _ = early_bundle(user_model, 1, "first")
    _, second, _, _ = early_bundle(user_model, 2, "second")
    _, third, _, _ = bundle(user_model, module=3, username="third", required=1)
    _, excluded, _, _ = bundle(user_model, module=1, username="excluded", required=1)
    for tier in (second, third, excluded):
        AdventureLevelTierCompletion.objects.create(
            player=player, tier=tier.adventure_level.tiers.get(difficulty="medium")
        )
    return player, [first, second, third, excluded]


@pytest.mark.django_db
@pytest.mark.parametrize(
    "policy", [ALL_MODULE_TRANSFER_POLICY, "mastery-kpis-v2", "mastery-kpis-v3-retry-rta"]
)
def test_study_scope_and_weights_do_not_follow_later_live_eligibility(
    django_user_model, monkeypatch, policy
):
    player, tiers = study_cohort(django_user_model)
    cutoff = timezone.now() + timedelta(hours=1)
    study = create_study(
        slug="fixed-scope",
        player_ids=[player.id],
        tier_ids=[t.id for t in tiers],
        cutoff=cutoff,
        weights={"1": 1, "2": 3, "3": 2},
    )
    assert study.manifest["policy"] == ALL_MODULE_TRANSFER_POLICY
    if policy != ALL_MODULE_TRANSFER_POLICY:
        study.manifest["policy"] = policy
        for spec in study.manifest["tiers"]:
            spec.pop("transfer_expected")
            if spec["module"] in (1, 2):
                spec["transfer"] = None
        study.save(update_fields=["manifest"])
    else:
        pin = study.manifest["tiers"][0]["transfer"]
        assert study_transfer_pins([player.id], [tiers[0].id])[player.id, tiers[0].id] == {
            (pin["id"], pin["hash"], pin["count"])
        }
    for tier, passed in zip(tiers[:3], [True, False, True], strict=True):
        end(start(player, tier))
        end(start(player, tier, transfer=True), passed=passed)
    monkeypatch.setattr("progress.objectives.EARLY_TRANSFER_LEVELS", {})
    monkeypatch.setattr(
        "progress.services.studies.timezone.now", lambda: cutoff + timedelta(seconds=1)
    )
    report = freeze_study(study)
    expected = (
        50 if policy == ALL_MODULE_TRANSFER_POLICY else 100 if policy == "mastery-kpis-v2" else None
    )
    assert report["kpis"]["rta"]["value"] == expected
    early = [r for r in report["records"] if r["module"] in (1, 2)]
    if policy != ALL_MODULE_TRANSFER_POLICY:
        assert all(
            r["transfer"] is None and not r["transfer_assigned"] and not r["transfer_missing"]
            for r in early
        )
    assert not next(r for r in early if r["tier_id"] == tiers[-1].id)["transfer_missing"]
    assert freeze_study(study) == report
    if destination := os.environ.get("EARLY_STUDY_EVIDENCE_PATH"):
        path = Path(destination)
        data = json.loads(path.read_text()) if path.exists() else {}
        data[policy] = {
            "manifest": copy.deepcopy(study.manifest),
            "report": report,
            "repeat_freeze_unchanged": True,
        }
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")


@pytest.mark.django_db
def test_backfill_previews_then_assigns_only_unseen_complete_mastery_idempotently(
    django_user_model,
):
    ready, tier, _, variants = early_bundle(django_user_model, 1, "ready")
    gap, other, _, _ = early_bundle(django_user_model, 2, "gap")
    for player, mastered, complete in ((ready, tier, True), (gap, other, False)):
        AdventureLevelTierCompletion.objects.create(player=player, tier=mastered)
        AdventureLevelTierProgress.objects.create(
            player=player, tier=mastered, exposure_complete=complete
        )

    def invoke(apply=False):
        output = io.StringIO()
        call_command("assign_transfer_checkpoints", modules=[1, 2], apply=apply, stdout=output)
        return json.loads(output.getvalue())

    dry = invoke()
    assert dry["eligible"] == 1 and dry["created"] == 0 and dry["ineligible"] == 1
    assert not KpiCheckpoint.objects.filter(kind="transfer").exists()
    applied = invoke(True)
    assert applied["created"] == 1
    point = KpiCheckpoint.objects.get(player=ready, kind="transfer")
    repeated = invoke(True)
    assert repeated["created"] == 0
    assert KpiCheckpoint.objects.get(pk=point.pk).variant_id == point.variant_id
    assert not KpiCheckpoint.objects.filter(player=gap, kind="transfer").exists()
    # Even complete tracking cannot promise novelty once reserved content was seen.
    KpiCheckpoint.objects.filter(pk=point.pk).delete()
    KpiExposure.objects.create(player=ready, variant=variants[1], state_key=state_key(variants[1]))
    seen = invoke(True)
    assert seen["created"] == 0
    if destination := os.environ.get("EARLY_BACKFILL_EVIDENCE_PATH"):
        Path(destination).write_text(
            json.dumps(
                {
                    "dry_run": dry,
                    "applied": applied,
                    "repeated": repeated,
                    "seen_content": seen,
                    "exposure_gap_excluded": True,
                },
                indent=2,
            ),
            encoding="utf-8",
        )


@pytest.mark.django_db
@pytest.mark.parametrize("backfill", [False, True])
def test_v4_prospective_pin_survives_live_roster_change(django_user_model, monkeypatch, backfill):
    player, tier, _, _ = early_bundle(django_user_model, 1, "pinned")
    cutoff = timezone.now() + timedelta(hours=1)
    study = create_study(
        slug="roster-before", player_ids=[player.id], tier_ids=[tier.id], cutoff=cutoff
    )
    original = study.manifest["tiers"][0]["transfer"]
    monkeypatch.setattr("progress.objectives.EARLY_TRANSFER_LEVELS", {})
    if backfill:
        AdventureLevelTierCompletion.objects.create(player=player, tier=tier)
        AdventureLevelTierProgress.objects.create(player=player, tier=tier, exposure_complete=True)
        output = io.StringIO()
        call_command("assign_transfer_checkpoints", modules=[1], apply=True, stdout=output)
        assert json.loads(output.getvalue())["created"] == 1
    else:
        end(start(player, tier))
    point = KpiCheckpoint.objects.get(player=player, tier=tier, kind="transfer")
    assert point.variant_id == original["id"] and point.ref_hash == original["hash"]
    end(start(player, tier, transfer=True))
    monkeypatch.setattr(
        "progress.services.studies.timezone.now", lambda: cutoff + timedelta(seconds=1)
    )
    report = freeze_study(study)
    assert report["kpis"]["rta"]["value"] == 100
    if destination := os.environ.get("EARLY_ROSTER_PIN_EVIDENCE_PATH"):
        path = Path(destination)
        data = json.loads(path.read_text()) if path.exists() else {}
        data["backfill" if backfill else "live"] = {
            "policy": study.manifest["policy"],
            "pin": original,
            "assigned_variant_id": point.variant_id,
            "completed_variant_id": point.variant_id,
            "first_result": True,
            "frozen_rta": report["kpis"]["rta"],
            "live_roster_removed_before_mastery": True,
        }
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
