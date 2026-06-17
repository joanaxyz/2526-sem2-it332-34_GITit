"""Response-payload builders for challenge runs.

These are presenter-layer functions (DB reads, snapshots, visualization) that
used to live in serializers.py; serializers now hold input validation only.
Payload shapes are part of the frontend contract - change them deliberately.
"""

from battle.payloads import battle_block, stage_payload
from challenges.models import ChallengeRun
from challenges.selectors import required_successful_attempts_for_level
from common.constants import (
    DIFFICULTIES,
    SESSION_MODE_PRIMARY,
    SESSION_MODE_REVIEW,
    SESSION_STATUS_COMPLETED,
    SESSION_STATUS_STARTED,
)
from practice.context import ScenarioContextNormalizer
from practice.scaffolding import ScaffoldingService
from practice.visualization import RepositoryVisualizationService
from progress.models import LevelCompletion
from simulator.services import RepositorySnapshotService


def prefetch_run_payload_context(run: ChallengeRun) -> None:
    if getattr(run, "_payload_context_loaded", False):
        return
    run._prefetched_completion = LevelCompletion.objects.filter(
        user_id=run.user_id,
        challenge_level_id=run.challenge_level_id,
    ).first()
    run._payload_context_loaded = True


def challenge_run_payload(run: ChallengeRun, *, include_steps: bool = True) -> dict:
    prefetch_run_payload_context(run)
    snapshotter = RepositorySnapshotService()
    visualizer = RepositoryVisualizationService()
    context = _scenario_context(run)
    repository_state = snapshotter.snapshot(run.repository_state, already_normalized=True)
    supports = ScaffoldingService().supports_for(run.challenge_level.difficulty)
    expected_target = run.variant.target_state
    target_state = run.variant.target_state if supports["expected_state"] else None
    # Stored repository_state is already normalized (the snapshotter calls beside
    # this rely on the same invariant), so the DAG snapshot can skip a redundant pass.
    visualization = visualizer.snapshot(
        run.repository_state, target_state=target_state, already_normalized=True
    )
    expected_state = (
        snapshotter.snapshot(expected_target, already_normalized=True)
        if supports["expected_state"] and expected_target
        else None
    )
    chapter_payload = {
        "id": run.chapter_id,
        "number": run.chapter.number,
        "title": run.chapter.title,
    }

    steps = list(run.steps.order_by("id")) if include_steps else []
    return {
        "id": run.id,
        "mode": run.mode,
        "status": run.status,
        "failure_reason": run.failure_reason or None,
        "completed_at": run.completed_at,
        "first_attempt_star_eligible": run.first_attempt_star_eligible,
        "challenge": _challenge_payload(run),
        "scenario_context": context,
        "chapter": chapter_payload,
        # Authored battle-stage dressing (background + artifacts); constant per
        # chapter so it rides the run payload, not the per-command patch.
        "battle_stage": stage_payload(run.chapter, user=run.user),
        "difficulty": run.difficulty or None,
        "variant": {
            "id": run.variant_id,
            "label": run.variant.label,
            "changed_variant": run.changed_variant,
            "looped_variant": run.looped_variant,
        },
        "mastery_progress": mastery_progress_payload(run),
        "policy": run.command_budget_snapshot,
        "counts": run_counts_payload(run),
        "scaffolding": supports,
        "repository_state": repository_state,
        "visualization": visualization,
        "expected_state": expected_state,
        # Boss roster for the battle strip; events ride only the per-command
        # response. Null for pre-battle runs means the client derives a fallback.
        "battle": battle_block(run.battle_state, user=run.user),
        "steps": [
            {
                "id": step.id,
                "command_text": step.command_text,
                "terminal_output": step.terminal_output,
                "result_category": step.result_category,
                "command_classification": step.command_classification,
                "contextual_feedback": step.contextual_feedback,
                "visualization_snapshot": step.visualization_snapshot,
                "created_at": step.created_at,
            }
            for step in steps
        ],
        "review_mode": run.mode == SESSION_MODE_REVIEW,
        "next_difficulty": next_difficulty_payload(run),
        "sibling_levels": sibling_levels_payload(run),
        "completion": completion_payload(run),
    }


