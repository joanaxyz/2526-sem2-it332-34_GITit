from django.contrib import admin

from adventures.models import (
    AdventureLevel,
    AdventureRun,
    AdventureWave,
    AdventureWaveVariant,
    SkillMastery,
)


class AdventureWaveInline(admin.TabularInline):
    model = AdventureWave
    extra = 0


@admin.register(AdventureLevel)
class AdventureLevelAdmin(admin.ModelAdmin):
    list_display = ("slug", "title", "chapter", "is_required", "is_published", "sort_order")
    list_filter = ("is_required", "is_published", "chapter")
    search_fields = ("title", "slug", "description", "brief")
    inlines = [AdventureWaveInline]


class AdventureWaveVariantInline(admin.TabularInline):
    model = AdventureWaveVariant
    extra = 0


@admin.register(AdventureWave)
class AdventureWaveAdmin(admin.ModelAdmin):
    list_display = ("slug", "title", "level", "sort_order", "is_published")
    list_filter = ("is_published",)
    search_fields = ("title", "slug")
    inlines = [AdventureWaveVariantInline]


@admin.register(AdventureRun)
class AdventureRunAdmin(admin.ModelAdmin):
    list_display = ("id", "player", "level", "current_wave", "is_replay", "stars", "status", "started_at")
    list_filter = ("is_replay", "status")


@admin.register(SkillMastery)
class SkillMasteryAdmin(admin.ModelAdmin):
    list_display = ("player", "command_form", "solves", "mastered", "learned_at")
    list_filter = ("mastered", "learned_at")
    search_fields = ("player__user__username", "command_form__slug", "command_form__usage_form")
