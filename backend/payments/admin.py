from django.contrib import admin

from payments.models import GitCoinPurchase


@admin.register(GitCoinPurchase)
class GitCoinPurchaseAdmin(admin.ModelAdmin):
    list_display = ("player", "pack_slug", "coins", "amount_cents", "status", "created_at")
    list_filter = ("status", "pack_slug")
    search_fields = ("player__user__username", "stripe_session_id")
