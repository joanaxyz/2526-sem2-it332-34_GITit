from django.db import models

from common.constants import (
    COMMAND_COUNTED,
    COMMAND_DIAGNOSTIC,
    COMMAND_UNPROCESSABLE,
    RESULT_INVALID,
    RESULT_TARGET_MATCHED,
    RESULT_TARGET_NOT_YET_MATCHED,
    RESULT_UNPROCESSABLE,
)


class CommandStep(models.Model):
    class ResultCategory(models.TextChoices):
        TARGET_MATCHED = RESULT_TARGET_MATCHED, "Target matched"
        TARGET_NOT_YET_MATCHED = RESULT_TARGET_NOT_YET_MATCHED, "Target not yet matched"
        UNPROCESSABLE = RESULT_UNPROCESSABLE, "Unprocessable"
        INVALID = RESULT_INVALID, "Invalid"

    class CommandClassification(models.TextChoices):
        COUNTED = COMMAND_COUNTED, "Counted action"
        DIAGNOSTIC = COMMAND_DIAGNOSTIC, "Non-counted diagnostic"
        UNPROCESSABLE = COMMAND_UNPROCESSABLE, "Unprocessable"

    challenge_run = models.ForeignKey(
        "challenges.ChallengeRun",
        null=True,
        blank=True,
        related_name="steps",
        on_delete=models.CASCADE,
    )
    attempt = models.ForeignKey(
        "adventures.AdventureQuestAttempt",
        null=True,
        blank=True,
        related_name="steps",
        on_delete=models.CASCADE,
    )
    command_text = models.TextField()
    terminal_output = models.TextField(blank=True)
    result_category = models.CharField(max_length=32, choices=ResultCategory.choices)
    command_classification = models.CharField(max_length=32, choices=CommandClassification.choices)
    counted_increment = models.PositiveIntegerField(default=0)
    attempt_number = models.PositiveIntegerField()
    counted_total_after = models.PositiveIntegerField(default=0)
    state_hash = models.CharField(max_length=128, blank=True)
    expected_state_hash = models.CharField(max_length=128, blank=True)
    repository_state = models.JSONField(default=dict, blank=True)
    visualization_snapshot = models.JSONField(default=dict, blank=True)
    contextual_feedback = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["challenge_run", "id"], name="cmdstep_run_id_idx"),
            # Adventure history is queried by attempt (attempt.steps ordered by id,
            # plus the command-history join); mirror the run index for it.
            models.Index(fields=["attempt", "id"], name="cmdstep_attempt_id_idx"),
        ]


class CommandLog(models.Model):
    step = models.OneToOneField(CommandStep, related_name="command_log", on_delete=models.CASCADE)
    raw_command = models.TextField()
    normalized_command = models.TextField()
    was_processable = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
