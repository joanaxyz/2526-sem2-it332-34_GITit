from common.constants import (
    DIFFICULTY_EASY,
    DIFFICULTY_HARD,
    DIFFICULTY_MEDIUM,
    SESSION_STATUS_ABANDONED,
    SESSION_STATUS_COMPLETED,
    SESSION_STATUS_FAILED,
    SESSION_STATUS_STARTED,
)
from common.models import VariantBase
from django.db import models
from django.db.models import Q


class AdventureLevel(models.Model):
    """A playable adventure level attached directly to a chapter.

    The content tree is:

        Chapter -> AdventureLevel -> AdventureLevelTier -> AdventureLevelTierScenario
                                                        -> AdventureLevelTierScenarioVariant
    """

    chapter = models.ForeignKey(
        "curriculum.Chapter",
        related_name="adventure_levels",
        on_delete=models.CASCADE,
    )
    slug = models.SlugField()
    title = models.CharField(max_length=180)
    description = models.TextField(blank=True)
    command_forms = models.ManyToManyField(
        "curriculum.CommandForm",
        related_name="adventure_levels",
        blank=True,
    )
    is_required = models.BooleanField(default=True)
    is_published = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["chapter__sort_order", "sort_order", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["chapter", "slug"], name="unique_adventure_level_chapter_slug"
            ),
        ]
        indexes = [
            models.Index(fields=["chapter", "sort_order"], name="adv_level_chapter_sort_idx"),
        ]

    def __str__(self) -> str:
        return self.title


class SkillMastery(models.Model):
    """Per-user mastery for one command form."""

    player = models.ForeignKey(
        "players.Player", on_delete=models.CASCADE, related_name="skill_mastery_states"
    )
    command_form = models.ForeignKey(
        "curriculum.CommandForm",
        related_name="skill_mastery_states",
        on_delete=models.CASCADE,
    )
    learned_at = models.DateTimeField(null=True, blank=True)
    solves = models.PositiveIntegerField(default=0)
    mastered = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["player", "command_form"], name="unique_skill_mastery_player_form"
            ),
        ]

    def __str__(self) -> str:
        return f"SkillMastery(player={self.player_id}, form={self.command_form_id}, solves={self.solves})"


