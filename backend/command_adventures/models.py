from django.conf import settings
from django.db import models

from common.constants import (
    SESSION_MODE_PRIMARY,
    SESSION_MODE_REPLAY,
    SESSION_STATUS_ABANDONED,
    SESSION_STATUS_COMPLETED,
    SESSION_STATUS_FAILED,
    SESSION_STATUS_STARTED,
)


class CommandAdventure(models.Model):
    chapter = models.ForeignKey(
        "curriculum.Chapter",
        related_name="command_adventures",
        on_delete=models.CASCADE,
    )
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=180)
    description = models.TextField(blank=True)
    is_published = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    source_content_definition = models.ForeignKey(
        "authoring.ContentDefinition",
        null=True,
        blank=True,
        related_name="runtime_command_adventures",
        on_delete=models.SET_NULL,
    )
    # Fraction of total achievable mastery points a learner must reach to pass
    # this adventure (and unlock Challenge). Null falls back to PASS_BAR_FRACTION.
    pass_bar_fraction = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self) -> str:
        return self.title


class AdventureLevel(models.Model):
    command_form = models.ForeignKey(
        "curriculum.CommandForm",
        related_name="adventure_levels",
        on_delete=models.CASCADE,
    )
    slug = models.SlugField()
    title = models.CharField(max_length=180)
    required_successful_attempts = models.PositiveIntegerField(default=3)
    # Command budget is authored on the level and shared by all its variants:
    # min_counted_commands is the efficiency target ("par"), max is the hard cap.
    min_counted_commands = models.PositiveIntegerField(default=1)
    max_counted_commands = models.PositiveIntegerField(default=4)
    is_required = models.BooleanField(default=True)
    evaluation_spec = models.JSONField(default=dict, blank=True)
    scenario_context = models.JSONField(default=dict, blank=True)
    # Adventure-only live checklist, authored as [{label, requirement}]. The
    # requirement predicates are server-side answers and must never be
    # serialized to the client; payloads expose evaluated {label, satisfied}
    # rows instead. Challenges deliberately have no counterpart field.
    objective_checks = models.JSONField(default=list, blank=True)
    is_published = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    # Authored battle roster for this level's encounter, [{species, hp, tier}].
    # Empty list = deterministic default derived from the level at attempt
    # start (battle.state), so unauthored levels need no seed changes.
    encounter_spec = models.JSONField(default=list, blank=True)
    # The runtime adventure this level belongs to. Legacy seeded rows may be
    # null until reseeded; services fall back to the chapter's first adventure.
    command_adventure = models.ForeignKey(
        CommandAdventure,
        null=True,
        blank=True,
        related_name="levels",
        on_delete=models.CASCADE,
    )
    # Explicit prerequisite graph (DAG): this command can only be introduced once
    # every prerequisite has been solved at least once. Strengthens the implicit
    # sort_order ordering; validated acyclic + preceding at seed time.
    prerequisites = models.ManyToManyField(
        "self",
        symmetrical=False,
        blank=True,
        related_name="dependents",
    )

    class Meta:
        ordering = ["command_form__command_skill__sort_order", "command_form__sort_order", "sort_order"]
        unique_together = [("command_form", "slug")]

    def __str__(self) -> str:
        return self.title

    @property
    def chapter(self):
        return self.command_form.command_skill.chapter


class VariantBase(models.Model):
    slug = models.SlugField()
    label = models.CharField(max_length=80)
    initial_state = models.JSONField(default=dict)
    evaluation_spec = models.JSONField(default=dict, blank=True)
    target_state = models.JSONField(default=dict, blank=True)
    solution_commands = models.JSONField(default=list, blank=True)
    # case_id (human-readable) and parameter_context (render inputs) record the
    # authoring provenance of a generated variant. semantic_key is the identity
    # used for dedup/selection; the others are not part of identity.
    case_id = models.CharField(max_length=160, blank=True)
    semantic_key = models.CharField(max_length=240, blank=True)
    parameter_context = models.JSONField(default=dict, blank=True)
    scenario_context = models.JSONField(default=dict, blank=True)
    hint_set = models.JSONField(default=list, blank=True)
    scaffold_policy = models.JSONField(default=dict, blank=True)
    is_published = models.BooleanField(default=True)

    class Meta:
        abstract = True
        ordering = ["semantic_key", "id"]


class AdventureVariant(VariantBase):
    adventure_level = models.ForeignKey(
        AdventureLevel,
        related_name="adventure_variants",
        on_delete=models.CASCADE,
    )

    class Meta(VariantBase.Meta):
        abstract = False
        ordering = ["adventure_level_id", "semantic_key", "id"]

    @property
    def level(self):
        return self.adventure_level

    def __str__(self) -> str:
        return f"command_adventure:{self.slug}"


