from django.contrib import admin

from adventures.models import (
    AdventureLevel,
    AdventureLevelTier,
    AdventureLevelTierRun,
    AdventureLevelTierWave,
    AdventureLevelTierWaveVariant,
    SkillMastery,
)


class AdventureLevelTierInline(admin.TabularInline):
    model = AdventureLevelTier
    extra = 0


@admin.register(AdventureLevel)
class AdventureLevelAdmin(admin.ModelAdmin):
    list_display = ("slug", "title", "chapter", "is_required", "is_published", "sort_order")
    list_filter = ("is_required", "is_published", "chapter")
    search_fields = ("title", "slug")
    inlines = [AdventureLevelTierInline]


class AdventureLevelTierWaveVariantInline(admin.TabularInline):
    model = AdventureLevelTierWaveVariant
    extra = 0
    fields = ("slug", "label", "sort_order", "is_transfer", "is_published")


@admin.register(AdventureLevelTierWave)
class AdventureLevelTierWaveAdmin(admin.ModelAdmin):
    list_display = ("slug", "title", "tier", "sort_order", "is_published")
    list_filter = ("is_published", "tier__difficulty")
    search_fields = ("title", "slug")
    inlines = [AdventureLevelTierWaveVariantInline]


@admin.register(AdventureLevelTierRun)
class AdventureLevelTierRunAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "player",
        "tier",
        "current_wave",
        "is_replay",
        "is_transfer",
        "stars",
        "status",
        "started_at",
    )
    list_filter = ("is_replay", "is_transfer", "status")


@admin.register(SkillMastery)
class SkillMasteryAdmin(admin.ModelAdmin):
    list_display = ("player", "command_form", "solves", "mastered", "learned_at")
    list_filter = ("mastered", "learned_at")
    search_fields = ("player__user__username", "command_form__slug", "command_form__usage_form")
