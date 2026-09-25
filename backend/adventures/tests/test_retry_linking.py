"""A fresh start right after a failure on the same tier is linked as its retry.

The level page starts runs without a prior_run; the Retry button passes one.
When the learner's most recent run on the tier failed and nothing has retried
it yet, a fresh start gets the same prior_run, retry_index and variant rotation
the Retry button would give it.
"""

import pytest

from adventures.models import (
    AdventureLevel,
    AdventureLevelTier,
    AdventureLevelTierRun,
    AdventureLevelTierWave,
    AdventureLevelTierWaveVariant,
)
from adventures.services import AdventureLevelTierRunService
from common.constants import (
    SESSION_STATUS_COMPLETED,
    SESSION_STATUS_FAILED,
    SESSION_STATUS_STARTED,
)
from curriculum.models import Chapter, Story
from players.services import get_or_create_player
from practice.models import CommandStep
from progress.services import MetricsService


def _tier(chapter, slug):
    level = AdventureLevel.objects.create(chapter=chapter, slug=slug, title=slug)
    tier = AdventureLevelTier.objects.create(adventure_level=level, difficulty="easy")
    wave = AdventureLevelTierWave.objects.create(tier=tier, slug=f"{slug}-wave")
    for key in ("a", "b"):
        AdventureLevelTierWaveVariant.objects.create(
            wave=wave,
            slug=f"{slug}-{key}",
            label=key,
            semantic_key=f"{slug}-{key}",
            initial_state={"repository_initialized": True, "files": {f"{key}.txt": key}},
            target_state={"files": {f"{key}.txt": f"{key}-done"}},
        )
    return tier


@pytest.fixture
def tiers(db):
    """Two Module 3 tiers in the RTA story, each with two structurally different variants."""
    story = Story.objects.create(slug=MetricsService.PERFORMANCE_STORY_SLUG, title="Legacy")
    chapter = Chapter.objects.create(story=story, slug="m3", number=3, title="Module 3")
    return _tier(chapter, "conflicts-a"), _tier(chapter, "conflicts-b")


@pytest.fixture
def player(db, django_user_model):
    return get_or_create_player(
        django_user_model.objects.create_user(username="relinker", password="pass12345")
    )


def _level_page_start(player, tier):
    """What the level page does: start a run with no prior_run."""
    return AdventureLevelTierRunService().start_run(
        player=player, tier=tier, source_entry_point="level_page"
    )


def _retry_button(player, run):
    """What the Retry button does: start a run with the failed run as prior_run."""
    return AdventureLevelTierRunService().start_run(
        player=player, tier=run.tier, source_entry_point="retry", prior_run=run
    )


def _end(run, status):
    """Finish a started run the way command processing would, with one command."""
    CommandStep.objects.create(
        adventure_tier_run=run,
        command_text="git status",
        normalized_command="git status",
        result_category=CommandStep.ResultCategory.TARGET_MATCHED,
        command_classification=CommandStep.CommandClassification.DIAGNOSTIC,
        was_processable=True,
        attempt_number=1,
    )
    AdventureLevelTierRun.objects.filter(pk=run.pk).update(status=status)
    run.refresh_from_db()
    return run


def _structurally_different(first, second):
    a, b = first.selected_variant, second.selected_variant
    return a.initial_state != b.initial_state or a.target_state != b.target_state


def test_fresh_start_after_a_failure_is_linked_and_counts_for_rta(tiers, player):
    tier, _ = tiers
    failed = _end(_level_page_start(player, tier), SESSION_STATUS_FAILED)

    retry = _level_page_start(player, tier)

    assert retry.prior_run_id == failed.id
    assert retry.retry_index == failed.retry_index + 1 == 1
    # Same rotation as the Retry button: a structurally different variant.
    assert retry.changed_variant is True
    assert _structurally_different(failed, retry)

    _end(retry, SESSION_STATUS_COMPLETED)
    rta = MetricsService().performance_summary(player=player)["kpis"]["rta"]
    assert rta == {"value": 100.0, "numerator": 1, "denominator": 1}


