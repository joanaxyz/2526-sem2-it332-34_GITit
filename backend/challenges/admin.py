from django.contrib import admin

from challenges.models import (
    ChallengeLevel,
    ChallengeRun,
    ChallengeTrial,
    ChallengeTrialVariant,
)


class ChallengeTrialInline(admin.TabularInline):
    model = ChallengeTrial
    extra = 0


@admin.register(ChallengeLevel)
class ChallengeLevelAdmin(admin.ModelAdmin):
    list_display = ("slug", "title", "chapter", "is_published", "sort_order")
    list_filter = ("is_published", "chapter")
    search_fields = ("title", "slug", "summary", "narrative")
    inlines = [ChallengeTrialInline]


class ChallengeTrialVariantInline(admin.TabularInline):
    model = ChallengeTrialVariant
    extra = 0


@admin.register(ChallengeTrial)
class ChallengeTrialAdmin(admin.ModelAdmin):
    list_display = ("challenge_level", "difficulty", "is_published")
    list_filter = ("difficulty", "is_published")
    inlines = [ChallengeTrialVariantInline]


@admin.register(ChallengeRun)
class ChallengeRunAdmin(admin.ModelAdmin):
    list_display = ("id", "player", "challenge_trial", "status", "is_replay", "stars", "started_at")
    list_filter = ("status", "is_replay")
    search_fields = ("player__user__email", "challenge_trial__challenge_level__title")
