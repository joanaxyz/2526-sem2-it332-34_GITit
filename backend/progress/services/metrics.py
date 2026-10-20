from datetime import date, datetime, time, timedelta

from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from django.utils import timezone

from adventures.models import AdventureLevelTierRun, SkillMastery
from common.constants import (
    DIFFICULTY_HARD,
    RESULT_INVALID,
    RESULT_UNPROCESSABLE,
    SESSION_STATUS_ABANDONED,
    SESSION_STATUS_COMPLETED,
    SESSION_STATUS_FAILED,
)
from curriculum.models import Chapter, CommandForm, CommandSkill
from curriculum.selectors import published_stories, stories_completed_map
from practice.models import CommandStep
from progress.models import AdventureLevelTierCompletion, Wallet
from progress.objectives import SO_CAR_LEVELS
from progress.services.kpi_range import ALL_TIME, KpiRange

# Trailing window (days) for the consistency axis.

TREND_DAYS = 14

# Activity trend windows the learner can switch between. Each one is a trailing
# span plus the bucket it is summed into, so a year is twelve points rather than
# 365 unreadable ones.
ACTIVITY_WINDOWS = {
    "week": {"buckets": 7, "unit": "day"},
    "month": {"buckets": 30, "unit": "day"},
    "year": {"buckets": 12, "unit": "month"},
}
DEFAULT_ACTIVITY_WINDOW = "month"


def resolve_activity_window(value: str | None) -> str:
    """Any unknown window falls back to the default rather than erroring: the
    window only decides how much history to draw."""

    return value if value in ACTIVITY_WINDOWS else DEFAULT_ACTIVITY_WINDOW


def _month_start(day: date, months_back: int) -> date:
    year, month = day.year, day.month - months_back
    while month <= 0:
        month += 12
        year -= 1
    return date(year, month, 1)


