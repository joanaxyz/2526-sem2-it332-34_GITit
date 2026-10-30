"""Ordered scenarios inside a tier, as documented in CONTENT_AUTHORING_GUIDE.md.

A run plays the learner's next uncleared scenario and rotates variants within it;
the tier completes on its last scenario; free play cycles the scenarios. A tier with
one scenario needing several clears behaves exactly as before.
"""

from adventures.models import (
    AdventureLevel,
    AdventureLevelTier,
    AdventureLevelTierProgress,
    AdventureLevelTierScenario,
    AdventureLevelTierScenarioVariant,
)
from adventures.services import AdventureLevelTierRunService
from adventures.services.tier_command_processing import AdventureLevelTierCommandProcessingService
from adventures.tier_payloads import progress_payload, scenario_payload
from curriculum.models import Chapter, Story
from players.services import get_or_create_player
from progress.models import AdventureLevelTierCompletion

STATE = {
    "repository_initialized": True,
    "commits": [],
    "branches": {},
    "head": {"type": "branch", "name": "main"},
    "staging": {},
    "working_tree": {},
    "conflicts": [],
}


def _tier(django_user_model, *, scenarios: list[tuple[str, list[str]]], name: str = "scenarios"):
    """``scenarios``: (slug, variant slugs in authored order); one clear each."""
    player = get_or_create_player(
        django_user_model.objects.create_user(username=name, password="pass12345")
    )
    story = Story.objects.create(slug=f"{name}-story", title="Story")
    chapter = Chapter.objects.create(
        story=story, slug=f"{name}-chapter", number=1, title="Module", description=""
    )
    level = AdventureLevel.objects.create(chapter=chapter, slug=f"{name}-level", title="Level")
    tier = AdventureLevelTier.objects.create(adventure_level=level, difficulty="easy")
    for order, (slug, variants) in enumerate(scenarios):
        scenario = AdventureLevelTierScenario.objects.create(
            tier=tier,
            slug=slug,
            title=slug.replace("-", " ").title(),
            sort_order=order,
            min_counted_commands=1,
            max_counted_commands=8,
        )
        # Authored order wins over alphabetical case IDs.
        for variant_order, variant_slug in enumerate(variants):
            AdventureLevelTierScenarioVariant.objects.create(
                scenario=scenario,
                slug=variant_slug,
                semantic_key=variant_slug,
                sort_order=variant_order,
                label=variant_slug,
                initial_state=STATE,
                evaluation_spec={"state_requirements": {}},
                solution_commands=["git status"],
            )
    return player, tier


def _start(player, tier, **kwargs):
    return AdventureLevelTierRunService().start_run(
        player=player, tier=tier, source_entry_point="level_page", **kwargs
    )


def _solve(run, *, within_budget: bool = True):
    """Solve the run: within the star budget earns 3 stars, over it 1."""
    run.counted_action_total = (
        run.min_counted_commands if within_budget else run.max_counted_commands
    )
    fields, rewards = AdventureLevelTierCommandProcessingService()._complete_run(run, [])
    run.save(update_fields=sorted(fields | {"counted_action_total"}))
    return rewards


def _fail(run):
    run.status = "failed"
    run.save(update_fields=["status"])


def test_runs_walk_the_scenarios_in_order_and_the_last_scenario_completes_the_tier(
    db, django_user_model
):
    player, tier = _tier(
        django_user_model,
        scenarios=[
            ("publish-a-branch", ["z-first", "a-second"]),
            ("publish-and-track", ["track-one", "track-two"]),
        ],
    )

    first = _start(player, tier)
    assert first.current_scenario.slug == "publish-a-branch"
    assert first.selected_variant.slug == "z-first"  # authored order, not alphabetical
    assert scenario_payload(first) == {"index": 1, "total": 2, "title": "Publish A Branch"}

    rewards = _solve(first)
    first._payload_context_loaded = False
    progress = progress_payload(first)
    assert progress["completed"] == 1 and progress["total"] == 2
    assert progress["cleared"] is False
    assert progress["next_scenario"] == {
        "index": 2,
        "slug": "publish-and-track",
        "title": "Publish And Track",
    }
    assert rewards["coins_awarded"] == 0
    assert not AdventureLevelTierCompletion.objects.filter(player=player, tier=tier).exists()

    second = _start(player, tier)
    assert second.current_scenario.slug == "publish-and-track"
    assert second.selected_variant.slug == "track-one"
    rewards = _solve(second, within_budget=False)

    completion = AdventureLevelTierCompletion.objects.get(player=player, tier=tier)
    assert rewards["coins_awarded"] == 25
    # The tier is graded by its weakest scenario (decision D3).
    assert completion.stars == 1
    assert AdventureLevelTierProgress.objects.get(
        player=player, tier=tier
    ).cleared_scenario_slugs == [
        "publish-a-branch",
        "publish-and-track",
    ]


def test_a_retry_rotates_variants_within_the_failed_scenario(db, django_user_model):
    player, tier = _tier(
        django_user_model,
        scenarios=[("scenario-one", ["one-a", "one-b"]), ("scenario-two", ["two-a", "two-b"])],
        name="rotate",
    )
    _solve(_start(player, tier))

    failed = _start(player, tier)
    assert failed.selected_variant.slug == "two-a"
    _fail(failed)
    retry = _start(player, tier)

    assert retry.current_scenario.slug == "scenario-two"
    assert retry.selected_variant.slug == "two-b"
    assert retry.prior_run_id == failed.id


def test_free_play_cycles_the_scenarios_after_the_tier_is_complete(db, django_user_model):
    player, tier = _tier(
        django_user_model,
        scenarios=[
            ("scenario-one", ["one-a"]),
            ("scenario-two", ["two-a"]),
            ("scenario-three", ["three-a"]),
        ],
        name="replay",
    )
    for _ in range(3):
        _solve(_start(player, tier))

    replays = []
    for _ in range(4):
        run = _start(player, tier)
        assert run.is_replay
        replays.append(run.current_scenario.slug)
        _solve(run)

    assert replays == ["scenario-one", "scenario-two", "scenario-three", "scenario-one"]
