from scenarios.models import (
    CompletionRecord,
    DifficultyInstance,
    ScenarioSession,
    ScenarioSkillFocus,
)
from scenarios.services import DifficultyAccessService


def command_accuracy_rate(
    *,
    status: str,
    counted_action_total: int,
    minimum_counted_commands: int,
) -> int | None:
    if status != "completed":
        return None
    if counted_action_total <= minimum_counted_commands:
        return 100
    if minimum_counted_commands == 0:
        return 0
    return round((minimum_counted_commands / counted_action_total) * 100)


def latest_attempt_payload(*, user, difficulty_instance: DifficultyInstance) -> dict | None:
    session = (
        ScenarioSession.objects.filter(
            user=user,
            difficulty_instance=difficulty_instance,
        )
        .order_by("-id")
        .first()
    )
    if not session:
        return None

    minimum_counted_commands = difficulty_instance.command_policy.min_counted_commands
    command_accurate = (
        session.status == "completed"
        and session.counted_action_total <= minimum_counted_commands
    )
    accuracy_rate = command_accuracy_rate(
        status=session.status,
        counted_action_total=session.counted_action_total,
        minimum_counted_commands=minimum_counted_commands,
    )

    return {
        "id": session.id,
        "status": session.status,
        "accuracy_rate": accuracy_rate,
        "command_accurate": command_accurate if session.status == "completed" else None,
        "counted_action_total": session.counted_action_total,
        "total_attempts": session.total_attempts,
        "completed_at": session.completed_at,
        "ended_at": session.ended_at,
    }


def scenario_queryset():
    return (
        ScenarioSkillFocus.objects.filter(
            is_published=True,
            learning_unit__is_published=True,
            lesson__is_published=True,
        )
        .select_related("learning_unit", "lesson")
        .prefetch_related(
            "difficulty_instances",
            "difficulty_instances__command_policy",
            "difficulty_instances__variants",
        )
    )


def scenario_status_payload(*, user, scenario: ScenarioSkillFocus) -> dict:
    access = DifficultyAccessService()
    difficulties = []
    for instance in scenario.difficulty_instances.all():
        completion = CompletionRecord.objects.filter(
            user=user, difficulty_instance=instance
        ).first()
        in_progress = ScenarioSession.objects.filter(
            user=user,
            difficulty_instance=instance,
            status="started",
            mode="primary",
        ).first()
        retryable_session = access.latest_retryable_session(
            user=user,
            difficulty_instance=instance,
        )
        difficulties.append(
            {
                "id": instance.id,
                "difficulty": instance.difficulty,
                "completion_type": instance.completion_type,
                "status": access.status_for(user=user, difficulty_instance=instance),
                "review_available": completion is not None,
                "completion": {
                    "first_attempt_star": completion.first_attempt_star if completion else False,
                    "counted_action_total": completion.counted_action_total if completion else None,
                    "completed_at": completion.completed_at if completion else None,
                }
                if completion
                else None,
                "latest_attempt": latest_attempt_payload(
                    user=user,
                    difficulty_instance=instance,
                ),
                "active_session_id": in_progress.id if in_progress else None,
                "retry_session_id": retryable_session.id if retryable_session else None,
                "policy": instance.command_policy.snapshot(),
            }
        )
    order = {"easy": 0, "medium": 1, "hard": 2}
    difficulties.sort(key=lambda item: order[item["difficulty"]])
    return {
        "id": scenario.id,
        "slug": scenario.slug,
        "title": scenario.title,
        "focus": scenario.focus,
        "summary": scenario.summary,
        "short_explanation": scenario.short_explanation,
        "skill_focus_type": scenario.skill_focus_type,
        "primary_focus_commands": scenario.primary_focus_commands,
        "supporting_inspection_commands": scenario.supporting_inspection_commands,
        "safe_demo_commands": scenario.safe_demo_commands,
        "demo_repository_state": scenario.demo_repository_state,
        "demo_dag_config": scenario.demo_dag_config,
        "demo_explanation_steps": scenario.demo_explanation_steps,
        "related_git_concepts": scenario.related_git_concepts,
        "learning_unit_id": scenario.learning_unit_id,
        "lesson_id": scenario.lesson_id,
        "difficulties": difficulties,
    }


def get_difficulty_instance(instance_id: int) -> DifficultyInstance:
    return (
        DifficultyInstance.objects.select_related(
            "scenario",
            "scenario__learning_unit",
            "command_policy",
            "target_rule",
        )
        .prefetch_related("variants")
        .get(
            id=instance_id,
            is_published=True,
            scenario__is_published=True,
            scenario__learning_unit__is_published=True,
            scenario__lesson__is_published=True,
        )
    )
