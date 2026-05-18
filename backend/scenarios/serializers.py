from rest_framework import serializers

from scaffolding.services import ScaffoldingService
from simulator.services import RepositorySnapshotService


class ScenarioStartSerializer(serializers.Serializer):
    difficulty_instance_id = serializers.IntegerField()
    source_entry_point = serializers.ChoiceField(
        choices=["lesson_overview", "unit_card", "retry", "review"],
        default="lesson_overview",
    )
    prior_session_id = serializers.IntegerField(required=False, allow_null=True)


class CommandSubmitSerializer(serializers.Serializer):
    command = serializers.CharField(max_length=500)


def session_payload(session) -> dict:
    supports = ScaffoldingService().supports_for(session.difficulty_instance.difficulty)
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
            "task_prompt": session.scenario.task_prompt,
        },
        "unit": {
            "id": session.learning_unit_id,
            "number": session.learning_unit.number,
            "title": session.learning_unit.title,
        },
        "difficulty": session.difficulty_instance.difficulty,
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
        "expected_state": session.variant.expected_state_diagram if supports["expected_state"] else None,
        "review_mode": session.mode == "review",
    }
