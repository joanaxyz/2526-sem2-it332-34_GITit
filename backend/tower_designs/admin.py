from django.contrib import admin

from towers.models import ArtifactPlacement, TowerContentBinding, TowerDesign, TowerPieceInstance


class TowerPieceInstanceInline(admin.TabularInline):
    model = TowerPieceInstance
    extra = 0


class ArtifactPlacementInline(admin.TabularInline):
    model = ArtifactPlacement
    extra = 0


@admin.register(TowerDesign)
class TowerDesignAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "visibility", "status", "is_active")
    list_filter = ("visibility", "status", "is_active")
    search_fields = ("title", "slug", "summary")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [TowerPieceInstanceInline, ArtifactPlacementInline]


@admin.register(TowerContentBinding)
class TowerContentBindingAdmin(admin.ModelAdmin):
    list_display = ("piece_instance", "content_definition")
    search_fields = ("content_definition__title",)

