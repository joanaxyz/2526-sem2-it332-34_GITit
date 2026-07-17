from datetime import timedelta

from django.db.models import Count, Prefetch, Q, Sum
from django.db.models.functions import TruncDate
from django.utils import timezone

from adventures.models import AdventureRun, SkillMastery
from challenges.models import ChallengeRun
from common.constants import (
    DIFFICULTY_HARD,
    RESULT_INVALID,
    RESULT_UNPROCESSABLE,
    SESSION_STATUS_ABANDONED,
    SESSION_STATUS_COMPLETED,
    SESSION_STATUS_FAILED,
)
from curriculum.models import CommandForm, CommandSkill
from curriculum.selectors import published_stories, stories_completed_map
from practice.models import CommandStep
from progress.models import (
    AdventureLevelCompletion,
    ChallengeTrialCompletion,
    StreakRecord,
    Wallet,
)

# Trailing window (days) for the activity trend.

TREND_DAYS = 14


class MetricsService:
    def dashboard_summary(self, *, player) -> dict:
        challenge_counts = ChallengeRun.objects.filter(player=player).aggregate(
            started=Count("id", filter=Q(is_replay=False)),
            completed=Count("id", filter=Q(is_replay=False, status=SESSION_STATUS_COMPLETED)),
            failed=Count("id", filter=Q(is_replay=False, status=SESSION_STATUS_FAILED)),
            abandoned=Count("id", filter=Q(is_replay=False, status=SESSION_STATUS_ABANDONED)),
            hard_started=Count(
                "id",
                filter=Q(is_replay=False, challenge_trial__difficulty=DIFFICULTY_HARD),
            ),
            hard_completed=Count(
                "id",
                filter=Q(
                    is_replay=False,
                    challenge_trial__difficulty=DIFFICULTY_HARD,
                    status=SESSION_STATUS_COMPLETED,
                ),
            ),
            completed_retry_total=Sum(
                "retry_index", filter=Q(is_replay=False, status=SESSION_STATUS_COMPLETED)
            ),
        )
        adventure_counts = AdventureRun.objects.filter(player=player, is_replay=False).aggregate(
            started=Count("id"),
            completed=Count("id", filter=Q(status=SESSION_STATUS_COMPLETED)),
            failed=Count("id", filter=Q(status=SESSION_STATUS_FAILED)),
            abandoned=Count("id", filter=Q(status=SESSION_STATUS_ABANDONED)),
        )
        started = (challenge_counts["started"] or 0) + (adventure_counts["started"] or 0)
        completed = (challenge_counts["completed"] or 0) + (adventure_counts["completed"] or 0)
        failed = (challenge_counts["failed"] or 0) + (adventure_counts["failed"] or 0)
        abandoned = (challenge_counts["abandoned"] or 0) + (adventure_counts["abandoned"] or 0)

        chapter_rows = (
            ChallengeRun.objects.filter(player=player, is_replay=False)
            .values("challenge_trial__challenge_level__chapter__number")
            .annotate(
                hard_started=Count("id", filter=Q(challenge_trial__difficulty=DIFFICULTY_HARD)),
                hard_completed=Count(
                    "id",
                    filter=Q(
                        challenge_trial__difficulty=DIFFICULTY_HARD, status=SESSION_STATUS_COMPLETED
                    ),
                ),
                started_count=Count("id"),
                completed_count=Count("id", filter=Q(status=SESSION_STATUS_COMPLETED)),
                completed_retry_total=Sum("retry_index", filter=Q(status=SESSION_STATUS_COMPLETED)),
            )
        )
        chapter_metrics_map = {
            int(row["challenge_trial__challenge_level__chapter__number"]): row
            for row in chapter_rows
            if row["challenge_trial__challenge_level__chapter__number"] is not None
        }
        chapter_kpis = {
            str(chapter_number): {
                "scr": self._rate(
                    chapter_metrics_map.get(chapter_number, {}).get("completed_count") or 0,
                    chapter_metrics_map.get(chapter_number, {}).get("started_count") or 0,
                ),
                "hlcr": self._rate(
                    chapter_metrics_map.get(chapter_number, {}).get("hard_completed") or 0,
                    chapter_metrics_map.get(chapter_number, {}).get("hard_started") or 0,
                ),
                "arc": self._average_retry_count_from_counts(
                    chapter_metrics_map.get(chapter_number, {}).get("completed_retry_total") or 0,
                    chapter_metrics_map.get(chapter_number, {}).get("completed_count") or 0,
                ),
            }
            for chapter_number in sorted(chapter_metrics_map)
        }
        streak = (
            StreakRecord.objects.filter(player=player)
            .only(
                "current_streak",
                "longest_streak",
                "last_completed_on",
            )
            .first()
        )
        stories = list(published_stories())
        completed_map = stories_completed_map(player=player, stories=stories)
        completed_stories = [story.slug for story in stories if completed_map.get(story.id, False)]
        perfect_stars = (
            AdventureLevelCompletion.objects.filter(player=player, stars=3).count()
            + ChallengeTrialCompletion.objects.filter(player=player, stars=3).count()
        )
        return {
            "kpis": {
                "scr": self._rate(completed, started),
                "arc": self._average_retry_count_from_counts(
                    challenge_counts["completed_retry_total"] or 0, completed
                ),
                "hlcr": self._rate(
                    challenge_counts["hard_completed"] or 0, challenge_counts["hard_started"] or 0
                ),
            },
            "chapter_kpis": chapter_kpis,
            "counts": {
                "started": started,
                "completed": completed,
                "failed": failed,
                "abandoned": abandoned,
            },
            "completed_story_slug": completed_stories[0] if completed_stories else None,
            "completed_stories": completed_stories,
            "streak": {
                "current": streak.current_streak if streak else 0,
                "longest": streak.longest_streak if streak else 0,
                "last_completed_on": streak.last_completed_on if streak else None,
            },
            "perfect_clears": perfect_stars,
            # Rank is expressed directly as a 0-100 mastery score.
            "mastery": self._mastery_score(player=player) or 0,
            "retry_trends": self._retry_trends(player=player, started=started),
        }

    def stats_summary(self, *, player) -> dict:
        """Learner-facing Stats page with per-command mastery, activity, and KPIs."""
        now = timezone.now()
        since = now - timedelta(days=TREND_DAYS - 1)
        today = timezone.localdate()

        # Accuracy + total volume from the unified command log (spans both modes).
        steps = CommandStep.objects.filter(
            Q(challenge_run__player=player) | Q(attempt__player=player)
        )
        step_totals = steps.aggregate(
            total=Count("id"),
            unclean=Count(
                "id", filter=Q(result_category__in=[RESULT_INVALID, RESULT_UNPROCESSABLE])
            ),
        )
        total_steps = step_totals["total"] or 0
        accuracy = (
            round((total_steps - (step_totals["unclean"] or 0)) / total_steps * 100, 1)
            if total_steps
            else None
        )

        adv_completions = AdventureLevelCompletion.objects.filter(player=player)
        chal_completions = ChallengeTrialCompletion.objects.filter(player=player)
        adv_perf_hits = adv_completions.filter(stars=3).count()
        chal_perf_hits = chal_completions.filter(stars=3).count()
        adv_done = adv_completions.count()
        chal_done = chal_completions.count()
        skill_profile = self._git_skill_profile(player=player)

        # Headline numbers.
        chal_counts = ChallengeRun.objects.filter(player=player, is_replay=False).aggregate(
            started=Count("id"),
            completed=Count("id", filter=Q(status=SESSION_STATUS_COMPLETED)),
            comebacks=Count("id", filter=Q(status=SESSION_STATUS_COMPLETED, retry_index__gt=0)),
            hard_completed=Count(
                "id",
                filter=Q(
                    status=SESSION_STATUS_COMPLETED, challenge_trial__difficulty=DIFFICULTY_HARD
                ),
            ),
        )
        adv_counts = AdventureRun.objects.filter(player=player, is_replay=False).aggregate(
            started=Count("id"),
            completed=Count("id", filter=Q(status=SESSION_STATUS_COMPLETED)),
        )
        started = (chal_counts["started"] or 0) + (adv_counts["started"] or 0)
        completed = (chal_counts["completed"] or 0) + (adv_counts["completed"] or 0)
        streak = (
            StreakRecord.objects.filter(player=player)
            .only("current_streak", "longest_streak")
            .first()
        )
        wallet = Wallet.objects.filter(player=player).only("balance").first()

        headline = {
            "levels_completed": adv_done + chal_done,
            "finish_rate": self._rate(completed, started),
            "accuracy": accuracy,
            # boss_floors / comebacks are challenge-only concepts (difficulty tiers,
            # retry-to-attempt). The scope flag lets the UI frame them honestly
            # instead of implying they cover adventures.
            "boss_floors": {"value": chal_counts["hard_completed"] or 0, "scope": "challenge"},
            "comebacks": {"value": chal_counts["comebacks"] or 0, "scope": "challenge"},
            "perfect_clears": adv_perf_hits + chal_perf_hits,
            "day_streak": streak.current_streak if streak else 0,
            "longest_streak": streak.longest_streak if streak else 0,
            "gitcoins": wallet.balance if wallet else 0,
            "commands_run": total_steps,
        }

        return {
            "skill_profile": skill_profile,
            "activity_trend": self._activity_trend(player=player, since=since, today=today),
            "headline": headline,
        }

    def _git_skill_profile(self, *, player) -> list[dict]:
        """Return every playable published Git skill with form-level mastery rolled up."""
        from adventures.services import form_solve_targets

        playable_forms = CommandForm.objects.filter(
            is_published=True,
            is_playable=True,
            chapter__is_published=True,
            chapter__is_playable=True,
            chapter__story__is_published=True,
        ).order_by("sort_order", "id")
        skills = list(
            CommandSkill.objects.filter(
                is_published=True,
                command_forms__is_published=True,
                command_forms__is_playable=True,
                command_forms__chapter__is_published=True,
                command_forms__chapter__is_playable=True,
                command_forms__chapter__story__is_published=True,
            )
            .distinct()
            .prefetch_related(
                Prefetch("command_forms", queryset=playable_forms, to_attr="playable_forms")
            )
            .order_by("sort_order", "base_command")
        )
        form_ids = {command_form.id for skill in skills for command_form in skill.playable_forms}
        solves_by_form = dict(
            SkillMastery.objects.filter(player=player, command_form_id__in=form_ids).values_list(
                "command_form_id",
                "solves",
            )
        )
        targets = form_solve_targets(form_ids)

        profile = []
        for skill in skills:
            ratios = [
                min(
                    1.0,
                    solves_by_form.get(command_form.id, 0) / (targets.get(command_form.id) or 1),
                )
                for command_form in skill.playable_forms
            ]
            profile.append(
                {
                    "key": skill.slug,
                    "command": skill.base_command,
                    "label": skill.base_command,
                    "hint": skill.title,
                    "value": round((sum(ratios) / len(ratios)) * 100, 1) if ratios else 0.0,
                }
            )
        return profile

    def _mastery_score(self, *, player) -> float | None:
        """Blend adventure solve depth with challenge clear ratio for rank."""
        from adventures.services import form_solve_targets

        masteries = list(
            SkillMastery.objects.filter(player=player, solves__gte=1).select_related("command_form")
        )
        targets = form_solve_targets({m.command_form_id for m in masteries})
        adv_ratios = [
            min(1.0, mastery.solves / (targets.get(mastery.command_form_id) or 1)) * 100
            for mastery in masteries
        ]
        chal_cleared = ChallengeTrialCompletion.objects.filter(player=player).count()
        chal_attempted = (
            ChallengeRun.objects.filter(player=player, is_replay=False)
            .values("challenge_trial")
            .distinct()
            .count()
        )
        return self._blend(
            [
                (self._mean(adv_ratios), len(adv_ratios)),
                (self._rate(chal_cleared, chal_attempted)["value"], chal_attempted),
            ]
        )

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

    def _activity_trend(self, *, player, since, today) -> list[dict]:
        completed_by_day = dict(
            AdventureLevelCompletion.objects.filter(player=player, completed_at__gte=since)
            .annotate(day=TruncDate("completed_at"))
            .values("day")
            .annotate(count=Count("id"))
            .values_list("day", "count")
        )
        for day, count in (
            ChallengeTrialCompletion.objects.filter(player=player, completed_at__gte=since)
            .annotate(day=TruncDate("completed_at"))
            .values("day")
            .annotate(count=Count("id"))
            .values_list("day", "count")
        ):
            completed_by_day[day] = completed_by_day.get(day, 0) + count
        commands_by_day = dict(
            CommandStep.objects.filter(
                Q(challenge_run__player=player) | Q(attempt__player=player), created_at__gte=since
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

    def _average_retry_count_from_counts(self, numerator: int, denominator: int) -> dict:
        return {
            "value": round(numerator / denominator, 2) if denominator else None,
            "numerator": numerator,
            "denominator": denominator,
        }

    def _retry_trends(self, *, player, started: int) -> list[dict]:
        if started < 2:
            return []
        rows = (
            ChallengeRun.objects.filter(player=player, is_replay=False)
            .values("challenge_trial__challenge_level__title")
            .annotate(
                attempts=Count("id"),
                retries=Count("id", filter=Q(prior_run__isnull=False)),
            )
            .order_by("-retries")[:6]
        )
        return [
            {
                "level_title": row["challenge_trial__challenge_level__title"],
                "attempts": row["attempts"],
                "retries": row["retries"],
                "label": "No trend available"
                if row["attempts"] < 2
                else f"{row['retries']} retry runs",
            }
            for row in rows
        ]
