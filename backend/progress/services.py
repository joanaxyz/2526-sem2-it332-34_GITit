from datetime import timedelta

from django.db.models import Count, Q, Sum
from django.utils import timezone

from common.constants import (
    DIFFICULTY_HARD,
    SESSION_MODE_PRIMARY,
    SESSION_MODE_REVIEW,
    SESSION_STATUS_ABANDONED,
    SESSION_STATUS_COMPLETED,
    SESSION_STATUS_FAILED,
)
from progress.models import StreakRecord
from scenarios.models import CompletionRecord, PracticeKind, PracticeSession
from scenarios.selectors import command_accuracy_rate, minimum_counted_for_session


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
        session_counts = PracticeSession.objects.filter(user=user).aggregate(
            started=Count("id", filter=Q(mode=SESSION_MODE_PRIMARY)),
            completed=Count("id", filter=Q(mode=SESSION_MODE_PRIMARY, status=SESSION_STATUS_COMPLETED)),
            failed=Count("id", filter=Q(mode=SESSION_MODE_PRIMARY, status=SESSION_STATUS_FAILED)),
            abandoned=Count("id", filter=Q(mode=SESSION_MODE_PRIMARY, status=SESSION_STATUS_ABANDONED)),
            hard_started=Count(
                "id",
                filter=Q(
                    mode=SESSION_MODE_PRIMARY,
                    practice_kind=PracticeKind.WORKFLOW_SCENARIO,
                    workflow_level__difficulty=DIFFICULTY_HARD,
                ),
            ),
            hard_completed=Count(
                "id",
                filter=Q(
                    mode=SESSION_MODE_PRIMARY,
                    practice_kind=PracticeKind.WORKFLOW_SCENARIO,
                    workflow_level__difficulty=DIFFICULTY_HARD,
                    status=SESSION_STATUS_COMPLETED,
                ),
            ),
            rta_success=Count("id", filter=Q(mode=SESSION_MODE_PRIMARY, rta_eligible=True, rta_success=True)),
            rta_total=Count("id", filter=Q(mode=SESSION_MODE_PRIMARY, rta_eligible=True)),
            completed_retry_total=Sum("retry_index", filter=Q(mode=SESSION_MODE_PRIMARY, status=SESSION_STATUS_COMPLETED)),
            review_started=Count("id", filter=Q(mode=SESSION_MODE_REVIEW)),
        )
        started = session_counts["started"] or 0
        completed = session_counts["completed"] or 0
        completion_records = CompletionRecord.objects.filter(user=user).select_related("session")
        accuracy_values = [
            command_accuracy_rate(
                status=record.session.status,
                counted_action_total=record.counted_action_total,
                minimum_counted_commands=minimum_counted_for_session(session=record.session),
            )
            or 0
            for record in completion_records
        ]
        module_rows = (
            PracticeSession.objects.filter(user=user, mode=SESSION_MODE_PRIMARY)
            .values("module__number")
            .annotate(
                hard_started=Count(
                    "id",
                    filter=Q(
                        practice_kind=PracticeKind.WORKFLOW_SCENARIO,
                        workflow_level__difficulty=DIFFICULTY_HARD,
                    ),
                ),
                hard_completed=Count(
                    "id",
                    filter=Q(
                        practice_kind=PracticeKind.WORKFLOW_SCENARIO,
                        workflow_level__difficulty=DIFFICULTY_HARD,
                        status=SESSION_STATUS_COMPLETED,
                    ),
                ),
                rta_success=Count("id", filter=Q(rta_eligible=True, rta_success=True)),
                rta_total=Count("id", filter=Q(rta_eligible=True)),
                started_count=Count("id"),
                completed_count=Count("id", filter=Q(status=SESSION_STATUS_COMPLETED)),
                completed_retry_total=Sum("retry_index", filter=Q(status=SESSION_STATUS_COMPLETED)),
            )
        )
        module_metrics_map = {
            int(row["module__number"]): row
            for row in module_rows
            if row["module__number"] is not None
        }
        streak = StreakRecord.objects.filter(user=user).only(
            "current_streak",
            "longest_streak",
            "last_completed_on",
        ).first()
        return {
            "kpis": {
                "practice_completion": self._rate(completed, started),
                "scr": self._rate(completed, started),
                "arc": self._average_retry_count_from_counts(
                    session_counts["completed_retry_total"] or 0,
                    completed,
                ),
                "car": self._average_percent(accuracy_values),
                "hlcr": self._rate(session_counts["hard_completed"] or 0, session_counts["hard_started"] or 0),
                "rta": self._rate(session_counts["rta_success"] or 0, session_counts["rta_total"] or 0),
            },
            "module_kpis": {
                str(module_number): {
                    "scr": self._rate(
                        module_metrics_map.get(module_number, {}).get("completed_count") or 0,
                        module_metrics_map.get(module_number, {}).get("started_count") or 0,
                    ),
                    "hlcr": self._rate(
                        module_metrics_map.get(module_number, {}).get("hard_completed") or 0,
                        module_metrics_map.get(module_number, {}).get("hard_started") or 0,
                    ),
                    "rta": self._rate(
                        module_metrics_map.get(module_number, {}).get("rta_success") or 0,
                        module_metrics_map.get(module_number, {}).get("rta_total") or 0,
                    ),
                    "arc": self._average_retry_count_from_counts(
                        module_metrics_map.get(module_number, {}).get("completed_retry_total") or 0,
                        module_metrics_map.get(module_number, {}).get("completed_count") or 0,
                    ),
                }
                for module_number in sorted(module_metrics_map)
            },
            "counts": {
                "started": started,
                "completed": completed,
                "failed": session_counts["failed"] or 0,
                "abandoned": session_counts["abandoned"] or 0,
                "review_started": session_counts["review_started"] or 0,
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
            "retry_trends": self._retry_trends(user=user, started=started),
        }

    def _rate(self, numerator: int, denominator: int) -> dict:
        return {
            "value": round((numerator / denominator) * 100, 1) if denominator else None,
            "numerator": numerator,
            "denominator": denominator,
        }

    def _average_percent(self, values: list[int]) -> dict:
        return {
            "value": round(sum(values) / len(values), 1) if values else None,
            "numerator": round(sum(values), 1),
            "denominator": len(values),
        }

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
            PracticeSession.objects.filter(user=user, mode=SESSION_MODE_PRIMARY)
            .values("practice_kind", "command_drill__title", "workflow_scenario__title")
            .annotate(
                attempts=Count("id"),
                retries=Count("id", filter=Q(prior_session__isnull=False)),
            )
            .order_by("-retries")[:6]
        )
        return [
            {
                "practice_kind": row["practice_kind"],
                "practice_title": row["command_drill__title"] or row["workflow_scenario__title"],
                "attempts": row["attempts"],
                "retries": row["retries"],
                "label": "No trend available" if row["attempts"] < 2 else f"{row['retries']} retry sessions",
            }
            for row in rows
        ]
