import time

from rest_framework import serializers

from common.agent_debug_log import agent_debug_log
from common.constants import (
    SESSION_MODE_PRIMARY,
    SESSION_STATUS_COMPLETED,
    SESSION_STATUS_FAILED,
    SESSION_STATUS_STARTED,
)
from scaffolding.services import ScaffoldingService
from scenarios.models import CompletionRecord, DifficultyInstance, ScenarioSession, ScenarioSkillFocus
from scenarios.selectors import (
    required_successful_attempts_for_difficulty,
    reviewable_difficulties_for_session,
)
from simulator.services import RepositorySnapshotService

DIFFICULTY_ORDER = ["easy", "medium", "hard"]


class ScenarioStartSerializer(serializers.Serializer):
    difficulty_instance_id = serializers.IntegerField()
    source_entry_point = serializers.ChoiceField(
        choices=["module_card", "retry", "review"],
        default="module_card",
    )
    prior_session_id = serializers.IntegerField(required=False, allow_null=True)


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


class SkillFocusDemoCommandSerializer(serializers.Serializer):
    command = serializers.CharField(max_length=500)
    repository_state = serializers.JSONField(required=False)


def prefetch_session_payload_context(session: ScenarioSession) -> None:
    if getattr(session, "_payload_context_loaded", False):
        return
    session._prefetched_completion = CompletionRecord.objects.filter(
        user_id=session.user_id,
        difficulty_instance_id=session.difficulty_instance_id,
    ).first()
    min_counted = session.difficulty_instance.command_policy.min_counted_commands
    session._prefetched_mastery_count = ScenarioSession.objects.filter(
        user_id=session.user_id,
        mode=SESSION_MODE_PRIMARY,
        status=SESSION_STATUS_COMPLETED,
        difficulty_instance_id=session.difficulty_instance_id,
        counted_action_total__lte=min_counted,
    ).count()
    session._payload_context_loaded = True


def session_payload(session, *, include_steps: bool = True) -> dict:
    # #region agent log
    payload_t0 = time.perf_counter()
    agent_debug_log(
        location="scenarios/serializers.py:session_payload",
        message="session_payload_start",
        data={"session_id": session.id, "include_steps": include_steps},
        hypothesis_id="B",
    )
    # #endregion
    prefetch_session_payload_context(session)
    supports = ScaffoldingService().supports_for(session.difficulty_instance.difficulty)
    snapshotter = RepositorySnapshotService()
    if include_steps:
        prefetched_steps = getattr(session, "_prefetched_objects_cache", {}).get("step_logs")
        step_logs = list(prefetched_steps) if prefetched_steps is not None else list(session.step_logs.order_by("id"))
    else:
        step_logs = []
    # #region agent log
    agent_debug_log(
        location="scenarios/serializers.py:session_payload",
        message="session_payload_after_step_logs",
        data={
            "elapsed_ms": round((time.perf_counter() - payload_t0) * 1000, 2),
            "step_count": len(step_logs),
        },
        hypothesis_id="B",
    )
    # #endregion
    mastery_progress = mastery_progress_payload(session)
    completion = completion_payload(session)
    student_context = session.variant.student_context or fallback_student_context(session)
    counts = session_counts_payload(session)
    repository_state = snapshotter.snapshot(session.repository_state, already_normalized=True)
    expected_target = session.variant.expected_state_diagram or session.variant.target_state
    expected_state = (
        snapshotter.snapshot(expected_target, already_normalized=True)
        if supports["expected_state"] and expected_target
        else None
    )
    reviewable_difficulties = (
        reviewable_difficulties_for_session(session=session)
        if session.status in {SESSION_STATUS_COMPLETED, SESSION_STATUS_FAILED}
        else []
    )
    # #region agent log
    agent_debug_log(
        location="scenarios/serializers.py:session_payload",
        message="session_payload_after_looped_variant",
        data={
            "total_elapsed_ms": round((time.perf_counter() - payload_t0) * 1000, 2),
            "looped_variant": session.looped_variant,
        },
        hypothesis_id="D",
    )
    # #endregion
    return {
        "id": session.id,
        "mode": session.mode,
        "status": session.status,
        "difficulty_instance_id": session.difficulty_instance_id,
        "completed_at": session.completed_at,
        "first_attempt_star_eligible": session.first_attempt_star_eligible,
        "scenario": {
            "id": session.scenario_id,
            "slug": session.scenario.slug,
            "title": session.scenario.title,
            "focus": session.scenario.focus,
            "narrative": session.difficulty_instance.narrative or session.scenario.narrative,
            "student_context": student_context,
            "lesson_number": ScenarioSkillFocus.objects.filter(
            learning_unit=session.learning_unit,
            is_published=True,
            lesson__sort_order__lte=session.scenario.lesson.sort_order,
            difficulty_instances__is_published=True,
        ).distinct().count(),
        },
        "student_context": student_context,
        "module": {
            "id": session.learning_unit_id,
            "number": session.learning_unit.number,
            "title": session.learning_unit.title,
        },
        "difficulty": session.difficulty_instance.difficulty,
        "completion_type": session.difficulty_instance.completion_type,
        "variant": {
            "id": session.variant_id,
            "label": session.variant.label,
            "changed_variant": session.changed_variant,
            "looped_variant": session.looped_variant,
        },
        "mastery_progress": mastery_progress,
        "mastered_records": mastery_progress,
        "policy": session.command_policy_snapshot,
        "counts": counts,
        "scaffolding": supports,
        "repository_state": repository_state,
        "expected_state": expected_state,
        "steps": [
            {
                "id": step.id,
                "command_text": step.command_text,
                "terminal_output": step.terminal_output,
                "result_category": step.result_category,
                "command_classification": step.command_classification,
                "contextual_feedback": step.contextual_feedback,
                "created_at": step.created_at,
            }
            for step in step_logs
        ],
        "review_mode": session.mode == "review",
        "next_difficulty": next_difficulty_payload(
            session,
            mastery_progress=mastery_progress,
        ),
        "completion": completion,
        "reviewable_difficulties": reviewable_difficulties,
    }


