from datetime import date

from django.db import connection
from django.test.utils import CaptureQueriesContext
from rest_framework.test import APIClient

from adventures.models import AdventureLevel, AdventureLevelTier, AdventureLevelTierScenario
from curriculum.models import Chapter, CommandForm, CommandSkill, Story
from players.services import get_or_create_player
from progress.serializers import StatsActivityResponseSerializer, StatsSummaryResponseSerializer
from progress.services import MetricsService

SUMMARY_KEYS = {"skill_profile", "activity_trend", "activity_window", "headline"}
SKILL_AXIS_KEYS = {"key", "label", "hint", "value", "command"}
TREND_POINT_KEYS = {"date", "levels_completed", "commands_run"}
HEADLINE_KEYS = {
    "levels_completed",
    "finish_rate",
    "accuracy",
    "hard_tier_clears",
    "comebacks",
    "perfect_clears",
    "day_streak",
    "longest_streak",
    "gitcoins",
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

    assert {
        "key": "status",
        "label": "Status",
        "hint": "Inspect the working tree.",
        "value": 0.0,
        "command": "git status",
    } in payload["skill_profile"]
    assert all(set(axis) == SKILL_AXIS_KEYS for axis in payload["skill_profile"])
    assert all(
        type(axis["key"]) is str
        and type(axis["label"]) is str
        and type(axis["hint"]) is str
        and (type(axis["value"]) is float or axis["value"] is None)
        and type(axis["command"]) is str
        for axis in payload["skill_profile"]
    )

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
        "day_streak",
        "longest_streak",
        "gitcoins",
        "commands_run",
    ):
        assert type(payload["headline"][field_name]) is int
    assert "activity" not in payload
    assert "headlines" not in payload
    assert "totals" not in payload

    documented = StatsSummaryResponseSerializer(data=payload)
    assert documented.is_valid(), documented.errors


def test_stats_skill_profile_excludes_unearnable_and_non_runebound_commands(db, django_user_model):
    CommandSkill.objects.create(
        slug="library-only",
        base_command="git library-only",
        title="Library only",
        summary="Reference material with no playable curriculum scenario.",
    )
    reference_skill = CommandSkill.objects.create(
        slug="reference-only",
        base_command="git reference-only",
        title="Reference only",
    )
    CommandForm.objects.create(
        command_skill=reference_skill,
        slug="reference",
        usage_form="git reference-only",
        label="Read about a command",
        is_published=True,
        is_playable=False,
    )
    simulator_only_skill = CommandSkill.objects.create(
        slug="simulator-only",
        base_command="git simulator-only",
        title="Simulator only",
    )
    CommandForm.objects.create(
        command_skill=simulator_only_skill,
        slug="supported",
        usage_form="git simulator-only",
        label="Supported but not taught",
        is_published=True,
        is_playable=True,
    )
    other_story = Story.objects.create(slug="frostbound-citadel", title="Frostbound Citadel")
    other_chapter = Chapter.objects.create(
        story=other_story,
        slug="arcane-chapter",
        number=1,
        title="Arcane Chapter",
        description="A published curriculum outside Runebound Turret.",
    )
    other_skill = CommandSkill.objects.create(
        slug="arcane-command",
        base_command="git arcane",
        title="Arcane command",
    )
    other_form = CommandForm.objects.create(
        command_skill=other_skill,
        chapter=other_chapter,
        slug="playable",
        usage_form="git arcane",
        label="A playable command from another story",
        is_published=True,
        is_playable=True,
    )
    other_level = AdventureLevel.objects.create(
        chapter=other_chapter,
        slug="arcane-level",
        title="Arcane Level",
        is_required=True,
        is_published=True,
    )
    other_level.command_forms.add(other_form)
    other_tier = AdventureLevelTier.objects.create(adventure_level=other_level, difficulty="easy")
    other_scenario = AdventureLevelTierScenario.objects.create(
        tier=other_tier,
        slug="arcane-scenario",
        title="Arcane Scenario",
        is_published=True,
    )
    other_scenario.command_forms.add(other_form)
    user = django_user_model.objects.create_user(username="stats-curriculum-scope")
    player = get_or_create_player(user)

    skill_profile = MetricsService()._command_skill_profile(player=player)

    assert skill_profile == []


def test_stats_contract_rejects_the_displaced_openapi_shape():
    serializer = StatsSummaryResponseSerializer(
        data={
            "skill_profile": [],
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
