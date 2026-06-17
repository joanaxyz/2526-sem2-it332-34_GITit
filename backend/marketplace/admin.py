from django.contrib import admin

from marketplace.models import Entitlement, StoreListing


@admin.register(StoreListing)
class StoreListingAdmin(admin.ModelAdmin):
    list_display = ("item_kind", "item_id", "seller", "price", "status", "created_at")
    list_filter = ("item_kind", "status")
    search_fields = ("asset__slug", "content_definition__title", "archive_design__title")


@admin.register(Entitlement)
class EntitlementAdmin(admin.ModelAdmin):
    list_display = ("user", "item_kind", "item", "source_listing", "granted_at")
    list_filter = ("item_kind",)
    search_fields = ("user__username", "asset__slug", "content_definition__title", "archive_design__title")

