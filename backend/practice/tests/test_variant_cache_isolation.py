"""The root conftest clears the per-variant evaluation caches around every test.

Each test's transaction rolls back and the database reuses row ids, so a
compiled spec or target hash cached under ``(variant.id, semantic_key)`` would
otherwise be served to a different variant in a later test. The two tests below
run in file order: the first fills both caches through a real tier command, the
second asserts it starts with both empty.
"""

from __future__ import annotations

from adventures.models import (
    AdventureLevel,
    AdventureLevelTier,
    AdventureLevelTierRun,
    AdventureLevelTierScenario,
    AdventureLevelTierScenarioVariant,
)
from adventures.services.tier_command_processing import AdventureLevelTierCommandProcessingService
from common.git.repository_state import VariantTargetStateHashCache
from curriculum.models import Chapter, Story
from evaluation.compiler import CompiledEvaluationSpecCache
from players.services import get_or_create_player
from testing.frontend_execution import frontend_execution_payload
from testing.runtime_factories import stage_readme_states


def _tier_run(django_user_model) -> AdventureLevelTierRun:
    user = django_user_model.objects.create_user(username="cache-isolation", password="test-pass")
    story = Story.objects.create(slug="cache-isolation", title="Cache isolation")
    chapter = Chapter.objects.create(story=story, slug="cache-isolation", number=1, title="Cache")
    level = AdventureLevel.objects.create(chapter=chapter, slug="cache-isolation", title="Cache")
    tier = AdventureLevelTier.objects.create(adventure_level=level, difficulty="easy")
    scenario = AdventureLevelTierScenario.objects.create(
        tier=tier, slug="cache-isolation", max_counted_commands=8
    )
    states = stage_readme_states()
    variant = AdventureLevelTierScenarioVariant.objects.create(
        scenario=scenario,
        slug="cache-isolation",
        label="Cache isolation",
        initial_state=states.initial,
        target_state=states.target,
        evaluation_spec={"completion_policy": {"mode": "state_hash"}},
        solution_commands=["git add README.md"],
    )
    return AdventureLevelTierRun.objects.create(
        player=get_or_create_player(user),
        tier=tier,
        current_scenario=scenario,
        selected_variant=variant,
        repository_state=states.initial,
        max_counted_commands=8,
    )


def test_a_real_tier_command_fills_both_variant_caches(db, django_user_model):
    run = _tier_run(django_user_model)

    AdventureLevelTierCommandProcessingService().submit_command(
        run=run,
        command="git add README.md",
        execution=frontend_execution_payload(
            "git add README.md", stage_readme_states().target, client_run_revision=0
        ),
    )

    assert CompiledEvaluationSpecCache._cache
    assert VariantTargetStateHashCache._cache


def test_the_next_test_starts_with_both_variant_caches_empty(db):
    assert not CompiledEvaluationSpecCache._cache
    assert not VariantTargetStateHashCache._cache