def command_session_payload(session, *, repository_state: dict) -> dict:
    payload = {
        "id": session.id,
        "mode": session.mode,
        "status": session.status,
        "difficulty_instance_id": session.difficulty_instance_id,
        "completed_at": session.completed_at,
        "first_attempt_star_eligible": session.first_attempt_star_eligible,
        "counts": session_counts_payload(session),
        "repository_state": repository_state,
        "review_mode": session.mode == "review",
    }
    if session.status == SESSION_STATUS_STARTED:
        return payload

    mastery_progress = mastery_progress_payload(session)
    payload.update(
        {
            "mastery_progress": mastery_progress,
            "mastered_records": mastery_progress,
            "completion": completion_payload(session),
            "next_difficulty": next_difficulty_payload(
                session,
                mastery_progress=mastery_progress,
            ),
        }
    )
    return payload


def mastery_progress_payload(session) -> dict:
    required = required_successful_attempts_for_difficulty(session.difficulty_instance)
    if hasattr(session, "_prefetched_mastery_count"):
        mastered_count = session._prefetched_mastery_count
    else:
        mastered_count = session.user.scenariosession_set.filter(
            mode=SESSION_MODE_PRIMARY,
            status=SESSION_STATUS_COMPLETED,
            difficulty_instance=session.difficulty_instance,
            counted_action_total__lte=session.difficulty_instance.command_policy.min_counted_commands,
        ).count()
    return {
        "mastered": min(mastered_count, required),
        "required": required,
    }


def completion_payload(session) -> dict | None:
    completion_record = getattr(session, "_prefetched_completion", None)
    if completion_record is None and not getattr(session, "_payload_context_loaded", False):
        completion_record = CompletionRecord.objects.filter(
            user=session.user, difficulty_instance=session.difficulty_instance
        ).first()
    if completion_record:
        return {
            "first_attempt_star": completion_record.first_attempt_star,
            "counted_action_total": completion_record.counted_action_total,
            "completed_at": completion_record.completed_at,
        }
    return None


def session_counts_payload(session) -> dict:
    minimum_counted_commands = session.command_policy_snapshot["min_counted_commands"]
    maximum_counted_commands = session.command_policy_snapshot["max_counted_commands"]
    remaining_counted_commands = max(
        0,
        maximum_counted_commands - session.counted_action_total,
    )
    max_reached = session.counted_action_total >= maximum_counted_commands
    return {
        "counted_action_total": session.counted_action_total,
        "minimum_counted_commands": minimum_counted_commands,
        "maximum_counted_commands": maximum_counted_commands,
        "non_counted_diagnostic_total": session.non_counted_diagnostic_total,
        "remaining_counted_commands": remaining_counted_commands,
        "max_reached": max_reached,
        "total_attempts": session.total_attempts,
    }


def fallback_student_context(session) -> dict:
    narrative = session.difficulty_instance.narrative or session.scenario.narrative
    context = {
        "story": narrative,
    }
    return {
        key: value
        for key, value in context.items()
        if value not in ("", [], None)
    }


def next_difficulty_payload(session, *, mastery_progress: dict | None = None) -> dict | None:
    if session.mode != "primary" or session.status != SESSION_STATUS_COMPLETED:
        return None
    progress = mastery_progress or mastery_progress_payload(session)
    # Require the current completed attempt to be accurate (100% accuracy)
    if session.counted_action_total > session.difficulty_instance.command_policy.min_counted_commands:
        return None
    if progress["mastered"] < progress["required"]:
        return None

    try:
        current_index = DIFFICULTY_ORDER.index(session.difficulty_instance.difficulty)
        next_difficulty = DIFFICULTY_ORDER[current_index + 1]
    except (ValueError, IndexError):
        return None

    next_instance = DifficultyInstance.objects.filter(
        scenario=session.scenario,
        difficulty=next_difficulty,
        is_published=True,
    ).first()
    if not next_instance:
        return None

    return {
        "id": next_instance.id,
        "difficulty": next_instance.difficulty,
    }
