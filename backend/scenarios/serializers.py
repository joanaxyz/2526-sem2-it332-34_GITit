import json
from pathlib import Path
from time import time

from django.db import connection
from rest_framework import serializers

from common.constants import SESSION_STATUS_STARTED
from retries.services import VariantSelectionService
from scaffolding.services import ScaffoldingService
from scenarios.models import CompletionRecord, DifficultyInstance
from scenarios.selectors import required_successful_attempts_for_difficulty
from simulator.services import RepositorySnapshotService

DIFFICULTY_ORDER = ["easy", "medium", "hard"]


def _debug_log(*, run_id: str, hypothesis_id: str, location: str, message: str, data: dict) -> None:
    payload = {
        "sessionId": "c81762",
        "runId": run_id,
        "hypothesisId": hypothesis_id,
        "location": location,
        "message": message,
        "data": data,
        "timestamp": int(time() * 1000),
    }
    # region agent log
    with Path("debug-c81762.log").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload) + "\n")
    # endregion


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


def session_payload(session, *, include_steps: bool = True) -> dict:
    # region agent log
    _debug_log(
        run_id="initial",
        hypothesis_id="H1",
        location="backend/scenarios/serializers.py:60",
        message="session_payload entry",
        data={
            "session_id": session.id,
            "include_steps": include_steps,
            "connection_usable": connection.is_usable(),
            "connection_closed_state": connection.connection.closed if connection.connection else None,
            "has_prefetched_step_logs": "step_logs" in getattr(session, "_prefetched_objects_cache", {}),
        },
    )
    # endregion
    supports = ScaffoldingService().supports_for(session.difficulty_instance.difficulty)
    snapshotter = RepositorySnapshotService()
    if include_steps:
        step_logs_qs = session.step_logs.order_by("id")
        # region agent log
        _debug_log(
            run_id="initial",
            hypothesis_id="H3",
            location="backend/scenarios/serializers.py:78",
            message="step logs queryset prepared",
            data={
                "session_id": session.id,
                "query_repr": str(step_logs_qs.query),
            },
        )
        # endregion
        try:
            step_logs = list(step_logs_qs)
            # region agent log
            _debug_log(
                run_id="initial",
                hypothesis_id="H2",
                location="backend/scenarios/serializers.py:90",
                message="step logs materialized",
                data={
                    "session_id": session.id,
                    "step_count": len(step_logs),
                },
            )
            # endregion
        except Exception as exc:
            # region agent log
            _debug_log(
                run_id="initial",
                hypothesis_id="H4",
                location="backend/scenarios/serializers.py:101",
                message="step logs materialization failed",
                data={
                    "session_id": session.id,
                    "error_type": exc.__class__.__name__,
                    "error_message": str(exc),
                    "connection_usable_after_error": connection.is_usable(),
                    "connection_closed_state_after_error": connection.connection.closed if connection.connection else None,
                },
            )
            # endregion
            raise
    else:
        step_logs = []
    mastery_progress = mastery_progress_payload(session)
    completion = completion_payload(session)
    student_context = session.variant.student_context or fallback_student_context(session)
    counts = session_counts_payload(session)
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
        "difficulty": session.difficulty_instance.difficulty,
        "completion_type": session.difficulty_instance.completion_type,
        "variant": {
            "id": session.variant_id,
            "label": session.variant.label,
            "changed_variant": session.changed_variant,
            "looped_variant": looped_variant_payload(session),
        },
        "mastery_progress": mastery_progress,
        "mastered_records": mastery_progress,
        "policy": session.command_policy_snapshot,
        "counts": counts,
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
        "next_difficulty": next_difficulty_payload(
            session,
            mastery_progress=mastery_progress,
        ),
        "completion": completion,
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
    return mastery_progress


def completion_payload(session) -> dict | None:
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
    if session.mode != "primary" or session.status != "completed":
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


def looped_variant_payload(session) -> bool:
    selector = VariantSelectionService()
    return selector.is_loopback_selection(
        user=session.user,
        difficulty_instance=session.difficulty_instance,
        selected_variant=session.variant,
        prior_session=session.prior_session,
        exclude_session_id=session.id,
    )
