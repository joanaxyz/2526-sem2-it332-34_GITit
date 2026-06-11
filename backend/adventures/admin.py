from django.contrib import admin

from adventures.models import (
    AdventureQuest,
    AdventureQuestAttempt,
    AdventureRun,
    AdventureVariant,
    CommandAdventure,
)


@admin.register(CommandAdventure)
class CommandAdventureAdmin(admin.ModelAdmin):
    list_display = ("slug", "title", "storey", "is_published", "sort_order")
    list_filter = ("is_published",)
    search_fields = ("title", "slug")


@admin.register(AdventureQuest)
class AdventureQuestAdmin(admin.ModelAdmin):
    list_display = ("slug", "title", "command_form", "is_published", "sort_order")
    list_filter = ("is_published",)
    search_fields = ("title", "slug")


@admin.register(AdventureVariant)
class AdventureVariantAdmin(admin.ModelAdmin):
    list_display = ("slug", "adventure_quest", "is_published")
    list_filter = ("is_published",)


@admin.register(AdventureRun)
class AdventureRunAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "command_adventure", "status", "started_at")
    list_filter = ("status",)


@admin.register(AdventureQuestAttempt)
class AdventureQuestAttemptAdmin(admin.ModelAdmin):
    list_display = ("id", "run", "adventure_quest", "status", "final_score")
    list_filter = ("status",)
