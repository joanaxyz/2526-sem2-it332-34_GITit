"""A tier run's command budget is always at least one counted command."""

from adventures.models import (
    AdventureLevel,
    AdventureLevelTier,
    AdventureLevelTierScenario,
    AdventureLevelTierScenarioVariant,
)
from adventures.services import AdventureLevelTierRunService
from common.constants import SESSION_STATUS_STARTED
from curriculum.models import Chapter, Story
from players.services import get_or_create_player


def test_read_only_scenario_with_zero_minimum_starts_with_a_budget_of_one(db, django_user_model):
    """Scenarios allow min_counted_commands=0; runs require >= 1. Starting used to
    raise IntegrityError, reported as an unrelated "active run" conflict."""
    story = Story.objects.create(slug="budget-story", title="Budget")
    chapter = Chapter.objects.create(story=story, slug="budget-m1", number=1, title="Module 1")
    level = AdventureLevel.objects.create(chapter=chapter, slug="budget-level", title="Level")
    tier = AdventureLevelTier.objects.create(adventure_level=level, difficulty="easy")
    scenario = AdventureLevelTierScenario.objects.create(
        tier=tier, slug="budget-scenario", min_counted_commands=0, max_counted_commands=0
    )
    AdventureLevelTierScenarioVariant.objects.create(
        scenario=scenario,
        slug="budget-v",
        label="v",
        initial_state={"repository_initialized": True},
    )
    player = get_or_create_player(
        django_user_model.objects.create_user(username="budget", password="pass12345")
    )

    run = AdventureLevelTierRunService().start_run(
        player=player, tier=tier, source_entry_point="level_page"
    )

    assert run.status == SESSION_STATUS_STARTED
    assert run.min_counted_commands == 1
    assert run.generous_counted_commands == 2
    assert run.max_counted_commands == 3


def test_variant_budget_overrides_the_shared_scenario_budget(db, django_user_model):
    story = Story.objects.create(slug="variant-budget-story", title="Variant budget")
    chapter = Chapter.objects.create(
        story=story, slug="variant-budget-m1", number=1, title="Module 1"
    )
    level = AdventureLevel.objects.create(
        chapter=chapter, slug="variant-budget-level", title="Level"
    )
    tier = AdventureLevelTier.objects.create(adventure_level=level, difficulty="easy")
    scenario = AdventureLevelTierScenario.objects.create(
        tier=tier, slug="variant-budget-scenario", min_counted_commands=2, max_counted_commands=5
    )
    AdventureLevelTierScenarioVariant.objects.create(
        scenario=scenario,
        slug="variant-budget-v",
        label="v",
        initial_state={"repository_initialized": True},
        parameter_context={"minimum_counted_commands": 4, "maximum_counted_commands": 7},
    )
    player = get_or_create_player(
        django_user_model.objects.create_user(username="variant-budget", password="pass12345")
    )

    run = AdventureLevelTierRunService().start_run(
        player=player, tier=tier, source_entry_point="level_page"
    )

    assert run.min_counted_commands == 4
    assert run.max_counted_commands == 7
