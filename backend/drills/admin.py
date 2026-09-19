from django.contrib import admin

from drills.models import DrillProgress, DrillRun, LevelDrill, LevelDrillCard


class LevelDrillCardInline(admin.TabularInline):
    model = LevelDrillCard
    extra = 0
    fields = ("sort_order", "form_key", "command", "intent")
    readonly_fields = fields
    show_change_link = True
    can_delete = False


@admin.register(LevelDrill)
class LevelDrillAdmin(admin.ModelAdmin):
    """Seeded content: inspect it here, change it by re-running seed_drills."""

    list_display = ("adventure_level", "card_count", "has_sequence", "is_published", "updated_at")
    list_filter = ("is_published", "adventure_level__chapter")
    search_fields = ("adventure_level__slug", "adventure_level__title")
    inlines = [LevelDrillCardInline]

    @admin.display(description="Cards")
    def card_count(self, obj: LevelDrill) -> int:
        return obj.cards.count()


@admin.register(LevelDrillCard)
class LevelDrillCardAdmin(admin.ModelAdmin):
    list_display = ("form_key", "command", "intent", "drill")
    search_fields = ("form_key", "command", "intent")
    list_filter = ("drill__adventure_level__chapter",)


@admin.register(DrillRun)
class DrillRunAdmin(admin.ModelAdmin):
    list_display = ("player", "adventure_level", "status", "answered", "correct", "updated_at")
    list_filter = ("status",)
    search_fields = ("player__user__username", "adventure_level__slug")


@admin.register(DrillProgress)
class DrillProgressAdmin(admin.ModelAdmin):
    list_display = ("player", "adventure_level", "clears", "best_accuracy", "last_played_at")
    list_filter = ("adventure_level__chapter",)
    search_fields = ("player__user__username", "adventure_level__slug")
