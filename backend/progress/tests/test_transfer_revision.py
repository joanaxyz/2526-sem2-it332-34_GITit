"""Assessment content cutover preserves pinned history and prerequisite fairness."""

import copy
import json
import os
from datetime import timedelta
from pathlib import Path

import pytest
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.utils import timezone

from adventures.models import (
    AdventureLevel,
    AdventureLevelTier,
    AdventureLevelTierProgress,
    AdventureLevelTierScenario,
    AdventureLevelTierScenarioVariant,
)
from curriculum.management.commands.seed_curriculum import Command
from curriculum.seed_data.source.scenario_fixtures import extension_case
from curriculum.seed_data.source.transfer_checkpoints import (
    RETIRED_TRANSFER_CHECKPOINTS,
    TRANSFER_CHECKPOINTS,
)
from players.services import get_or_create_player
from progress.models import AdventureLevelTierCompletion, KpiCheckpoint, KpiStudy
from progress.services import MetricsService
from progress.services.checkpoints import assign_transfer
from progress.services.references import ref_hash, seed_refs
from progress.services.studies import create_study, freeze_study
from testing.kpi_fixtures import bundle, end, start, variant


def player(user_model, username):
    return get_or_create_player(user_model.objects.create_user(username=username))


def legacy_variant(tier, case_id):
    scenario = tier.scenarios.filter(is_published=True).order_by("sort_order", "id").first()
    old = AdventureLevelTierScenarioVariant.objects.create(
        scenario=scenario,
        slug=case_id,
        **Command._variant_defaults(extension_case(case_id)),
        is_transfer=True,
        transfer_note="Original assessment decision.",
    )
    seed_refs([old])
    return old


@pytest.mark.django_db
def test_reseed_preserves_every_old_version_and_pending_active_concluded_points(django_user_model):
    call_command("seed_curriculum", verbosity=0)
    assert not AdventureLevelTierScenarioVariant.objects.filter(
        slug__in=RETIRED_TRANSFER_CHECKPOINTS
    ).exists()
    old_versions = []
    for case_id, slug in RETIRED_TRANSFER_CHECKPOINTS.items():
        tier = AdventureLevelTier.objects.get(adventure_level__slug=slug, difficulty="hard")
        old_versions.append(legacy_variant(tier, case_id))
    old = old_versions[0]
    original_hashes = {v.id: v.ref_hash for v in old_versions}
    fields = (
        "initial_state",
        "target_state",
        "evaluation_spec",
        "solution_commands",
        "solution_workspace_files",
        "ref_count",
        "ref_hash",
        "transfer_note",
    )
    original = {v.id: {f: copy.deepcopy(getattr(v, f)) for f in fields} for v in old_versions}
    learners = []
    for status in ("pending", "active", "concluded"):
        learner = player(django_user_model, status)
        AdventureLevelTierCompletion.objects.create(player=learner, tier=old.scenario.tier)
        point = KpiCheckpoint.objects.create(
            player=learner,
            tier=old.scenario.tier,
            kind="transfer",
            variant=old,
            ref_count=old.ref_count,
            ref_hash=old.ref_hash,
        )
        run = start(learner, old.scenario.tier, transfer=True) if status != "pending" else None
        if status == "concluded":
            end(run, passed=False)
        learners.append((status, learner, point, run))
    call_command("seed_curriculum", verbosity=0)
    call_command("seed_curriculum", verbosity=0)
    for old in old_versions:
        old.refresh_from_db()
        assert old.is_published and old.is_transfer and old.parameter_context["retired_transfer"]
        assert {f: getattr(old, f) for f in fields} == original[old.id]
        assert ref_hash(old) == original_hashes[old.id]
    for status, learner, point, run in learners:
        point.refresh_from_db()
        launched = start(learner, point.tier, transfer=True)
        assert launched.selected_variant_id == point.variant_id
        if status == "active":
            assert launched.id == run.id
        if status == "concluded":
            assert launched.is_transfer and launched.is_replay and point.passed is False
            assert point.run_id == run.id and point.ref_hash == original_hashes[point.variant_id]


