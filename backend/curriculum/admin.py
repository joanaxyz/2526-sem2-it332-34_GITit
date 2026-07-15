from django.contrib import admin

from curriculum.models import Chapter, ChapterLesson, CommandForm, CommandSkill, LibraryEntry, Story


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "is_published", "sort_order")
    list_filter = ("is_published",)
    search_fields = ("title", "slug")


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ("number", "title", "slug", "story", "is_published", "sort_order")
    list_filter = ("is_published", "story")
    search_fields = ("title", "slug")


@admin.register(ChapterLesson)
class ChapterLessonAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "chapter", "is_published", "sort_order")
    list_filter = ("is_published", "chapter")
    search_fields = ("title", "slug")


@admin.register(LibraryEntry)
class LibraryEntryAdmin(admin.ModelAdmin):
    list_display = ("command_key", "title", "is_published")
    list_filter = ("is_published",)
    search_fields = ("command_key", "title")


@admin.register(CommandSkill)
class CommandSkillAdmin(admin.ModelAdmin):
    list_display = ("slug", "base_command", "is_published", "sort_order")
    list_filter = ("is_published", "base_command")
    search_fields = ("title", "slug", "base_command")


@admin.register(CommandForm)
class CommandFormAdmin(admin.ModelAdmin):
    list_display = ("slug", "usage_form", "command_skill", "chapter", "is_published", "sort_order")
    list_filter = ("is_published", "chapter")
    search_fields = ("label", "usage_form", "slug")
