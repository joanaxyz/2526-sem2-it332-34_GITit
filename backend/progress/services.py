from datetime import timedelta

from django.db.models import Avg, Count, Q, Sum
from django.db.models.functions import TruncDate
from django.utils import timezone

from challenges.models import ChallengeLevel, ChallengeRun
from challenges.selectors import command_accuracy_rate, minimum_counted_for_run
from command_adventures.models import (
    AdventureLevel,
    AdventureLevelAttempt,
    AdventureMastery,
    AdventureRun,
)
from common.constants import (
    DIFFICULTY_HARD,
    RESULT_INVALID,
    RESULT_UNPROCESSABLE,
    SESSION_MODE_PRIMARY,
    SESSION_MODE_REVIEW,
    SESSION_STATUS_ABANDONED,
    SESSION_STATUS_COMPLETED,
    SESSION_STATUS_FAILED,
)
from practice.models import CommandStep
from progress.models import LevelCompletion, StreakRecord, Wallet

# Trailing window (days) for the activity trend and the consistency axis.
TREND_DAYS = 14

# The six axes of the Skill Profile radar. Each is a friendly, learner-facing
# quality scored 0-100; `hint` is the plain-language tooltip. Adventures and
# challenges are blended per-axis wherever both produce data (see stats_summary).
SKILL_AXES = [
    ("accuracy", "Accuracy", "How many of your commands run cleanly, with no typos or invalid git."),
    ("efficiency", "Efficiency", "How close to the ideal number of commands you solve in."),
    ("independence", "Independence", "Solving on your own, without leaning on hints."),
    ("consistency", "Consistency", f"How many of the last {TREND_DAYS} days you showed up to train."),
    ("mastery", "Mastery", "How deeply you've drilled the commands you've met."),
    ("coverage", "Coverage", "The share of all levels you've completed at least once."),
]


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
        challenge_counts = ChallengeRun.objects.filter(user=user).aggregate(
            started=Count("id", filter=Q(mode=SESSION_MODE_PRIMARY)),
            completed=Count("id", filter=Q(mode=SESSION_MODE_PRIMARY, status=SESSION_STATUS_COMPLETED)),
            failed=Count("id", filter=Q(mode=SESSION_MODE_PRIMARY, status=SESSION_STATUS_FAILED)),
            abandoned=Count("id", filter=Q(mode=SESSION_MODE_PRIMARY, status=SESSION_STATUS_ABANDONED)),
            hard_started=Count(
                "id",
                filter=Q(mode=SESSION_MODE_PRIMARY, challenge_level__difficulty=DIFFICULTY_HARD),
            ),
            hard_completed=Count(
                "id",
                filter=Q(
                    mode=SESSION_MODE_PRIMARY,
                    challenge_level__difficulty=DIFFICULTY_HARD,
                    status=SESSION_STATUS_COMPLETED,
                ),
            ),
            rta_success=Count("id", filter=Q(mode=SESSION_MODE_PRIMARY, rta_eligible=True, rta_success=True)),
            rta_total=Count("id", filter=Q(mode=SESSION_MODE_PRIMARY, rta_eligible=True)),
            completed_retry_total=Sum("retry_index", filter=Q(mode=SESSION_MODE_PRIMARY, status=SESSION_STATUS_COMPLETED)),
            review_started=Count("id", filter=Q(mode=SESSION_MODE_REVIEW)),
        )
        adventure_counts = AdventureRun.objects.filter(
            user=user, mode=SESSION_MODE_PRIMARY
        ).aggregate(
            started=Count("id"),
            completed=Count("id", filter=Q(status=SESSION_STATUS_COMPLETED)),
            failed=Count("id", filter=Q(status=SESSION_STATUS_FAILED)),
            abandoned=Count("id", filter=Q(status=SESSION_STATUS_ABANDONED)),
        )
        started = (challenge_counts["started"] or 0) + (adventure_counts["started"] or 0)
        completed = (challenge_counts["completed"] or 0) + (adventure_counts["completed"] or 0)
        failed = (challenge_counts["failed"] or 0) + (adventure_counts["failed"] or 0)
        abandoned = (challenge_counts["abandoned"] or 0) + (adventure_counts["abandoned"] or 0)

        completion_records = LevelCompletion.objects.filter(user=user).select_related("challenge_run")
        accuracy_values = [
            command_accuracy_rate(
                status=record.challenge_run.status,
                counted_action_total=record.counted_action_total,
                minimum_counted_commands=minimum_counted_for_run(run=record.challenge_run),
            )
            or 0
            for record in completion_records
            if record.challenge_run_id
        ]
        storey_rows = (
            ChallengeRun.objects.filter(user=user, mode=SESSION_MODE_PRIMARY)
            .values("storey__number")
            .annotate(
                hard_started=Count("id", filter=Q(challenge_level__difficulty=DIFFICULTY_HARD)),
                hard_completed=Count(
                    "id",
                    filter=Q(challenge_level__difficulty=DIFFICULTY_HARD, status=SESSION_STATUS_COMPLETED),
                ),
                rta_success=Count("id", filter=Q(rta_eligible=True, rta_success=True)),
                rta_total=Count("id", filter=Q(rta_eligible=True)),
                started_count=Count("id"),
                completed_count=Count("id", filter=Q(status=SESSION_STATUS_COMPLETED)),
                completed_retry_total=Sum("retry_index", filter=Q(status=SESSION_STATUS_COMPLETED)),
            )
        )
        storey_metrics_map = {
            int(row["storey__number"]): row
            for row in storey_rows
            if row["storey__number"] is not None
        }
        storey_kpis = {
            str(storey_number): {
                "scr": self._rate(
                    storey_metrics_map.get(storey_number, {}).get("completed_count") or 0,
                    storey_metrics_map.get(storey_number, {}).get("started_count") or 0,
                ),
                "hlcr": self._rate(
                    storey_metrics_map.get(storey_number, {}).get("hard_completed") or 0,
                    storey_metrics_map.get(storey_number, {}).get("hard_started") or 0,
                ),
                "rta": self._rate(
                    storey_metrics_map.get(storey_number, {}).get("rta_success") or 0,
                    storey_metrics_map.get(storey_number, {}).get("rta_total") or 0,
                ),
                "arc": self._average_retry_count_from_counts(
                    storey_metrics_map.get(storey_number, {}).get("completed_retry_total") or 0,
                    storey_metrics_map.get(storey_number, {}).get("completed_count") or 0,
                ),
            }
            for storey_number in sorted(storey_metrics_map)
        }
        streak = StreakRecord.objects.filter(user=user).only(
            "current_streak",
            "longest_streak",
            "last_completed_on",
        ).first()
        return {
            "kpis": {
                "scr": self._rate(completed, started),
                "arc": self._average_retry_count_from_counts(challenge_counts["completed_retry_total"] or 0, completed),
                "car": self._average_percent(accuracy_values),
                "hlcr": self._rate(challenge_counts["hard_completed"] or 0, challenge_counts["hard_started"] or 0),
                "rta": self._rate(challenge_counts["rta_success"] or 0, challenge_counts["rta_total"] or 0),
            },
            "storey_kpis": storey_kpis,
            "counts": {
                "started": started,
                "completed": completed,
                "failed": failed,
                "abandoned": abandoned,
                "review_started": challenge_counts["review_started"] or 0,
            },
            "streak": {
                "current": streak.current_streak if streak else 0,
                "longest": streak.longest_streak if streak else 0,
                "last_completed_on": streak.last_completed_on if streak else None,
            },
            "first_attempt_stars": LevelCompletion.objects.filter(user=user, first_attempt_star=True).count(),
            "retry_trends": self._retry_trends(user=user, started=started),
        }

    def stats_summary(self, *, user) -> dict:
        """Learner-facing Stats page: a 6-axis Skill Profile radar, a daily
        activity trend, and friendly headline numbers. Unlike dashboard_summary
        (challenge-weighted), every axis blends adventures and challenges where
        both produce data, so adventure-only learners still get a full profile."""
        now = timezone.now()
        since = now - timedelta(days=TREND_DAYS - 1)
        today = timezone.localdate()

        # Accuracy + total volume from the unified command log (spans both modes
        # via challenge_run=ChallengeRun and attempt=AdventureLevelAttempt).
        steps = CommandStep.objects.filter(Q(challenge_run__user=user) | Q(attempt__run__user=user))
        step_totals = steps.aggregate(
            total=Count("id"),
            unclean=Count("id", filter=Q(result_category__in=[RESULT_INVALID, RESULT_UNPROCESSABLE])),
        )
        total_steps = step_totals["total"] or 0
        accuracy = (
            round((total_steps - (step_totals["unclean"] or 0)) / total_steps * 100, 1)
            if total_steps
            else None
        )

        # Efficiency: adventure efficiency_score + challenge command-accuracy rate.
        adv_attempts = AdventureLevelAttempt.objects.filter(run__user=user, status=SESSION_STATUS_COMPLETED)
        adv_scores = adv_attempts.aggregate(
            efficiency=Avg("efficiency_score"),
            independence=Avg("independence_score"),
            n=Count("id"),
        )
        chal_completion = LevelCompletion.objects.filter(
            user=user, challenge_run__isnull=False
        ).select_related("challenge_run")
        chal_eff_values = [
            command_accuracy_rate(
                status=record.challenge_run.status,
                counted_action_total=record.counted_action_total,
                minimum_counted_commands=minimum_counted_for_run(run=record.challenge_run),
            )
            or 0
            for record in chal_completion
        ]
        efficiency = self._blend(
            [
                (adv_scores["efficiency"], adv_scores["n"] or 0),
                (self._mean(chal_eff_values), len(chal_eff_values)),
            ]
        )

        # Independence is adventure-only (challenges have no hint mechanic), so we
        # report it only when adventure attempts exist rather than faking a 100.
        independence = round(adv_scores["independence"], 1) if adv_scores["n"] else None

        # Consistency: how many of the last TREND_DAYS days had any activity.
        active_days = self._active_days(user=user, since=since)
        consistency = round(min(1.0, len(active_days) / TREND_DAYS) * 100, 1) if total_steps else None

        # Mastery: adventure Leitner depth (box / required) + challenge clear ratio.
        masteries = AdventureMastery.objects.filter(user=user, introduced=True).select_related("adventure_level")
        adv_ratios = [
            min(1.0, mastery.strength / (mastery.adventure_level.required_successful_attempts or 1)) * 100
            for mastery in masteries
        ]
        chal_attempted = (
            ChallengeRun.objects.filter(user=user, mode=SESSION_MODE_PRIMARY)
            .values("challenge_level")
            .distinct()
            .count()
        )
        chal_cleared = (
            ChallengeRun.objects.filter(user=user, mode=SESSION_MODE_PRIMARY, status=SESSION_STATUS_COMPLETED)
            .values("challenge_level")
            .distinct()
            .count()
        )
        mastery = self._blend(
            [
                (self._mean(adv_ratios), len(adv_ratios)),
                (self._rate(chal_cleared, chal_attempted)["value"], chal_attempted),
            ]
        )

        # Coverage: distinct levels completed over all published levels (both ladders).
        adv_done = LevelCompletion.objects.filter(user=user, adventure_level__isnull=False).count()
        chal_done = LevelCompletion.objects.filter(user=user, challenge_level__isnull=False).count()
        total_levels = (
            AdventureLevel.objects.filter(is_published=True).count()
            + ChallengeLevel.objects.filter(is_published=True).count()
        )
        coverage = round((adv_done + chal_done) / total_levels * 100, 1) if total_levels else None

        axis_values = {
            "accuracy": accuracy,
            "efficiency": efficiency,
            "independence": independence,
            "consistency": consistency,
            "mastery": mastery,
            "coverage": coverage,
        }
        skill_profile = [
            {"key": key, "label": label, "hint": hint, "value": axis_values[key]}
            for key, label, hint in SKILL_AXES
        ]

        # Headline numbers.
        chal_counts = ChallengeRun.objects.filter(user=user, mode=SESSION_MODE_PRIMARY).aggregate(
            started=Count("id"),
            completed=Count("id", filter=Q(status=SESSION_STATUS_COMPLETED)),
            hard_completed=Count(
                "id", filter=Q(status=SESSION_STATUS_COMPLETED, challenge_level__difficulty=DIFFICULTY_HARD)
            ),
            comebacks=Count("id", filter=Q(rta_eligible=True, rta_success=True)),
        )
        adv_counts = AdventureRun.objects.filter(user=user, mode=SESSION_MODE_PRIMARY).aggregate(
            started=Count("id"),
            completed=Count("id", filter=Q(status=SESSION_STATUS_COMPLETED)),
        )
        started = (chal_counts["started"] or 0) + (adv_counts["started"] or 0)
        completed = (chal_counts["completed"] or 0) + (adv_counts["completed"] or 0)
        streak = StreakRecord.objects.filter(user=user).only("current_streak", "longest_streak").first()
        wallet = Wallet.objects.filter(user=user).only("balance").first()

        headline = {
            "levels_completed": adv_done + chal_done,
            "finish_rate": self._rate(completed, started),
            "accuracy": accuracy,
            # boss_floors / comebacks are challenge-only concepts (difficulty tiers,
            # retry-to-attempt). The scope flag lets the UI frame them honestly
            # instead of implying they cover adventures.
            "boss_floors": {"value": chal_counts["hard_completed"] or 0, "scope": "challenge"},
            "comebacks": {"value": chal_counts["comebacks"] or 0, "scope": "challenge"},
            "perfect_clears": LevelCompletion.objects.filter(user=user, first_attempt_star=True).count(),
            "day_streak": streak.current_streak if streak else 0,
            "longest_streak": streak.longest_streak if streak else 0,
            "gitcoins": wallet.balance if wallet else 0,
            "commands_run": total_steps,
        }

        return {
            "skill_profile": skill_profile,
            "activity_trend": self._activity_trend(user=user, since=since, today=today),
            "headline": headline,
        }

    def _mean(self, values: list) -> float | None:
        return round(sum(values) / len(values), 1) if values else None

    def _blend(self, parts: list[tuple]) -> float | None:
        """Volume-weighted average of (value, weight) pairs, skipping empty parts.
        Returns None only when no part has data, so a learner with just one mode
        still gets a real axis value."""
        numerator = 0.0
        denominator = 0.0
        for value, weight in parts:
            if value is None or weight <= 0:
                continue
            numerator += value * weight
            denominator += weight
        return round(numerator / denominator, 1) if denominator else None

    def _active_days(self, *, user, since) -> set:
        completion_days = (
            LevelCompletion.objects.filter(user=user, completed_at__gte=since)
            .annotate(day=TruncDate("completed_at"))
            .values_list("day", flat=True)
            .distinct()
        )
        step_days = (
            CommandStep.objects.filter(
                Q(challenge_run__user=user) | Q(attempt__run__user=user), created_at__gte=since
            )
            .annotate(day=TruncDate("created_at"))
            .values_list("day", flat=True)
            .distinct()
        )
        return set(completion_days) | set(step_days)

    def _activity_trend(self, *, user, since, today) -> list[dict]:
        completed_by_day = dict(
            LevelCompletion.objects.filter(user=user, completed_at__gte=since)
            .annotate(day=TruncDate("completed_at"))
            .values("day")
            .annotate(count=Count("id"))
            .values_list("day", "count")
        )
        commands_by_day = dict(
            CommandStep.objects.filter(
                Q(challenge_run__user=user) | Q(attempt__run__user=user), created_at__gte=since
            )
            .annotate(day=TruncDate("created_at"))
            .values("day")
            .annotate(count=Count("id"))
            .values_list("day", "count")
        )
        trend = []
        for offset in range(TREND_DAYS - 1, -1, -1):
            day = today - timedelta(days=offset)
            trend.append(
                {
                    "date": day.isoformat(),
                    "levels_completed": completed_by_day.get(day, 0),
                    "commands_run": commands_by_day.get(day, 0),
                }
            )
        return trend

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
            ChallengeRun.objects.filter(user=user, mode=SESSION_MODE_PRIMARY)
            .values("challenge__title")
            .annotate(
                attempts=Count("id"),
                retries=Count("id", filter=Q(prior_run__isnull=False)),
            )
            .order_by("-retries")[:6]
        )
        return [
            {
                "level_title": row["challenge__title"],
                "attempts": row["attempts"],
                "retries": row["retries"],
                "label": "No trend available" if row["attempts"] < 2 else f"{row['retries']} retry runs",
            }
            for row in rows
        ]