def command_run_payload(run: ChallengeRun, *, repository_state: dict, visualization: dict) -> dict:
    payload = {
        "id": run.id,
        "mode": run.mode,
        "status": run.status,
        "failure_reason": run.failure_reason or None,
        "completed_at": run.completed_at,
        "first_attempt_star_eligible": run.first_attempt_star_eligible,
        "counts": run_counts_payload(run),
        "repository_state": repository_state,
        "visualization": visualization,
        "review_mode": run.mode == SESSION_MODE_REVIEW,
    }
    if run.status != SESSION_STATUS_STARTED:
        payload.update(
            {
                "mastery_progress": mastery_progress_payload(run),
                "completion": completion_payload(run),
                "next_difficulty": next_difficulty_payload(run),
                "sibling_levels": sibling_levels_payload(run),
            }
        )
    return payload


def mastery_progress_payload(run: ChallengeRun) -> dict:
    # Memoized on the run: the full payload needs this both directly and inside
    # next_difficulty_payload, and each COUNT costs a DB round trip.
    cached = getattr(run, "_mastery_progress_payload", None)
    if cached is not None:
        return cached
    required = required_successful_attempts_for_level(run.challenge_level)
    mastered_count = ChallengeRun.objects.filter(
        user_id=run.user_id,
        mode=SESSION_MODE_PRIMARY,
        status=SESSION_STATUS_COMPLETED,
        challenge_level_id=run.challenge_level_id,
        counted_action_total__lte=run.command_budget_snapshot["min_counted_commands"],
    ).count()
    payload = {"mastered": min(mastered_count, required), "required": required}
    run._mastery_progress_payload = payload
    return payload


def completion_payload(run: ChallengeRun) -> dict | None:
    completion = getattr(run, "_prefetched_completion", None)
    if completion is None and not getattr(run, "_payload_context_loaded", False):
        completion = LevelCompletion.objects.filter(user=run.user, challenge_level=run.challenge_level).first()
    if not completion:
        return None
    return {
        "first_attempt_star": completion.first_attempt_star,
        "counted_action_total": completion.counted_action_total,
        "completed_at": completion.completed_at,
    }


def run_counts_payload(run: ChallengeRun) -> dict:
    minimum = run.command_budget_snapshot["min_counted_commands"]
    maximum = run.command_budget_snapshot["max_counted_commands"]
    return {
        "counted_action_total": run.counted_action_total,
        "minimum_counted_commands": minimum,
        "maximum_counted_commands": maximum,
        "non_counted_diagnostic_total": run.non_counted_diagnostic_total,
        "remaining_counted_commands": max(0, maximum - run.counted_action_total),
        "max_reached": run.counted_action_total >= maximum,
        "total_attempts": run.total_attempts,
    }


def next_difficulty_payload(run: ChallengeRun) -> dict | None:
    if (
        run.mode != "primary"
        or run.status != SESSION_STATUS_COMPLETED
        or not run.challenge_level
    ):
        return None
    progress = mastery_progress_payload(run)
    if run.counted_action_total > run.command_budget_snapshot["min_counted_commands"]:
        return None
    if progress["mastered"] < progress["required"]:
        return None
    try:
        next_difficulty = DIFFICULTIES[DIFFICULTIES.index(run.challenge_level.difficulty) + 1]
    except (ValueError, IndexError):
        return None
    next_level = run.challenge_level.challenge.challenge_levels.filter(
        difficulty=next_difficulty,
        is_published=True,
    ).first()
    if not next_level:
        return None
    return {"id": next_level.id, "difficulty": next_level.difficulty}


def sibling_levels_payload(run: ChallengeRun) -> list[dict]:
    """Every level of this run's challenge (easy-to-hard) with the user's access state,
    powering the completion modal's level navigator. Imported lazily to avoid a
    challenges/curriculum import cycle at module load."""
    if not run.challenge_level:
        return []
    from curriculum.selectors import challenge_levels_access_payload

    return challenge_levels_access_payload(user=run.user, challenge=run.challenge_level.challenge)


def _scenario_context(run: ChallengeRun) -> dict:
    # The brief is authored on the level and shared across its variants; the
    # variant only carries a generated fallback, so the level's authored context
    # wins.
    raw = run.challenge_level.scenario_context or run.variant.scenario_context
    return ScenarioContextNormalizer().normalize(raw, fallback_story=run.challenge.narrative)


def _challenge_payload(run: ChallengeRun) -> dict:
    return {
        "id": run.challenge_id,
        "slug": run.challenge.slug,
        "title": run.challenge.title,
        "summary": run.challenge.summary,
        "narrative": run.challenge.narrative,
        "level_id": run.challenge_level_id,
    }
