from django.conf import settings
from django.db import models

from common.constants import (
    COMMAND_COUNTED,
    COMMAND_DIAGNOSTIC,
    COMMAND_UNPROCESSABLE,
    COMPLETION_EXPANDED_STATE_BASED,
    COMPLETION_STATE_BASED,
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


class ScenarioSkillFocus(models.Model):
    class SkillFocusType(models.TextChoices):
        COMMAND_SPECIFIC = "command_specific", "Command-specific"
        CONCEPT_SPECIFIC = "concept_specific", "Concept-specific"
        WORKFLOW_SPECIFIC = "workflow_specific", "Workflow-specific"

    learning_unit = models.ForeignKey(
        "learning.LearningUnit", related_name="scenarios", on_delete=models.CASCADE
    )
    lesson = models.ForeignKey(
        "learning.Lesson", related_name="scenarios", on_delete=models.CASCADE
    )
    slug = models.SlugField()
    title = models.CharField(max_length=180)
    focus = models.CharField(max_length=140)
    summary = models.CharField(max_length=240, blank=True)
    short_explanation = models.TextField(blank=True)
    skill_focus_type = models.CharField(
        max_length=24,
        choices=SkillFocusType.choices,
        default=SkillFocusType.COMMAND_SPECIFIC,
    )
    primary_focus_commands = models.JSONField(default=list, blank=True)
    supporting_diagnostic_commands = models.JSONField(default=list, blank=True)
    safe_demo_commands = models.JSONField(default=list, blank=True)
    demo_repository_state = models.JSONField(default=dict, blank=True)
    demo_dag_config = models.JSONField(default=dict, blank=True)
    demo_explanation_steps = models.JSONField(default=list, blank=True)
    command_preview_config = models.JSONField(default=dict, blank=True)
    related_git_concepts = models.JSONField(default=list, blank=True)
    narrative = models.TextField(blank=True)
    task_prompt = models.TextField(blank=True)
    is_published = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["learning_unit__sort_order", "lesson__sort_order", "sort_order"]
        unique_together = [("learning_unit", "slug")]

    def __str__(self) -> str:
        return self.title


class GitCommandContent(models.Model):
    key = models.SlugField(unique=True)
    base_command = models.CharField(max_length=120, blank=True)
    display_name = models.CharField(max_length=120)
    canonical_command = models.CharField(max_length=160)
    aliases = models.JSONField(default=list, blank=True)
    summary = models.TextField(blank=True)
    tags = models.JSONField(default=list, blank=True)
    sections = models.JSONField(default=list, blank=True)
    pages = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    version = models.PositiveIntegerField(default=1)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "key"]

    def __str__(self) -> str:
        return self.display_name


class DifficultyInstance(models.Model):
    class Difficulty(models.TextChoices):
        EASY = DIFFICULTY_EASY, "Easy"
        MEDIUM = DIFFICULTY_MEDIUM, "Medium"
        HARD = DIFFICULTY_HARD, "Hard"

    class CompletionType(models.TextChoices):
        STATE_BASED = COMPLETION_STATE_BASED, "State based"
        EXPANDED_STATE_BASED = (
            COMPLETION_EXPANDED_STATE_BASED,
            "State based with detailed target rules",
        )

    scenario = models.ForeignKey(
        ScenarioSkillFocus, related_name="difficulty_instances", on_delete=models.CASCADE
    )
    difficulty = models.CharField(max_length=12, choices=Difficulty.choices)
    completion_type = models.CharField(
        max_length=32,
        choices=CompletionType.choices,
        default=CompletionType.STATE_BASED,
    )
    required_successful_attempts = models.PositiveIntegerField(default=2)
    narrative = models.TextField(blank=True)
    task_prompt = models.TextField(blank=True)
    is_published = models.BooleanField(default=True)

    class Meta:
        unique_together = [("scenario", "difficulty")]

    def __str__(self) -> str:
        return f"{self.scenario} / {self.difficulty}"


class CommandCountPolicy(models.Model):
    difficulty_instance = models.OneToOneField(
        DifficultyInstance, related_name="command_policy", on_delete=models.CASCADE
    )
    min_counted_commands = models.PositiveIntegerField()
    max_counted_commands = models.PositiveIntegerField()
    non_counted_patterns = models.JSONField(default=list, blank=True)

    def snapshot(self) -> dict:
        return {
            "id": self.id,
            "min_counted_commands": self.min_counted_commands,
            "max_counted_commands": self.max_counted_commands,
            "non_counted_patterns": self.non_counted_patterns,
        }


