"""Response-payload builders for AdventureLevelTierRun.

Mirrors challenges/payloads.py. Presenter-layer functions (DB reads,
snapshots, visualization) - serializers hold input validation only.
Payload shapes are part of the frontend contract - change them deliberately.
"""

from django.db.models import Q

from adventures.models import AdventureLevelTier, AdventureLevelTierRun
from adventures.rewards import claimed_tier_reward_keys, tier_reward_payload
from adventures.tier_scenarios import published_scenarios, scenario_progress
from common.constants import DIFFICULTIES, SESSION_STATUS_COMPLETED, SESSION_STATUS_STARTED
from practice.services.context import ScenarioContextNormalizer
from practice.services.scaffolding import ScaffoldingService
from practice.services.visualization import RepositoryVisualizationService
from progress.models import AdventureLevelTierCompletion
from simulator.services import RepositorySnapshotService
from tutoring.payloads import teaching_payload


def prefetch_run_payload_context(run: AdventureLevelTierRun) -> None:
    if getattr(run, "_payload_context_loaded", False):
        return
    run._prefetched_completion = AdventureLevelTierCompletion.objects.filter(
        player_id=run.player_id,
        tier_id=run.tier_id,
    ).first()
    run._payload_context_loaded = True


def tier_run_payload(run: AdventureLevelTierRun, *, include_steps: bool = True) -> dict:
    prefetch_run_payload_context(run)
    snapshotter = RepositorySnapshotService()
    visualizer = RepositoryVisualizationService()
    context = _scenario_context(run)
    repository_state = snapshotter.snapshot(run.repository_state, already_normalized=True)
    supports = ScaffoldingService().supports_for_tier(
        "hard" if run.is_transfer else run.tier.difficulty
    )
    expected_target = run.selected_variant.target_state
    target_state = run.selected_variant.target_state if supports["expected_state"] else None
    visualization = visualizer.snapshot(
        run.repository_state, target_state=target_state, already_normalized=True
    )
    expected_state = (
        snapshotter.snapshot(expected_target, already_normalized=True)
        if supports["expected_state"] and expected_target
        else None
    )
    adventure_level = run.tier.adventure_level
    chapter = adventure_level.chapter
    chapter_payload = None
    story_payload = None
    if chapter is not None:
        chapter_payload = {
            "id": chapter.id,
            "number": chapter.number,
            "title": chapter.title,
        }
        story = chapter.story if chapter.story_id else None
        story_payload = (
            {
                "id": story.id,
                "slug": story.slug,
                "title": story.title,
                "world_slug": story.world_slug,
            }
            if story
            else None
        )

    steps = list(run.steps.order_by("id")) if include_steps else []
    return {
        "id": run.id,
        **teaching_payload(run),
        "replay": run.is_replay,
        "transfer": run.is_transfer,
        "stars": run.stars,
        "status": run.status,
        "failure_reason": run.failure_reason or None,
        "completed_at": run.completed_at,
        "tier": _tier_payload(run),
        "scenario_context": context,
        "chapter": chapter_payload,
        "story": story_payload,
        "difficulty": run.tier.difficulty,
        "variant": {
            "id": run.selected_variant_id,
            "label": run.selected_variant.label,
            "changed_variant": run.changed_variant,
        },
        "scenario": scenario_payload(run),
        "progress": progress_payload(run),
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
        "completion": completion_payload(run),
        "reward": tier_reward_payload(
            run.tier,
            claimed_keys=claimed_tier_reward_keys(player=run.player, tiers=[run.tier]),
        ),
    }


def command_run_payload(
    run: AdventureLevelTierRun,
    *,
    repository_state: dict,
    visualization: dict,
    rewards: dict | None = None,
    tutor_context: dict | None = None,
) -> dict:
    """``tutor_context`` carries what the submission already read for the tutor."""

    payload = {
        "id": run.id,
        **teaching_payload(run, **(tutor_context or {})),
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
                "progress": progress_payload(run),
                "completion": completion_payload(run),
                "next_difficulty": next_difficulty_payload(run),
                "rewards": rewards,
            }
        )
    return payload


