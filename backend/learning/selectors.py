from django.db.models import BooleanField, Count, Exists, IntegerField, OuterRef, Prefetch, Q, Value

from learning.models import LearningUnit, Lesson, OrientationProgress
from scenarios.models import CompletionRecord


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
                "scenarios", filter=Q(scenarios__is_published=True), distinct=True
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
                "scenarios", filter=Q(scenarios__is_published=True), distinct=True
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
