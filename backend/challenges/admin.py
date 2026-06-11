from django.contrib import admin

from challenges.models import Challenge, ChallengeQuest, ChallengeRun, ChallengeVariant


@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ("slug", "title", "storey", "is_published", "sort_order")
    list_filter = ("is_published",)
    search_fields = ("title", "slug")


@admin.register(ChallengeQuest)
class ChallengeQuestAdmin(admin.ModelAdmin):
    list_display = ("challenge", "difficulty", "is_published")
    list_filter = ("difficulty", "is_published")


@admin.register(ChallengeVariant)
class ChallengeVariantAdmin(admin.ModelAdmin):
    list_display = ("slug", "challenge_quest", "is_published")
    list_filter = ("is_published",)


@admin.register(ChallengeRun)
class ChallengeRunAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "challenge", "challenge_quest", "status", "mode", "started_at")
    list_filter = ("status", "mode", "difficulty")
    search_fields = ("user__email", "challenge__title")
