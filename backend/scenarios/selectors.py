from scenarios.models import CompletionRecord, DifficultyInstance, ScenarioSkillFocus, ScenarioSession
from scenarios.services import DifficultyAccessService


def scenario_queryset():
    return (
        ScenarioSkillFocus.objects.filter(is_published=True)
        .select_related("learning_unit", "lesson")
        .prefetch_related(
            "difficulty_instances",
            "difficulty_instances__command_policy",
            "variants",
        )
    )


def scenario_status_payload(*, user, scenario: ScenarioSkillFocus) -> dict:
    access = DifficultyAccessService()
    difficulties = []
    for instance in scenario.difficulty_instances.all():
        completion = CompletionRecord.objects.filter(user=user, difficulty_instance=instance).first()
        in_progress = ScenarioSession.objects.filter(
            user=user,
            difficulty_instance=instance,
            status="started",
            mode="primary",
        ).first()
        difficulties.append(
            {
                "id": instance.id,
                "difficulty": instance.difficulty,
                "status": access.status_for(user=user, difficulty_instance=instance),
                "review_available": completion is not None,
                "completion": {
                    "first_attempt_star": completion.first_attempt_star if completion else False,
                    "counted_action_total": completion.counted_action_total if completion else None,
                    "completed_at": completion.completed_at if completion else None,
                }
                if completion
                else None,
                "active_session_id": in_progress.id if in_progress else None,
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
        "narrative": scenario.narrative,
        "task_prompt": scenario.task_prompt,
        "learning_unit_id": scenario.learning_unit_id,
        "lesson_id": scenario.lesson_id,
        "difficulties": difficulties,
    }


def get_difficulty_instance(instance_id: int) -> DifficultyInstance:
    return DifficultyInstance.objects.select_related(
        "scenario",
        "scenario__learning_unit",
        "command_policy",
        "target_rule",
    ).get(id=instance_id, is_published=True, scenario__is_published=True)
