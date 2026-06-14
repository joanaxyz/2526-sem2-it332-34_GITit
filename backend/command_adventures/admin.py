from django.contrib import admin

from adventures.models import (
    AdventureLevel,
    AdventureLevelAttempt,
    AdventureRun,
    AdventureVariant,
    CommandAdventure,
)


@admin.register(CommandAdventure)
class CommandAdventureAdmin(admin.ModelAdmin):
    list_display = ("slug", "title", "storey", "is_published", "sort_order")
    list_filter = ("is_published",)
    search_fields = ("title", "slug")


@admin.register(AdventureLevel)
class AdventureLevelAdmin(admin.ModelAdmin):
    list_display = ("slug", "title", "command_form", "is_published", "sort_order")
    list_filter = ("is_published",)
    search_fields = ("title", "slug")


@admin.register(AdventureVariant)
class AdventureVariantAdmin(admin.ModelAdmin):
    list_display = ("slug", "adventure_level", "is_published")
    list_filter = ("is_published",)


@admin.register(AdventureRun)
class AdventureRunAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "command_adventure", "status", "started_at")
    list_filter = ("status",)


@admin.register(AdventureLevelAttempt)
class AdventureLevelAttemptAdmin(admin.ModelAdmin):
    list_display = ("id", "run", "adventure_level", "status", "final_score")
    list_filter = ("status",)
