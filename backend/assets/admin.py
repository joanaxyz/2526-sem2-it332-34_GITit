from django.contrib import admin

from assets.models import Asset, AssetSprite, RelicAsset


class AssetSpriteInline(admin.TabularInline):
    model = AssetSprite
    extra = 1
    # Frame grid is derived from the uploaded image on save - show it read-only
    # so authors see what the system counted, but never type it.
    readonly_fields = ("columns", "rows", "frame_count")
    fields = ("action", "image", "frame_width", "frame_height", "columns", "rows", "frame_count", "fps", "loops")


class RelicAssetInline(admin.StackedInline):
    model = RelicAsset
    extra = 0
    fields = (
        "view_box",
        "interactive_viewbox",
        "landing_viewbox",
        "svg_sanitized",
    )


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ("slug", "kind", "label", "owner", "visibility", "price", "is_published")
    list_filter = ("kind", "visibility", "is_published")
    search_fields = ("slug", "label", "tags")
    prepopulated_fields = {"slug": ("label",)}
    inlines = [RelicAssetInline, AssetSpriteInline]