@pytest.mark.django_db
def test_new_assignment_and_study_never_fall_back_to_retired_content(django_user_model):
    call_command("seed_curriculum", verbosity=0)
    tier = AdventureLevelTier.objects.get(
        adventure_level__slug="resolving-conflicts-manually", difficulty="hard"
    )
    old = legacy_variant(tier, "manual-transfer-checkout-v2")
    call_command("seed_curriculum", verbosity=0)
    current = tier.scenarios.first().variants.get(
        slug=TRANSFER_CHECKPOINTS[tier.adventure_level.slug]["case_id"]
    )
    learner = player(django_user_model, "new-live")
    AdventureLevelTierProgress.objects.create(player=learner, tier=tier, exposure_complete=True)
    point = assign_transfer(player=learner, tier=tier)
    assert point.variant_id == current.id
    study_learner = player(django_user_model, "new-study")
    cutoff = timezone.now() + timedelta(hours=1)
    study = create_study(
        slug="new-version", player_ids=[study_learner.id], tier_ids=[tier.id], cutoff=cutoff
    )
    assert study.manifest["tiers"][0]["transfer"]["id"] == current.id
    current.is_published = False
    current.save(update_fields=["is_published"])
    unavailable = player(django_user_model, "no-current")
    AdventureLevelTierProgress.objects.create(player=unavailable, tier=tier, exposure_complete=True)
    assert assign_transfer(player=unavailable, tier=tier) is None
    study_learner2 = player(django_user_model, "no-current-study")
    without = create_study(
        slug="no-fallback", player_ids=[study_learner2.id], tier_ids=[tier.id], cutoff=cutoff
    )
    assert without.manifest["tiers"][0]["transfer"] is None
    old.refresh_from_db()
    assert old.is_published


@pytest.mark.django_db
def test_old_unfrozen_study_keeps_its_original_reference_after_cutover(
    django_user_model, monkeypatch
):
    call_command("seed_curriculum", verbosity=0)
    tier = AdventureLevelTier.objects.get(
        adventure_level__slug="resolving-conflicts-manually", difficulty="hard"
    )
    old = legacy_variant(tier, "manual-transfer-checkout-v2")
    learner = player(django_user_model, "pinned-study")
    cutoff = timezone.now() + timedelta(hours=1)
    study = create_study(
        slug="pinned-version", player_ids=[learner.id], tier_ids=[tier.id], cutoff=cutoff
    )
    study.manifest["tiers"][0]["transfer"] = {
        "id": old.id,
        "hash": old.ref_hash,
        "count": old.ref_count,
    }
    study.save(update_fields=["manifest"])
    call_command("seed_curriculum", verbosity=0)
    monkeypatch.setattr(
        "progress.services.studies.timezone.now", lambda: cutoff + timedelta(seconds=1)
    )
    report = freeze_study(study)
    assert report["manifest"]["tiers"][0]["transfer"]["id"] == old.id
    assert report["kpis"]["rta"]["value"] == 0
    assert report["coverage"]["transfer_missing"] == 0
    assert freeze_study(study) == report


