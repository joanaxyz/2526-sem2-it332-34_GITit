from datetime import date, datetime, time, timedelta

from django.db.models import Count, Q, Sum
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

# Learner retry success rate: any run started from a prior run. Abandoned runs
# are left out so the learner-facing measure keeps its meaning from before
# abandoned runs were recorded (they used to be deleted).
LEARNER_RETRY = Q(prior_run__isnull=False) & ~Q(status=SESSION_STATUS_ABANDONED)

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
            runs=self._kpi_runs(kpi_range=kpi_range), kpi_range=kpi_range
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

    _CAR_COUNTS = {
        "total": Count("id"),
        "unprocessable": Count(
            "id", filter=Q(result_category__in=[RESULT_INVALID, RESULT_UNPROCESSABLE])
        ),
    }

    def _car_steps(self, *, runs):
        """The submitted commands CAR is computed from, overall and per SO."""
        return CommandStep.objects.filter(adventure_tier_run__in=runs)

    def all_player_objective_car(self, *, kpi_range: KpiRange = ALL_TIME) -> dict:
        """Per-SO CAR across all learners (staff console), keyed by SO code.

        Uses the same runs and command steps as the overall CAR, grouped by
        adventure level through the static SO_CAR_LEVELS mapping.
        """
        return self._objective_car_for_runs(runs=self._kpi_runs(kpi_range=kpi_range))

    def _objective_car_for_runs(self, *, runs) -> dict:
        by_level = {
            row["adventure_tier_run__tier__adventure_level__slug"]: row
            for row in self._car_steps(runs=runs)
            .values("adventure_tier_run__tier__adventure_level__slug")
            .annotate(**self._CAR_COUNTS)
        }
        objectives = {}
        for so_code, level_slugs in SO_CAR_LEVELS.items():
            total = sum((by_level.get(slug) or {}).get("total", 0) for slug in level_slugs)
            unprocessable = sum(
                (by_level.get(slug) or {}).get("unprocessable", 0) for slug in level_slugs
            )
            objectives[so_code] = self._rate(total - unprocessable, total)
        return objectives

    def _rta_for_runs(self, *, runs, kpi_range: KpiRange = ALL_TIME) -> dict:
        """Retry Transfer Accuracy (RTA) over a set of performance runs.

        An eligible retry session is the first run started directly after a
        failed run, where that failed run was not itself a retry-after-failure
        (so continue-after-success runs and later retries in the same failure
        streak are excluded), in Modules 3-4 only, whose variant is
        structurally different from the failed run's variant (initial_state or
        target_state differs - a different variant key alone is not enough).
        Success means that eligible run completes; an eligible run the learner
        abandoned counts as eligible but not successful. Runs still in progress
        have no outcome yet and are left out. With a date range, both the retry
        and the failed run before it must have started inside it, so a retry of
        a pre-range failure is not counted. No eligible sessions returns a null
        rate, never 0%.
        """
        candidates = (
            runs.filter(
                tier__adventure_level__chapter__number__in=self.RTA_MODULE_NUMBERS,
                prior_run__status=SESSION_STATUS_FAILED,
                status__in=(
                    SESSION_STATUS_COMPLETED,
                    SESSION_STATUS_FAILED,
                    SESSION_STATUS_ABANDONED,
                ),
            )
            .exclude(prior_run__prior_run__status=SESSION_STATUS_FAILED)
            .filter(kpi_range.q("prior_run__started_at"))
            .select_related("selected_variant", "prior_run__selected_variant")
        )
        eligible = successful = 0
        for run in candidates:
            prior_variant = run.prior_run.selected_variant
            variant = run.selected_variant
            if (
                prior_variant.initial_state == variant.initial_state
                and prior_variant.target_state == variant.target_state
            ):
                continue
            eligible += 1
            if run.status == SESSION_STATUS_COMPLETED:
                successful += 1
        return self._rate(successful, eligible)

    def _performance_summary_for_runs(self, *, runs, kpi_range: KpiRange = ALL_TIME) -> dict:
        """Performance KPIs for the Arcane Spire module attempts.

        CAR is the share of submitted commands the simulator could process.
        RTA is Retry Transfer Accuracy (see ``_rta_for_runs``). The learner
        retry success rate is the share of any run with a prior run that ends
        successfully. Replays are excluded from every attempt-based measure.

        An abandoned run is a started session that did not succeed: it counts
        in SCR's and HLCR's started totals, its commands count in CAR, and it
        can be an unsuccessful RTA session. ARC (completed runs only) and the
        learner retry success rate leave it out.
        """
        aggregate = runs.aggregate(
            started=Count("id"),
            completed=Count("id", filter=Q(status=SESSION_STATUS_COMPLETED)),
            hard_started=Count("id", filter=Q(tier__difficulty=DIFFICULTY_HARD)),
            hard_completed=Count(
                "id",
                filter=Q(tier__difficulty=DIFFICULTY_HARD, status=SESSION_STATUS_COMPLETED),
            ),
            retry_started=Count("id", filter=LEARNER_RETRY),
            retry_completed=Count(
                "id", filter=Q(prior_run__isnull=False, status=SESSION_STATUS_COMPLETED)
            ),
            completed_retry_total=Sum("retry_index", filter=Q(status=SESSION_STATUS_COMPLETED)),
        )

        step_counts = self._car_steps(runs=runs).aggregate(**self._CAR_COUNTS)
        total_commands = step_counts["total"] or 0
        processable_commands = total_commands - (step_counts["unprocessable"] or 0)

        grouped = {
            row["tier__adventure_level__chapter_id"]: row
            for row in runs.values("tier__adventure_level__chapter_id").annotate(
                started=Count("id"),
                completed=Count("id", filter=Q(status=SESSION_STATUS_COMPLETED)),
                hard_started=Count("id", filter=Q(tier__difficulty=DIFFICULTY_HARD)),
                hard_completed=Count(
                    "id",
                    filter=Q(
                        tier__difficulty=DIFFICULTY_HARD,
                        status=SESSION_STATUS_COMPLETED,
                    ),
                ),
                retry_started=Count("id", filter=LEARNER_RETRY),
                retry_completed=Count(
                    "id", filter=Q(prior_run__isnull=False, status=SESSION_STATUS_COMPLETED)
                ),
                completed_retry_total=Sum("retry_index", filter=Q(status=SESSION_STATUS_COMPLETED)),
            )
        }
        chapters = Chapter.objects.filter(
            story__slug=self.PERFORMANCE_STORY_SLUG,
            is_published=True,
            number__in=self.PERFORMANCE_MODULE_NUMBERS,
        ).order_by("sort_order", "number")
        modules = []
        for chapter in chapters:
            row = grouped.get(chapter.id, {})
            started = row.get("started") or 0
            completed = row.get("completed") or 0
            retry_success_rate = self._rate(
                row.get("retry_completed") or 0,
                row.get("retry_started") or 0,
            )
            modules.append(
                {
                    "number": chapter.number,
                    "title": chapter.title,
                    "scr": self._rate(completed, started),
                    "hlcr": self._rate(
                        row.get("hard_completed") or 0,
                        row.get("hard_started") or 0,
                    ),
                    "rta": self._rta_for_runs(
                        runs=runs.filter(tier__adventure_level__chapter_id=chapter.id),
                        kpi_range=kpi_range,
                    ),
                    "retry_success_rate": retry_success_rate,
                    # TODO(next release): remove the deprecated "rtr" alias once
                    # the frontend reading "retry_success_rate"/"rta" is live.
                    "rtr": retry_success_rate,
                    "arc": self._average_retry_count_from_counts(
                        row.get("completed_retry_total") or 0,
                        completed,
                    ),
                }
            )

        started = aggregate["started"] or 0
        completed = aggregate["completed"] or 0
        retry_success_rate = self._rate(
            aggregate["retry_completed"] or 0,
            aggregate["retry_started"] or 0,
        )
        return {
            "kpis": {
                "scr": self._rate(completed, started),
                "car": self._rate(processable_commands, total_commands),
                "hlcr": self._rate(
                    aggregate["hard_completed"] or 0,
                    aggregate["hard_started"] or 0,
                ),
                "rta": self._rta_for_runs(runs=runs, kpi_range=kpi_range),
                "retry_success_rate": retry_success_rate,
                # TODO(next release): remove the deprecated "rtr" alias once the
                # frontend reading "retry_success_rate"/"rta" is live.
                "rtr": retry_success_rate,
                "arc": self._average_retry_count_from_counts(
                    aggregate["completed_retry_total"] or 0,
                    completed,
                ),
            },
            "completed_sessions": completed,
            "modules": modules,
        }

    def dashboard_summary(self, *, player) -> dict:
        runs = self._runebound_runs(player=player)
        run_counts = runs.aggregate(
            started=Count("id"),
            completed=Count("id", filter=Q(status=SESSION_STATUS_COMPLETED)),
            failed=Count("id", filter=Q(status=SESSION_STATUS_FAILED)),
            abandoned=Count("id", filter=Q(status=SESSION_STATUS_ABANDONED)),
            hard_started=Count(
                "id",
                filter=Q(tier__difficulty=DIFFICULTY_HARD),
            ),
            hard_completed=Count(
                "id",
                filter=Q(
                    tier__difficulty=DIFFICULTY_HARD,
                    status=SESSION_STATUS_COMPLETED,
                ),
            ),
            completed_retry_total=Sum("retry_index", filter=Q(status=SESSION_STATUS_COMPLETED)),
        )
        started = run_counts["started"] or 0
        completed = run_counts["completed"] or 0
        failed = run_counts["failed"] or 0
        abandoned = run_counts["abandoned"] or 0

        chapter_rows = runs.values("tier__adventure_level__chapter__number").annotate(
            hard_started=Count("id", filter=Q(tier__difficulty=DIFFICULTY_HARD)),
            hard_completed=Count(
                "id",
                filter=Q(tier__difficulty=DIFFICULTY_HARD, status=SESSION_STATUS_COMPLETED),
            ),
            started_count=Count("id"),
            completed_count=Count("id", filter=Q(status=SESSION_STATUS_COMPLETED)),
            completed_retry_total=Sum("retry_index", filter=Q(status=SESSION_STATUS_COMPLETED)),
        )
        chapter_metrics_map = {
            int(row["tier__adventure_level__chapter__number"]): row
            for row in chapter_rows
            if row["tier__adventure_level__chapter__number"] is not None
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
        streak = self._runebound_streak(player=player)
        stories = list(published_stories().filter(slug=self.LEARNER_CURRICULUM_STORY_SLUG))
        completed_map = stories_completed_map(player=player, stories=stories)
        completed_stories = [story.slug for story in stories if completed_map.get(story.id, False)]
        perfect_stars = self._runebound_completions(player=player).filter(stars=3).count()
        return {
            "kpis": {
                "scr": self._rate(completed, started),
                "arc": self._average_retry_count_from_counts(
                    run_counts["completed_retry_total"] or 0, completed
                ),
                "hlcr": self._rate(
                    run_counts["hard_completed"] or 0, run_counts["hard_started"] or 0
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
                Q(
                    adventure_waves__is_published=True,
                    adventure_waves__level__is_published=True,
                    adventure_waves__level__is_required=True,
                    adventure_waves__level__chapter__story__slug=(
                        self.LEARNER_CURRICULUM_STORY_SLUG
                    ),
                )
                | Q(
                    adventure_level_tier_waves__is_published=True,
                    adventure_level_tier_waves__tier__is_published=True,
                    adventure_level_tier_waves__tier__adventure_level__is_published=True,
                    adventure_level_tier_waves__tier__adventure_level__is_required=True,
                    adventure_level_tier_waves__tier__adventure_level__chapter__story__slug=(
                        self.LEARNER_CURRICULUM_STORY_SLUG
                    ),
                )
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
