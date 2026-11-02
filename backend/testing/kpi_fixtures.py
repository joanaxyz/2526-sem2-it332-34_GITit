"""Small real-engine routes for KPI lifecycle and cutoff acceptance tests."""

import json
from functools import lru_cache
from pathlib import Path

from django.utils import timezone

from adventures.models import (
    AdventureLevel,
    AdventureLevelTier,
    AdventureLevelTierScenario,
    AdventureLevelTierScenarioVariant,
)
from adventures.services import (
    AdventureLevelTierCommandProcessingService,
    AdventureLevelTierRunService,
)
from curriculum.models import Chapter, Story
from players.services import get_or_create_player
from practice.models import CommandStep
from progress.models import AdventureLevelTierCompletion
from progress.services.references import ref_hash


@lru_cache(maxsize=1)
def routes():
    data = json.loads(
        (Path(__file__).parent / "fixtures/kpi_routes.json").read_text(encoding="utf-8")
    )
    return data["cases"], data["targets"], data["replays"]


def variant(scenario, slug, key="practice"):
    """A published variant on a real KPI route with a validated reference of 3."""
    cases, targets, _ = routes()
    created = AdventureLevelTierScenarioVariant.objects.create(
        scenario=scenario,
        slug=slug,
        label=key,
        # One case per variant, as in the curriculum, though scenarios share routes.
        semantic_key=slug,
        initial_state=cases[key]["initial_state"],
        target_state=targets[key],
        evaluation_spec={"completion_policy": {"mode": "state_hash"}},
        solution_commands=cases[key]["solution_commands"],
        ref_count=3,
        is_transfer=key == "transfer",
        transfer_note="Apply the workflow to multiple files instead of one."
        if key == "transfer"
        else "",
    )
    created.ref_hash = ref_hash(created)
    created.save(update_fields=["ref_hash"])
    return created


def bundle(user_model, *, username="kpi", required=3, module=3):
    """A Hard tier of ``required`` single-clear scenarios, with real KPI routes.

    The first scenario holds the practice and the reserved transfer variant; each
    later scenario has its own practice variant. Returns the first scenario and its
    two variants.
    """
    player = get_or_create_player(user_model.objects.create_user(username=username))
    story, _ = Story.objects.get_or_create(slug="arcane-spire", defaults={"title": "Arcane Spire"})
    chapter, _ = Chapter.objects.get_or_create(
        story=story,
        number=module,
        defaults={"slug": f"m{module}", "title": f"Module {module}"},
    )
    level = AdventureLevel.objects.create(
        chapter=chapter,
        slug=f"resolving-conflicts-{username}",
        title="Checkpoint exercise",
        is_required=True,
    )
    tier = AdventureLevelTier.objects.create(adventure_level=level, difficulty="hard")
    medium = AdventureLevelTier.objects.create(adventure_level=level, difficulty="medium")
    AdventureLevelTierCompletion.objects.create(player=player, tier=medium)
    scenarios = [
        AdventureLevelTierScenario.objects.create(
            tier=tier,
            slug=f"scenario-{username}" if index == 0 else f"scenario-{username}-{index + 1}",
            sort_order=index,
            min_counted_commands=3,
            max_counted_commands=8,
        )
        for index in range(required)
    ]
    variants = [variant(scenarios[0], f"{username}-{key}", key) for key in ("practice", "transfer")]
    for index, scenario in enumerate(scenarios[1:], start=2):
        variant(scenario, f"{username}-practice-{index}", "practice")
    return player, tier, scenarios[0], variants


def start(player, tier, **kwargs):
    return AdventureLevelTierRunService().start_run(
        player=player,
        tier=tier,
        source_entry_point="level_page",
        **kwargs,
    )


def end(run, *, passed=True, count=3):
    """Persist the completion orchestration with a real authored route count."""
    run.counted_action_total = count
    run.total_attempts = count
    for i in range(count):
        CommandStep.objects.create(
            adventure_tier_run=run,
            command_text="git init",
            normalized_command="git init",
            command_classification="counted",
            result_category="target_not_yet_matched",
            was_processable=True,
            counted_increment=1,
            attempt_number=i + 1,
            counted_total_after=i + 1,
        )
    if passed:
        AdventureLevelTierCommandProcessingService()._complete_run(run, [])
    else:
        run.status, run.ended_at = "failed", timezone.now()
    run.save()
    if run.is_transfer:
        from progress.services.checkpoints import finish_transfer

        finish_transfer(run)
    return run