class MetricsService:
    # The learner dashboard reports only the sole active Arcane Spire
    # curriculum. Retired story fixtures must never expand this profile.
    LEARNER_CURRICULUM_STORY_SLUG = "arcane-spire"
    PERFORMANCE_STORY_SLUG = LEARNER_CURRICULUM_STORY_SLUG
    PERFORMANCE_MODULE_NUMBERS = (1, 2, 3, 4)
    # RTA measures transfer to structurally changed scenarios; it is defined
    # for the conflict-resolution and recovery modules only.
    RTA_MODULE_NUMBERS = (3, 4)

    def performance_summary(self, *, player) -> dict:
        return self._performance_summary_for_runs(
            runs=self._performance_runs().filter(player=player)
        )

    def all_player_performance_summary(self, *, kpi_range: KpiRange = ALL_TIME) -> dict:
        """Return the same Arcane Spire diagnostic metrics across all learners.

        This is deliberately staff-console data: staff accounts are excluded
        and the optional date range applies. The player-facing endpoint keeps
        using ``performance_summary`` so its response and scope remain unchanged.
        """
        return self._performance_summary_for_runs(
            runs=self._kpi_runs(kpi_range=kpi_range), kpi_range=kpi_range, cohort=True
        )

    def admin_player_performance_summary(self, *, player, kpi_range: KpiRange = ALL_TIME) -> dict:
        """One learner's KPIs as the staff console reports them (same scope as
        the dashboard: staff accounts excluded, optional date range)."""
        return self._performance_summary_for_runs(
            runs=self._kpi_runs(kpi_range=kpi_range).filter(player=player),
            kpi_range=kpi_range,
        )

    def _performance_runs(self):
        return AdventureLevelTierRun.objects.filter(
            is_replay=False,
            is_transfer=False,
            tier__adventure_level__chapter__story__slug=self.PERFORMANCE_STORY_SLUG,
            tier__adventure_level__chapter__number__in=self.PERFORMANCE_MODULE_NUMBERS,
        )

    def _kpi_runs(self, *, kpi_range: KpiRange):
        """Runs every admin KPI is computed from.

        Staff accounts are excluded so play-testing on production never counts,
        and runs are limited to those started inside the (Manila-time) range.
        """
        return (
            self._performance_runs()
            .exclude(player__user__is_staff=True)
            .filter(kpi_range.q("started_at"))
        )

    def all_player_objective_car(self, *, kpi_range: KpiRange = ALL_TIME) -> dict:
        from .mastery_metrics import balanced, live_records

        records = live_records(self._kpi_runs(kpi_range=kpi_range), end_before=kpi_range.end_before)
        return {
            code: balanced([r for r in records if r["slug"] in slugs], cohort=True)["car"]
            for code, slugs in SO_CAR_LEVELS.items()
        }

    def _performance_summary_for_runs(
        self, *, runs, kpi_range: KpiRange = ALL_TIME, cohort=False
    ) -> dict:
        """One backend owner for mastery KPIs; activity totals are separate."""
        from progress.models import KpiCheckpoint

        from .mastery_metrics import balanced, live_records, samples

        records = live_records(runs, end_before=kpi_range.end_before)
        chapters = Chapter.objects.filter(
            story__slug=self.PERFORMANCE_STORY_SLUG,
            is_published=True,
            number__in=self.PERFORMANCE_MODULE_NUMBERS,
        ).order_by("sort_order", "number")
        modules = [
            {
                "number": c.number,
                "title": c.title,
                **balanced([r for r in records if r["module"] == c.number], cohort=cohort),
            }
            for c in chapters
        ]
        transfers = []
        players = {r["player_id"] for r in records}
        if not cohort and len(players) == 1:
            ready_tiers = {
                r["tier_id"]
                for r in records
                if r["transfer_assigned"] and r["transfer"] is None and not r["transfer_missing"]
            }
            for point in KpiCheckpoint.objects.filter(
                player_id__in=players,
                tier_id__in=ready_tiers,
                kind="transfer",
                ended_at__isnull=True,
            ).select_related("tier__adventure_level"):
                transfers.append(
                    {
                        "tier_id": point.tier_id,
                        "title": point.tier.adventure_level.title,
                        "run_id": point.run_id,
                    }
                )
        return {
            "kpis": balanced(records, cohort=cohort),
            "completed_sessions": runs.filter(status=SESSION_STATUS_COMPLETED).count(),
            "modules": modules,
            "samples": samples(records),
            "transfers": transfers,
        }

    def dashboard_summary(self, *, player) -> dict:
        runs = self._runebound_runs(player=player)
        run_counts = runs.aggregate(
            started=Count("id"),
            completed=Count("id", filter=Q(status=SESSION_STATUS_COMPLETED)),
            failed=Count("id", filter=Q(status=SESSION_STATUS_FAILED)),
            abandoned=Count("id", filter=Q(status=SESSION_STATUS_ABANDONED)),
        )
        started = run_counts["started"] or 0
        completed = run_counts["completed"] or 0
        failed = run_counts["failed"] or 0
        abandoned = run_counts["abandoned"] or 0

        performance = self.performance_summary(player=player)
        chapter_kpis = {
            str(module["number"]): {key: module[key] for key in ("scr", "hlcr", "arc")}
            for module in performance["modules"]
        }
        streak = self._runebound_streak(player=player)
        stories = list(published_stories().filter(slug=self.LEARNER_CURRICULUM_STORY_SLUG))
        completed_map = stories_completed_map(player=player, stories=stories)
        completed_stories = [story.slug for story in stories if completed_map.get(story.id, False)]
        perfect_stars = self._runebound_completions(player=player).filter(stars=3).count()
        return {
            "kpis": {key: performance["kpis"][key] for key in ("scr", "arc", "hlcr")},
            "chapter_kpis": chapter_kpis,
            "counts": {
                "started": started,
                "completed": completed,
                "failed": failed,
                "abandoned": abandoned,
            },
            "completed_story_slug": completed_stories[0] if completed_stories else None,
            "completed_stories": completed_stories,
            "streak": streak,
            "perfect_clears": perfect_stars,
            # Rank is expressed directly in terms of this (0-100): the same
            # "how deeply have you drilled what you've met" score as the Stats
            # page's Mastery radar axis.
            "mastery": self._mastery_score(player=player) or 0,
            "retry_trends": self._retry_trends(runs=runs, started=started),
        }

    def stats_summary(self, *, player, activity_window: str | None = None) -> dict:
        """Learner-facing Arcane Spire Stats page: a per-command Skill Profile, an
        activity trend over the requested window, and friendly headline numbers.

        Only `activity_trend` answers to `activity_window`; every headline number
        is all-time, so switching the window never changes what the rest of the
        screen reports."""
        # Accuracy + total volume from Arcane Spire tier runs only. Retired
        # story tracks must never alter the active-curriculum record.
        steps = self._runebound_steps(player=player)
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

        # Per-command skill mastery: only commands the playable curriculum can
        # actually teach and award progress for.
        skill_profile = self._command_skill_profile(player=player)

        # Arcane Spire tier completions are the progress units shown as levels.
        completion_counts = self._runebound_completions(player=player).aggregate(
            total=Count("id"),
            perfect=Count("id", filter=Q(stars=3)),
            hard=Count("id", filter=Q(tier__difficulty=DIFFICULTY_HARD)),
        )

        # Headline numbers.
        run_counts = self._runebound_runs(player=player).aggregate(
            started=Count("id"),
            completed=Count("id", filter=Q(status=SESSION_STATUS_COMPLETED)),
            comebacks=Count("id", filter=Q(status=SESSION_STATUS_COMPLETED, retry_index__gt=0)),
        )
        started = run_counts["started"] or 0
        completed = run_counts["completed"] or 0
        streak = self._runebound_streak(player=player)
        wallet = Wallet.objects.filter(player=player).only("balance").first()

        headline = {
            "levels_completed": completion_counts["total"] or 0,
            "finish_rate": self._rate(completed, started),
            "accuracy": accuracy,
            "boss_floors": {"value": completion_counts["hard"] or 0, "scope": "runebound"},
            "comebacks": {"value": run_counts["comebacks"] or 0, "scope": "runebound"},
            "perfect_clears": completion_counts["perfect"] or 0,
            "day_streak": streak["current"],
            "longest_streak": streak["longest"],
            "gitcoins": wallet.balance if wallet else 0,
            "commands_run": total_steps,
        }

        activity = self.activity_summary(player=player, activity_window=activity_window)
        return {
            "skill_profile": skill_profile,
            **activity,
            "headline": headline,
        }

    def activity_summary(self, *, player, activity_window: str | None = None) -> dict:
        """Return only the range-dependent portion of learner stats.

        Headline and skill-profile values are all-time. Keeping this narrow
        boundary lets a chart range change avoid recomputing those invariant
        aggregates while sharing the exact same bucketing implementation used
        by the full summary.
        """

        window = resolve_activity_window(activity_window)
        return {
            "activity_trend": self._activity_trend(
                player=player,
                window=window,
                today=timezone.localdate(),
            ),
            "activity_window": window,
        }

    def _command_skill_profile(self, *, player) -> list[dict]:
        """One row per mastery-bearing Arcane Spire command.

        The command library is intentionally broader than the active learner
        curriculum: it also contains other story tracks, reference-only entries,
        and forms the simulator may support before a required Arcane Spire wave
        teaches them. Those entries must not show up as learner mastery because
        they are outside this dashboard's curriculum boundary.

        Mastery for each included skill = average of (solves / target) across its
        published, playable forms that are exercised by a required published wave,
        capped at 100%.
        """
        from adventures.services import form_solve_targets

        forms = list(
            CommandForm.objects.filter(
                is_published=True,
                is_playable=True,
                command_skill__is_published=True,
            )
            .filter(
                adventure_level_tier_waves__is_published=True,
                adventure_level_tier_waves__tier__is_published=True,
                adventure_level_tier_waves__tier__adventure_level__is_published=True,
                adventure_level_tier_waves__tier__adventure_level__is_required=True,
                adventure_level_tier_waves__tier__adventure_level__chapter__story__slug=(
                    self.LEARNER_CURRICULUM_STORY_SLUG
                ),
            )
            .only("id", "command_skill_id")
            .distinct()
        )
        if not forms:
            return []

        skill_ids = {form.command_skill_id for form in forms}
        skills = list(
            CommandSkill.objects.filter(id__in=skill_ids, is_published=True).order_by(
                "sort_order", "base_command"
            )
        )

        forms_by_skill: dict[int, list[int]] = {}
        all_form_ids: set[int] = set()
        for f in forms:
            forms_by_skill.setdefault(f.command_skill_id, []).append(f.id)
            all_form_ids.add(f.id)

        targets = form_solve_targets(all_form_ids) if all_form_ids else {}
        solves_map: dict[int, int] = {}
        if all_form_ids:
            for row in SkillMastery.objects.filter(
                player=player, command_form_id__in=all_form_ids
            ).values_list("command_form_id", "solves"):
                solves_map[row[0]] = row[1]

        rows = []
        for skill in skills:
            form_ids = forms_by_skill[skill.id]
            ratios = [
                min(1.0, (solves_map.get(fid, 0) / max(1, targets.get(fid, 1)))) for fid in form_ids
            ]
            value = round(sum(ratios) / len(ratios) * 100, 1)
            rows.append(
                {
                    "key": skill.slug,
                    "label": skill.title,
                    "hint": skill.summary or f"Mastery of {skill.base_command}",
                    "value": value,
                    "command": skill.base_command,
                }
            )
        return rows

    def _mastery_score(self, *, player) -> float | None:
        """The same overall Arcane Spire command mastery shown in the Skills tab."""
        values = [row["value"] for row in self._command_skill_profile(player=player)]
        return self._mean(values)

    def _mean(self, values: list) -> float | None:
        return round(sum(values) / len(values), 1) if values else None

    def _player_steps(self, *, player):
        return CommandStep.objects.filter(player=player)

    def _runebound_runs(self, *, player):
        return AdventureLevelTierRun.objects.filter(
            player=player,
            is_replay=False,
            tier__adventure_level__chapter__story__slug=self.LEARNER_CURRICULUM_STORY_SLUG,
        )

    def _runebound_completions(self, *, player):
        return AdventureLevelTierCompletion.objects.filter(
            player=player,
            tier__adventure_level__chapter__story__slug=self.LEARNER_CURRICULUM_STORY_SLUG,
        )

    def _runebound_steps(self, *, player):
        return self._player_steps(player=player).filter(
            adventure_tier_run__tier__adventure_level__chapter__story__slug=(
                self.LEARNER_CURRICULUM_STORY_SLUG
            )
        )

    def _runebound_streak(self, *, player) -> dict:
        """Derive streaks from Arcane Spire completions, not global legacy state."""
        days = list(
            self._runebound_completions(player=player)
            .annotate(day=TruncDate("completed_at"))
            .order_by("day")
            .values_list("day", flat=True)
            .distinct()
        )
        if not days:
            return {"current": 0, "longest": 0, "last_completed_on": None}

        longest = current = run = 1
        for previous, day in zip(days, days[1:], strict=False):
            run = run + 1 if day == previous + timedelta(days=1) else 1
            longest = max(longest, run)
        current = run
        return {
            "current": current,
            "longest": longest,
            "last_completed_on": days[-1],
        }

    def _active_days(self, *, player, since) -> set:
        completion_days = (
            self._runebound_completions(player=player)
            .filter(completed_at__gte=since)
            .annotate(day=TruncDate("completed_at"))
            .values_list("day", flat=True)
            .distinct()
        )
        step_days = (
            self._runebound_steps(player=player)
            .filter(created_at__gte=since)
            .annotate(day=TruncDate("created_at"))
            .values_list("day", flat=True)
            .distinct()
        )
        return set(completion_days) | set(step_days)

    def _activity_trend(self, *, player, window: str, today) -> list[dict]:
        spec = ACTIVITY_WINDOWS[window]
        buckets = spec["buckets"]
        if spec["unit"] == "month":
            starts = [_month_start(today, offset) for offset in range(buckets - 1, -1, -1)]
        else:
            starts = [today - timedelta(days=offset) for offset in range(buckets - 1, -1, -1)]
        # The queries filter on aware datetimes, so the first bucket starts at
        # local midnight rather than at this time of day N days ago.
        since = timezone.make_aware(
            datetime.combine(starts[0], time.min), timezone.get_current_timezone()
        )

        completed_by_day = dict(
            self._runebound_completions(player=player)
            .filter(completed_at__gte=since)
            .annotate(day=TruncDate("completed_at"))
            .values("day")
            .annotate(count=Count("id"))
            .values_list("day", "count")
        )
        commands_by_day = dict(
            self._runebound_steps(player=player)
            .filter(created_at__gte=since)
            .annotate(day=TruncDate("created_at"))
            .values("day")
            .annotate(count=Count("id"))
            .values_list("day", "count")
        )

        # One point per bucket, each labelled by the day the bucket starts. Daily
        # windows sum a single day; the year window sums the whole month, so the
        # two shapes stay the same three keys for the client.
        def bucket_end(index: int):
            return starts[index + 1] if index + 1 < len(starts) else None

        trend = []
        for index, start in enumerate(starts):
            end = bucket_end(index)
            if spec["unit"] == "day":
                levels_completed = completed_by_day.get(start, 0)
                commands_run = commands_by_day.get(start, 0)
            else:
                levels_completed = sum(
                    count
                    for day, count in completed_by_day.items()
                    if day >= start and (end is None or day < end)
                )
                commands_run = sum(
                    count
                    for day, count in commands_by_day.items()
                    if day >= start and (end is None or day < end)
                )
            trend.append(
                {
                    "date": start.isoformat(),
                    "levels_completed": levels_completed,
                    "commands_run": commands_run,
                }
            )
        return trend

    def _rate(self, numerator: int, denominator: int) -> dict:
        return {
            "value": round((numerator / denominator) * 100, 1) if denominator else None,
            "numerator": numerator,
            "denominator": denominator,
        }

    def _retry_trends(self, *, runs, started: int) -> list[dict]:
        if started < 2:
            return []
        rows = (
            runs.values("tier__adventure_level__title")
            .annotate(
                attempts=Count("id"),
                retries=Count("id", filter=Q(prior_run__isnull=False)),
            )
            .order_by("-retries")[:6]
        )
        return [
            {
                "level_title": row["tier__adventure_level__title"],
                "attempts": row["attempts"],
                "retries": row["retries"],
                "label": "No trend available"
                if row["attempts"] < 2
                else f"{row['retries']} retry run{'s' if row['retries'] != 1 else ''}",
            }
            for row in rows
        ]
