from django.db.models import Prefetch

from common.constants import (
    COMMAND_ACCURACY_PROGRESS_THRESHOLD,
    DIFFICULTY_EASY,
    DIFFICULTY_HARD,
    DIFFICULTY_MEDIUM,
    SESSION_MODE_PRIMARY,
    SESSION_STATUS_ABANDONED,
    SESSION_STATUS_COMPLETED,
    SESSION_STATUS_FAILED,
    SESSION_STATUS_STARTED,
)
from scenarios.models import (
    CommandDrill,
    CommandTopic,
    CommandUsage,
    CompletionRecord,
    PracticeKind,
    PracticeSession,
    WorkflowScenario,
    WorkflowScenarioLevel,
)

DIFFICULTY_ORDER = [DIFFICULTY_EASY, DIFFICULTY_MEDIUM, DIFFICULTY_HARD]


def required_successful_attempts_for_problem(problem) -> int:
    return int(getattr(problem, "required_successful_attempts", 1) or 1)


def minimum_counted_for_session(*, session: PracticeSession) -> int:
    snapshot = session.command_budget_snapshot or {}
    return int(snapshot.get("min_counted_commands", 0) or 0)


def command_accuracy_rate(
    *,
    status: str,
    counted_action_total: int,
    minimum_counted_commands: int,
) -> int | None:
    if status == SESSION_STATUS_STARTED:
        return None
    if status in {SESSION_STATUS_FAILED, SESSION_STATUS_ABANDONED}:
        return 0
    if counted_action_total <= minimum_counted_commands:
        return 100
    if minimum_counted_commands == 0:
        return 0
    return round((minimum_counted_commands / counted_action_total) * 100)


def session_meets_progress_threshold(*, session: PracticeSession) -> bool:
    rate = command_accuracy_rate(
        status=session.status,
        counted_action_total=session.counted_action_total,
        minimum_counted_commands=minimum_counted_for_session(session=session),
    )
    return rate is not None and rate >= COMMAND_ACCURACY_PROGRESS_THRESHOLD


def module_content_page(
    *,
    user,
    module_id: int,
    section: str,
    cursor: int | None = None,
    limit: int = 8,
) -> dict:
    limit = max(1, min(limit, 24))
    if section == "workflow_scenarios":
        queryset = workflow_scenario_queryset(module_id=module_id)
        if cursor:
            queryset = queryset.filter(id__gt=cursor)
        items = list(queryset[: limit + 1])
        visible = items[:limit]
        return {
            "section": section,
            "results": [
                workflow_scenario_summary_payload(user=user, scenario=scenario)
                for scenario in visible
            ],
            "next_cursor": visible[-1].id if len(items) > limit and visible else None,
        }

    queryset = command_topic_queryset(module_id=module_id)
    if cursor:
        queryset = queryset.filter(id__gt=cursor)
    items = list(queryset[: limit + 1])
    visible = items[:limit]
    return {
        "section": "command_topics",
        "results": [
            command_topic_summary_payload(user=user, topic=topic)
            for topic in visible
        ],
        "next_cursor": visible[-1].id if len(items) > limit and visible else None,
    }


def command_topic_queryset(*, module_id: int):
    return (
        CommandTopic.objects.filter(module_id=module_id, is_published=True)
        .prefetch_related(
            Prefetch(
                "usages",
                queryset=CommandUsage.objects.filter(is_published=True).prefetch_related(
                    Prefetch(
                        "drills",
                        queryset=CommandDrill.objects.filter(is_published=True).order_by(
                            "sort_order",
                            "id",
                        ),
                    )
                ),
            )
        )
        .order_by("sort_order", "id")
    )


def workflow_scenario_queryset(*, module_id: int):
    return (
        WorkflowScenario.objects.filter(module_id=module_id, is_published=True)
        .prefetch_related(
            Prefetch(
                "levels",
                queryset=WorkflowScenarioLevel.objects.filter(is_published=True).order_by(
                    "difficulty",
                    "id",
                ),
            )
        )
        .order_by("sort_order", "id")
    )