class AdventureLevelTier(models.Model):
    """One difficulty (Easy, Medium or Hard) of an AdventureLevel.

        AdventureLevel -> AdventureLevelTier -> AdventureLevelTierScenario (ordered)
                                              -> AdventureLevelTierScenarioVariant
                        -> AdventureLevelTierRun (one attempt at one scenario)

    A tier's GitCoin reward is the ladder in ``adventures/rewards.py``.
    """

    class Difficulty(models.TextChoices):
        EASY = DIFFICULTY_EASY, "Easy"
        MEDIUM = DIFFICULTY_MEDIUM, "Medium"
        HARD = DIFFICULTY_HARD, "Hard"

    adventure_level = models.ForeignKey(
        AdventureLevel, related_name="tiers", on_delete=models.CASCADE
    )
    difficulty = models.CharField(max_length=12, choices=Difficulty.choices)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["adventure_level_id", "difficulty"]
        constraints = [
            models.UniqueConstraint(
                fields=["adventure_level", "difficulty"],
                name="unique_adv_level_tier_difficulty",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.adventure_level_id}:tier:{self.difficulty}"


class AdventureLevelTierScenario(models.Model):
    """One ordered, playable Git problem inside a difficulty tier.

    A run plays the learner's next uncleared scenario (``adventures/tier_scenarios.py``).
    """

    tier = models.ForeignKey(AdventureLevelTier, related_name="scenarios", on_delete=models.CASCADE)
    slug = models.SlugField()
    title = models.CharField(max_length=180, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    story = models.TextField(blank=True)
    task = models.TextField(blank=True)
    command_forms = models.ManyToManyField(
        "curriculum.CommandForm",
        related_name="adventure_level_tier_scenarios",
        blank=True,
    )
    generous_counted_commands = models.PositiveIntegerField(null=True, blank=True)
    min_counted_commands = models.PositiveIntegerField(default=1)
    max_counted_commands = models.PositiveIntegerField(default=4)
    objective_checks = models.JSONField(default=list, blank=True)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["tier_id", "sort_order", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["tier", "slug"], name="unique_adv_level_tier_scenario_slug"
            ),
            models.CheckConstraint(
                condition=(
                    Q(min_counted_commands__gte=0)
                    & Q(max_counted_commands__gte=models.F("min_counted_commands"))
                ),
                name="adv_level_tier_scenario_valid_command_budget",
            ),
        ]
        indexes = [
            models.Index(fields=["tier", "sort_order"], name="adv_lvl_tier_scenario_slot_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.tier_id}:scenario:{self.slug}"

    @property
    def adventure_level(self):
        return self.tier.adventure_level


class AdventureLevelTierScenarioVariant(VariantBase):
    scenario = models.ForeignKey(
        AdventureLevelTierScenario, related_name="variants", on_delete=models.CASCADE
    )
    # Validated reference route, independent of the star-scoring budget.
    # KPI columns carry database defaults so code predating them can still
    # write rows to a shared, already migrated database.
    ref_count = models.PositiveIntegerField(null=True, blank=True)
    ref_hash = models.CharField(max_length=64, blank=True, db_default="")
    assess_diag = models.BooleanField(default=False, db_default=False)
    is_transfer = models.BooleanField(default=False, db_default=False)
    transfer_note = models.TextField(blank=True, db_default="")
    # Authored order within the scenario: the first published variant is a
    # first-time learner's pick, and retries rotate in this order.
    sort_order = models.PositiveIntegerField(default=0, db_default=0)

    class Meta:
        ordering = ["scenario_id", "sort_order", "semantic_key", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["scenario", "slug"], name="unique_adv_level_tier_scenario_variant_slug"
            ),
        ]

    def __str__(self) -> str:
        return f"adventure-level-tier-scenario:{self.scenario_id}:{self.slug}"


class AdventureLevelTierRun(models.Model):
    """One playable attempt at a difficulty tier.

    Mirrors ChallengeRun's lifecycle shape (one row per attempt; a fresh row
    is created for each retry rather than one long-lived row looping
    internally). A tier's progress through its scenarios is NOT tracked here - a
    run field would reset every attempt - see AdventureLevelTierProgress for
    the per-(player, tier) rollup.
    """

    class Status(models.TextChoices):
        STARTED = SESSION_STATUS_STARTED, "Started"
        COMPLETED = SESSION_STATUS_COMPLETED, "Completed"
        FAILED = SESSION_STATUS_FAILED, "Failed"
        ABANDONED = SESSION_STATUS_ABANDONED, "Abandoned"

    player = models.ForeignKey(
        "players.Player", on_delete=models.CASCADE, related_name="adventure_tier_runs"
    )
    tier = models.ForeignKey(AdventureLevelTier, related_name="runs", on_delete=models.PROTECT)
    current_scenario = models.ForeignKey(
        AdventureLevelTierScenario,
        null=True,
        blank=True,
        related_name="current_runs",
        on_delete=models.PROTECT,
    )
    selected_variant = models.ForeignKey(
        AdventureLevelTierScenarioVariant,
        related_name="runs",
        on_delete=models.PROTECT,
    )
    prior_run = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="retry_runs",
        on_delete=models.SET_NULL,
    )
    source_entry_point = models.CharField(max_length=40, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=SESSION_STATUS_STARTED)
    is_replay = models.BooleanField(default=False)
    is_transfer = models.BooleanField(default=False, db_default=False)
    ref_count = models.PositiveIntegerField(null=True, blank=True)
    ref_hash = models.CharField(max_length=64, blank=True, db_default="")
    assess_diag = models.BooleanField(default=False, db_default=False)
    # True when this run's selected_variant differs from the player's
    # immediately-previous attempt on this tier (mirrors the old app's
    # ScenarioSession.changed_variant, computed once at selection time via
    # TierVariantSelectionService.changed_between() - see start_run). Powers
    # the "Changed variant" context-panel tag; not used by any grading logic.
    changed_variant = models.BooleanField(default=False)
    stars = models.PositiveSmallIntegerField(default=0)
    scoring_policy_version = models.PositiveSmallIntegerField(default=1, db_default=1)
    generous_counted_commands = models.PositiveIntegerField(null=True, blank=True)
    example_counted_commands = models.PositiveIntegerField(null=True, blank=True)
    required_techniques = models.JSONField(default=list, blank=True)
    verified_techniques = models.JSONField(default=list, blank=True)
    min_counted_commands = models.PositiveIntegerField(default=1)
    max_counted_commands = models.PositiveIntegerField(default=4)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    passed_at = models.DateTimeField(null=True, blank=True)
    total_attempts = models.PositiveIntegerField(default=0)
    counted_action_total = models.PositiveIntegerField(default=0)
    non_counted_diagnostic_total = models.PositiveIntegerField(default=0)
    retry_index = models.PositiveIntegerField(default=0)
    failure_reason = models.CharField(max_length=160, blank=True)
    repository_state = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [
            models.Index(
                fields=["player", "tier", "status"], name="advtier_run_plyr_tier_stat_idx"
            ),
            models.Index(fields=["player", "status"], name="advtier_run_plyr_stat_idx"),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(scoring_policy_version=1)
                | (
                    Q(generous_counted_commands__isnull=False)
                    & Q(generous_counted_commands__gt=models.F("min_counted_commands"))
                    & Q(max_counted_commands__gt=models.F("generous_counted_commands"))
                ),
                name="adv_run_v2_targets",
            ),
            models.UniqueConstraint(
                fields=["player", "tier"],
                condition=Q(status=SESSION_STATUS_STARTED),
                name="unique_active_adv_level_tier_run",
            ),
            models.CheckConstraint(
                condition=Q(stars__lte=3),
                name="adv_level_tier_run_stars_lte_3",
            ),
            models.CheckConstraint(
                condition=(
                    Q(min_counted_commands__gte=1)
                    & Q(max_counted_commands__gte=models.F("min_counted_commands"))
                ),
                name="adv_level_tier_run_valid_command_budget",
            ),
        ]

    @property
    def adventure_level(self):
        return self.tier.adventure_level

    def __str__(self) -> str:
        return f"AdventureLevelTierRun({self.id}, tier={self.tier_id}, {self.status})"


