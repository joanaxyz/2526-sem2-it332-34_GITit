from datetime import date

from django.db import connection
from django.test.utils import CaptureQueriesContext
from rest_framework.test import APIClient

from adventures.models import AdventureLevel, AdventureLevelTier, AdventureLevelTierScenario
from challenges.models import ChallengeLevel, ChallengeTrial
from common.constants import DIFFICULTY_EASY, DIFFICULTY_HARD
from curriculum.models import Chapter, CommandForm, CommandSkill, Story
from players.services import get_or_create_player
from progress.models import ChallengeTrialCompletion, CoinTransaction
from progress.serializers import StatsActivityResponseSerializer, StatsSummaryResponseSerializer
from progress.services import MetricsService

SUMMARY_KEYS = {"activity_trend", "activity_window", "headline"}
TREND_POINT_KEYS = {"date", "levels_completed", "commands_run"}
HEADLINE_KEYS = {
    "levels_completed",
    "finish_rate",
    "accuracy",
    "hard_tier_clears",
    "comebacks",
    "perfect_clears",
    "gate_trial_clears",
    "hard_gate_trial_clears",
    "gitcoins",
    "gitcoins_earned",
    "commands_run",
}


def test_authenticated_stats_summary_matches_documented_contract(db, django_user_model):
    skill = CommandSkill.objects.create(
        slug="status",
        base_command="git status",
        title="Status",
        summary="Inspect the working tree.",
        sort_order=1,
    )
    story = Story.objects.create(slug="arcane-spire", title="The Arcane Spire")
    chapter = Chapter.objects.create(
        story=story,
        slug="stats-chapter",
        number=1,
        title="Stats Chapter",
        description="A chapter used to verify mastery metrics.",
    )
    form = CommandForm.objects.create(
        command_skill=skill,
        chapter=chapter,
        slug="plain",
        usage_form="git status",
        label="Read repository status",
        is_published=True,
        is_playable=True,
    )
    level = AdventureLevel.objects.create(
        chapter=chapter,
        slug="stats-level",
        title="Stats Level",
        is_required=True,
        is_published=True,
    )
    level.command_forms.add(form)
    tier = AdventureLevelTier.objects.create(adventure_level=level, difficulty="easy")
    scenario = AdventureLevelTierScenario.objects.create(
        tier=tier,
        slug="stats-scenario",
        title="Stats Scenario",
        is_published=True,
    )
    scenario.command_forms.add(form)
    user = django_user_model.objects.create_user(
        username="stats-contract",
        email="stats-contract@example.com",
        password="pass12345",
    )
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.get("/api/progress/stats/")

    assert response.status_code == 200
    payload = response.json()
    assert set(payload) == SUMMARY_KEYS

    # The default window is a trailing month of daily points.
    assert payload["activity_window"] == "month"
    assert len(payload["activity_trend"]) == 30
    assert all(set(point) == TREND_POINT_KEYS for point in payload["activity_trend"])
    assert all(
        type(point["date"]) is str
        and type(point["levels_completed"]) is int
        and type(point["commands_run"]) is int
        for point in payload["activity_trend"]
    )
    assert all(date.fromisoformat(point["date"]) for point in payload["activity_trend"])

    assert set(payload["headline"]) == HEADLINE_KEYS
    finish_rate = payload["headline"]["finish_rate"]
    assert finish_rate == {
        "value": None,
        "numerator": 0,
        "denominator": 0,
    }
    assert set(finish_rate) == {
        "value",
        "numerator",
        "denominator",
    }
    assert finish_rate["value"] is None
    assert type(finish_rate["numerator"]) is int
    assert type(finish_rate["denominator"]) is int
    assert payload["headline"]["accuracy"] is None
    for field_name in ("hard_tier_clears", "comebacks"):
        scoped_count = payload["headline"][field_name]
        assert set(scoped_count) == {"value", "scope"}
        assert type(scoped_count["value"]) is int
        assert type(scoped_count["scope"]) is str
    for field_name in (
        "levels_completed",
        "perfect_clears",
        "gate_trial_clears",
        "hard_gate_trial_clears",
        "gitcoins",
        "gitcoins_earned",
        "commands_run",
    ):
        assert type(payload["headline"][field_name]) is int
    assert "activity" not in payload
    assert "headlines" not in payload
    assert "totals" not in payload

    documented = StatsSummaryResponseSerializer(data=payload)
    assert documented.is_valid(), documented.errors


