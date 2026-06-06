from django.contrib import admin

from scenarios.models import (
    CommandDrill,
    CommandTopic,
    CommandUsage,
    CompletionRecord,
    PracticeSession,
    ProblemVariant,
    WorkflowScenario,
    WorkflowScenarioLevel,
)


@admin.register(CommandTopic)
class CommandTopicAdmin(admin.ModelAdmin):
    list_display = ("title", "base_command", "module", "is_published", "sort_order")
    list_filter = ("module", "is_published")
    search_fields = ("title", "base_command", "summary")


@admin.register(CommandUsage)
class CommandUsageAdmin(admin.ModelAdmin):
    list_display = ("label", "usage_form", "topic", "is_published", "sort_order")
    list_filter = ("topic__module", "topic", "is_published")
    search_fields = ("label", "usage_form", "summary")


@admin.register(CommandDrill)
class CommandDrillAdmin(admin.ModelAdmin):
    list_display = ("title", "usage", "required_successful_attempts", "is_published")
    list_filter = ("usage__topic__module", "usage__topic", "is_published")
    search_fields = ("title", "summary")


@admin.register(WorkflowScenario)
class WorkflowScenarioAdmin(admin.ModelAdmin):
    list_display = ("title", "module", "is_published", "sort_order")
    list_filter = ("module", "is_published")
    search_fields = ("title", "summary", "narrative")


@admin.register(WorkflowScenarioLevel)
class WorkflowScenarioLevelAdmin(admin.ModelAdmin):
    list_display = ("scenario", "difficulty", "required_successful_attempts", "is_published")
    list_filter = ("difficulty", "is_published", "scenario__module")


@admin.register(ProblemVariant)
class ProblemVariantAdmin(admin.ModelAdmin):
    list_display = ("slug", "practice_kind", "command_drill", "workflow_level", "is_published")
    list_filter = ("is_published",)
    search_fields = ("slug", "label", "case_id", "semantic_key")


@admin.register(PracticeSession)
class PracticeSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "practice_kind", "status", "mode", "started_at")
    list_filter = ("practice_kind", "status", "mode")
    search_fields = ("user__email", "command_drill__title", "workflow_scenario__title")


@admin.register(CompletionRecord)
class CompletionRecordAdmin(admin.ModelAdmin):
    list_display = ("user", "practice_kind", "command_drill", "workflow_level", "completed_at")
    list_filter = ("practice_kind",)