class AdventureLevelTierProgress(models.Model):
    """Per-(player, tier) rollup of the tier's cleared scenarios.

    Each AdventureLevelTierRun is one attempt and ends (completed/failed) on
    its own - a run field can't hold this since it would reset on every new
    attempt. This row persists across attempts; AdventureLevelTierCompletion
    is written once every published scenario of the tier is cleared.
    """

    player = models.ForeignKey(
        "players.Player", on_delete=models.CASCADE, related_name="adventure_tier_progress"
    )
    tier = models.ForeignKey(
        AdventureLevelTier, on_delete=models.CASCADE, related_name="progress_rows"
    )
    successful_clears = models.PositiveIntegerField(default=0)
    # Slugs of the tier's scenarios this player has cleared, in clear order. Scenario
    # slugs are authored and stable across reseeds; the tier completes once
    # every published scenario's slug is here.
    cleared_scenario_slugs = models.JSONField(
        default=list, blank=True, db_default=models.Value([], output_field=models.JSONField())
    )
    # Legacy histories can have deleted launches; only prospective tracking
    # can certify that a transfer repository has never been shown.
    exposure_complete = models.BooleanField(default=False, db_default=False)
    # The variant shown on the player's most recent start_run call for this
    # tier, solved or not. AdventureLevelTierRun rows are hard-deleted on
    # discard (see common.runtime.discard_started_run), so an abandoned,
    # never-solved attempt leaves no run row behind - this field is the only
    # way start_run can still know which variant to rotate away from after
    # an exit-without-solving. Set on every start_run call, independent of
    # successful_clears.
    last_shown_variant = models.ForeignKey(
        "AdventureLevelTierScenarioVariant",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["player", "tier"], name="unique_adv_level_tier_progress_player_tier"
            ),
        ]

    def __str__(self) -> str:
        return f"AdventureLevelTierProgress(player={self.player_id}, tier={self.tier_id}, clears={self.successful_clears})"