@pytest.mark.django_db
@pytest.mark.parametrize("study_policy", ["mastery-kpis-v2", "mastery-kpis-v4-all-module-transfer"])
def test_prospective_old_study_gets_its_pinned_checkpoint_after_mastery(
    django_user_model, monkeypatch, study_policy
):
    call_command("seed_curriculum", verbosity=0)
    tier = AdventureLevelTier.objects.get(
        adventure_level__slug="resolving-conflicts-manually", difficulty="hard"
    )
    old = legacy_variant(tier, "manual-transfer-checkout-v2")
    learner = player(django_user_model, "old-study-completes")
    medium = tier.adventure_level.tiers.get(difficulty="medium")
    AdventureLevelTierCompletion.objects.create(player=learner, tier=medium)
    cutoff = timezone.now() + timedelta(hours=1)
    study = create_study(
        slug="prospective-old", player_ids=[learner.id], tier_ids=[tier.id], cutoff=cutoff
    )
    # Reproduce the already-saved manifest from before the content cutover.
    original_ref = {"id": old.id, "hash": old.ref_hash, "count": old.ref_count}
    study.manifest["policy"] = study_policy
    study.manifest["tiers"][0]["transfer"] = original_ref
    study.save(update_fields=["manifest"])
    call_command("seed_curriculum", verbosity=0)
    for _ in range(tier.scenarios.filter(is_published=True).count()):
        end(start(learner, tier))
    point = KpiCheckpoint.objects.get(player=learner, tier=tier, kind="transfer")
    assert point.variant_id == old.id and point.ref_hash == original_ref["hash"]
    from rest_framework.test import APIClient

    from curriculum.services.solution_replay import replay_solutions

    assessed = start(learner, tier, transfer=True)
    assert assessed.selected_variant_id == old.id
    case = extension_case(old.slug)
    _, replays = replay_solutions(
        {
            old.slug: {
                "initial_state": case["initial_state"],
                "solution_commands": case["solution_commands"],
                "workspace_files": case["solution_workspace_files"],
                "max_counted_commands": case["max_counted_commands"],
            }
        }
    )
    client = APIClient()
    client.force_authenticate(user=learner.user)
    for index, step in enumerate(replays[old.slug]["steps"]):
        for edit in old.solution_workspace_files:
            if edit["after_command_index"] == index:
                response = client.patch(
                    f"/api/adventure-tier-runs/{assessed.id}/files/",
                    {"path": edit["path"], "content": edit["content"]},
                    format="json",
                )
                assert response.status_code == 200, response.content
        assessed.refresh_from_db()
        response = client.post(
            f"/api/adventure-tier-runs/{assessed.id}/submit-command/",
            {
                "command": step["command"],
                "execution": {
                    **step["execution"],
                    "cwd": step["cwd"],
                    "client_run_revision": assessed.total_attempts,
                },
            },
            format="json",
        )
        assert response.status_code == 200, response.content
    assessed.refresh_from_db()
    point.refresh_from_db()
    assert assessed.status == "completed" and point.passed is True
    monkeypatch.setattr(
        "progress.services.studies.timezone.now", lambda: cutoff + timedelta(seconds=1)
    )
    report = freeze_study(study)
    assert report["manifest"]["tiers"][0]["transfer"] == original_ref
    assert report["kpis"]["rta"]["value"] == 100
    assert report["coverage"]["transfer_missing"] == 0
    assert freeze_study(study) == report
    if destination := os.environ.get("RTA_STUDY_EVIDENCE_PATH"):
        Path(destination).write_text(
            json.dumps(
                {
                    "study": study.slug,
                    "pinned_reference": original_ref,
                    "assigned_variant_id": point.variant_id,
                    "completed_variant_id": assessed.selected_variant_id,
                    "completed_status": assessed.status,
                    "first_result": point.passed,
                    "frozen_rta": report["kpis"]["rta"],
                    "missing": report["coverage"]["transfer_missing"],
                    "repeat_freeze_unchanged": freeze_study(study) == report,
                },
                indent=2,
            ),
            encoding="utf-8",
        )


@pytest.mark.django_db
def test_overlapping_studies_cannot_reserve_conflicting_transfer_versions(django_user_model):
    call_command("seed_curriculum", verbosity=0)
    tier = AdventureLevelTier.objects.get(
        adventure_level__slug="resolving-conflicts-manually", difficulty="hard"
    )
    old = legacy_variant(tier, "manual-transfer-checkout-v2")
    learner = player(django_user_model, "overlapping-studies")
    cutoff = timezone.now() + timedelta(hours=1)
    study = create_study(
        slug="first-version", player_ids=[learner.id], tier_ids=[tier.id], cutoff=cutoff
    )
    conflicting_manifest = copy.deepcopy(study.manifest)
    study.manifest["tiers"][0]["transfer"] = {
        "id": old.id,
        "hash": old.ref_hash,
        "count": old.ref_count,
    }
    study.save(update_fields=["manifest"])
    call_command("seed_curriculum", verbosity=0)
    with pytest.raises(ValidationError, match="different transfer version"):
        create_study(
            slug="conflicting-version", player_ids=[learner.id], tier_ids=[tier.id], cutoff=cutoff
        )
    # Pre-existing inconsistent data must not silently select either version.
    KpiStudy.objects.create(slug="historic-conflict", cutoff=cutoff, manifest=conflicting_manifest)
    AdventureLevelTierProgress.objects.create(player=learner, tier=tier, exposure_complete=True)
    assert assign_transfer(player=learner, tier=tier) is None


