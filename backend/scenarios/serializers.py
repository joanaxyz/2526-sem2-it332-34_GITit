from rest_framework import serializers

from common.constants import (
    SESSION_MODE_REVIEW,
    SESSION_STATUS_COMPLETED,
    SESSION_STATUS_STARTED,
)
from learning.curriculum_v2.adventures import command_drill_adventure_for
from scaffolding.services import ScaffoldingService
from scenarios.context import StudentContextNormalizer
from scenarios.models import CommandTopic, CompletionRecord, PracticeKind, PracticeSession
from scenarios.selectors import (
    DIFFICULTY_ORDER,
    required_successful_attempts_for_problem,
)
from scenarios.visualization import RepositoryVisualizationService
from simulator.services import RepositorySnapshotService


class PracticeStartSerializer(serializers.Serializer):
    problem_type = serializers.ChoiceField(choices=PracticeKind.values)
    command_drill_id = serializers.IntegerField(required=False, allow_null=True)
    workflow_level_id = serializers.IntegerField(required=False, allow_null=True)
    source_entry_point = serializers.ChoiceField(
        choices=["tower_page", "module_page", "retry", "review"],
        default="tower_page",
    )
    prior_session_id = serializers.IntegerField(required=False, allow_null=True)

    def validate(self, attrs):
        if attrs["problem_type"] == PracticeKind.COMMAND_DRILL and not attrs.get("command_drill_id"):
            raise serializers.ValidationError("command_drill_id is required for command drills.")
        if attrs["problem_type"] == PracticeKind.WORKFLOW_SCENARIO and not attrs.get("workflow_level_id"):
            raise serializers.ValidationError("workflow_level_id is required for workflow scenarios.")
        return attrs


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


def prefetch_session_payload_context(session: PracticeSession) -> None:
    if getattr(session, "_payload_context_loaded", False):
        return
    completion_filter = {"user_id": session.user_id}
    if session.practice_kind == PracticeKind.COMMAND_DRILL:
        completion_filter["command_drill_id"] = session.command_drill_id
    else:
        completion_filter["workflow_level_id"] = session.workflow_level_id
    session._prefetched_completion = CompletionRecord.objects.filter(**completion_filter).first()
    session._payload_context_loaded = True


def session_payload(session: PracticeSession, *, include_steps: bool = True) -> dict:
    prefetch_session_payload_context(session)
    snapshotter = RepositorySnapshotService()
    visualizer = RepositoryVisualizationService()
    problem = session.problem
    context = _student_context(session)
    repository_state = snapshotter.snapshot(session.repository_state, already_normalized=True)
    supports = _scaffolding_supports(session)
    expected_target = session.variant.expected_state_diagram or session.variant.target_state
    target_state = session.variant.target_state if supports["expected_state"] else None
    visualization = visualizer.snapshot(session.repository_state, target_state=target_state)
    expected_state = (
        snapshotter.snapshot(expected_target, already_normalized=True)
        if supports["expected_state"] and expected_target
        else None
    )
    tower_payload = {
        "id": session.module_id,
        "number": session.module.number,
        "title": session.module.title,
    }

    step_logs = list(session.step_logs.order_by("id")) if include_steps else []
    return {
        "id": session.id,
        "mode": session.mode,
        "status": session.status,
        "failure_reason": session.failure_reason or None,
        "practice_kind": session.practice_kind,
        "completed_at": session.completed_at,
        "first_attempt_star_eligible": session.first_attempt_star_eligible,
        "problem": _problem_payload(session),
        "student_context": context,
        "tower": tower_payload,
        "module": tower_payload,
        "difficulty": session.difficulty or None,
        "variant": {
            "id": session.variant_id,
            "label": session.variant.label,
            "changed_variant": session.changed_variant,
            "looped_variant": session.looped_variant,
        },
        "mastery_progress": mastery_progress_payload(session, problem=problem),
        "policy": session.command_budget_snapshot,
        "counts": session_counts_payload(session),
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
        "review_mode": session.mode == SESSION_MODE_REVIEW,
        "next_difficulty": next_difficulty_payload(session),
        "completion": completion_payload(session),
    }


def command_session_payload(session: PracticeSession, *, repository_state: dict, visualization: dict) -> dict:
    payload = {
        "id": session.id,
        "mode": session.mode,
        "status": session.status,
        "failure_reason": session.failure_reason or None,
        "practice_kind": session.practice_kind,
        "completed_at": session.completed_at,
        "first_attempt_star_eligible": session.first_attempt_star_eligible,
        "counts": session_counts_payload(session),
        "repository_state": repository_state,
        "visualization": visualization,
        "review_mode": session.mode == SESSION_MODE_REVIEW,
    }
    if session.status != SESSION_STATUS_STARTED:
        payload.update(
            {
                "mastery_progress": mastery_progress_payload(session, problem=session.problem),
                "completion": completion_payload(session),
                "next_difficulty": next_difficulty_payload(session),
            }
        )
    return payload


