import json
import os
from datetime import date, datetime, timedelta
from pathlib import Path

import pytest
from django.db.models import RestrictedError
from django.utils import timezone
from rest_framework.test import APIClient

from adventures.models import AdventureLevelTierProgress
from adventures.services import (
    AdventureLevelTierCommandProcessingService,
    AdventureLevelTierRunService,
)
from common.exceptions import Locked
from practice.models import CommandStep
from progress.models import AdventureLevelTierCompletion, KpiCheckpoint, KpiExposure
from progress.serializers import PerformanceSummaryResponseSerializer
from progress.services import MetricsService
from progress.services.kpi_range import KPI_TIMEZONE, KpiRange
from progress.services.mastery_metrics import car_score
from testing.frontend_execution import frontend_execution_payload
from testing.kpi_fixtures import bundle, end, routes, start


@pytest.mark.django_db
def test_five_kpis_use_one_mastery_record_and_preserve_first_transfer(django_user_model):
    player, tier, scenario, variants = bundle(django_user_model)
    prior = None
    for passed in (False, True, False, True):
        prior = end(start(player, tier, prior_run=prior), passed=passed)
    run = start(player, tier, prior_run=prior)
    assert run.retry_index == 2
    service = AdventureLevelTierCommandProcessingService()
    # The assessed run includes a real invalid command before the three-command solution.
    service.submit_command(
        run=run,
        command="git nonsense",
        execution=frontend_execution_payload(
            "git nonsense",
            run.repository_state,
            processed=False,
            exit_code=129,
            command_family="",
            client_run_revision=run.total_attempts,
        ),
    )
    _, _, replays = routes()
    replay = replays["practice"]
    for index, step in enumerate(replay["steps"]):
        next_state = (
            replay["steps"][index + 1]["ready"]
            if index + 1 < len(replay["steps"])
            else replay["final"]
        )
        service.submit_command(
            run=run,
            command=step["command"],
            execution=frontend_execution_payload(
                step["command"],
                next_state,
                client_run_revision=run.total_attempts,
            ),
        )
    assert run.status == "completed"
    assert run.counted_action_total == 4
    transfer = end(start(player, tier, transfer=True))
    assert transfer.is_transfer and not transfer.is_replay
    from adventures.tier_payloads import tier_run_payload

    payload = tier_run_payload(transfer)
    assert (
        payload["stars"] == 0
        and payload["completion"] is None
        and payload["next_difficulty"] is None
    )
    assert payload["progress"] == {
        "completed": 1,
        "total": 1,
        "cleared": True,
        "next_scenario": None,
    }
    report = MetricsService().performance_summary(player=player)
    assert {key: report["kpis"][key]["value"] for key in ("scr", "car", "hlcr", "arc", "rta")} == {
        "scr": 100,
        "car": 75,
        "hlcr": 100,
        "arc": 2,
        "rta": 100,
    }
    assert report["kpis"]["arc"]["denominator"] == 1
    assert report["kpis"]["scr"]["denominator"] == 1
    assert AdventureLevelTierProgress.objects.get(player=player, tier=tier).successful_clears == 3
    checkpoint = KpiCheckpoint.objects.get(player=player, tier=tier, kind="car")
    assert checkpoint.run_id == run.id and checkpoint.actual == 4
    end(start(player, tier), count=3)  # A better replay may replace the best-star pointer.
    assert MetricsService().performance_summary(player=player)["kpis"] == report["kpis"]
    assert MetricsService().admin_player_performance_summary(player=player) == report
    client = APIClient()
    client.force_authenticate(user=player.user)
    response = client.get("/api/progress/performance/")
    assert response.status_code == 200
    assert PerformanceSummaryResponseSerializer(data=response.json()).is_valid()
    assert response.json()["kpis"] == report["kpis"]
    if os.environ.get("KPI_EVIDENCE_PATH"):
        Path(os.environ["KPI_EVIDENCE_PATH"]).write_text(
            json.dumps(
                {
                    "history": ["failure", "success", "failure", "success", "success"],
                    "assessment_run": run.id,
                    "reference": 3,
                    "actual": 4,
                    "transfer_run": transfer.id,
                    "response": response.json(),
                },
                indent=2,
            ),
            encoding="utf-8",
        )


