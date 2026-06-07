from django.conf import settings
from django.db import models

from common.constants import (
    SESSION_STATUS_ABANDONED,
    SESSION_STATUS_COMPLETED,
    SESSION_STATUS_FAILED,
    SESSION_STATUS_STARTED,
)


class CommandAdventure(models.Model):
    module = models.OneToOneField(
        "curriculum.Storey",
        related_name="command_adventure",
        on_delete=models.CASCADE,
    )
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=180)
    description = models.TextField(blank=True)
    is_published = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self) -> str:
        return self.title


class AdventureProblem(models.Model):
    usage = models.ForeignKey(
        "curriculum.CommandForm",
        related_name="drills",
        on_delete=models.CASCADE,
    )
    slug = models.SlugField()
    title = models.CharField(max_length=180)
    summary = models.TextField(blank=True)
    required_successful_attempts = models.PositiveIntegerField(default=3)
    min_counted_commands = models.PositiveIntegerField(default=1)
    max_counted_commands = models.PositiveIntegerField(default=4)
    ideal_counted_commands = models.PositiveIntegerField(default=1)
    is_required = models.BooleanField(default=True)
    evaluation_spec = models.JSONField(default=dict, blank=True)
    student_context = models.JSONField(default=dict, blank=True)
    is_published = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["usage__topic__sort_order", "usage__sort_order", "sort_order"]
        unique_together = [("usage", "slug")]

    def __str__(self) -> str:
        return self.title

    @property
    def module(self):
        return self.usage.topic.module

    @property
    def command_adventure(self):
        return getattr(self.usage.topic.module, "command_adventure", None)


class VariantBase(models.Model):
    slug = models.SlugField()
    label = models.CharField(max_length=80)
    structure_signature = models.CharField(max_length=120, blank=True)
    initial_state = models.JSONField(default=dict)
    evaluation_spec = models.JSONField(default=dict, blank=True)
    target_state = models.JSONField(default=dict, blank=True)
    expected_state_diagram = models.JSONField(default=dict, blank=True)
    solution_commands = models.JSONField(default=list, blank=True)
    case_id = models.CharField(max_length=160, blank=True)
    semantic_key = models.CharField(max_length=240, blank=True)
    parameter_context = models.JSONField(default=dict, blank=True)
    student_context = models.JSONField(default=dict, blank=True)
    min_counted_commands = models.PositiveIntegerField(default=1)
    max_counted_commands = models.PositiveIntegerField(default=8)
    ideal_counted_commands = models.PositiveIntegerField(default=1)
    hint_set = models.JSONField(default=list, blank=True)
    scaffold_policy = models.JSONField(default=dict, blank=True)
    is_published = models.BooleanField(default=True)

    class Meta:
        abstract = True
        ordering = ["semantic_key", "id"]


class AdventureVariant(VariantBase):
    adventure_problem = models.ForeignKey(
        AdventureProblem,
        related_name="variants",
        on_delete=models.CASCADE,
    )

    class Meta(VariantBase.Meta):
        abstract = False
        ordering = ["adventure_problem_id", "semantic_key", "id"]

    @property
    def problem(self):
        return self.adventure_problem

    def __str__(self) -> str:
        return f"command_adventure:{self.slug}"


class AdventureRun(models.Model):
    class Status(models.TextChoices):
        STARTED = SESSION_STATUS_STARTED, "Started"
        COMPLETED = SESSION_STATUS_COMPLETED, "Completed"
        FAILED = SESSION_STATUS_FAILED, "Failed"
        ABANDONED = SESSION_STATUS_ABANDONED, "Abandoned"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    command_adventure = models.ForeignKey(
        CommandAdventure,
        related_name="runs",
        on_delete=models.CASCADE,
    )
    status = models.CharField(max_length=16, choices=Status.choices, default=SESSION_STATUS_STARTED)
    current_problem_index = models.PositiveIntegerField(default=0)
    total_score = models.PositiveIntegerField(default=0)
    mastery_progress_gained = models.FloatField(default=0.0)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "command_adventure", "status"], name="advrun_user_adv_status_idx"),
        ]

    def __str__(self) -> str:
        return f"AdventureRun({self.id}, {self.command_adventure_id}, {self.status})"


class AdventureProblemAttempt(models.Model):
    class Status(models.TextChoices):
        STARTED = SESSION_STATUS_STARTED, "Started"
        COMPLETED = SESSION_STATUS_COMPLETED, "Completed"
        FAILED = SESSION_STATUS_FAILED, "Failed"

    run = models.ForeignKey(AdventureRun, related_name="attempts", on_delete=models.CASCADE)
    adventure_problem = models.ForeignKey(
        AdventureProblem,
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
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["run_id", "order", "id"]
        indexes = [
            models.Index(fields=["run", "order"], name="advattempt_run_order_idx"),
        ]

    def __str__(self) -> str:
        return f"AdventureProblemAttempt({self.id}, run={self.run_id}, {self.status})"