class AdventureRun(models.Model):
    class Status(models.TextChoices):
        STARTED = SESSION_STATUS_STARTED, "Started"
        COMPLETED = SESSION_STATUS_COMPLETED, "Completed"
        FAILED = SESSION_STATUS_FAILED, "Failed"
        ABANDONED = SESSION_STATUS_ABANDONED, "Abandoned"

    class Mode(models.TextChoices):
        PRIMARY = SESSION_MODE_PRIMARY, "Primary"
        REPLAY = SESSION_MODE_REPLAY, "Replay"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    command_adventure = models.ForeignKey(
        CommandAdventure,
        related_name="runs",
        on_delete=models.CASCADE,
    )
    status = models.CharField(max_length=16, choices=Status.choices, default=SESSION_STATUS_STARTED)
    # Primary is the first counted playthrough (drives mastery, pass, KPIs);
    # replay is an uncounted free-play re-run started once the adventure is
    # already passed. Replay never reads or writes AdventureMastery.
    mode = models.CharField(max_length=16, choices=Mode.choices, default=SESSION_MODE_PRIMARY)
    current_level_index = models.PositiveIntegerField(default=0)
    total_score = models.PositiveIntegerField(default=0)
    # Accumulating mastery points this session (sum of box-advance x quality).
    session_score = models.PositiveIntegerField(default=0)
    mastery_progress_gained = models.FloatField(default=0.0)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    # Set the moment session_score crosses the pass bar (with the per-command
    # floor met). Drives Challenge unlock; independent of run status.
    passed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "command_adventure", "status"], name="advrun_user_adv_status_idx"),
        ]

    def __str__(self) -> str:
        return f"AdventureRun({self.id}, {self.command_adventure_id}, {self.status})"


class AdventureLevelAttempt(models.Model):
    class Status(models.TextChoices):
        STARTED = SESSION_STATUS_STARTED, "Started"
        COMPLETED = SESSION_STATUS_COMPLETED, "Completed"
        FAILED = SESSION_STATUS_FAILED, "Failed"

    run = models.ForeignKey(AdventureRun, related_name="attempts", on_delete=models.CASCADE)
    adventure_level = models.ForeignKey(
        AdventureLevel,
        related_name="attempts",
        on_delete=models.PROTECT,
    )
    selected_variant = models.ForeignKey(
        AdventureVariant,
        related_name="attempts",
        on_delete=models.PROTECT,
    )
    order = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=16, choices=Status.choices, default=SESSION_STATUS_STARTED)
    correctness_score = models.PositiveIntegerField(default=0)
    efficiency_score = models.PositiveIntegerField(default=0)
    independence_score = models.PositiveIntegerField(default=0)
    final_score = models.PositiveIntegerField(default=0)
    mastery_gain = models.FloatField(default=0.0)
    hint_count = models.PositiveIntegerField(default=0)
    command_count = models.PositiveIntegerField(default=0)
    counted_command_count = models.PositiveIntegerField(default=0)
    retry_count = models.PositiveIntegerField(default=0)
    repository_state = models.JSONField(default=dict, blank=True)
    # Monster roster + turn bookkeeping for the battle layer (battle.state).
    # Written in the same save() the submit path already performs.
    battle_state = models.JSONField(default=dict, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["run_id", "order", "id"]
        indexes = [
            models.Index(fields=["run", "order"], name="advattempt_run_order_idx"),
        ]

    def __str__(self) -> str:
        return f"AdventureLevelAttempt({self.id}, run={self.run_id}, {self.status})"


class AdventureMastery(models.Model):
    """Per-user Leitner state for one command-level. Drives the spaced-repetition
    scheduler: `strength` is the box (0..N where N = level.required_successful_attempts),
    and `last_seen_seq` is the user's adventure encounter index when last served, so
    spacing is measured in encounters rather than wall-clock time. Persists across runs."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    adventure_level = models.ForeignKey(
        AdventureLevel,
        related_name="mastery_states",
        on_delete=models.CASCADE,
    )
    strength = models.PositiveIntegerField(default=0)
    introduced = models.BooleanField(default=False)
    last_seen_seq = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("user", "adventure_level")]
        indexes = [
            models.Index(fields=["user", "adventure_level"], name="advmastery_user_level_idx"),
        ]

    def __str__(self) -> str:
        return f"AdventureMastery(user={self.user_id}, level={self.adventure_level_id}, box={self.strength})"
