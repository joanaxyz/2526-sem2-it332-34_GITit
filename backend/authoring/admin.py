from django.contrib import admin

from authoring.models import ContentDefinition, PublishedContentRuntime


@admin.register(ContentDefinition)
class ContentDefinitionAdmin(admin.ModelAdmin):
    list_display = ("title", "kind", "owner", "visibility", "status", "published_at")
    list_filter = ("kind", "visibility", "status")
    search_fields = ("title", "slug", "summary")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(PublishedContentRuntime)
class PublishedContentRuntimeAdmin(admin.ModelAdmin):
    list_display = ("content_definition", "chapter", "adventure", "challenge", "lesson", "compiled_at")
    search_fields = ("content_definition__title", "content_definition__slug")

