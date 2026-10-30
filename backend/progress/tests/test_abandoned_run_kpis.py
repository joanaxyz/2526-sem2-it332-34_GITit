"""Meaningful abandonment is an unsuccessful attempt, never an extra tier."""

from adventures.services import (
    AdventureLevelTierCommandProcessingService,
    AdventureLevelTierRunService,
)
from progress.services import MetricsService
from testing.frontend_execution import frontend_execution_payload
from testing.kpi_fixtures import bundle, end, start


def test_abandonment_counts_once_before_mastery(db, django_user_model):
    player, tier, _, _ = bundle(django_user_model, required=1)
    run = start(player, tier)
    AdventureLevelTierCommandProcessingService().submit_command(
        run=run,
        command="git nonsense",
        execution=frontend_execution_payload(
            "git nonsense",
            run.repository_state,
            processed=False,
            exit_code=129,
            command_family="",
            client_run_revision=0,
        ),
    )
    AdventureLevelTierRunService().discard(run=run)
    before = MetricsService().performance_summary(player=player)["kpis"]
    assert before["scr"]["value"] == 0 and before["scr"]["denominator"] == 1
    assert before["car"]["value"] is None and before["arc"]["value"] is None
    end(start(player, tier))
    after = MetricsService().performance_summary(player=player)["kpis"]
    assert after["scr"]["value"] == 100 and after["scr"]["denominator"] == 1
    assert after["arc"]["value"] == 1
