from django.contrib import admin

from curriculum.models import CommandForm, CommandSkill, LibraryEntry, Chapter, Tome


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ("number", "title", "slug", "is_published", "sort_order")
    list_filter = ("is_published",)
    search_fields = ("title", "slug")


@admin.register(Tome)
class TomeAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "chapter", "placement", "is_published", "sort_order")
    list_filter = ("is_published", "placement")
    search_fields = ("title", "slug")


@admin.register(LibraryEntry)
class LibraryEntryAdmin(admin.ModelAdmin):
    list_display = ("command_key", "title", "is_published")
    list_filter = ("is_published",)
    search_fields = ("command_key", "title")


@admin.register(CommandSkill)
class CommandSkillAdmin(admin.ModelAdmin):
    list_display = ("slug", "base_command", "chapter", "is_published", "sort_order")
    list_filter = ("is_published", "base_command")
    search_fields = ("title", "slug", "base_command")


@admin.register(CommandForm)
class CommandFormAdmin(admin.ModelAdmin):
    list_display = ("slug", "usage_form", "command_skill", "is_published", "sort_order")
    list_filter = ("is_published",)
    search_fields = ("label", "usage_form", "slug")