def test_linked_fresh_start_matches_what_the_retry_button_gives(tiers, player, django_user_model):
    tier, _ = tiers
    failed = _end(_level_page_start(player, tier), SESSION_STATUS_FAILED)
    fresh = _level_page_start(player, tier)

    other = get_or_create_player(
        django_user_model.objects.create_user(username="retry-button", password="pass12345")
    )
    other_failed = _end(_level_page_start(other, tier), SESSION_STATUS_FAILED)
    button = _retry_button(other, other_failed)

    assert (fresh.retry_index, fresh.changed_variant, fresh.selected_variant_id) == (
        button.retry_index,
        button.changed_variant,
        button.selected_variant_id,
    )
    assert fresh.prior_run_id == failed.id and button.prior_run_id == other_failed.id


def test_a_run_on_another_tier_in_between_does_not_block_the_link(tiers, player):
    tier, other_tier = tiers
    failed = _end(_level_page_start(player, tier), SESSION_STATUS_FAILED)
    _end(_level_page_start(player, other_tier), SESSION_STATUS_COMPLETED)

    restart = _level_page_start(player, tier)

    assert restart.prior_run_id == failed.id
    assert restart.retry_index == 1


def test_restart_after_a_completed_run_is_not_linked(tiers, player):
    tier, _ = tiers
    _end(_level_page_start(player, tier), SESSION_STATUS_COMPLETED)

    restart = _level_page_start(player, tier)

    assert restart.prior_run_id is None
    assert restart.retry_index == 0


def test_restart_after_an_abandoned_run_is_not_linked(tiers, player):
    tier, _ = tiers
    left = _level_page_start(player, tier)
    _end(left, SESSION_STATUS_STARTED)  # one command, still open
    AdventureLevelTierRunService().discard(run=left)  # exit: kept as abandoned

    restart = _level_page_start(player, tier)

    assert restart.prior_run_id is None
    assert restart.retry_index == 0


def test_an_abandoned_run_after_the_failure_blocks_the_link(tiers, player):
    tier, _ = tiers
    _end(_level_page_start(player, tier), SESSION_STATUS_FAILED)
    # The learner tries again (linked), submits a command, and leaves: that
    # abandoned run is now the latest, and the failure already has a retry.
    in_between = _level_page_start(player, tier)
    _end(in_between, SESSION_STATUS_STARTED)
    AdventureLevelTierRunService().discard(run=in_between)

    restart = _level_page_start(player, tier)

    assert restart.prior_run_id is None


def test_an_empty_run_left_open_after_the_failure_does_not_block_the_link(tiers, player):
    """A run with no commands is deleted when replaced, so it is not "in between"."""
    tier, _ = tiers
    failed = _end(_level_page_start(player, tier), SESSION_STATUS_FAILED)
    AdventureLevelTierRun.objects.create(
        player=player,
        tier=tier,
        current_wave=failed.current_wave,
        selected_variant=failed.selected_variant,
        status=SESSION_STATUS_STARTED,
    )

    restart = _level_page_start(player, tier)

    assert restart.prior_run_id == failed.id


def test_a_failure_already_retried_with_the_retry_button_is_not_linked_twice(tiers, player):
    tier, _ = tiers
    failed = _end(_level_page_start(player, tier), SESSION_STATUS_FAILED)
    button_retry = _end(_retry_button(player, failed), SESSION_STATUS_FAILED)

    restart = _level_page_start(player, tier)

    # Linked to the newest failure (the Retry-button run), never to `failed` again.
    assert restart.prior_run_id == button_retry.id
    assert list(failed.retry_runs.values_list("id", flat=True)) == [button_retry.id]


def test_a_failure_that_already_has_a_retry_is_never_linked_again(tiers, player):
    """Guard: a failed run that is someone's prior_run is not relinked, even if
    it is the latest run by start time."""
    tier, _ = tiers
    failed = _end(_level_page_start(player, tier), SESSION_STATUS_FAILED)
    older_retry = AdventureLevelTierRun.objects.create(
        player=player,
        tier=tier,
        current_wave=failed.current_wave,
        selected_variant=failed.selected_variant,
        prior_run=failed,
        retry_index=1,
        status=SESSION_STATUS_COMPLETED,
    )
    AdventureLevelTierRun.objects.filter(pk=older_retry.pk).update(
        started_at=failed.started_at.replace(year=failed.started_at.year - 1)
    )

    restart = _level_page_start(player, tier)

    assert restart.prior_run_id is None


def test_replays_are_never_linked(tiers, player):
    tier, _ = tiers
    failed = _end(_level_page_start(player, tier), SESSION_STATUS_FAILED)
    AdventureLevelTierRun.objects.filter(pk=failed.pk).update(is_replay=True)

    restart = _level_page_start(player, tier)

    assert restart.prior_run_id is None
