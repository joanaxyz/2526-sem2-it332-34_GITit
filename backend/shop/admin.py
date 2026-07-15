from django.contrib import admin

from shop.models import Entitlement, PlayerLoadout


@admin.register(Entitlement)
class EntitlementAdmin(admin.ModelAdmin):
    list_display = ("player", "kind", "slug", "granted_at")
    list_filter = ("kind",)
    search_fields = ("player__user__username", "slug")


@admin.register(PlayerLoadout)
class PlayerLoadoutAdmin(admin.ModelAdmin):
    list_display = ("player", "active_companion_slug", "updated_at")
    search_fields = ("player__user__username",)
