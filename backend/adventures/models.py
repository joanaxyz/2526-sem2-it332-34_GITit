from django.db import models
from django.db.models import Q

from common.constants import (
    SESSION_STATUS_ABANDONED,
    SESSION_STATUS_COMPLETED,
    SESSION_STATUS_FAILED,
    SESSION_STATUS_STARTED,
)
from common.models import VariantBase


class AdventureLevel(models.Model):
    """A playable adventure level attached directly to a chapter.

    The content tree is:

        Chapter -> AdventureLevel -> AdventureWave -> AdventureWaveVariant
    """

    chapter = models.ForeignKey(
        "curriculum.Chapter",
        related_name="adventure_levels",
        on_delete=models.CASCADE,
    )
    slug = models.SlugField()
    title = models.CharField(max_length=180)
    command_forms = models.ManyToManyField(
        "curriculum.CommandForm",
        related_name="adventure_levels",
        blank=True,
    )
    is_required = models.BooleanField(default=True)
    is_published = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    # GitCoins paid (once, via the idempotent wallet ledger) on first completion.
    reward_coins = models.PositiveIntegerField(default=0)
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
            models.UniqueConstraint(fields=["chapter", "slug"], name="unique_adventure_level_chapter_slug"),
        ]
        indexes = [
            models.Index(fields=["chapter", "sort_order"], name="adv_level_chapter_sort_idx"),
        ]

    def __str__(self) -> str:
        return self.title


class AdventureWave(models.Model):
    """The playable Git problem inside an adventure level."""

    level = models.ForeignKey(
        AdventureLevel, related_name="waves", on_delete=models.CASCADE
    )
    slug = models.SlugField()
    title = models.CharField(max_length=180, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    story = models.TextField(blank=True)
    task = models.TextField(blank=True)
    command_forms = models.ManyToManyField(
        "curriculum.CommandForm",
        related_name="adventure_waves",
        blank=True,
    )
    min_counted_commands = models.PositiveIntegerField(default=1)
    max_counted_commands = models.PositiveIntegerField(default=4)
    objective_checks = models.JSONField(default=list, blank=True)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["level_id", "sort_order", "id"]
        constraints = [
            models.UniqueConstraint(fields=["level", "slug"], name="unique_adventure_wave_slug"),
        ]
        indexes = [
            models.Index(fields=["level", "sort_order"], name="adv_wave_slot_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.level_id}:wave:{self.slug}"

    @property
    def chapter(self):
        return self.level.chapter


class AdventureWaveVariant(VariantBase):
    wave = models.ForeignKey(AdventureWave, related_name="variants", on_delete=models.CASCADE)

    class Meta:
        ordering = ["wave_id", "semantic_key", "id"]
        constraints = [
            models.UniqueConstraint(fields=["wave", "slug"], name="unique_adventure_wave_variant_slug"),
        ]

    def __str__(self) -> str:
        return f"adventure-wave:{self.wave_id}:{self.slug}"


class AdventureRun(models.Model):
    """One playable adventure level run.

    The run walks the level's waves in order: each wave selects its own variant,
    and the run completes only when the last wave is cleared.
    """

    class Status(models.TextChoices):
        STARTED = SESSION_STATUS_STARTED, "Started"
        COMPLETED = SESSION_STATUS_COMPLETED, "Completed"
        FAILED = SESSION_STATUS_FAILED, "Failed"
        ABANDONED = SESSION_STATUS_ABANDONED, "Abandoned"

    player = models.ForeignKey("players.Player", on_delete=models.CASCADE, related_name="adventure_runs")
    level = models.ForeignKey(
        AdventureLevel,
        related_name="runs",
        on_delete=models.CASCADE,
    )
    current_wave = models.ForeignKey(
        AdventureWave,
        null=True,
        blank=True,
        related_name="current_runs",
        on_delete=models.PROTECT,
    )
    selected_variant = models.ForeignKey(
        AdventureWaveVariant,
        related_name="runs",
        on_delete=models.PROTECT,
    )
    status = models.CharField(max_length=16, choices=Status.choices, default=SESSION_STATUS_STARTED)
    is_replay = models.BooleanField(default=False)
    stars = models.PositiveSmallIntegerField(default=0)
    library_opened = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    passed_at = models.DateTimeField(null=True, blank=True)
    command_count = models.PositiveIntegerField(default=0)
    counted_command_count = models.PositiveIntegerField(default=0)
    repository_state = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["player", "level", "status"], name="advrun_plyr_level_status_idx"),
            models.Index(fields=["player", "status"], name="advrun_plyr_status_idx"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["player", "level"],
                condition=Q(status=SESSION_STATUS_STARTED),
                name="unique_active_adventure_run",
            ),
        ]

    @property
    def chapter(self):
        return self.level.chapter

    @property
    def story(self):
        return self.level.chapter.story

    def __str__(self) -> str:
        return f"AdventureRun({self.id}, level={self.level_id}, {self.status})"


class AdventureRunWave(models.Model):
    """Per-wave progress inside one level run."""

    class Status(models.TextChoices):
        STARTED = SESSION_STATUS_STARTED, "Started"
        COMPLETED = SESSION_STATUS_COMPLETED, "Completed"

    run = models.ForeignKey(AdventureRun, related_name="run_waves", on_delete=models.CASCADE)
    wave = models.ForeignKey(AdventureWave, related_name="run_waves", on_delete=models.CASCADE)
    selected_variant = models.ForeignKey(
        AdventureWaveVariant,
        related_name="run_waves",
        on_delete=models.PROTECT,
    )
    status = models.CharField(max_length=16, choices=Status.choices, default=SESSION_STATUS_STARTED)
    stars = models.PositiveSmallIntegerField(default=0)
    counted_command_count = models.PositiveIntegerField(default=0)
    command_count = models.PositiveIntegerField(default=0)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["run_id", "wave__sort_order", "id"]
        constraints = [
            models.UniqueConstraint(fields=["run", "wave"], name="unique_adventure_run_wave"),
        ]

    def __str__(self) -> str:
        return f"AdventureRunWave(run={self.run_id}, wave={self.wave_id}, {self.status})"


class SkillMastery(models.Model):
    """Per-user mastery for one command form."""

    player = models.ForeignKey("players.Player", on_delete=models.CASCADE, related_name="skill_mastery_states")
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
            models.UniqueConstraint(fields=["player", "command_form"], name="unique_skill_mastery_player_form"),
        ]
        indexes = [
            models.Index(fields=["player", "command_form"], name="skillmastery_plyr_form_idx"),
        ]

    def __str__(self) -> str:
        return f"SkillMastery(player={self.player_id}, form={self.command_form_id}, solves={self.solves})"
