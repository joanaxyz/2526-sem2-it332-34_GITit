from django.db.models import Count, Q

from learning.models import FoundationTopic, LearningModule
from scenarios.models import (
    CommandDrill,
    PracticeKind,
    PracticeSession,
    WorkflowScenarioLevel,
)
from scenarios.selectors import session_meets_progress_threshold


def published_foundations():
    return FoundationTopic.objects.filter(is_published=True).order_by("sort_order", "title")


def published_modules():
    return (
        LearningModule.objects.filter(is_published=True)
        .annotate(
            command_topic_count=Count(
                "command_topics",
                filter=Q(command_topics__is_published=True),
                distinct=True,
            ),
            workflow_scenario_count=Count(
                "workflow_scenarios",
                filter=Q(workflow_scenarios__is_published=True),
                distinct=True,
            ),
        )
        .order_by("sort_order", "number")
    )


def practice_completion_count_map(*, user, module_ids: list[int]) -> dict[int, int]:
    if not getattr(user, "is_authenticated", False) or not module_ids:
        return {}

    completion_by_module = {module_id: 0 for module_id in module_ids}
    completed_sessions = (
        PracticeSession.objects.filter(
            user=user,
            mode="primary",
            status="completed",
            module_id__in=module_ids,
        )
        .select_related("command_drill", "workflow_level")
        .only(
            "id",
            "module_id",
            "practice_kind",
            "command_drill_id",
            "workflow_level_id",
            "counted_action_total",
            "command_budget_snapshot",
            "command_drill__required_successful_attempts",
            "workflow_level__required_successful_attempts",
        )
    )
    counts_by_problem: dict[tuple[str, int], int] = {}
    required_by_problem: dict[tuple[str, int], int] = {}
    module_by_problem: dict[tuple[str, int], int] = {}

    for session in completed_sessions:
        if not session_meets_progress_threshold(session=session):
            continue
        if session.practice_kind == PracticeKind.COMMAND_DRILL:
            problem_id = session.command_drill_id
            required = session.command_drill.required_successful_attempts
        else:
            problem_id = session.workflow_level_id
            required = session.workflow_level.required_successful_attempts
        if not problem_id:
            continue
        key = (session.practice_kind, problem_id)
        counts_by_problem[key] = counts_by_problem.get(key, 0) + 1
        required_by_problem[key] = required
        module_by_problem[key] = session.module_id

    for key, count in counts_by_problem.items():
        module_id = module_by_problem[key]
        completion_by_module[module_id] = completion_by_module.get(module_id, 0) + min(
            count,
            required_by_problem.get(key, 1),
        )
    return completion_by_module


def practice_completion_denominator_map(*, module_ids: list[int]) -> dict[int, int]:
    if not module_ids:
        return {}

    denominator_by_module = {module_id: 0 for module_id in module_ids}
    for row in (
        CommandDrill.objects.filter(
            is_published=True,
            usage__is_published=True,
            usage__topic__is_published=True,
            usage__topic__module_id__in=module_ids,
        )
        .values("usage__topic__module_id", "required_successful_attempts")
    ):
        module_id = row["usage__topic__module_id"]
        denominator_by_module[module_id] = denominator_by_module.get(module_id, 0) + int(
            row["required_successful_attempts"] or 0
        )

    for row in (
        WorkflowScenarioLevel.objects.filter(
            is_published=True,
            scenario__is_published=True,
            scenario__module_id__in=module_ids,
        )
        .values("scenario__module_id", "required_successful_attempts")
    ):
        module_id = row["scenario__module_id"]
        denominator_by_module[module_id] = denominator_by_module.get(module_id, 0) + int(
            row["required_successful_attempts"] or 0
        )
    return denominator_by_module