def mastery_progress_payload(session: PracticeSession, *, problem) -> dict:
    required = required_successful_attempts_for_problem(problem)
    filters = {
        "user_id": session.user_id,
        "mode": "primary",
        "status": "completed",
        "counted_action_total__lte": session.command_budget_snapshot["min_counted_commands"],
    }
    if session.practice_kind == PracticeKind.COMMAND_DRILL:
        filters["command_drill_id"] = session.command_drill_id
    else:
        filters["workflow_level_id"] = session.workflow_level_id
    mastered_count = PracticeSession.objects.filter(**filters).count()
    return {"mastered": min(mastered_count, required), "required": required}


def completion_payload(session: PracticeSession) -> dict | None:
    completion = getattr(session, "_prefetched_completion", None)
    if completion is None and not getattr(session, "_payload_context_loaded", False):
        filters = {"user": session.user}
        if session.practice_kind == PracticeKind.COMMAND_DRILL:
            filters["command_drill"] = session.command_drill
        else:
            filters["workflow_level"] = session.workflow_level
        completion = CompletionRecord.objects.filter(**filters).first()
    if not completion:
        return None
    return {
        "first_attempt_star": completion.first_attempt_star,
        "counted_action_total": completion.counted_action_total,
        "completed_at": completion.completed_at,
    }


def session_counts_payload(session: PracticeSession) -> dict:
    minimum = session.command_budget_snapshot["min_counted_commands"]
    maximum = session.command_budget_snapshot["max_counted_commands"]
    return {
        "counted_action_total": session.counted_action_total,
        "minimum_counted_commands": minimum,
        "maximum_counted_commands": maximum,
        "non_counted_diagnostic_total": session.non_counted_diagnostic_total,
        "remaining_counted_commands": max(0, maximum - session.counted_action_total),
        "max_reached": session.counted_action_total >= maximum,
        "total_attempts": session.total_attempts,
    }


def next_difficulty_payload(session: PracticeSession) -> dict | None:
    if (
        session.practice_kind != PracticeKind.WORKFLOW_SCENARIO
        or session.mode != "primary"
        or session.status != SESSION_STATUS_COMPLETED
        or not session.workflow_level
    ):
        return None
    progress = mastery_progress_payload(session, problem=session.workflow_level)
    if session.counted_action_total > session.command_budget_snapshot["min_counted_commands"]:
        return None
    if progress["mastered"] < progress["required"]:
        return None
    try:
        next_difficulty = DIFFICULTY_ORDER[DIFFICULTY_ORDER.index(session.workflow_level.difficulty) + 1]
    except (ValueError, IndexError):
        return None
    next_level = session.workflow_level.scenario.levels.filter(
        difficulty=next_difficulty,
        is_published=True,
    ).first()
    if not next_level:
        return None
    return {"id": next_level.id, "difficulty": next_level.difficulty}


def _student_context(session: PracticeSession) -> dict:
    raw = session.variant.student_context or getattr(session.problem, "student_context", {})
    fallback = _problem_narrative(session)
    return StudentContextNormalizer().normalize(raw, fallback_story=fallback)


def _problem_payload(session: PracticeSession) -> dict:
    if session.practice_kind == PracticeKind.COMMAND_DRILL:
        usage = session.command_drill.usage
        topic = usage.topic
        adventure = command_drill_adventure_for(topic.module)
        level_number = _command_level_number(topic)
        return {
            "id": session.command_drill_id,
            "slug": session.command_drill.slug,
            "title": session.command_drill.title,
            "summary": session.command_drill.summary,
            "adventure": adventure,
            "command_level": {
                "id": topic.id,
                "number": level_number,
                "label": f"Level {level_number}",
            },
            "topic": {
                "id": topic.id,
                "base_command": topic.base_command,
                "title": topic.title,
            },
            "usage": {
                "id": usage.id,
                "usage_form": usage.usage_form,
                "label": usage.label,
            },
        }
    return {
        "id": session.workflow_scenario_id,
        "slug": session.workflow_scenario.slug,
        "title": session.workflow_scenario.title,
        "summary": session.workflow_scenario.summary,
        "narrative": session.workflow_level.narrative or session.workflow_scenario.narrative,
        "level_id": session.workflow_level_id,
    }


def _problem_narrative(session: PracticeSession) -> str:
    if session.practice_kind == PracticeKind.COMMAND_DRILL:
        return session.command_drill.summary
    return session.workflow_level.narrative or session.workflow_scenario.narrative


def _scaffolding_supports(session: PracticeSession) -> dict:
    if session.practice_kind == PracticeKind.COMMAND_DRILL:
        return {
            "live_dag": True,
            "expected_state": True,
            "contextual_feedback": True,
        }
    return ScaffoldingService().supports_for(session.workflow_level.difficulty)


def _command_level_number(topic: CommandTopic) -> int:
    previous_published = CommandTopic.objects.filter(
        module_id=topic.module_id,
        is_published=True,
        sort_order__lt=topic.sort_order,
    ).count()
    return previous_published + 1
