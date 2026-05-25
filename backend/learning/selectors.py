from django.db.models import BooleanField, Count, Exists, IntegerField, OuterRef, Prefetch, Q, Value

from common.constants import COMPLETION_TYPES
from learning.models import LearningUnit, Lesson, OrientationProgress
from scenarios.models import DifficultyInstance, ScenarioSession


def published_units(*, user=None):
    user_is_authenticated = bool(getattr(user, "is_authenticated", False))
    lesson_complete_annotation = (
        Exists(
            OrientationProgress.objects.filter(
                user=user,
                lesson_id=OuterRef("pk"),
                completed_at__isnull=False,
            )
        )
        if user_is_authenticated
        else Value(False, output_field=BooleanField())
    )
    practice_completion_annotation = (
        Count(
            "scenarios__completionrecord__difficulty_instance_id",
            filter=Q(
                scenarios__completionrecord__user=user,
                scenarios__completionrecord__difficulty_instance__is_published=True,
            ),
            distinct=True,
        )
        if user_is_authenticated
        else Value(0, output_field=IntegerField())
    )
    lesson_queryset = (
        Lesson.objects.filter(is_published=True)
        .only("id", "unit_id", "slug", "title", "subtitle", "kind", "sort_order")
        .annotate(
            is_complete_for_user=lesson_complete_annotation,
            published_scenario_count=Count(
                "scenarios",
                filter=Q(
                    scenarios__is_published=True,
                    scenarios__difficulty_instances__is_published=True,
                    scenarios__difficulty_instances__completion_type__in=COMPLETION_TYPES,
                ),
                distinct=True,
            )
        )
    )
    return (
        LearningUnit.objects.filter(is_published=True)
        .only("id", "slug", "number", "title", "description", "is_orientation", "sort_order")
        .prefetch_related(Prefetch("lessons", queryset=lesson_queryset))
        .annotate(
            published_lesson_count=Count(
                "lessons", filter=Q(lessons__is_published=True), distinct=True
            ),
            published_scenario_count=Count(
                "scenarios",
                filter=Q(
                    scenarios__is_published=True,
                    scenarios__difficulty_instances__is_published=True,
                    scenarios__difficulty_instances__completion_type__in=COMPLETION_TYPES,
                ),
                distinct=True,
            ),
            practice_completion_count=practice_completion_annotation,
        )
        .order_by("sort_order", "number")
    )


def published_lesson(lesson_id: int) -> Lesson:
    return Lesson.objects.select_related("unit").get(
        id=lesson_id,
        is_published=True,
        unit__is_published=True,
    )


def orientation_progress_map(user) -> dict[int, OrientationProgress]:
    return {
        item.lesson_id: item
        for item in OrientationProgress.objects.filter(user=user).select_related("lesson")
    }


def practice_completion_count_map(*, user, unit_ids: list[int]) -> dict[int, int]:
    if not getattr(user, "is_authenticated", False) or not unit_ids:
        return {}

    counts_by_instance: dict[int, int] = {}
    unit_by_instance: dict[int, int] = {}
    required_by_instance: dict[int, int] = {}
    for session in (
        ScenarioSession.objects.filter(
            user=user,
            mode="primary",
            status="completed",
            difficulty_instance__is_published=True,
            difficulty_instance__completion_type__in=COMPLETION_TYPES,
            scenario__is_published=True,
            scenario__learning_unit_id__in=unit_ids,
        )
        .select_related("difficulty_instance__command_policy")
        .only(
            "id",
            "scenario__learning_unit_id",
            "difficulty_instance_id",
            "difficulty_instance__difficulty",
            "difficulty_instance__required_successful_attempts",
            "difficulty_instance__command_policy__min_counted_commands",
            "status",
            "counted_action_total",
        )
    ):
        policy = session.difficulty_instance.command_policy
        if session.counted_action_total > policy.min_counted_commands:
            continue
        counts_by_instance[session.difficulty_instance_id] = (
            counts_by_instance.get(session.difficulty_instance_id, 0) + 1
        )
        unit_by_instance[session.difficulty_instance_id] = session.scenario.learning_unit_id
        required_by_instance[session.difficulty_instance_id] = (
            session.difficulty_instance.required_successful_attempts
        )

    completion_by_unit = {unit_id: 0 for unit_id in unit_ids}
    for difficulty_instance_id, count in counts_by_instance.items():
        unit_id = unit_by_instance[difficulty_instance_id]
        required = required_by_instance.get(difficulty_instance_id, 2)
        completion_by_unit[unit_id] = completion_by_unit.get(unit_id, 0) + min(count, required)
    return completion_by_unit


def practice_completion_denominator_map(*, unit_ids: list[int]) -> dict[int, int]:
    if not unit_ids:
        return {}

    denominator_by_unit = {unit_id: 0 for unit_id in unit_ids}
    for item in (
        DifficultyInstance.objects.filter(
            is_published=True,
            completion_type__in=COMPLETION_TYPES,
            scenario__is_published=True,
            scenario__learning_unit__is_published=True,
            scenario__learning_unit_id__in=unit_ids,
        )
        .values(
            "scenario__learning_unit_id",
            "required_successful_attempts",
        )
    ):
        unit_id = item["scenario__learning_unit_id"]
        denominator_by_unit[unit_id] = denominator_by_unit.get(unit_id, 0) + int(
            item["required_successful_attempts"] or 0
        )
    return denominator_by_unit
