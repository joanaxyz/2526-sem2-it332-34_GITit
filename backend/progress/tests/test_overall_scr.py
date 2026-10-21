"""Overall SCR shares its source and filters with the per-module SCR.

The admin dashboard's overall SCR card reads runebound_performance.kpis.scr,
so its individual tier counts equal the sum of the per-module rows: Runebound tier runs in story
arcane-spire, Modules 1-4, replays excluded.
"""

from rest_framework.test import APIClient

from adventures.models import (
    AdventureLevel,
    AdventureLevelTier,
    AdventureLevelTierRun,
    AdventureLevelTierScenario,
    AdventureLevelTierScenarioVariant,
)
from common.constants import (
    SESSION_STATUS_COMPLETED,
    SESSION_STATUS_FAILED,
    SESSION_STATUS_STARTED,
)
from curriculum.models import Chapter, Story
from players.services import get_or_create_player
from progress.models import AdventureLevelTierCompletion
from progress.services import MetricsService


def _tier(story, number):
    chapter = Chapter.objects.create(
        story=story, slug=f"{story.slug}-m{number}", number=number, title=f"Module {number}"
    )
    level = AdventureLevel.objects.create(
        chapter=chapter, slug=f"{story.slug}-level-{number}", title=f"Level {number}"
    )
    tier = AdventureLevelTier.objects.create(adventure_level=level, difficulty="easy")
    scenario = AdventureLevelTierScenario.objects.create(tier=tier, slug=f"{story.slug}-scenario-{number}")
    variant = AdventureLevelTierScenarioVariant.objects.create(
        scenario=scenario, slug=f"{story.slug}-v{number}", label="v"
    )
    return tier, scenario, variant


def _run(player, tier_bundle, status, **extra):
    tier, scenario, variant = tier_bundle
    return AdventureLevelTierRun.objects.create(
        player=player,
        tier=tier,
        current_scenario=scenario,
        selected_variant=variant,
        status=status,
        **extra,
    )


def test_overall_scr_matches_per_module_scr_source(db, django_user_model):
    legacy = Story.objects.create(slug=MetricsService.PERFORMANCE_STORY_SLUG, title="Legacy")
    other = Story.objects.create(slug="other-story", title="Other")
    tiers = {number: _tier(legacy, number) for number in (1, 2, 3, 4, 5)}
    other_tier = _tier(other, 1)

    user = django_user_model.objects.create_user(username="scr-learner", password="pass12345")
    player = get_or_create_player(user)
    # Counted: 3 tiers with an outcome, 2 mastered.
    _run(player, tiers[1], SESSION_STATUS_COMPLETED)
    _run(player, tiers[1], SESSION_STATUS_FAILED)
    _run(player, tiers[2], SESSION_STATUS_COMPLETED)
    _run(player, tiers[3], SESSION_STATUS_FAILED)
    # Not counted: an opened tier with no commands, a replay, a module
    # outside 1-4, and another story.
    _run(player, tiers[4], SESSION_STATUS_STARTED)
    _run(player, tiers[4], SESSION_STATUS_COMPLETED, is_replay=True)
    _run(player, tiers[5], SESSION_STATUS_COMPLETED)
    _run(player, other_tier, SESSION_STATUS_COMPLETED)

    for number in (1, 2):
        AdventureLevelTierCompletion.objects.create(player=player, tier=tiers[number][0])
    summary = MetricsService().performance_summary(player=player)

    assert summary["kpis"]["scr"] == {"value": 66.7, "numerator": 2, "denominator": 3}
    modules = summary["modules"]
    assert [m["number"] for m in modules] == [1, 2, 3, 4]
    assert sum(m["scr"]["numerator"] for m in modules) == summary["kpis"]["scr"]["numerator"]
    assert sum(m["scr"]["denominator"] for m in modules) == summary["kpis"]["scr"]["denominator"]

    staff = django_user_model.objects.create_user(
        username="scr-staff", password="pass12345", is_staff=True
    )
    client = APIClient()
    client.force_authenticate(user=staff)
    body = client.get("/api/admin/analytics/").json()
    assert body["runebound_performance"]["kpis"]["scr"]["value"] == summary["kpis"]["scr"]["value"]
    # data.runs counts every tier and challenge run across every story,
    # including the replay, the open run, and the other story's run.
    assert body["runs"]["adventure"]["total"] == AdventureLevelTierRun.objects.count()
    assert body["runs"]["total"] == AdventureLevelTierRun.objects.count()


def test_overall_scr_without_runs_is_null(db):
    Story.objects.create(slug=MetricsService.PERFORMANCE_STORY_SLUG, title="Legacy")

    summary = MetricsService().all_player_performance_summary()

    assert summary["kpis"]["scr"] == {
        "value": None,
        "numerator": 0,
        "denominator": 0,
        "unit": "participants",
    }