def command_topic_summary_payload(*, user, topic: CommandTopic) -> dict:
    usages = []
    for usage in topic.usages.all():
        drills = [
            command_drill_access_payload(user=user, drill=drill)
            for drill in usage.drills.all()
        ]
        usages.append(
            {
                "id": usage.id,
                "slug": usage.slug,
                "usage_form": usage.usage_form,
                "label": usage.label,
                "summary": usage.summary,
                "drills": drills,
            }
        )
    return {
        "item_type": "command_topic",
        "id": topic.id,
        "slug": topic.slug,
        "base_command": topic.base_command,
        "title": topic.title,
        "summary": topic.summary,
        "mental_model": topic.mental_model,
        "progress": _progress_for_drills(user=user, usages=topic.usages.all()),
        "usages": usages,
    }


def command_drill_access_payload(*, user, drill: CommandDrill) -> dict:
    completion = CompletionRecord.objects.filter(user=user, command_drill=drill).first()
    active_session = _active_session(user=user, command_drill=drill)
    latest_session = _latest_session(user=user, command_drill=drill)
    progress = _progress_payload(user=user, problem=drill, practice_kind=PracticeKind.COMMAND_DRILL)
    return {
        "id": drill.id,
        "slug": drill.slug,
        "title": drill.title,
        "summary": drill.summary,
        "practice_kind": PracticeKind.COMMAND_DRILL,
        "status": _status(completion=completion, active_session=active_session),
        "review_available": bool(completion),
        "required_successful_attempts": drill.required_successful_attempts,
        "successful_attempts": progress,
        "active_session_id": active_session.id if active_session else None,
        "latest_attempt": _latest_attempt_payload(latest_session),
        "completion": _completion_payload(completion),
        "command_budget": {
            "min_counted_commands": drill.min_counted_commands,
            "max_counted_commands": drill.max_counted_commands,
        },
    }


def workflow_scenario_summary_payload(*, user, scenario: WorkflowScenario) -> dict:
    levels = [
        workflow_level_access_payload(user=user, level=level)
        for level in _ordered_levels(scenario.levels.all())
    ]
    return {
        "item_type": "workflow_scenario",
        "id": scenario.id,
        "slug": scenario.slug,
        "title": scenario.title,
        "summary": scenario.summary,
        "narrative": scenario.narrative,
        "command_topics": scenario.command_topics,
        "levels": levels,
    }


def workflow_level_access_payload(*, user, level: WorkflowScenarioLevel) -> dict:
    completion = CompletionRecord.objects.filter(user=user, workflow_level=level).first()
    active_session = _active_session(user=user, workflow_level=level)
    latest_session = _latest_session(user=user, workflow_level=level)
    progress = _progress_payload(
        user=user,
        problem=level,
        practice_kind=PracticeKind.WORKFLOW_SCENARIO,
    )
    return {
        "id": level.id,
        "difficulty": level.difficulty,
        "practice_kind": PracticeKind.WORKFLOW_SCENARIO,
        "status": _workflow_status(
            user=user,
            level=level,
            completion=completion,
            active_session=active_session,
        ),
        "required_successful_attempts": level.required_successful_attempts,
        "successful_attempts": progress,
        "active_session_id": active_session.id if active_session else None,
        "latest_attempt": _latest_attempt_payload(latest_session),
        "completion": _completion_payload(completion),
        "command_budget": {
            "min_counted_commands": level.min_counted_commands,
            "max_counted_commands": level.max_counted_commands,
        },
    }


def get_command_drill(drill_id: int) -> CommandDrill:
    return (
        CommandDrill.objects.select_related("usage", "usage__topic", "usage__topic__module")
        .prefetch_related("variants")
        .get(
            id=drill_id,
            is_published=True,
            usage__is_published=True,
            usage__topic__is_published=True,
            usage__topic__module__is_published=True,
        )
    )


def get_command_usage(usage_id: int) -> CommandUsage:
    return CommandUsage.objects.select_related("topic", "topic__module").get(
        id=usage_id,
        is_published=True,
        topic__is_published=True,
        topic__module__is_published=True,
    )


def get_workflow_level(level_id: int) -> WorkflowScenarioLevel:
    return (
        WorkflowScenarioLevel.objects.select_related("scenario", "scenario__module")
        .prefetch_related("variants")
        .get(
            id=level_id,
            is_published=True,
            scenario__is_published=True,
            scenario__module__is_published=True,
        )
    )


