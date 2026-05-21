from rest_framework import serializers

from scaffolding.services import ScaffoldingService
from scenarios.models import DifficultyInstance
from simulator.services import RepositorySnapshotService

DIFFICULTY_ORDER = ["easy", "medium", "hard"]


class ScenarioStartSerializer(serializers.Serializer):
    difficulty_instance_id = serializers.IntegerField()
    source_entry_point = serializers.ChoiceField(
        choices=["lesson", "unit_card", "retry", "review"],
        default="lesson",
    )
    prior_session_id = serializers.IntegerField(required=False, allow_null=True)


class CommandSubmitSerializer(serializers.Serializer):
    command = serializers.CharField(max_length=500)


class SkillFocusDemoCommandSerializer(serializers.Serializer):
    command = serializers.CharField(max_length=500)
    repository_state = serializers.JSONField(required=False)


def session_payload(session) -> dict:
    supports = ScaffoldingService().supports_for(session.difficulty_instance.difficulty)
    step_logs = session.step_logs.order_by("id")
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
            "task_prompt": session.difficulty_instance.task_prompt or session.scenario.task_prompt,
        },
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
        "policy": session.command_policy_snapshot,
        "counts": {
            "counted_action_total": session.counted_action_total,
            "non_counted_diagnostic_total": session.non_counted_diagnostic_total,
            "remaining_counted_commands": max(
                0,
                session.command_policy_snapshot["max_counted_commands"]
                - session.counted_action_total,
            ),
            "total_attempts": session.total_attempts,
        },
        "scaffolding": supports,
        "repository_state": RepositorySnapshotService().snapshot(session.repository_state),
        "expected_state": session.variant.expected_state_diagram
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
    }


def next_difficulty_payload(session) -> dict | None:
    if session.mode != "primary" or session.status != "completed":
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
