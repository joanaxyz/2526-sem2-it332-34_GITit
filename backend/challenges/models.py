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


class ChallengeLevel(models.Model):
    """A playable challenge level attached directly to a chapter.

    The content tree is:

        Chapter -> ChallengeLevel -> ChallengeTrial -> ChallengeTrialVariant
    """

    chapter = models.ForeignKey(
        "curriculum.Chapter",
        related_name="challenge_levels",
        on_delete=models.CASCADE,
    )
    slug = models.SlugField()
    title = models.CharField(max_length=180)
    summary = models.TextField(blank=True)
    narrative = models.TextField(blank=True)
    command_forms = models.ManyToManyField(
        "curriculum.CommandForm",
        related_name="challenge_levels",
        blank=True,
    )
    is_published = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    source_content_definition = models.ForeignKey(
        "authoring.ContentDefinition",
        null=True,
        blank=True,
        related_name="runtime_challenge_levels",
        on_delete=models.SET_NULL,
    )

    class Meta:
        ordering = ["chapter__sort_order", "sort_order", "id"]
        constraints = [
            models.UniqueConstraint(fields=["chapter", "slug"], name="unique_challenge_level_chapter_slug"),
        ]
        indexes = [
            models.Index(fields=["chapter", "sort_order"], name="chal_level_chapter_sort_idx"),
        ]

    def __str__(self) -> str:
        return self.title


class ChallengeTrial(models.Model):
    """A directly playable difficulty tier inside a challenge level."""

    class Difficulty(models.TextChoices):
        EASY = DIFFICULTY_EASY, "Easy"
        MEDIUM = DIFFICULTY_MEDIUM, "Medium"
        HARD = DIFFICULTY_HARD, "Hard"

    challenge_level = models.ForeignKey(
        ChallengeLevel,
        related_name="trials",
        on_delete=models.CASCADE,
    )
    difficulty = models.CharField(max_length=12, choices=Difficulty.choices)
    story = models.TextField(blank=True)
    task = models.TextField(blank=True)
    min_counted_commands = models.PositiveIntegerField(default=1)
    max_counted_commands = models.PositiveIntegerField(default=4)
    reward_coins = models.PositiveIntegerField(default=0)
    objective_checks = models.JSONField(default=list, blank=True)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = [
            "challenge_level__chapter__sort_order",
            "challenge_level__sort_order",
            "difficulty",
        ]
        constraints = [
            models.UniqueConstraint(fields=["challenge_level", "difficulty"], name="unique_challenge_trial_difficulty"),
        ]

    def __str__(self) -> str:
        return f"{self.challenge_level} / {self.difficulty}"

    @property
    def chapter(self):
        return self.challenge_level.chapter


class ChallengeTrialVariant(VariantBase):
    trial = models.ForeignKey(
        ChallengeTrial,
        related_name="variants",
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ["trial_id", "semantic_key", "id"]
        constraints = [
            models.UniqueConstraint(fields=["trial", "slug"], name="unique_challenge_trial_variant_slug"),
        ]

    def __str__(self) -> str:
        return f"challenge-trial:{self.trial_id}:{self.slug}"


class ChallengeRun(models.Model):
    class Status(models.TextChoices):
        STARTED = SESSION_STATUS_STARTED, "Started"
        COMPLETED = SESSION_STATUS_COMPLETED, "Completed"
        FAILED = SESSION_STATUS_FAILED, "Failed"
        ABANDONED = SESSION_STATUS_ABANDONED, "Abandoned"

    player = models.ForeignKey("players.Player", on_delete=models.CASCADE, related_name="challenge_runs")
    challenge_trial = models.ForeignKey(
        ChallengeTrial,
        on_delete=models.PROTECT,
    )
    selected_variant = models.ForeignKey(
        ChallengeTrialVariant,
        related_name="challenge_runs",
        on_delete=models.PROTECT,
    )
    prior_run = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="retry_runs",
        on_delete=models.SET_NULL,
    )
    source_entry_point = models.CharField(max_length=40)
    is_replay = models.BooleanField(default=False)
    status = models.CharField(max_length=16, choices=Status.choices, default=SESSION_STATUS_STARTED)
    stars = models.PositiveSmallIntegerField(default=0)
    min_counted_commands = models.PositiveIntegerField(default=1)
    max_counted_commands = models.PositiveIntegerField(default=4)
    repository_state = models.JSONField(default=dict)
    counted_action_total = models.PositiveIntegerField(default=0)
    non_counted_diagnostic_total = models.PositiveIntegerField(default=0)
    total_attempts = models.PositiveIntegerField(default=0)
    retry_index = models.PositiveIntegerField(default=0)
    failure_reason = models.CharField(max_length=160, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["player", "is_replay", "status"], name="chal_plyr_replay_status_idx"),
            models.Index(fields=["player", "challenge_trial", "-id"], name="chal_plyr_trial_latest_idx"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["player", "challenge_trial"],
                condition=Q(status=SESSION_STATUS_STARTED),
                name="unique_active_challenge_run",
            ),
        ]

    @property
    def chapter(self):
        return self.challenge_trial.chapter

    @property
    def challenge(self):
        return self.challenge_trial.challenge_level

    @property
    def difficulty(self) -> str:
        return self.challenge_trial.difficulty

    @property
    def trial(self):
        return self.challenge_trial

    @property
    def variant(self):
        return self.selected_variant

    @property
    def variant_id(self):
        return self.selected_variant_id

    def __str__(self) -> str:
        return f"ChallengeRun({self.id}, {self.status})"
