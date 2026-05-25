from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from learning.models import Lesson, OrientationProgress
from progress.models import StudentProgress


class OrientationService:
    def orientation_lessons(self):
        return Lesson.objects.filter(
            unit__is_orientation=True,
            is_published=True,
        ).select_related("unit")

    def is_orientation_complete(self, user) -> bool:
        lesson_ids = list(self.orientation_lessons().values_list("id", flat=True))
        if not lesson_ids:
            return False
        completed = OrientationProgress.objects.filter(
            user=user,
            lesson_id__in=lesson_ids,
            completed_at__isnull=False,
        ).count()
        return completed == len(lesson_ids)

    @transaction.atomic
    def mark_complete(self, *, user, lesson: Lesson, highest_step_seen: int) -> OrientationProgress:
        if not lesson.unit.is_orientation:
            raise ValidationError("This lesson does not use the mark-read action.")
        progress, _ = OrientationProgress.objects.select_for_update().get_or_create(
            user=user,
            lesson=lesson,
            defaults={"highest_step_seen": highest_step_seen},
        )
        progress.highest_step_seen = max(progress.highest_step_seen, highest_step_seen)
        if progress.completed_at is None:
            progress.completed_at = timezone.now()
        progress.save(update_fields=["highest_step_seen", "completed_at"])

        student_progress, _ = StudentProgress.objects.get_or_create(user=user)
        if student_progress.first_scenario_started_at is None and self.is_orientation_complete(user):
            student_progress.orientation_complete_at_first_start = True
            student_progress.save(update_fields=["orientation_complete_at_first_start"])
        return progress
