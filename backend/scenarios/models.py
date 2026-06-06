from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from common.constants import (
    COMMAND_COUNTED,
    COMMAND_DIAGNOSTIC,
    COMMAND_UNPROCESSABLE,
    DIFFICULTY_EASY,
    DIFFICULTY_HARD,
    DIFFICULTY_MEDIUM,
    RESULT_INVALID,
    RESULT_TARGET_MATCHED,
    RESULT_TARGET_NOT_YET_MATCHED,
    RESULT_UNPROCESSABLE,
    SESSION_MODE_PRIMARY,
    SESSION_MODE_REVIEW,
    SESSION_STATUS_ABANDONED,
    SESSION_STATUS_COMPLETED,
    SESSION_STATUS_FAILED,
    SESSION_STATUS_STARTED,
)


class PracticeKind(models.TextChoices):
    COMMAND_DRILL = "command_drill", "Command drill"
    WORKFLOW_SCENARIO = "workflow_scenario", "Workflow scenario"


class CommandTopic(models.Model):
    module = models.ForeignKey(
        "learning.LearningModule", related_name="command_topics", on_delete=models.CASCADE
    )
    slug = models.SlugField()
    base_command = models.CharField(max_length=80)
    title = models.CharField(max_length=160)
    summary = models.TextField(blank=True)
    mental_model = models.JSONField(default=dict, blank=True)
    command_preview = models.JSONField(default=dict, blank=True)
    is_published = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["module__sort_order", "sort_order", "base_command"]
        unique_together = [("module", "slug")]

    def __str__(self) -> str:
        return self.title


class CommandUsage(models.Model):
    topic = models.ForeignKey(CommandTopic, related_name="usages", on_delete=models.CASCADE)
    slug = models.SlugField()
    usage_form = models.CharField(max_length=140)
    label = models.CharField(max_length=180)
    summary = models.TextField(blank=True)
    command_preview = models.JSONField(default=dict, blank=True)
    is_published = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["topic__sort_order", "sort_order", "usage_form"]
        unique_together = [("topic", "slug")]

    def __str__(self) -> str:
        return self.label


class CommandDrill(models.Model):
    usage = models.ForeignKey(CommandUsage, related_name="drills", on_delete=models.CASCADE)
    slug = models.SlugField()
    title = models.CharField(max_length=180)
    summary = models.TextField(blank=True)
    required_successful_attempts = models.PositiveIntegerField(default=3)
    min_counted_commands = models.PositiveIntegerField(default=1)
    max_counted_commands = models.PositiveIntegerField(default=4)
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


