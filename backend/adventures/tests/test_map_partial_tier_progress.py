from django.core.management import call_command

from adventures.models import (
    AdventureLevel,
    AdventureLevelTier,
    AdventureLevelTierProgress,
    AdventureLevelTierScenario,
)
from curriculum.models import Chapter, Story
from players.services import get_or_create_player
from progress.models import AdventureLevelTierCompletion

SCENARIOS = ["debut", "practice", "spiral"]


def _setup(django_user_model):
    story = Story.objects.create(slug="cutover-story", title="Story")
    chapter = Chapter.objects.create(story=story, slug="cutover", number=1, title="Module")
    level = AdventureLevel.objects.create(chapter=chapter, slug="cutover-level", title="Level")
    tier = AdventureLevelTier.objects.create(adventure_level=level, difficulty="easy")
    # The pre-plan pool scenario, now unpublished, and the designed scenarios.
    AdventureLevelTierScenario.objects.create(
        tier=tier, slug="cutover-level-easy", sort_order=0, is_published=False
    )
    for order, slug in enumerate(SCENARIOS, start=1):
        AdventureLevelTierScenario.objects.create(tier=tier, slug=slug, sort_order=order)

    def player(name: str, clears: int, cleared: list[str] | None = None):
        learner = get_or_create_player(django_user_model.objects.create_user(username=name))
        AdventureLevelTierProgress.objects.create(
            player=learner, tier=tier, successful_clears=clears, cleared_scenario_slugs=cleared or []
        )
        return learner

    return tier, player


def _cleared(player, tier) -> list[str]:
    return AdventureLevelTierProgress.objects.get(player=player, tier=tier).cleared_scenario_slugs


def test_partial_clears_map_onto_the_first_scenarios_without_completing_the_tier(db, django_user_model):
    tier, player = _setup(django_user_model)
    one = player("one", 1)
    many = player("many", 5)

    call_command("map_partial_tier_progress", verbosity=0)

    assert _cleared(one, tier) == ["debut"]
    # Never more than all but the last scenario: the tier is not completed for anyone.
    assert _cleared(many, tier) == ["debut", "practice"]
    assert not AdventureLevelTierCompletion.objects.exists()


def test_completed_tiers_and_new_scenario_progress_are_left_alone_and_a_rerun_is_a_no_op(
    db, django_user_model
):
    tier, player = _setup(django_user_model)
    done = player("done", 2)
    AdventureLevelTierCompletion.objects.create(player=done, tier=tier)
    playing = player("playing", 1, ["debut"])
    partial = player("partial", 2)

    call_command("map_partial_tier_progress", verbosity=0)
    first = {
        name: _cleared(p, tier)
        for name, p in (("done", done), ("playing", playing), ("partial", partial))
    }
    call_command("map_partial_tier_progress", verbosity=0)

    assert first == {"done": [], "playing": ["debut"], "partial": ["debut", "practice"]}
    assert {
        name: _cleared(p, tier)
        for name, p in (("done", done), ("playing", playing), ("partial", partial))
    } == first


def test_dry_run_reports_without_writing(db, django_user_model, capsys):
    tier, player = _setup(django_user_model)
    partial = player("partial", 2)

    call_command("map_partial_tier_progress", "--dry-run")

    assert "Would map 1 partly done tiers onto 2 first scenarios." in capsys.readouterr().out
    assert _cleared(partial, tier) == []
