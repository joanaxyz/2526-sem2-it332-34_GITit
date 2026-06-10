from rest_framework import serializers

from common.constants import SESSION_MODE_REVIEW, SESSION_STATUS_COMPLETED, SESSION_STATUS_STARTED
from challenges.models import ChallengeRun
from challenges.selectors import minimum_counted_for_session, required_successful_attempts_for_problem
from practice.context import ScenarioContextNormalizer
from practice.scaffolding import ScaffoldingService
from practice.visualization import RepositoryVisualizationService
from progress.models import ProblemCompletion
from simulator.services import RepositorySnapshotService

DIFFICULTY_ORDER = ["easy", "medium", "hard"]


class ChallengeRunStartSerializer(serializers.Serializer):
    source_entry_point = serializers.ChoiceField(
        choices=["tower_page", "retry", "review"],
        default="tower_page",
    )
    prior_run_id = serializers.IntegerField(required=False, allow_null=True)
    review = serializers.BooleanField(required=False, default=False)


class CommandSubmitSerializer(serializers.Serializer):
    command = serializers.CharField(max_length=500)


class WorkspaceFileCreateSerializer(serializers.Serializer):
    path = serializers.CharField(max_length=240)
    content = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=20000,
        default="",
        trim_whitespace=False,
    )


def prefetch_run_payload_context(run: ChallengeRun) -> None:
    if getattr(run, "_payload_context_loaded", False):
        return
    run._prefetched_completion = ProblemCompletion.objects.filter(
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
    visualization = visualizer.snapshot(run.repository_state, target_state=target_state)
    expected_state = (
        snapshotter.snapshot(expected_target, already_normalized=True)
        if supports["expected_state"] and expected_target
        else None
    )
    storey_payload = {
        "id": run.module_id,
        "number": run.module.number,
        "title": run.module.title,
    }

    step_logs = list(run.step_logs.order_by("id")) if include_steps else []
    return {
        "id": run.id,
        "mode": run.mode,
        "status": run.status,
        "failure_reason": run.failure_reason or None,
        "completed_at": run.completed_at,
        "first_attempt_star_eligible": run.first_attempt_star_eligible,
        "challenge": _challenge_payload(run),
        "scenario_context": context,
        "storey": storey_payload,
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
            for step in step_logs
        ],
        "review_mode": run.mode == SESSION_MODE_REVIEW,
        "next_difficulty": next_difficulty_payload(run),
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
            }
        )
    return payload


def mastery_progress_payload(run: ChallengeRun) -> dict:
    required = required_successful_attempts_for_problem(run.challenge_level)
    mastered_count = ChallengeRun.objects.filter(
        user_id=run.user_id,
        mode="primary",
        status="completed",
        challenge_level_id=run.challenge_level_id,
        counted_action_total__lte=run.command_budget_snapshot["min_counted_commands"],
    ).count()
    return {"mastered": min(mastered_count, required), "required": required}


def completion_payload(run: ChallengeRun) -> dict | None:
    completion = getattr(run, "_prefetched_completion", None)
    if completion is None and not getattr(run, "_payload_context_loaded", False):
        completion = ProblemCompletion.objects.filter(user=run.user, challenge_level=run.challenge_level).first()
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
        next_difficulty = DIFFICULTY_ORDER[DIFFICULTY_ORDER.index(run.challenge_level.difficulty) + 1]
    except (ValueError, IndexError):
        return None
    next_level = run.challenge_level.scenario.levels.filter(
        difficulty=next_difficulty,
        is_published=True,
    ).first()
    if not next_level:
        return None
    return {"id": next_level.id, "difficulty": next_level.difficulty}


def _scenario_context(run: ChallengeRun) -> dict:
    # The brief is authored on the level and shared across its variants; the
    # variant only carries a generated fallback, so the level's authored context
    # wins.
    raw = run.challenge_level.scenario_context or run.variant.scenario_context
    return ScenarioContextNormalizer().normalize(raw, fallback_story=run.workflow_scenario.narrative)


def _challenge_payload(run: ChallengeRun) -> dict:
    return {
        "id": run.workflow_scenario_id,
        "slug": run.workflow_scenario.slug,
        "title": run.workflow_scenario.title,
        "summary": run.workflow_scenario.summary,
        "narrative": run.workflow_scenario.narrative,
        "level_id": run.challenge_level_id,
    }
