from django.contrib import admin

from archive.models import ArchiveDesign, RelicPlacement


class RelicPlacementInline(admin.TabularInline):
    model = RelicPlacement
    extra = 0


@admin.register(ArchiveDesign)
class ArchiveDesignAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "visibility", "status", "origin", "is_active")
    list_filter = ("visibility", "status", "origin", "is_active")
    search_fields = ("title", "slug", "summary")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [RelicPlacementInline]
