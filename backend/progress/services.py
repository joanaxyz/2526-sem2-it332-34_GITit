from datetime import timedelta

from django.db.models import Case, Count, ExpressionWrapper, F, FloatField, Q, Sum, Value, When
from django.utils import timezone

from common.constants import (
    DIFFICULTY_HARD,
    SESSION_MODE_PRIMARY,
    SESSION_MODE_REVIEW,
    SESSION_STATUS_ABANDONED,
    SESSION_STATUS_COMPLETED,
    SESSION_STATUS_FAILED,
)
from learning.models import Lesson
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
        session_counts = ScenarioSession.objects.filter(user=user).aggregate(
            started=Count("id", filter=Q(mode=SESSION_MODE_PRIMARY)),
            completed=Count(
                "id",
                filter=Q(mode=SESSION_MODE_PRIMARY, status=SESSION_STATUS_COMPLETED),
            ),
            failed=Count(
                "id",
                filter=Q(mode=SESSION_MODE_PRIMARY, status=SESSION_STATUS_FAILED),
            ),
            abandoned=Count(
                "id",
                filter=Q(mode=SESSION_MODE_PRIMARY, status=SESSION_STATUS_ABANDONED),
            ),
            hard_started=Count(
                "id",
                filter=Q(
                    mode=SESSION_MODE_PRIMARY,
                    difficulty_instance__difficulty=DIFFICULTY_HARD,
                ),
            ),
            hard_completed=Count(
                "id",
                filter=Q(
                    mode=SESSION_MODE_PRIMARY,
                    difficulty_instance__difficulty=DIFFICULTY_HARD,
                    status=SESSION_STATUS_COMPLETED,
                ),
            ),
            rta_success=Count(
                "id",
                filter=Q(mode=SESSION_MODE_PRIMARY, rta_eligible=True, rta_success=True),
            ),
            rta_total=Count(
                "id",
                filter=Q(mode=SESSION_MODE_PRIMARY, rta_eligible=True),
            ),
            completed_retry_total=Sum(
                "retry_index",
                filter=Q(mode=SESSION_MODE_PRIMARY, status=SESSION_STATUS_COMPLETED),
            ),
            review_started=Count("id", filter=Q(mode=SESSION_MODE_REVIEW)),
            review_completed=Count(
                "id",
                filter=Q(mode=SESSION_MODE_REVIEW, status=SESSION_STATUS_COMPLETED),
            ),
        )
        started = session_counts["started"] or 0
        completed = session_counts["completed"] or 0
        failed = session_counts["failed"] or 0
        abandoned = session_counts["abandoned"] or 0
        hard_started = session_counts["hard_started"] or 0
        hard_completed = session_counts["hard_completed"] or 0
        review_started = session_counts["review_started"] or 0
        review_completed = session_counts["review_completed"] or 0
        orientation_counts = Lesson.objects.filter(
            unit__is_orientation=True,
            is_published=True,
        ).aggregate(
            total=Count("id", distinct=True),
            completed=Count(
                "orientationprogress",
                filter=Q(
                    orientationprogress__user=user,
                    orientationprogress__completed_at__isnull=False,
                ),
                distinct=True,
            ),
        )
        orientation_lesson_count = orientation_counts["total"] or 0
        orientation_completed = orientation_counts["completed"] or 0

        completion_metrics = CompletionRecord.objects.filter(user=user).aggregate(
            first_attempt_stars=Count("id", filter=Q(first_attempt_star=True)),
            command_accuracy_total=Sum(
                Case(
                    When(
                        counted_action_total__lte=F(
                            "difficulty_instance__command_policy__min_counted_commands"
                        ),
                        then=Value(100.0),
                    ),
                    When(
                        difficulty_instance__command_policy__min_counted_commands=0,
                        then=Value(0.0),
                    ),
                    default=ExpressionWrapper(
                        Value(100.0)
                        * F("difficulty_instance__command_policy__min_counted_commands")
                        / F("counted_action_total"),
                        output_field=FloatField(),
                    ),
                    output_field=FloatField(),
                )
            ),
            command_accuracy_count=Count("id"),
        )
        module_rows = (
            ScenarioSession.objects.filter(user=user, mode=SESSION_MODE_PRIMARY)
            .values("learning_unit__number")
            .annotate(
                hard_started=Count(
                    "id",
                    filter=Q(difficulty_instance__difficulty=DIFFICULTY_HARD),
                ),
                hard_completed=Count(
                    "id",
                    filter=Q(
                        difficulty_instance__difficulty=DIFFICULTY_HARD,
                        status=SESSION_STATUS_COMPLETED,
                    ),
                ),
                rta_success=Count("id", filter=Q(rta_eligible=True, rta_success=True)),
                rta_total=Count("id", filter=Q(rta_eligible=True)),
            )
        )
        module_metrics_map = {
            int(row["learning_unit__number"]): row
            for row in module_rows
            if row["learning_unit__number"] is not None
        }

        streak = StreakRecord.objects.filter(user=user).only(
            "current_streak",
            "longest_streak",
            "last_completed_on",
        ).first()
        return {
            "kpis": {
                "orientation_completion": self._rate(
                    orientation_completed,
                    orientation_lesson_count,
                ),
                "scr": self._rate(completed, started),
                "arc": self._average_retry_count_from_counts(
                    session_counts["completed_retry_total"] or 0,
                    completed,
                ),
                "car": self._average_percent_from_counts(
                    completion_metrics["command_accuracy_total"] or 0,
                    completion_metrics["command_accuracy_count"] or 0,
                ),
                "hlcr": self._rate(hard_completed, hard_started),
                "rta": self._rate(
                    session_counts["rta_success"] or 0,
                    session_counts["rta_total"] or 0,
                ),
                "sar": self._rate(abandoned, started),
                "review_scr": self._rate(review_completed, review_started),
            },
            "module_kpis": {
                str(module_number): {
                    "hlcr": self._rate(
                        (
                            module_metrics_map.get(module_number, {}).get("hard_completed")
                            or 0
                        ),
                        (
                            module_metrics_map.get(module_number, {}).get("hard_started")
                            or 0
                        ),
                    ),
                    "rta": self._rate(
                        (module_metrics_map.get(module_number, {}).get("rta_success") or 0),
                        (module_metrics_map.get(module_number, {}).get("rta_total") or 0),
                    ),
                }
                for module_number in [1, 2, 3, 4]
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
            "first_attempt_stars": completion_metrics["first_attempt_stars"] or 0,
            "retry_trends": self._retry_trends(user=user, started=started),
        }

    def _rate(self, numerator: int, denominator: int) -> dict:
        return {
            "value": round((numerator / denominator) * 100, 1) if denominator else None,
            "numerator": numerator,
            "denominator": denominator,
        }

    def _average_percent(self, values: list[int]) -> dict:
        total = sum(values)
        return self._average_percent_from_counts(total, len(values))

    def _average_percent_from_counts(self, total: float, count: int) -> dict:
        return {
            "value": round(total / count, 1) if count else None,
            "numerator": round(total, 1),
            "denominator": count,
        }

    def _command_accuracy_for_completion(self, completion: CompletionRecord) -> int:
        target_actions = completion.difficulty_instance.command_policy.min_counted_commands
        used_actions = completion.counted_action_total
        if used_actions <= target_actions:
            return 100
        if target_actions == 0:
            return 0
        return round((target_actions / used_actions) * 100)

    def _average_retry_count_from_counts(self, numerator: int, denominator: int) -> dict:
        return {
            "value": round(numerator / denominator, 2) if denominator else None,
            "numerator": numerator,
            "denominator": denominator,
        }

    def _retry_trends(self, *, user, started: int) -> list[dict]:
        if started < 2:
            return []
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