def _progress_for_drills(*, user, usages) -> dict:
    drills = [drill for usage in usages for drill in usage.drills.all()]
    denominator = sum(drill.required_successful_attempts for drill in drills)
    numerator = 0
    for drill in drills:
        progress = _progress_payload(
            user=user,
            problem=drill,
            practice_kind=PracticeKind.COMMAND_DRILL,
        )
        numerator += min(progress["count"], progress["required"])
    return {
        "value": round((numerator / denominator) * 100, 1) if denominator else 0.0,
        "numerator": numerator,
        "denominator": denominator,
    }


def _progress_payload(*, user, problem, practice_kind: str) -> dict:
    required = required_successful_attempts_for_problem(problem)
    filters = {
        "user": user,
        "mode": SESSION_MODE_PRIMARY,
        "status": SESSION_STATUS_COMPLETED,
    }
    if practice_kind == PracticeKind.COMMAND_DRILL:
        filters["command_drill"] = problem
    else:
        filters["workflow_level"] = problem
    count = 0
    for session in PracticeSession.objects.filter(**filters):
        if session_meets_progress_threshold(session=session):
            count += 1
    return {"count": min(count, required), "required": required}


def _status(*, completion, active_session) -> str:
    if completion:
        return "completed"
    if active_session:
        return "in_progress"
    return "not_started"


def _workflow_status(*, user, level: WorkflowScenarioLevel, completion, active_session) -> str:
    if completion:
        return "completed"
    if active_session:
        return "in_progress"
    if _workflow_unlocked(user=user, level=level):
        latest = _latest_session(user=user, workflow_level=level)
        return latest.status if latest and latest.status in {SESSION_STATUS_FAILED, SESSION_STATUS_ABANDONED} else "not_started"
    return "locked"


def _workflow_unlocked(*, user, level: WorkflowScenarioLevel) -> bool:
    if level.difficulty == DIFFICULTY_EASY:
        return True
    previous = DIFFICULTY_EASY if level.difficulty == DIFFICULTY_MEDIUM else DIFFICULTY_MEDIUM
    previous_level = WorkflowScenarioLevel.objects.filter(
        scenario=level.scenario,
        difficulty=previous,
        is_published=True,
    ).first()
    return bool(
        previous_level
        and CompletionRecord.objects.filter(user=user, workflow_level=previous_level).exists()
    )


def _active_session(*, user, command_drill=None, workflow_level=None):
    filters = {
        "user": user,
        "status": SESSION_STATUS_STARTED,
        "mode": SESSION_MODE_PRIMARY,
    }
    if command_drill is not None:
        filters["command_drill"] = command_drill
    if workflow_level is not None:
        filters["workflow_level"] = workflow_level
    return PracticeSession.objects.filter(**filters).order_by("-id").first()


def _latest_session(*, user, command_drill=None, workflow_level=None):
    filters = {"user": user}
    if command_drill is not None:
        filters["command_drill"] = command_drill
    if workflow_level is not None:
        filters["workflow_level"] = workflow_level
    return PracticeSession.objects.filter(**filters).order_by("-id").first()


def _latest_attempt_payload(session) -> dict | None:
    if not session:
        return None
    return {
        "id": session.id,
        "status": session.status,
        "accuracy_rate": command_accuracy_rate(
            status=session.status,
            counted_action_total=session.counted_action_total,
            minimum_counted_commands=minimum_counted_for_session(session=session),
        ),
        "counted_action_total": session.counted_action_total,
        "total_attempts": session.total_attempts,
        "completed_at": session.completed_at,
        "ended_at": session.ended_at,
    }


def _completion_payload(completion) -> dict | None:
    if not completion:
        return None
    return {
        "first_attempt_star": completion.first_attempt_star,
        "counted_action_total": completion.counted_action_total,
        "completed_at": completion.completed_at,
    }


def _ordered_levels(levels) -> list[WorkflowScenarioLevel]:
    order = {DIFFICULTY_EASY: 0, DIFFICULTY_MEDIUM: 1, DIFFICULTY_HARD: 2}
    return sorted(levels, key=lambda level: order.get(level.difficulty, 99))
