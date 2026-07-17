from __future__ import annotations

from dataclasses import dataclass, field

from challenges.models import ChallengeLevel, ChallengeRun, ChallengeTrial
from common.constants import (
    DIFFICULTY_EASY,
    DIFFICULTY_MEDIUM,
    SESSION_STATUS_STARTED,
)
from curriculum.models import CommandForm

from .access_helpers import _completion_payload, _latest_attempt_payload, _ordered_trials
from .adventure_access import _adventure_passed


@dataclass(frozen=True)
class ChallengeAccessContext:
    """Per-page batch of every user-specific fact the level payloads need, so
    serializing a page of challenges costs a fixed handful of queries instead
    of several per level."""

    completions: dict[int, object] = field(default_factory=dict)
    level_completions: set[int] = field(default_factory=set)
    latest_runs: dict[int, ChallengeRun] = field(default_factory=dict)
    adventure_passed: bool = False


def _build_challenge_access(
    *,
    player,
    chapter_id: int,
    challenges: list[ChallengeLevel],
    adventure_passed: bool | None = None,
) -> ChallengeAccessContext:
    from progress.models import ChallengeLevelCompletion, ChallengeTrialCompletion

    if player is None:
        return ChallengeAccessContext()
    if adventure_passed is None:
        adventure_passed = _adventure_passed(player=player, chapter_id=chapter_id)
    challenge_levels = list(challenges)
    challenge_level_ids = [level.id for level in challenge_levels]
    trial_ids = [trial.id for level in challenge_levels for trial in level.trials.all()]
    if not trial_ids:
        return ChallengeAccessContext(adventure_passed=adventure_passed)

    completions = {
        completion.challenge_trial_id: completion
        for completion in ChallengeTrialCompletion.objects.filter(
            player=player, challenge_trial_id__in=trial_ids
        )
    }
    level_completions = set(
        ChallengeLevelCompletion.objects.filter(
            player=player,
            challenge_level_id__in=challenge_level_ids,
        ).values_list("challenge_level_id", flat=True)
    )

    latest_runs: dict[int, ChallengeRun] = {}
    runs = (
        ChallengeRun.objects.filter(player=player, challenge_trial_id__in=trial_ids)
        .order_by("id")
        .only(
            "id",
            "is_replay",
            "status",
            "challenge_trial_id",
            "counted_action_total",
            "min_counted_commands",
            "max_counted_commands",
            "stars",
            "total_attempts",
            "completed_at",
            "ended_at",
        )
    )
    for run in runs:
        # Started runs are not resumable sessions. The map only receives
        # completed/failed historical attempts; active rows are discarded by
        # launch/retry/leave flows and never become navigation targets.
        if run.status != SESSION_STATUS_STARTED:
            latest_runs[run.challenge_trial_id] = run

    return ChallengeAccessContext(
        completions=completions,
        level_completions=level_completions,
        latest_runs=latest_runs,
        adventure_passed=adventure_passed,
    )


def challenge_summary_payload(
    *,
    challenge: ChallengeLevel,
    access: ChallengeAccessContext,
    sibling_levels: list[ChallengeLevel] | None = None,
) -> dict:
    if sibling_levels is None:
        sibling_levels = list(
            ChallengeLevel.objects.filter(
                chapter_id=challenge.chapter_id,
                is_published=True,
            ).prefetch_related("trials")
        )
        sibling_levels.sort(key=lambda level: (level.sort_order, level.id))
    level_payload = challenge_level_access_payload(
        level=challenge,
        access=access,
        sibling_levels=sibling_levels,
    )
    return {
        "item_type": "challenge",
        "id": challenge.id,
        "slug": challenge.slug,
        "title": challenge.title,
        "summary": challenge.summary,
        "narrative": challenge.narrative,
        **level_payload,
    }


def challenge_levels_access_payload(*, player, challenge: ChallengeLevel) -> list[dict]:
    """Per-level access for every sibling challenge level."""
    access = _build_challenge_access(
        player=player, chapter_id=challenge.chapter_id, challenges=[challenge]
    )
    ordered = list(ChallengeLevel.objects.filter(chapter_id=challenge.chapter_id, is_published=True).prefetch_related("trials"))
    ordered.sort(key=lambda level: (level.sort_order, level.id))
    return [
        challenge_level_access_payload(level=level, access=access, sibling_levels=ordered)
        for level in ordered
    ]


