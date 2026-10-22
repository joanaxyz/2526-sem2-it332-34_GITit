import json
import os
from datetime import timedelta
from pathlib import Path

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from adventures.models import AdventureLevelTierRun
from players.services import get_or_create_player
from progress.models import AdventureLevelTierCompletion
from progress.services import MetricsService
from progress.services.studies import _weighted, create_study, freeze_study
from testing.kpi_fixtures import bundle, end, start


def test_predefined_module_weights_prevent_larger_modules_dominating():
    def row(module, mastered, transfer):
        return {
            "module": module,
            "difficulty": "hard",
            "mastered": mastered,
            "car": 100 if mastered else 0,
            "failures": 0,
            "transfer": transfer,
        }

    records = [row(1, True, None), row(1, True, None), row(3, False, 1)]
    scores = _weighted(records, {"1": 1, "3": 1})
    assert scores["scr"] == 50  # Equal modules, despite two tiers in Module 1.
    assert scores["car"] == 50
    assert scores["rta"] == 100  # Module 1 is outside the RTA domain.
    assert _weighted(records, {"1": 1, "3": 3})["scr"] == 25
    assert _weighted([*records, row(4, True, None)], {"1": 1, "3": 1, "4": 1})["rta"] is None


@pytest.mark.django_db
def test_fixed_assignments_include_unattempted_and_freeze_ignores_later_practice(
    django_user_model, monkeypatch
):
    player, tier, _, _ = bundle(django_user_model, required=1)
    cutoff = timezone.now() + timedelta(hours=1)
    study = create_study(
        slug="cohort-v1", player_ids=[player.id], tier_ids=[tier.id], cutoff=cutoff
    )
    with pytest.raises(ValidationError, match="cutoff"):
        freeze_study(study)
    monkeypatch.setattr(
        "progress.services.studies.timezone.now", lambda: cutoff + timedelta(seconds=1)
    )
    report = freeze_study(study)
    assert report["kpis"]["scr"]["value"] == 0
    assert report["kpis"]["car"]["value"] == 0
    assert report["kpis"]["hlcr"]["value"] == 0
    assert report["kpis"]["arc"]["value"] is None
    assert report["kpis"]["rta"]["value"] == 0
    assert report["unattempted"] == 1
    assert report["coverage"]["attempted_tiers"] == 0
    end(start(player, tier))
    end(start(player, tier, transfer=True))
    assert freeze_study(study) == report


@pytest.mark.django_db
def test_cohort_averages_people_and_normalizes_rta_over_modules_3_4(django_user_model, monkeypatch):
    player, tier, _, _ = bundle(django_user_model, required=1)
    other = get_or_create_player(django_user_model.objects.create_user(username="light-user"))
    medium = tier.adventure_level.tiers.get(difficulty="medium")
    AdventureLevelTierCompletion.objects.create(player=other, tier=medium)
    cutoff = timezone.now() + timedelta(hours=1)
    study = create_study(
        slug="equal-v1", player_ids=[player.id, other.id], tier_ids=[tier.id], cutoff=cutoff
    )
    for _ in range(7):
        end(start(player, tier), passed=False)
    end(start(player, tier), count=4)
    end(start(other, tier), count=3)
    end(start(player, tier, transfer=True))
    end(start(other, tier, transfer=True), passed=False)
    live = MetricsService().all_player_performance_summary()
    assert live["kpis"]["car"]["value"] == 87.5
    assert live["kpis"]["car"]["unit"] == "participants"
    assert live["kpis"]["scr"]["value"] == 100
    monkeypatch.setattr(
        "progress.services.studies.timezone.now", lambda: cutoff + timedelta(seconds=1)
    )
    report = freeze_study(study)
    assert report["kpis"]["scr"]["value"] == 100
    assert report["kpis"]["car"]["value"] == 87.5
    assert report["kpis"]["arc"]["value"] == 3.5
    assert report["kpis"]["rta"]["value"] == 50
    assert len(report["participants"]) == 2
    if os.environ.get("KPI_STUDY_EVIDENCE_PATH"):
        Path(os.environ["KPI_STUDY_EVIDENCE_PATH"]).write_text(
            json.dumps(report, indent=2), encoding="utf-8"
        )


@pytest.mark.django_db
def test_run_crossing_cutoff_cannot_retroactively_complete_an_assignment(
    django_user_model, monkeypatch
):
    player, tier, _, _ = bundle(django_user_model, required=1)
    cutoff = timezone.now() + timedelta(hours=1)
    study = create_study(
        slug="cutoff-v1", player_ids=[player.id], tier_ids=[tier.id], cutoff=cutoff
    )
    run = end(start(player, tier))
    AdventureLevelTierRun.objects.filter(pk=run.pk).update(ended_at=cutoff + timedelta(seconds=1))
    monkeypatch.setattr(
        "progress.services.studies.timezone.now", lambda: cutoff + timedelta(seconds=2)
    )
    report = freeze_study(study)
    assert report["kpis"]["scr"]["value"] == 0
    assert report["kpis"]["car"]["value"] == 0
    assert report["unattempted"] == 0


@pytest.mark.django_db
def test_study_rejects_retroactive_enrollment_and_missing_reference(django_user_model):
    player, tier, _, variants = bundle(django_user_model, required=1)
    variants[0].ref_hash = "stale"
    variants[0].save(update_fields=["ref_hash"])
    with pytest.raises(ValidationError, match="Validate"):
        create_study(
            slug="bad-ref",
            player_ids=[player.id],
            tier_ids=[tier.id],
            cutoff=timezone.now() + timedelta(days=1),
        )

    end(start(player, tier))
    with pytest.raises(ValidationError, match="Enroll before"):
        create_study(
            slug="late",
            player_ids=[player.id],
            tier_ids=[tier.id],
            cutoff=timezone.now() + timedelta(days=1),
        )


@pytest.mark.django_db
def test_changed_required_clears_are_missing_evidence_not_failed_mastery(
    django_user_model, monkeypatch
):
    player, tier, scenario, _ = bundle(django_user_model, required=3)
    cutoff = timezone.now() + timedelta(hours=1)
    study = create_study(
        slug="changed-requirement", player_ids=[player.id], tier_ids=[tier.id], cutoff=cutoff
    )
    # A reseed now gives the tier a single scenario: mastery means something else.
    tier.scenarios.exclude(id=scenario.id).update(is_published=False)
    end(start(player, tier))
    monkeypatch.setattr(
        "progress.services.studies.timezone.now", lambda: cutoff + timedelta(seconds=1)
    )
    report = freeze_study(study)
    assert report["kpis"]["scr"]["value"] is None
    assert report["kpis"]["car"]["value"] is None
    assert report["kpis"]["rta"]["value"] is None
    assert report["coverage"]["mastery_missing"] == 1