def progress_payload(run: AdventureLevelTierRun) -> dict:
    """The tier's scenario counter - "1/2" and the next scenario to play - sourced
    from AdventureLevelTierProgress (persists across runs), counted over the
    tier's published scenarios."""
    from adventures.models import AdventureLevelTierProgress

    if run.is_transfer:
        return {
            "completed": int(run.status == SESSION_STATUS_COMPLETED),
            "total": 1,
            "cleared": run.status == SESSION_STATUS_COMPLETED,
            "next_scenario": None,
        }
    # A solve already holds the row it just counted.
    progress = getattr(run, "_prefetched_progress", None)
    if progress is None:
        progress = AdventureLevelTierProgress.objects.filter(
            player_id=run.player_id, tier_id=run.tier_id
        ).first()
    prefetch_run_payload_context(run)
    return scenario_progress(
        _run_scenarios(run), progress, tier_completed=run._prefetched_completion is not None
    )


def scenario_payload(run: AdventureLevelTierRun) -> dict:
    """Which of the tier's scenarios this run plays, for the workspace header."""
    scenarios = _run_scenarios(run)
    index = next(
        (
            number
            for number, scenario in enumerate(scenarios, start=1)
            if scenario.id == run.current_scenario_id
        ),
        None,
    )
    return {
        "index": index,
        "total": len(scenarios),
        "title": run.current_scenario.title if run.current_scenario_id else "",
    }


def _run_scenarios(run: AdventureLevelTierRun) -> list:
    scenarios = getattr(run, "_published_scenarios", None)
    if scenarios is None:
        scenarios = run._published_scenarios = published_scenarios(run.tier)
    return scenarios


def completion_payload(run: AdventureLevelTierRun) -> dict | None:
    if run.is_transfer:
        return None
    completion = getattr(run, "_prefetched_completion", None)
    if completion is None and not getattr(run, "_payload_context_loaded", False):
        completion = AdventureLevelTierCompletion.objects.filter(
            player=run.player, tier=run.tier
        ).first()
    if not completion:
        return None
    return {
        "stars": completion.stars,
        "counted_action_total": completion.counted_action_total,
        "completed_at": completion.completed_at,
    }


def run_counts_payload(run: AdventureLevelTierRun) -> dict:
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


def next_difficulty_payload(run: AdventureLevelTierRun) -> dict | None:
    if (
        run.is_transfer
        or run.is_replay
        or run.status != SESSION_STATUS_COMPLETED
        or not run.tier_id
    ):
        return None
    if not progress_payload(run)["cleared"]:
        return None
    try:
        next_difficulty = DIFFICULTIES[DIFFICULTIES.index(run.tier.difficulty) + 1]
    except (ValueError, IndexError):
        return None
    next_tier = AdventureLevelTier.objects.filter(
        adventure_level_id=run.tier.adventure_level_id,
        difficulty=next_difficulty,
        is_published=True,
    ).first()
    if not next_tier:
        return None
    return {"id": next_tier.id, "difficulty": next_tier.difficulty}


def _scenario_context(run: AdventureLevelTierRun) -> dict:
    variant = run.selected_variant
    scenario = run.current_scenario
    raw = (variant.scenario_context if variant else None) or {
        "schema_version": 3,
        "story": scenario.story if scenario else "",
        "task": scenario.task if scenario else "",
    }
    fallback_story = scenario.story if scenario else ""
    return ScenarioContextNormalizer().normalize(raw, fallback_story=fallback_story)


def _tier_payload(run: AdventureLevelTierRun) -> dict:
    adventure_level = run.tier.adventure_level
    return {
        "id": run.tier_id,
        "difficulty": run.tier.difficulty,
        "adventure_level_id": adventure_level.id,
        "adventure_level_slug": adventure_level.slug,
        "adventure_level_title": adventure_level.title,
        "adventure_level_number": _level_number(adventure_level),
    }


def _level_number(adventure_level) -> int:
    """The level's place in its chapter, as the story map numbers it."""
    earlier = adventure_level.chapter.adventure_levels.filter(is_published=True).filter(
        Q(sort_order__lt=adventure_level.sort_order)
        | Q(sort_order=adventure_level.sort_order, id__lt=adventure_level.id)
    )
    return earlier.count() + 1
