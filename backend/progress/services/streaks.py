from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from progress.models import StreakRecord


class StreakService:
    @transaction.atomic
    def record_completion(self, *, player, completed_at) -> None:
        day = timezone.localtime(completed_at).date()
        streak, _ = StreakRecord.objects.select_for_update().get_or_create(player=player)
        if streak.last_completed_on == day:
            return
        if streak.last_completed_on == day - timedelta(days=1):
            streak.current_streak += 1
        else:
            streak.current_streak = 1
        streak.longest_streak = max(streak.longest_streak, streak.current_streak)
        streak.last_completed_on = day
        streak.save(update_fields=["current_streak", "longest_streak", "last_completed_on"])