def test_stats_headline_counts_gate_trials_and_coins_won_through_play(db, django_user_model):
    user = django_user_model.objects.create_user(
        username="stats-gates",
        email="stats-gates@example.com",
        password="pass12345",
    )
    player = get_or_create_player(user)

    def gate_trials(story_slug: str) -> list[ChallengeTrial]:
        story, _ = Story.objects.get_or_create(slug=story_slug, defaults={"title": story_slug})
        chapter = Chapter.objects.create(
            story=story, slug=f"{story_slug}-gate-chapter", number=1, title="Gate", description=""
        )
        level = ChallengeLevel.objects.create(
            chapter=chapter, slug=f"{story_slug}-gate", title="Gate", is_published=True
        )
        return [
            ChallengeTrial.objects.create(
                challenge_level=level,
                difficulty=difficulty,
                min_counted_commands=1,
                max_counted_commands=3,
                is_published=True,
            )
            for difficulty in (DIFFICULTY_EASY, DIFFICULTY_HARD)
        ]

    # Both Arcane Spire trials count; a retired story's gate never does.
    for trial in gate_trials("arcane-spire") + gate_trials("frostbound-citadel")[:1]:
        ChallengeTrialCompletion.objects.create(player=player, challenge_trial=trial, stars=2)

    for amount, reason, key in (
        (100, "signup_grant", "signup"),
        (25, "adventure_level_reward", "level"),
        (50, "adventure_tier_reward", "tier"),
        (100, "challenge_trial_reward", "trial"),
        (40, "chapter_chest", "chest"),
        (-80, "shop_purchase", "shop"),
    ):
        CoinTransaction.objects.create(player=player, amount=amount, reason=reason, award_key=key)

    headline = MetricsService().stats_summary(player=player)["headline"]

    assert headline["gate_trial_clears"] == 2
    assert headline["hard_gate_trial_clears"] == 1
    # Spending in the shop never lowers it, and the signup grant is not won.
    assert headline["gitcoins_earned"] == 215


def test_stats_contract_rejects_the_displaced_openapi_shape():
    serializer = StatsSummaryResponseSerializer(
        data={
            "activity": [],
            "headlines": {},
            "totals": {},
        }
    )

    assert set(serializer.fields) == SUMMARY_KEYS
    assert serializer.is_valid() is False
    assert set(serializer.errors) == {"activity_trend", "activity_window", "headline"}


def test_stats_summary_activity_window_selects_the_trailing_span(db, django_user_model):
    user = django_user_model.objects.create_user(
        username="stats-window",
        email="stats-window@example.com",
        password="pass12345",
    )
    client = APIClient()
    client.force_authenticate(user=user)

    week = client.get("/api/progress/stats/", {"window": "week"}).json()
    assert week["activity_window"] == "week"
    assert len(week["activity_trend"]) == 7

    year = client.get("/api/progress/stats/", {"window": "year"}).json()
    assert year["activity_window"] == "year"
    # A year is twelve monthly buckets, not 365 daily ones, and every bucket is
    # labelled by the first day of its month.
    assert len(year["activity_trend"]) == 12
    assert all(date.fromisoformat(point["date"]).day == 1 for point in year["activity_trend"])

    # An unknown window is not an error; it falls back to the default.
    fallback = client.get("/api/progress/stats/", {"window": "decade"}).json()
    assert fallback["activity_window"] == "month"
    assert len(fallback["activity_trend"]) == 30

    months = [date.fromisoformat(point["date"]) for point in year["activity_trend"]]
    assert months == sorted(months)
    assert months[-1].month == date.today().month


def test_stats_activity_endpoint_returns_only_range_dependent_data(db, django_user_model):
    user = django_user_model.objects.create_user(
        username="stats-activity",
        email="stats-activity@example.com",
        password="pass12345",
    )
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.get("/api/progress/stats/activity/", {"window": "week"})

    assert response.status_code == 200
    payload = response.json()
    assert set(payload) == {"activity_trend", "activity_window"}
    assert payload["activity_window"] == "week"
    assert len(payload["activity_trend"]) == 7
    assert "headline" not in payload
    assert "skill_profile" not in payload
    documented = StatsActivityResponseSerializer(data=payload)
    assert documented.is_valid(), documented.errors


def test_activity_summary_uses_only_the_two_runebound_trend_queries(db, django_user_model):
    user = django_user_model.objects.create_user(username="stats-activity-query-count")
    player = get_or_create_player(user)
    with CaptureQueriesContext(connection) as captured:
        payload = MetricsService().activity_summary(player=player, activity_window="month")

    assert payload["activity_window"] == "month"
    assert len(captured) == 2
