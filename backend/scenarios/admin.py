from django.contrib import admin

from scenarios.models import GitCommandContent


@admin.register(GitCommandContent)
class GitCommandContentAdmin(admin.ModelAdmin):
    list_display = (
        "key",
        "base_command",
        "display_name",
        "canonical_command",
        "is_active",
        "version",
        "sort_order",
    )
    list_filter = ("is_active",)
    search_fields = ("key", "base_command", "display_name", "canonical_command")
    ordering = ("sort_order", "key")