class ScenarioVariant(models.Model):
    scenario = models.ForeignKey(
        ScenarioSkillFocus, related_name="variants", on_delete=models.CASCADE
    )
    difficulty_instance = models.ForeignKey(
        DifficultyInstance, related_name="variants", on_delete=models.CASCADE
    )
    slug = models.SlugField()
    label = models.CharField(max_length=80)
    structure_signature = models.CharField(max_length=120)
    initial_state = models.JSONField()
    target_rule = models.JSONField(default=dict, blank=True)
    target_state = models.JSONField()
    expected_state_diagram = models.JSONField(default=dict, blank=True)
    solution_commands = models.JSONField(default=list, blank=True)
    case_id = models.CharField(max_length=160, blank=True)
    semantic_key = models.CharField(max_length=240, blank=True)
    parameter_context = models.JSONField(default=dict, blank=True)
    student_context = models.JSONField(default=dict, blank=True)
    is_published = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["difficulty_instance", "slug"],
                name="unique_variant_slug_per_difficulty",
            ),
            models.UniqueConstraint(
                fields=["difficulty_instance", "semantic_key"],
                name="unique_variant_semantic_key_per_difficulty",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.scenario.slug}:{self.difficulty_instance.difficulty}:{self.slug}"


class TargetStateRule(models.Model):
    difficulty_instance = models.OneToOneField(
        DifficultyInstance, related_name="target_rule", on_delete=models.CASCADE
    )
    rule = models.JSONField()
    target_state_hash = models.CharField(max_length=128, blank=True)


class ScenarioSession(models.Model):
    class Status(models.TextChoices):
        STARTED = SESSION_STATUS_STARTED, "Started"
        COMPLETED = SESSION_STATUS_COMPLETED, "Completed"
        FAILED = SESSION_STATUS_FAILED, "Failed"
        ABANDONED = SESSION_STATUS_ABANDONED, "Abandoned"

    class Mode(models.TextChoices):
        PRIMARY = SESSION_MODE_PRIMARY, "Primary"
        REVIEW = SESSION_MODE_REVIEW, "Review"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    learning_unit = models.ForeignKey("learning.LearningUnit", on_delete=models.PROTECT)
    scenario = models.ForeignKey(ScenarioSkillFocus, on_delete=models.PROTECT)
    difficulty_instance = models.ForeignKey(DifficultyInstance, on_delete=models.PROTECT)
    variant = models.ForeignKey(ScenarioVariant, on_delete=models.PROTECT)
    prior_session = models.ForeignKey(
        "self", null=True, blank=True, related_name="retry_sessions", on_delete=models.SET_NULL
    )
    source_entry_point = models.CharField(max_length=40)
    mode = models.CharField(max_length=16, choices=Mode.choices, default=SESSION_MODE_PRIMARY)
    status = models.CharField(max_length=16, choices=Status.choices, default=SESSION_STATUS_STARTED)
    orientation_complete_at_start = models.BooleanField(default=False)
    rta_eligible = models.BooleanField(default=False)
    rta_success = models.BooleanField(default=False)
    changed_variant = models.BooleanField(default=False)
    command_policy_snapshot = models.JSONField(default=dict)
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

    def __str__(self) -> str:
        return f"Session({self.id}, {self.scenario.slug}, {self.mode}, {self.status})"

    class Meta:
        indexes = [
            models.Index(fields=["user", "mode", "status"], name="sess_user_mode_status_idx"),
            models.Index(
                fields=["user", "difficulty_instance", "status", "mode"],
                name="sess_user_diff_state_idx",
            ),
            models.Index(
                fields=["user", "difficulty_instance", "-id"],
                name="sess_user_diff_latest_idx",
            ),
        ]


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

    session = models.ForeignKey(ScenarioSession, related_name="step_logs", on_delete=models.CASCADE)
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
    scenario = models.ForeignKey(ScenarioSkillFocus, on_delete=models.CASCADE)
    difficulty_instance = models.ForeignKey(DifficultyInstance, on_delete=models.CASCADE)
    session = models.OneToOneField(ScenarioSession, on_delete=models.CASCADE)
    first_attempt_star = models.BooleanField(default=False)
    counted_action_total = models.PositiveIntegerField(default=0)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("user", "difficulty_instance")]