@pytest.mark.django_db
def test_repetitions_are_not_retries_and_abandonments_are(django_user_model):
    player, tier, _, _ = bundle(django_user_model)
    first = end(start(player, tier))
    second = end(start(player, tier, prior_run=first))
    assert second.retry_index == 0 and second.stars == 3
    empty = start(player, tier, prior_run=second)
    empty_id = empty.id
    AdventureLevelTierRunService().discard(run=empty)
    assert KpiExposure.objects.filter(player=player).exists()
    run = start(player, tier)
    assert run.retry_index == 0
    service = AdventureLevelTierCommandProcessingService()
    service.submit_command(
        run=run,
        command="git nonsense",
        execution=frontend_execution_payload(
            "git nonsense",
            run.repository_state,
            processed=False,
            exit_code=129,
            command_family="",
            client_run_revision=run.total_attempts,
        ),
    )
    AdventureLevelTierRunService().discard(run=run)
    final = end(start(player, tier))
    assert final.id != empty_id and final.retry_index == 1
    report = MetricsService().performance_summary(player=player)
    assert report["kpis"]["arc"]["value"] == 1
    assert report["kpis"]["scr"]["denominator"] == 1


@pytest.mark.django_db
def test_failed_transfer_cannot_be_erased_even_by_empty_restart(django_user_model):
    player, tier, _, _ = bundle(django_user_model, required=1)
    end(start(player, tier))
    point = KpiCheckpoint.objects.get(player=player, tier=tier, kind="transfer")
    first = start(player, tier, transfer=True)
    assert start(player, tier, transfer=True).id == first.id
    AdventureLevelTierRunService().discard(run=first)
    point.refresh_from_db()
    assert point.passed is False
    with pytest.raises(Locked):
        start(player, tier, transfer=True)
    end(start(player, tier))
    assert MetricsService().performance_summary(player=player)["kpis"]["rta"]["value"] == 0


@pytest.mark.django_db
def test_legacy_reference_and_exposure_gaps_stay_missing(django_user_model):
    player, tier, _, variants = bundle(django_user_model, required=1)
    variants[0].ref_hash = "stale"
    variants[0].save(update_fields=["ref_hash"])
    AdventureLevelTierProgress.objects.create(player=player, tier=tier, exposure_complete=False)
    end(start(player, tier))
    report = MetricsService().performance_summary(player=player)
    assert report["kpis"]["scr"]["value"] == 100
    assert report["kpis"]["car"]["value"] is None
    assert report["kpis"]["rta"]["value"] is None
    assert report["samples"]["car_missing"] == 1
    assert report["samples"]["transfer_missing"] == 1


@pytest.mark.django_db
def test_changed_transfer_objective_is_missing_not_success_or_failure(django_user_model):
    player, tier, _, _ = bundle(django_user_model, required=1)
    end(start(player, tier))
    run = start(player, tier, transfer=True)
    run.selected_variant.solution_commands = [*run.selected_variant.solution_commands, "git status"]
    run.selected_variant.save(update_fields=["solution_commands"])
    end(run)
    report = MetricsService().performance_summary(player=player)
    assert report["kpis"]["rta"]["value"] is None
    assert report["samples"]["transfer_missing"] == 1
    assert report["samples"]["transfer_pending"] == 0


@pytest.mark.django_db
def test_changed_pending_transfer_is_missing_and_has_no_start_link(django_user_model):
    player, tier, _, variants = bundle(django_user_model, required=1)
    end(start(player, tier))
    assert MetricsService().performance_summary(player=player)["transfers"]
    variants[1].solution_commands = [*variants[1].solution_commands, "git status"]
    variants[1].save(update_fields=["solution_commands"])
    report = MetricsService().performance_summary(player=player)
    assert report["kpis"]["rta"]["value"] is None
    assert report["samples"]["transfer_missing"] == 1
    assert report["samples"]["transfer_pending"] == 0
    assert report["transfers"] == []
    with pytest.raises(Locked):
        start(player, tier, transfer=True)


@pytest.mark.django_db
def test_unpublished_scenario_does_not_rollback_a_valid_mastery(django_user_model):
    player, tier, scenario, _ = bundle(django_user_model, required=1)
    run = start(player, tier)
    scenario.is_published = False
    scenario.save(update_fields=["is_published"])
    end(run)
    assert AdventureLevelTierCompletion.objects.filter(player=player, tier=tier).exists()
    assert not KpiCheckpoint.objects.filter(player=player, tier=tier, kind="transfer").exists()