@pytest.mark.django_db
def test_expired_study_does_not_pin_a_new_live_checkpoint(django_user_model):
    call_command("seed_curriculum", verbosity=0)
    tier = AdventureLevelTier.objects.get(
        adventure_level__slug="resolving-conflicts-manually", difficulty="hard"
    )
    old = legacy_variant(tier, "manual-transfer-checkout-v2")
    learner = player(django_user_model, "expired-study")
    study = create_study(
        slug="expired-version",
        player_ids=[learner.id],
        tier_ids=[tier.id],
        cutoff=timezone.now() + timedelta(hours=1),
    )
    study.manifest["tiers"][0]["transfer"] = {
        "id": old.id,
        "hash": old.ref_hash,
        "count": old.ref_count,
    }
    study.cutoff = timezone.now() - timedelta(seconds=1)
    study.save(update_fields=["manifest", "cutoff"])
    call_command("seed_curriculum", verbosity=0)
    AdventureLevelTierProgress.objects.create(player=learner, tier=tier, exposure_complete=True)
    point = assign_transfer(player=learner, tier=tier)
    assert point.variant.slug == TRANSFER_CHECKPOINTS[tier.adventure_level.slug]["case_id"]


@pytest.mark.django_db
def test_unusable_study_pin_does_not_fall_back_to_a_replacement(django_user_model):
    learner, tier, scenario, versions = bundle(django_user_model, required=1)
    old = versions[1]
    create_study(
        slug="unusable-pin",
        player_ids=[learner.id],
        tier_ids=[tier.id],
        cutoff=timezone.now() + timedelta(hours=1),
    )
    old.parameter_context = {"retired_transfer": True}
    old.ref_count = None
    old.save(update_fields=["parameter_context", "ref_count"])
    current = variant(scenario, "replacement-for-pinned", "transfer")
    assert current.ref_count
    AdventureLevelTierProgress.objects.create(player=learner, tier=tier, exposure_complete=True)
    assert assign_transfer(player=learner, tier=tier) is None


@pytest.mark.django_db
def test_prerequisite_mastery_refreshes_an_already_mastered_dependent_tier(django_user_model):
    learner, manual, _, _ = bundle(django_user_model, required=1)
    manual.adventure_level.slug = "resolving-conflicts-manually"
    manual.adventure_level.save(update_fields=["slug"])
    level = AdventureLevel.objects.create(
        chapter=manual.adventure_level.chapter,
        slug="using-a-merge-tool",
        title="Tool",
        is_required=True,
    )
    tool = AdventureLevelTier.objects.create(adventure_level=level, difficulty="hard")
    medium = AdventureLevelTier.objects.create(adventure_level=level, difficulty="medium")
    AdventureLevelTierCompletion.objects.create(player=learner, tier=medium)
    scenario = AdventureLevelTierScenario.objects.create(
        tier=tool, slug="tool-scenario", min_counted_commands=3, max_counted_commands=8
    )
    variant(scenario, "tool-practice", "practice")
    checkpoint = variant(scenario, "tool-transfer", "transfer")
    checkpoint.parameter_context = {
        "transfer_revision": 2,
        "transfer_prerequisites": ["resolving-conflicts-manually"],
    }
    checkpoint.ref_hash = ref_hash(checkpoint)
    checkpoint.save(update_fields=["parameter_context", "ref_hash"])
    end(start(learner, tool))
    assert not KpiCheckpoint.objects.filter(player=learner, tier=tool, kind="transfer").exists()
    report = MetricsService().performance_summary(player=learner)
    assert report["samples"]["transfer_missing"] == 0
    end(start(learner, manual))
    assert (
        KpiCheckpoint.objects.get(player=learner, tier=tool, kind="transfer").variant_id
        == checkpoint.id
    )


