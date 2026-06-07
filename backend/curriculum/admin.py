from django.contrib import admin

from curriculum.models import CommandForm, CommandSkill, ConceptPage, Storey


@admin.register(Storey)
class StoreyAdmin(admin.ModelAdmin):
    list_display = ("number", "title", "slug", "is_published", "sort_order")
    list_filter = ("is_published",)
    search_fields = ("title", "slug")


@admin.register(ConceptPage)
class ConceptPageAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "is_published", "sort_order")
    list_filter = ("is_published",)
    search_fields = ("title", "slug")


@admin.register(CommandSkill)
class CommandSkillAdmin(admin.ModelAdmin):
    list_display = ("slug", "base_command", "module", "is_published", "sort_order")
    list_filter = ("is_published", "base_command")
    search_fields = ("title", "slug", "base_command")


@admin.register(CommandForm)
class CommandFormAdmin(admin.ModelAdmin):
    list_display = ("slug", "usage_form", "topic", "is_published", "sort_order")
    list_filter = ("is_published",)
    search_fields = ("label", "usage_form", "slug")