@pytest.mark.django_db
def test_ranged_mastery_is_dated_by_first_clear_not_best_score(django_user_model):
    player, tier, _, _ = bundle(django_user_model, required=1)
    run = end(start(player, tier), count=5)
    mastered_at = datetime(2026, 10, 5, 12, tzinfo=KPI_TIMEZONE)
    type(run).objects.filter(pk=run.pk).update(
        started_at=mastered_at, ended_at=mastered_at, completed_at=mastered_at
    )
    KpiCheckpoint.objects.filter(player=player, tier=tier, kind="car").update(
        assigned_at=mastered_at, ended_at=mastered_at
    )
    assert end(start(player, tier), count=3).is_replay
    # The better replay moved the completion's timestamp past the range end.
    AdventureLevelTierCompletion.objects.filter(player=player, tier=tier).update(
        completed_at=mastered_at + timedelta(days=10)
    )
    october = KpiRange(start_date=date(2026, 10, 1), end_date=date(2026, 10, 10))
    report = MetricsService().all_player_performance_summary(kpi_range=october)
    assert report["kpis"]["scr"]["value"] == 100
    # Without the immutable checkpoint, the last non-replay clear dates mastery.
    KpiCheckpoint.objects.filter(player=player, tier=tier).delete()
    report = MetricsService().all_player_performance_summary(kpi_range=october)
    assert report["kpis"]["scr"]["value"] == 100


@pytest.mark.django_db
def test_completion_rates_count_a_tier_once_it_has_an_outcome(django_user_model):
    player, tier, _, _ = bundle(django_user_model, required=1)
    run = start(player, tier)

    def scr():
        report = MetricsService().performance_summary(player=player)
        return report["kpis"]["scr"], report["samples"]

    # Opening a tier is not an attempt.
    rate, samples = scr()
    assert rate["denominator"] == 0 and samples["in_progress_tiers"] == 1
    step = CommandStep.objects.create(
        adventure_tier_run=run,
        command_text="git status",
        normalized_command="git status",
        command_classification="counted",
        result_category="target_not_yet_matched",
        was_processable=True,
        counted_increment=1,
        attempt_number=1,
        counted_total_after=1,
    )
    assert scr()[0]["denominator"] == 0  # Still working on it.
    CommandStep.objects.filter(pk=step.pk).update(created_at=timezone.now() - timedelta(days=8))
    rate, samples = scr()  # Left idle after typing commands: a drop-off.
    assert (rate["value"], rate["denominator"]) == (0, 1)
    assert (samples["attempted_tiers"], samples["in_progress_tiers"]) == (1, 0)
    end(run)
    assert scr()[0]["value"] == 100


@pytest.mark.django_db
def test_legacy_mastery_counts_meaningful_abandonments_as_retries(django_user_model):
    player, tier, _, _ = bundle(django_user_model, required=1)
    left = start(player, tier)
    CommandStep.objects.create(
        adventure_tier_run=left,
        command_text="git status",
        normalized_command="git status",
        command_classification="counted",
        result_category="target_not_yet_matched",
        was_processable=True,
        counted_increment=1,
        attempt_number=1,
        counted_total_after=1,
    )
    AdventureLevelTierRunService().discard(run=left)
    end(start(player, tier))
    # Histories from before checkpoints existed fall back to run evidence.
    KpiCheckpoint.objects.filter(player=player, tier=tier).delete()
    arc = MetricsService().performance_summary(player=player)["kpis"]["arc"]
    assert (arc["value"], arc["denominator"]) == (1, 1)


@pytest.mark.django_db
def test_deleting_a_learner_removes_their_checkpoints(django_user_model):
    player, tier, _, _ = bundle(django_user_model, required=1)
    run = end(start(player, tier))
    assert KpiCheckpoint.objects.filter(player=player).count() == 2
    with pytest.raises(RestrictedError):
        run.delete()  # A recorded assessment run cannot disappear on its own.
    player.user.delete()
    assert not KpiCheckpoint.objects.exists()


@pytest.mark.parametrize(
    "passed,target,actual,expected",
    [
        (True, 3, 4, 75),
        (False, 3, 3, 0),
        (True, 3, 2, 100),
        (True, 3, 0, 100),
        (True, None, 4, None),
    ],
)
def test_car_ratio(passed, target, actual, expected):
    assert car_score(passed=passed, target=target, actual=actual) == expected
