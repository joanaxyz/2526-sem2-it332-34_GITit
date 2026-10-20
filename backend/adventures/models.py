from django.db import models
from django.db.models import Q

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


class AdventureLevel(models.Model):
    """A playable adventure level attached directly to a chapter.

    The content tree is:

        Chapter -> AdventureLevel -> AdventureLevelTier -> AdventureLevelTierWave
                                                        -> AdventureLevelTierWaveVariant
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
    source_content_definition = models.ForeignKey(
        "authoring.ContentDefinition",
        null=True,
        blank=True,
        related_name="runtime_adventure_levels",
        on_delete=models.SET_NULL,
    )

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

        AdventureLevel -> AdventureLevelTier -> AdventureLevelTierWave (ordered)
                                              -> AdventureLevelTierWaveVariant
                        -> AdventureLevelTierRun (one attempt at one wave)

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


class AdventureLevelTierWave(models.Model):
    """One ordered, playable Git problem inside a difficulty tier.

    A run plays the learner's next uncleared wave (``adventures/tier_waves.py``).
    """

    tier = models.ForeignKey(AdventureLevelTier, related_name="waves", on_delete=models.CASCADE)
    slug = models.SlugField()
    title = models.CharField(max_length=180, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    story = models.TextField(blank=True)
    task = models.TextField(blank=True)
    command_forms = models.ManyToManyField(
        "curriculum.CommandForm",
        related_name="adventure_level_tier_waves",
        blank=True,
    )
    min_counted_commands = models.PositiveIntegerField(default=1)
    max_counted_commands = models.PositiveIntegerField(default=4)
    objective_checks = models.JSONField(default=list, blank=True)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["tier_id", "sort_order", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["tier", "slug"], name="unique_adv_level_tier_wave_slug"
            ),
            models.CheckConstraint(
                condition=(
                    Q(min_counted_commands__gte=0)
                    & Q(max_counted_commands__gte=models.F("min_counted_commands"))
                ),
                name="adv_level_tier_wave_valid_command_budget",
            ),
        ]
        indexes = [
            models.Index(fields=["tier", "sort_order"], name="adv_lvl_tier_wave_slot_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.tier_id}:wave:{self.slug}"

    @property
    def adventure_level(self):
        return self.tier.adventure_level


class AdventureLevelTierWaveVariant(VariantBase):
    wave = models.ForeignKey(
        AdventureLevelTierWave, related_name="variants", on_delete=models.CASCADE
    )
    # Validated reference route, independent of the star-scoring budget.
    # KPI columns carry database defaults so code predating them can still
    # write rows to a shared, already migrated database.
    ref_count = models.PositiveIntegerField(null=True, blank=True)
    ref_hash = models.CharField(max_length=64, blank=True, db_default="")
    assess_diag = models.BooleanField(default=False, db_default=False)
    is_transfer = models.BooleanField(default=False, db_default=False)
    transfer_note = models.TextField(blank=True, db_default="")
    # Authored order within the wave: the first published variant is a
    # first-time learner's pick, and retries rotate in this order.
    sort_order = models.PositiveIntegerField(default=0, db_default=0)

    class Meta:
        ordering = ["wave_id", "sort_order", "semantic_key", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["wave", "slug"], name="unique_adv_level_tier_wave_variant_slug"
            ),
        ]

    def __str__(self) -> str:
        return f"adventure-level-tier-wave:{self.wave_id}:{self.slug}"


class AdventureLevelTierRun(models.Model):
    """One playable attempt at a difficulty tier.

    Mirrors ChallengeRun's lifecycle shape (one row per attempt; a fresh row
    is created for each retry rather than one long-lived row looping
    internally). A tier's progress through its waves is NOT tracked here - a
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
    current_wave = models.ForeignKey(
        AdventureLevelTierWave,
        null=True,
        blank=True,
        related_name="current_runs",
        on_delete=models.PROTECT,
    )
    selected_variant = models.ForeignKey(
        AdventureLevelTierWaveVariant,
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
    """Per-(player, tier) rollup of the tier's cleared waves.

    Each AdventureLevelTierRun is one attempt and ends (completed/failed) on
    its own - a run field can't hold this since it would reset on every new
    attempt. This row persists across attempts; AdventureLevelTierCompletion
    is written once every published wave of the tier is cleared.
    """

    player = models.ForeignKey(
        "players.Player", on_delete=models.CASCADE, related_name="adventure_tier_progress"
    )
    tier = models.ForeignKey(
        AdventureLevelTier, on_delete=models.CASCADE, related_name="progress_rows"
    )
    successful_clears = models.PositiveIntegerField(default=0)
    # Slugs of the tier's waves this player has cleared, in clear order. Wave
    # slugs are authored and stable across reseeds; the tier completes once
    # every published wave's slug is here.
    cleared_wave_slugs = models.JSONField(
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
        "AdventureLevelTierWaveVariant",
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
