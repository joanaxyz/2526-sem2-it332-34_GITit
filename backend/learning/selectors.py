from django.db.models import Count, Prefetch, Q

from learning.models import LearningUnit, Lesson, OrientationProgress
from scenarios.models import CompletionRecord


def published_units():
    lesson_queryset = Lesson.objects.filter(is_published=True).annotate(
        published_scenario_count=Count(
            "scenarios", filter=Q(scenarios__is_published=True), distinct=True
        )
    )
    return (
        LearningUnit.objects.filter(is_published=True)
        .prefetch_related(
            Prefetch("lessons", queryset=lesson_queryset),
            "scenarios",
        )
        .annotate(
            published_lesson_count=Count(
                "lessons", filter=Q(lessons__is_published=True), distinct=True
            ),
            published_scenario_count=Count(
                "scenarios", filter=Q(scenarios__is_published=True), distinct=True
            ),
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

    rows = (
        CompletionRecord.objects.filter(
            user=user,
            difficulty_instance__is_published=True,
            scenario__is_published=True,
            scenario__learning_unit_id__in=unit_ids,
        )
        .values("scenario__learning_unit_id")
        .annotate(completed=Count("difficulty_instance_id", distinct=True))
        .order_by()
    )
    return {row["scenario__learning_unit_id"]: row["completed"] for row in rows}
