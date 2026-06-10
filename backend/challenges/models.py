from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from adventures.models import VariantBase
from common.constants import (
    DIFFICULTY_EASY,
    DIFFICULTY_HARD,
    DIFFICULTY_MEDIUM,
    SESSION_MODE_PRIMARY,
    SESSION_MODE_REVIEW,
    SESSION_STATUS_ABANDONED,
    SESSION_STATUS_COMPLETED,
    SESSION_STATUS_FAILED,
    SESSION_STATUS_STARTED,
)


class Challenge(models.Model):
    module = models.ForeignKey(
        "curriculum.Storey",
        related_name="workflow_scenarios",
        on_delete=models.CASCADE,
    )
    slug = models.SlugField()
    title = models.CharField(max_length=180)
    summary = models.TextField(blank=True)
    narrative = models.TextField(blank=True)
    command_topics = models.JSONField(default=list, blank=True)
    is_published = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["module__sort_order", "sort_order", "title"]
        unique_together = [("module", "slug")]

    def __str__(self) -> str:
        return self.title


class ChallengeLevel(models.Model):
    class Difficulty(models.TextChoices):
        EASY = DIFFICULTY_EASY, "Easy"
        MEDIUM = DIFFICULTY_MEDIUM, "Medium"
        HARD = DIFFICULTY_HARD, "Hard"

    scenario = models.ForeignKey(Challenge, related_name="levels", on_delete=models.CASCADE)
    difficulty = models.CharField(max_length=12, choices=Difficulty.choices)
    required_successful_attempts = models.PositiveIntegerField(default=2)
    min_counted_commands = models.PositiveIntegerField(default=1)
    max_counted_commands = models.PositiveIntegerField(default=8)
    evaluation_spec = models.JSONField(default=dict, blank=True)
    scenario_context = models.JSONField(default=dict, blank=True)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["scenario__sort_order", "difficulty"]
        unique_together = [("scenario", "difficulty")]

    def __str__(self) -> str:
        return f"{self.scenario} / {self.difficulty}"

    @property
    def module(self):
        return self.scenario.module


class ChallengeVariant(VariantBase):
    challenge_level = models.ForeignKey(
        ChallengeLevel,
        related_name="variants",
        on_delete=models.CASCADE,
    )
    command_budget = models.JSONField(default=dict, blank=True)

    class Meta(VariantBase.Meta):
        abstract = False
        ordering = ["challenge_level_id", "semantic_key", "id"]

    @property
    def problem(self):
        return self.challenge_level

    def __str__(self) -> str:
        return f"challenge:{self.slug}"


class ChallengeRun(models.Model):
    class Status(models.TextChoices):
        STARTED = SESSION_STATUS_STARTED, "Started"
        COMPLETED = SESSION_STATUS_COMPLETED, "Completed"
        FAILED = SESSION_STATUS_FAILED, "Failed"
        ABANDONED = SESSION_STATUS_ABANDONED, "Abandoned"

    class Mode(models.TextChoices):
        PRIMARY = SESSION_MODE_PRIMARY, "Primary"
        REVIEW = SESSION_MODE_REVIEW, "Review"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    module = models.ForeignKey("curriculum.Storey", on_delete=models.PROTECT)
    workflow_scenario = models.ForeignKey(Challenge, on_delete=models.PROTECT)
    challenge_level = models.ForeignKey(ChallengeLevel, on_delete=models.PROTECT)
    challenge_variant = models.ForeignKey(ChallengeVariant, on_delete=models.PROTECT)
    prior_session = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="retry_sessions",
        on_delete=models.SET_NULL,
    )
    source_entry_point = models.CharField(max_length=40)
    mode = models.CharField(max_length=16, choices=Mode.choices, default=SESSION_MODE_PRIMARY)
    status = models.CharField(max_length=16, choices=Status.choices, default=SESSION_STATUS_STARTED)
    difficulty = models.CharField(max_length=12, blank=True)
    rta_eligible = models.BooleanField(default=False)
    rta_success = models.BooleanField(default=False)
    changed_variant = models.BooleanField(default=False)
    looped_variant = models.BooleanField(default=False)
    command_budget_snapshot = models.JSONField(default=dict)
    repository_state = models.JSONField(default=dict)
    counted_action_total = models.PositiveIntegerField(default=0)
    non_counted_diagnostic_total = models.PositiveIntegerField(default=0)
    total_attempts = models.PositiveIntegerField(default=0)
    retry_index = models.PositiveIntegerField(default=0)
    first_attempt_star_eligible = models.BooleanField(default=True)
    failure_reason = models.CharField(max_length=160, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    # completed_at is set only on a successful completion; ended_at is set on any
    # terminal outcome (completed, failed, or abandoned). On success both are set
    # to the same instant. Use ended_at for "is this run over?" and completed_at
    # for "did this run succeed?".
    completed_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "mode", "status"], name="challenge_user_mode_status_idx"),
            models.Index(fields=["user", "challenge_level", "-id"], name="chal_user_level_latest_idx"),
        ]

    def clean(self) -> None:
        if self.workflow_scenario_id != self.challenge_level.scenario_id:
            raise ValidationError("Challenge run level must belong to the selected challenge.")

    @property
    def problem(self):
        return self.challenge_level

    @property
    def variant(self):
        return self.challenge_variant

    @property
    def variant_id(self):
        return self.challenge_variant_id

    def __str__(self) -> str:
        return f"ChallengeRun({self.id}, {self.status})"
