from datetime import timedelta

from django.db.models import Count, Q
from django.utils import timezone

from common.constants import (
    DIFFICULTY_HARD,
    SESSION_MODE_PRIMARY,
    SESSION_MODE_REVIEW,
    SESSION_STATUS_ABANDONED,
    SESSION_STATUS_COMPLETED,
    SESSION_STATUS_FAILED,
)
from learning.models import Lesson, OrientationProgress
from progress.models import StreakRecord
from scenarios.models import CompletionRecord, ScenarioSession


class StreakService:
    def record_completion(self, *, user, completed_at) -> None:
        day = timezone.localtime(completed_at).date()
        streak, _ = StreakRecord.objects.get_or_create(user=user)
        if streak.last_completed_on == day:
            return
        if streak.last_completed_on == day - timedelta(days=1):
            streak.current_streak += 1
        else:
            streak.current_streak = 1
        streak.longest_streak = max(streak.longest_streak, streak.current_streak)
        streak.last_completed_on = day
        streak.save(update_fields=["current_streak", "longest_streak", "last_completed_on"])


class MetricsService:
    def dashboard_summary(self, *, user) -> dict:
        primary = ScenarioSession.objects.filter(user=user, mode=SESSION_MODE_PRIMARY)
        review = ScenarioSession.objects.filter(user=user, mode=SESSION_MODE_REVIEW)
        started = primary.count()
        completed = primary.filter(status=SESSION_STATUS_COMPLETED).count()
        failed = primary.filter(status=SESSION_STATUS_FAILED).count()
        abandoned = primary.filter(status=SESSION_STATUS_ABANDONED).count()
        hard_started = primary.filter(difficulty_instance__difficulty=DIFFICULTY_HARD).count()
        hard_completed = primary.filter(
            difficulty_instance__difficulty=DIFFICULTY_HARD,
            status=SESSION_STATUS_COMPLETED,
        ).count()
        rta = primary.filter(rta_eligible=True)
        review_started = review.count()
        review_completed = review.filter(status=SESSION_STATUS_COMPLETED).count()
        orientation_lesson_ids = list(
            Lesson.objects.filter(
                unit__is_orientation=True,
                kind=Lesson.LessonKind.ORIENTATION,
                is_published=True,
            ).values_list("id", flat=True)
        )
        orientation_completed = (
            OrientationProgress.objects.filter(
                user=user,
                lesson_id__in=orientation_lesson_ids,
                completed_at__isnull=False,
            ).count()
            if orientation_lesson_ids
            else 0
        )

        latest_completion_ids = []
        for completion in (
            CompletionRecord.objects.filter(user=user)
            .select_related("difficulty_instance__command_policy")
            .order_by("difficulty_instance_id", "-completed_at")
        ):
            if completion.difficulty_instance_id not in latest_completion_ids:
                latest_completion_ids.append(completion.difficulty_instance_id)
        latest_completions = CompletionRecord.objects.filter(
            user=user,
            difficulty_instance_id__in=latest_completion_ids,
        ).select_related("difficulty_instance__command_policy")
        command_accuracy_values = [
            self._command_accuracy_for_completion(item)
            for item in latest_completions
        ]

        streak = getattr(user, "streakrecord", None)
        return {
            "kpis": {
                "orientation_completion": self._rate(
                    orientation_completed,
                    len(orientation_lesson_ids),
                ),
                "scr": self._rate(completed, started),
                "arc": self._average_retry_count(primary),
                "car": self._average_percent(command_accuracy_values),
                "hlcr": self._rate(hard_completed, hard_started),
                "rta": self._rate(rta.filter(rta_success=True).count(), rta.count()),
                "sar": self._rate(abandoned, started),
                "review_scr": self._rate(review_completed, review_started),
            },
            "counts": {
                "started": started,
                "completed": completed,
                "failed": failed,
                "abandoned": abandoned,
                "review_started": review_started,
            },
            "streak": {
                "current": streak.current_streak if streak else 0,
                "longest": streak.longest_streak if streak else 0,
                "last_completed_on": streak.last_completed_on if streak else None,
            },
            "first_attempt_stars": CompletionRecord.objects.filter(
                user=user,
                first_attempt_star=True,
            ).count(),
            "retry_trends": self._retry_trends(user=user),
        }

    def _rate(self, numerator: int, denominator: int) -> dict:
        return {
            "value": round((numerator / denominator) * 100, 1) if denominator else None,
            "numerator": numerator,
            "denominator": denominator,
        }

    def _average_percent(self, values: list[int]) -> dict:
        total = sum(values)
        return {
            "value": round(total / len(values), 1) if values else None,
            "numerator": round(total, 1),
            "denominator": len(values),
        }

    def _command_accuracy_for_completion(self, completion: CompletionRecord) -> int:
        target_actions = completion.difficulty_instance.command_policy.min_counted_commands
        used_actions = completion.counted_action_total
        if used_actions <= target_actions:
            return 100
        if target_actions == 0:
            return 0
        return round((target_actions / used_actions) * 100)

    def _average_retry_count(self, sessions) -> dict:
        completed = sessions.filter(status=SESSION_STATUS_COMPLETED)
        denominator = completed.count()
        numerator = sum(item.retry_index for item in completed)
        return {
            "value": round(numerator / denominator, 2) if denominator else None,
            "numerator": numerator,
            "denominator": denominator,
        }

    def _retry_trends(self, *, user) -> list[dict]:
        rows = (
            ScenarioSession.objects.filter(user=user, mode=SESSION_MODE_PRIMARY)
            .values("scenario_id", "scenario__title")
            .annotate(
                attempts=Count("id"),
                retries=Count("id", filter=Q(prior_session__isnull=False)),
            )
            .order_by("-retries")[:6]
        )
        return [
            {
                "scenario_id": row["scenario_id"],
                "scenario_title": row["scenario__title"],
                "attempts": row["attempts"],
                "retries": row["retries"],
                "label": "No trend available" if row["attempts"] < 2 else f"{row['retries']} retry sessions",
            }
            for row in rows
        ]
