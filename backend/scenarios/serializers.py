from rest_framework import serializers

from scaffolding.services import ScaffoldingService
from scenarios.models import CompletionRecord, DifficultyInstance
from scenarios.selectors import required_successful_attempts_for_difficulty
from simulator.services import RepositorySnapshotService

DIFFICULTY_ORDER = ["easy", "medium", "hard"]


class ScenarioStartSerializer(serializers.Serializer):
    difficulty_instance_id = serializers.IntegerField()
    source_entry_point = serializers.ChoiceField(
        choices=["lesson", "module_card", "unit_card", "retry", "review"],
        default="lesson",
    )
    prior_session_id = serializers.IntegerField(required=False, allow_null=True)


class CommandSubmitSerializer(serializers.Serializer):
    command = serializers.CharField(max_length=500)


class SkillFocusDemoCommandSerializer(serializers.Serializer):
    command = serializers.CharField(max_length=500)
    repository_state = serializers.JSONField(required=False)


def session_payload(session, *, include_steps: bool = True) -> dict:
    supports = ScaffoldingService().supports_for(session.difficulty_instance.difficulty)
    snapshotter = RepositorySnapshotService()
    step_logs = session.step_logs.order_by("id") if include_steps else []
    mastered_count = session.user.scenariosession_set.filter(
        mode="primary",
        status="completed",
        difficulty_instance=session.difficulty_instance,
        counted_action_total__lte=session.difficulty_instance.command_policy.min_counted_commands,
    ).count()
    required = required_successful_attempts_for_difficulty(session.difficulty_instance)
    mastery_progress = {
        "mastered": min(mastered_count, required),
        "required": required,
    }
    # Include completion record if one exists for this user/difficulty instance.
    completion_record = CompletionRecord.objects.filter(
        user=session.user, difficulty_instance=session.difficulty_instance
    ).first()
    completion = None
    if completion_record:
        completion = {
            "first_attempt_star": completion_record.first_attempt_star,
            "counted_action_total": completion_record.counted_action_total,
            "completed_at": completion_record.completed_at,
        }
    student_context = session.variant.student_context or fallback_student_context(session)
    minimum_counted_commands = session.command_policy_snapshot["min_counted_commands"]
    maximum_counted_commands = session.command_policy_snapshot["max_counted_commands"]
    remaining_counted_commands = max(
        0,
        maximum_counted_commands - session.counted_action_total,
    )
    max_reached = session.counted_action_total >= maximum_counted_commands
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
        },
        "student_context": student_context,
        "module": {
            "id": session.learning_unit_id,
            "number": session.learning_unit.number,
            "title": session.learning_unit.title,
        },
        # Backward-compatible alias while the frontend migrates to module naming.
        "unit": {
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
        },
        "mastery_progress": mastery_progress,
        "mastered_records": mastery_progress,
        "policy": session.command_policy_snapshot,
        "counts": {
            "counted_action_total": session.counted_action_total,
            "minimum_counted_commands": minimum_counted_commands,
            "maximum_counted_commands": maximum_counted_commands,
            "non_counted_diagnostic_total": session.non_counted_diagnostic_total,
            "remaining_counted_commands": remaining_counted_commands,
            "max_reached": max_reached,
            "total_attempts": session.total_attempts,
        },
        "scaffolding": supports,
        "repository_state": snapshotter.snapshot(session.repository_state),
        "expected_state": snapshotter.snapshot(
            session.variant.expected_state_diagram or session.variant.target_state
        )
        if supports["expected_state"]
        else None,
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
        "next_difficulty": next_difficulty_payload(session),
        "completion": completion,
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


def next_difficulty_payload(session) -> dict | None:
    if session.mode != "primary" or session.status != "completed":
        return None
    mastered_count = session.user.scenariosession_set.filter(
        mode="primary",
        status="completed",
        difficulty_instance=session.difficulty_instance,
        counted_action_total__lte=session.difficulty_instance.command_policy.min_counted_commands,
    ).count()
    required = required_successful_attempts_for_difficulty(session.difficulty_instance)
    # Require the current completed attempt to be accurate (100% accuracy)
    if session.counted_action_total > session.difficulty_instance.command_policy.min_counted_commands:
        return None
    if mastered_count < required:
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