@pytest.mark.django_db
def test_study_requires_declared_practice_assigned_or_already_mastered(django_user_model):
    call_command("seed_curriculum", verbosity=0)
    learner = player(django_user_model, "prerequisite-study")
    tool = AdventureLevelTier.objects.get(
        adventure_level__slug="using-a-merge-tool", difficulty="hard"
    )
    manual = AdventureLevelTier.objects.get(
        adventure_level__slug="resolving-conflicts-manually", difficulty="hard"
    )
    kwargs = dict(player_ids=[learner.id], cutoff=timezone.now() + timedelta(hours=1))
    with pytest.raises(ValidationError, match="prerequisite"):
        create_study(slug="unfair-study", tier_ids=[tool.id], **kwargs)
    assert create_study(slug="fair-study", tier_ids=[tool.id, manual.id], **kwargs)
    AdventureLevelTierCompletion.objects.create(player=learner, tier=manual)
    assert create_study(slug="practised-study", tier_ids=[tool.id], **kwargs)


@pytest.mark.django_db
def test_new_reference_hash_binds_assessment_requirements_but_legacy_retirement_does_not(
    django_user_model,
):
    _, _, _, variants = bundle(django_user_model)
    old = variants[1]
    original = old.ref_hash
    old.parameter_context = {**old.parameter_context, "retired_transfer": True}
    assert ref_hash(old) == original

    old.parameter_context["transfer_revision"] = 2
    revised = ref_hash(old)
    assert revised != original
    old.parameter_context["transfer_prerequisites"] = ["resolving-conflicts-manually"]
    assert ref_hash(old) != revised
    revised = ref_hash(old)
    old.parameter_context["required_techniques"] = ["mergetool"]
    assert ref_hash(old) != revised


@pytest.mark.django_db
def test_tightened_index_version_preserves_original_revision_two_assignments(django_user_model):
    call_command("seed_curriculum", verbosity=0)
    tier = AdventureLevelTier.objects.get(
        adventure_level__slug="unstaging-and-discarding-changes", difficulty="hard"
    )
    old = legacy_variant(tier, "restore-transfer-contaminated-index")
    baseline_hash = "c2b016e51f4fea1f02bb8d49217f05a68a03472b1dfa2c6d97faf1c1a5b66264"
    assert old.ref_hash == baseline_hash
    assert old.parameter_context["transfer_revision"] == 2
    old_context = copy.deepcopy(old.scenario_context)
    old_spec = copy.deepcopy(old.evaluation_spec)
    learners = []
    for status in ("pending", "active", "concluded"):
        learner = player(django_user_model, f"index-{status}")
        AdventureLevelTierCompletion.objects.create(player=learner, tier=tier)
        point = KpiCheckpoint.objects.create(
            player=learner,
            tier=tier,
            kind="transfer",
            variant=old,
            ref_hash=old.ref_hash,
            ref_count=old.ref_count,
        )
        run = start(learner, tier, transfer=True) if status != "pending" else None
        if status == "concluded":
            end(run, passed=False)
        learners.append((status, learner, point, run))
    call_command("seed_curriculum", verbosity=0)
    old.refresh_from_db()
    assert old.evaluation_spec == old_spec and old.scenario_context == old_context
    assert old.ref_hash == ref_hash(old) == baseline_hash
    assert old.parameter_context["retired_transfer"] is True
    current = AdventureLevelTierScenarioVariant.objects.get(
        case_id="restore-transfer-contaminated-index-v2"
    )
    assert current.ref_hash != old.ref_hash
    evidence = {
        "legacy_hash": old.ref_hash,
        "current_hash": current.ref_hash,
        "legacy_retired": True,
        "legacy_content_unchanged": True,
        "assignments": [],
    }
    for status, learner, point, run in learners:
        resumed = start(learner, tier, transfer=True)
        point.refresh_from_db()
        assert resumed.selected_variant_id == old.id and point.variant_id == old.id
        if status == "active":
            assert resumed.id == run.id
        if status == "concluded":
            assert resumed.is_replay and point.run_id == run.id and point.passed is False
        evidence["assignments"].append(
            {
                "status": status,
                "variant": resumed.selected_variant.slug,
                "original_first_failure_preserved": status == "concluded" and point.passed is False,
            }
        )
    if destination := os.environ.get("TIGHTENING_CUTOVER_EVIDENCE_PATH"):
        Path(destination).write_text(json.dumps(evidence, indent=2), encoding="utf-8")