class WorkflowScenario(models.Model):
    module = models.ForeignKey(
        "learning.LearningModule", related_name="workflow_scenarios", on_delete=models.CASCADE
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


class WorkflowScenarioLevel(models.Model):
    class Difficulty(models.TextChoices):
        EASY = DIFFICULTY_EASY, "Easy"
        MEDIUM = DIFFICULTY_MEDIUM, "Medium"
        HARD = DIFFICULTY_HARD, "Hard"

    scenario = models.ForeignKey(WorkflowScenario, related_name="levels", on_delete=models.CASCADE)
    difficulty = models.CharField(max_length=12, choices=Difficulty.choices)
    narrative = models.TextField(blank=True)
    task_prompt = models.TextField(blank=True)
    required_successful_attempts = models.PositiveIntegerField(default=2)
    min_counted_commands = models.PositiveIntegerField(default=1)
    max_counted_commands = models.PositiveIntegerField(default=8)
    evaluation_spec = models.JSONField(default=dict, blank=True)
    student_context = models.JSONField(default=dict, blank=True)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["scenario__sort_order", "difficulty"]
        unique_together = [("scenario", "difficulty")]

    def __str__(self) -> str:
        return f"{self.scenario} / {self.difficulty}"

    @property
    def module(self):
        return self.scenario.module


class ProblemVariant(models.Model):
    command_drill = models.ForeignKey(
        CommandDrill,
        null=True,
        blank=True,
        related_name="variants",
        on_delete=models.CASCADE,
    )
    workflow_level = models.ForeignKey(
        WorkflowScenarioLevel,
        null=True,
        blank=True,
        related_name="variants",
        on_delete=models.CASCADE,
    )
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
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["command_drill_id", "workflow_level_id", "semantic_key", "id"]

    def clean(self) -> None:
        parents = [bool(self.command_drill_id), bool(self.workflow_level_id)]
        if sum(parents) != 1:
            raise ValidationError("A problem variant must belong to exactly one problem.")

    @property
    def practice_kind(self) -> str:
        return (
            PracticeKind.COMMAND_DRILL
            if self.command_drill_id
            else PracticeKind.WORKFLOW_SCENARIO
        )

    @property
    def problem(self):
        return self.command_drill or self.workflow_level

    def __str__(self) -> str:
        return f"{self.practice_kind}:{self.slug}"


class PracticeSession(models.Model):
    class Status(models.TextChoices):
        STARTED = SESSION_STATUS_STARTED, "Started"
        COMPLETED = SESSION_STATUS_COMPLETED, "Completed"
        FAILED = SESSION_STATUS_FAILED, "Failed"
        ABANDONED = SESSION_STATUS_ABANDONED, "Abandoned"

    class Mode(models.TextChoices):
        PRIMARY = SESSION_MODE_PRIMARY, "Primary"
        REVIEW = SESSION_MODE_REVIEW, "Review"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    module = models.ForeignKey("learning.LearningModule", on_delete=models.PROTECT)
    practice_kind = models.CharField(max_length=24, choices=PracticeKind.choices)
    command_drill = models.ForeignKey(
        CommandDrill, null=True, blank=True, on_delete=models.PROTECT
    )
    workflow_scenario = models.ForeignKey(
        WorkflowScenario, null=True, blank=True, on_delete=models.PROTECT
    )
    workflow_level = models.ForeignKey(
        WorkflowScenarioLevel, null=True, blank=True, on_delete=models.PROTECT
    )
    variant = models.ForeignKey(ProblemVariant, on_delete=models.PROTECT)
    prior_session = models.ForeignKey(
        "self", null=True, blank=True, related_name="retry_sessions", on_delete=models.SET_NULL
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
    completed_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "mode", "status"], name="practice_user_mode_status_idx"),
            models.Index(fields=["user", "practice_kind", "status"], name="practice_user_kind_status_idx"),
            models.Index(fields=["user", "workflow_level", "-id"], name="practice_user_level_latest_idx"),
            models.Index(fields=["user", "command_drill", "-id"], name="practice_user_drill_latest_idx"),
        ]

    def clean(self) -> None:
        if self.practice_kind == PracticeKind.COMMAND_DRILL and not self.command_drill_id:
            raise ValidationError("Command drill sessions need a command_drill.")
        if self.practice_kind == PracticeKind.WORKFLOW_SCENARIO and not self.workflow_level_id:
            raise ValidationError("Workflow scenario sessions need a workflow_level.")

    @property
    def problem(self):
        return self.command_drill or self.workflow_level

    def __str__(self) -> str:
        return f"PracticeSession({self.id}, {self.practice_kind}, {self.status})"


class StepLog(models.Model):
    class ResultCategory(models.TextChoices):
        TARGET_MATCHED = RESULT_TARGET_MATCHED, "Target matched"
        TARGET_NOT_YET_MATCHED = RESULT_TARGET_NOT_YET_MATCHED, "Target not yet matched"
        UNPROCESSABLE = RESULT_UNPROCESSABLE, "Unprocessable"
        INVALID = RESULT_INVALID, "Invalid"

    class CommandClassification(models.TextChoices):
        COUNTED = COMMAND_COUNTED, "Counted action"
        DIAGNOSTIC = COMMAND_DIAGNOSTIC, "Non-counted diagnostic"
        UNPROCESSABLE = COMMAND_UNPROCESSABLE, "Unprocessable"

    session = models.ForeignKey(PracticeSession, related_name="step_logs", on_delete=models.CASCADE)
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
            models.Index(fields=["session", "id"], name="steplog_session_id_idx"),
        ]


class CommandLog(models.Model):
    step_log = models.OneToOneField(StepLog, related_name="command_log", on_delete=models.CASCADE)
    raw_command = models.TextField()
    normalized_command = models.TextField()
    was_processable = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class CompletionRecord(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    practice_kind = models.CharField(max_length=24, choices=PracticeKind.choices)
    command_drill = models.ForeignKey(
        CommandDrill, null=True, blank=True, on_delete=models.CASCADE
    )
    workflow_level = models.ForeignKey(
        WorkflowScenarioLevel, null=True, blank=True, on_delete=models.CASCADE
    )
    session = models.OneToOneField(PracticeSession, on_delete=models.CASCADE)
    first_attempt_star = models.BooleanField(default=False)
    counted_action_total = models.PositiveIntegerField(default=0)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "command_drill"],
                name="unique_command_drill_completion",
                condition=models.Q(command_drill__isnull=False),
            ),
            models.UniqueConstraint(
                fields=["user", "workflow_level"],
                name="unique_workflow_level_completion",
                condition=models.Q(workflow_level__isnull=False),
            ),
        ]

    @property
    def problem(self):
        return self.command_drill or self.workflow_level