def challenge_level_access_payload(
    *,
    level: ChallengeLevel,
    access: ChallengeAccessContext,
    sibling_levels: list[ChallengeLevel],
) -> dict:
    trials = _ordered_trials(level.trials.all())
    trial_payloads = [
        challenge_trial_access_payload(
            trial=trial,
            access=access,
            sibling_levels=sibling_levels,
            sibling_trials=trials,
        )
        for trial in trials
    ]
    return {
        "id": level.id,
        "slug": level.slug,
        "title": level.title,
        "status": _challenge_level_status(
            level=level,
            access=access,
            sibling_levels=sibling_levels,
            trial_payloads=trial_payloads,
        ),
        "completed": level.id in access.level_completions,
        "locked": not _challenge_level_unlocked(
            level=level,
            access=access,
            sibling_levels=sibling_levels,
        ),
        "trials": trial_payloads,
    }


def challenge_trial_access_payload(
    *,
    trial: ChallengeTrial,
    access: ChallengeAccessContext,
    sibling_levels: list[ChallengeLevel],
    sibling_trials: list[ChallengeTrial],
) -> dict:
    completion = access.completions.get(trial.id)
    status = _challenge_status(
        trial=trial,
        access=access,
        sibling_levels=sibling_levels,
        sibling_trials=sibling_trials,
    )
    return {
        "id": trial.id,
        "difficulty": trial.difficulty,
        "status": status,
        "replay_available": bool(completion),
        "cleared": bool(completion),
        "latest_attempt": _latest_attempt_payload(access.latest_runs.get(trial.id)),
        "completion": _completion_payload(completion),
        "command_budget": _trial_budget(trial),
    }


def _trial_budget(trial: ChallengeTrial) -> dict:
    return {
        "min_counted_commands": trial.min_counted_commands,
        "max_counted_commands": trial.max_counted_commands,
    }


def get_command_form(form_id: int) -> CommandForm:
    return CommandForm.objects.select_related("command_skill", "chapter").get(
        id=form_id,
        is_published=True,
        command_skill__is_published=True,
        chapter__is_published=True,
    )


def _challenge_status(
    *,
    trial: ChallengeTrial,
    access: ChallengeAccessContext,
    sibling_levels: list[ChallengeLevel],
    sibling_trials: list[ChallengeTrial],
    ) -> str:
    if trial.id in access.completions:
        return "completed"
    if _challenge_unlocked(
        trial=trial,
        access=access,
        sibling_levels=sibling_levels,
        sibling_trials=sibling_trials,
    ):
        latest = access.latest_runs.get(trial.id)
        return (
            latest.status if latest and latest.status in {"failed", "abandoned"} else "not_started"
        )
    return "locked"


def _challenge_unlocked(
    *,
    trial: ChallengeTrial,
    access: ChallengeAccessContext,
    sibling_levels: list[ChallengeLevel],
    sibling_trials: list[ChallengeTrial],
) -> bool:
    if not _challenge_level_unlocked(
        level=trial.challenge_level,
        access=access,
        sibling_levels=sibling_levels,
    ):
        return False
    if trial.difficulty == DIFFICULTY_EASY:
        return access.adventure_passed
    previous = DIFFICULTY_EASY if trial.difficulty == DIFFICULTY_MEDIUM else DIFFICULTY_MEDIUM
    previous_trial = next(
        (
            candidate
            for candidate in sibling_trials
            if candidate.difficulty == previous and candidate.is_published
        ),
        None,
    )
    return bool(previous_trial and previous_trial.id in access.completions)


def _challenge_level_status(
    *,
    level: ChallengeLevel,
    access: ChallengeAccessContext,
    sibling_levels: list[ChallengeLevel],
    trial_payloads: list[dict],
) -> str:
    if level.id in access.level_completions:
        return "completed"
    if not _challenge_level_unlocked(level=level, access=access, sibling_levels=sibling_levels):
        return "locked"
    if any(payload["status"] in {"failed", "abandoned"} for payload in trial_payloads):
        return "failed"
    return "not_started"


def _challenge_level_unlocked(
    *,
    level: ChallengeLevel,
    access: ChallengeAccessContext,
    sibling_levels: list[ChallengeLevel],
) -> bool:
    previous = [
        candidate
        for candidate in sibling_levels
        if candidate.is_published and (candidate.sort_order, candidate.id) < (level.sort_order, level.id)
    ]
    if not previous:
        return True
    previous_level = sorted(previous, key=lambda item: (item.sort_order, item.id))[-1]
    return previous_level.id in access.level_completions
