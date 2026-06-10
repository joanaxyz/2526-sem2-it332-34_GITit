from common.constants import (
    COMMAND_ACCURACY_PROGRESS_THRESHOLD,
    SESSION_STATUS_ABANDONED,
    SESSION_STATUS_FAILED,
    SESSION_STATUS_STARTED,
)
from challenges.models import ChallengeQuest, ChallengeRun


def required_successful_attempts_for_problem(problem) -> int:
    return int(getattr(problem, "required_successful_attempts", 1) or 1)


def minimum_counted_for_session(*, session: ChallengeRun) -> int:
    snapshot = session.command_budget_snapshot or {}
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


def session_meets_progress_threshold(*, session: ChallengeRun) -> bool:
    rate = command_accuracy_rate(
        status=session.status,
        counted_action_total=session.counted_action_total,
        minimum_counted_commands=minimum_counted_for_session(session=session),
    )
    return rate is not None and rate >= COMMAND_ACCURACY_PROGRESS_THRESHOLD


def get_challenge_quest(level_id: int) -> ChallengeQuest:
    return (
        ChallengeQuest.objects.select_related("scenario", "scenario__module")
        .prefetch_related("variants")
        .get(
            id=level_id,
            is_published=True,
            scenario__is_published=True,
            scenario__module__is_published=True,
        )
    )
