"""Response-payload builders for challenge runs.

These are presenter-layer functions (DB reads, snapshots, visualization) that
used to live in serializers.py; serializers now hold input validation only.
Payload shapes are part of the frontend contract - change them deliberately.
"""

from challenges.models import ChallengeRun
from common.constants import (
    DIFFICULTIES,
    SESSION_STATUS_COMPLETED,
    SESSION_STATUS_STARTED,
)
from curriculum.stage_config import merged_battle_stage, stage_payload
from practice.services.context import ScenarioContextNormalizer
from practice.services.scaffolding import ScaffoldingService
from practice.services.visualization import RepositoryVisualizationService
from progress.models import ChallengeTrialCompletion
from simulator.services import RepositorySnapshotService


def prefetch_run_payload_context(run: ChallengeRun) -> None:
    if getattr(run, "_payload_context_loaded", False):
        return
    run._prefetched_completion = ChallengeTrialCompletion.objects.filter(
        player_id=run.player_id,
        challenge_trial_id=run.challenge_trial_id,
    ).first()
    run._payload_context_loaded = True


def challenge_run_payload(run: ChallengeRun, *, include_steps: bool = True) -> dict:
    prefetch_run_payload_context(run)
    snapshotter = RepositorySnapshotService()
    visualizer = RepositoryVisualizationService()
    context = _scenario_context(run)
    repository_state = snapshotter.snapshot(run.repository_state, already_normalized=True)
    supports = ScaffoldingService().supports_for(run.difficulty)
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
    chapter = run.chapter
    chapter_payload = {
        "id": chapter.id,
        "number": chapter.number,
        "title": chapter.title,
    }
    story = chapter.story if chapter.story_id else None
    story_payload = {
        "id": story.id,
        "slug": story.slug,
        "title": story.title,
        "world_slug": story.world_slug,
    } if story else None

    steps = list(run.steps.order_by("id")) if include_steps else []
    return {
        "id": run.id,
        "replay": run.is_replay,
        "stars": run.stars,
        "status": run.status,
        "failure_reason": run.failure_reason or None,
        "completed_at": run.completed_at,
        "challenge": _challenge_payload(run),
        "scenario_context": context,
        "chapter": chapter_payload,
        "story": story_payload,
        # Authored battle-stage backdrop; constant per chapter so it rides the
        # run payload, not the per-command patch.
        "battle_stage": stage_payload(
            merged_battle_stage(chapter=chapter, content_owner=run.challenge_trial.challenge_level)
        ),
        "difficulty": run.difficulty or None,
        # GitCoins paid on first completion of this trial (0 = no reward).
        "reward_coins": run.challenge_trial.reward_coins if run.challenge_trial_id else 0,
        "variant": {
            "id": run.variant_id,
            "label": run.variant.label,
        },
        "mastery_progress": mastery_progress_payload(run),
        "policy": {
            "min_counted_commands": run.min_counted_commands,
            "max_counted_commands": run.max_counted_commands,
        },
        "counts": run_counts_payload(run),
        "scaffolding": supports,
        "repository_state": repository_state,
        "visualization": visualization,
        "expected_state": expected_state,
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
        "next_difficulty": next_difficulty_payload(run),
        "sibling_levels": sibling_levels_payload(run),
        "completion": completion_payload(run),
    }


def command_run_payload(run: ChallengeRun, *, repository_state: dict, visualization: dict) -> dict:
    payload = {
        "id": run.id,
        "replay": run.is_replay,
        "stars": run.stars,
        "status": run.status,
        "failure_reason": run.failure_reason or None,
        "completed_at": run.completed_at,
        "counts": run_counts_payload(run),
        "repository_state": repository_state,
        "visualization": visualization,
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
    completion = getattr(run, "_prefetched_completion", None)
    cleared = completion is not None or ChallengeRun.objects.filter(
        player_id=run.player_id,
        is_replay=False,
        status=SESSION_STATUS_COMPLETED,
        challenge_trial_id=run.challenge_trial_id,
    ).exists()
    return {"cleared": cleared, "stars": run.stars}


def completion_payload(run: ChallengeRun) -> dict | None:
    completion = getattr(run, "_prefetched_completion", None)
    if completion is None and not getattr(run, "_payload_context_loaded", False):
        completion = ChallengeTrialCompletion.objects.filter(
            player=run.player,
            challenge_trial=run.challenge_trial,
        ).first()
    if not completion:
        return None
    return {
        "stars": completion.stars,
        "counted_action_total": completion.counted_action_total,
        "completed_at": completion.completed_at,
    }


def run_counts_payload(run: ChallengeRun) -> dict:
    minimum = run.min_counted_commands
    maximum = run.max_counted_commands
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
        run.is_replay
        or run.status != SESSION_STATUS_COMPLETED
        or not run.challenge_trial_id
    ):
        return None
    if not mastery_progress_payload(run)["cleared"]:
        return None
    try:
        next_difficulty = DIFFICULTIES[DIFFICULTIES.index(run.difficulty) + 1]
    except (ValueError, IndexError):
        return None
    next_trial = run.challenge_trial.challenge_level.trials.filter(
        difficulty=next_difficulty,
        is_published=True,
    ).first()
    if not next_trial:
        return None
    return {"id": next_trial.id, "difficulty": next_trial.difficulty}


def sibling_levels_payload(run: ChallengeRun) -> list[dict]:
    """Every trial of this run's challenge (easy-to-hard) with the user's access
    state, powering the completion modal's trial navigator. Imported lazily to
    avoid a challenges/curriculum import cycle at module load."""
    if not run.challenge_trial_id:
        return []
    from curriculum.selectors import challenge_levels_access_payload

    levels = challenge_levels_access_payload(player=run.player, challenge=run.challenge_trial.challenge_level)
    return [trial for level in levels for trial in level.get("trials", [])]


def _scenario_context(run: ChallengeRun) -> dict:
    variant = run.variant
    raw = (variant.scenario_context if variant else None) or {
        "schema_version": 3,
        "story": run.challenge_trial.story,
        "task": run.challenge_trial.task,
    }
    return ScenarioContextNormalizer().normalize(raw, fallback_story=run.challenge_trial.challenge_level.narrative)


def _challenge_payload(run: ChallengeRun) -> dict:
    level = run.challenge_trial.challenge_level
    return {
        "id": level.id,
        "slug": level.slug,
        "title": level.title,
        "summary": level.summary,
        "narrative": level.narrative,
        "challenge_level_id": level.id,
        "challenge_level_slug": level.slug,
        "challenge_level_title": level.title,
        "level_id": run.challenge_trial_id,
        "trial_id": run.challenge_trial_id,
    }
