from django.db.models import Count, Q

from learning.models import LearningUnit, Lesson, OrientationProgress


def published_units():
    return (
        LearningUnit.objects.filter(is_published=True)
        .prefetch_related("lessons", "scenarios")
        .annotate(
            published_lesson_count=Count("lessons", filter=Q(lessons__is_published=True), distinct=True),
            published_scenario_count=Count("scenarios", filter=Q(scenarios__is_published=True), distinct=True),
        )
        .order_by("sort_order", "number")
    )


def published_lesson(lesson_id: int) -> Lesson:
    return Lesson.objects.select_related("unit").get(id=lesson_id, is_published=True)


def orientation_progress_map(user) -> dict[int, OrientationProgress]:
    return {
        item.lesson_id: item
        for item in OrientationProgress.objects.filter(user=user).select_related("lesson")
    }
