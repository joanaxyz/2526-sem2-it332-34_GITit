from challenges.models import ChallengeLevel, ChallengeRun
from common.constants import (
    COMMAND_ACCURACY_PROGRESS_THRESHOLD,
    SESSION_STATUS_ABANDONED,
    SESSION_STATUS_FAILED,
    SESSION_STATUS_STARTED,
)


def required_successful_attempts_for_level(level) -> int:
    return int(getattr(level, "required_successful_attempts", 1) or 1)


def minimum_counted_for_run(*, run: ChallengeRun) -> int:
    snapshot = run.command_budget_snapshot or {}
    return int(snapshot.get("min_counted_commands", 0) or 0)


def command_accuracy_rate(
    *,
    status: str,
    counted_action_total: int,
    minimum_counted_commands: int,
) -> int | None:
    if status == SESSION_STATUS_STARTED:
        return None
    if status in {SESSION_STATUS_FAILED, SESSION_STATUS_ABANDONED}:
        return 0
    if counted_action_total <= minimum_counted_commands:
        return 100
    if minimum_counted_commands == 0:
        return 0
    return round((minimum_counted_commands / counted_action_total) * 100)


def run_meets_progress_threshold(*, run: ChallengeRun) -> bool:
    rate = command_accuracy_rate(
        status=run.status,
        counted_action_total=run.counted_action_total,
        minimum_counted_commands=minimum_counted_for_run(run=run),
    )
    return rate is not None and rate >= COMMAND_ACCURACY_PROGRESS_THRESHOLD


def get_challenge_level(level_id: int) -> ChallengeLevel:
    return (
        ChallengeLevel.objects.select_related("challenge", "challenge__storey")
        .prefetch_related("challenge_variants")
        .get(
            id=level_id,
            is_published=True,
            challenge__is_published=True,
            challenge__storey__is_published=True,
        )
    )
