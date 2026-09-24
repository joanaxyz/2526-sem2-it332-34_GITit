"""Leaving a tier run: keep it as abandoned once a command was submitted.

Every way a learner leaves an active run goes through
AdventureLevelTierRunService.discard: the exit button (DELETE), "start over"
(retry while the run is still active), and a new start on the same tier
replacing an active run, which is also what happens after a closed tab.
"""

import pytest
from rest_framework.test import APIClient

from adventures.models import (
    AdventureLevel,
    AdventureLevelTier,
    AdventureLevelTierRun,
    AdventureLevelTierWave,
    AdventureLevelTierWaveVariant,
)
from adventures.services import AdventureLevelTierRunService
from adventures.services.tier_variants import TierVariantSelectionService
from common.constants import (
    SESSION_STATUS_ABANDONED,
    SESSION_STATUS_FAILED,
    SESSION_STATUS_STARTED,
)
from curriculum.models import Chapter, Story
from players.services import get_or_create_player
from practice.models import CommandStep


@pytest.fixture
def tier(db):
    story = Story.objects.create(slug="abandon-story", title="Abandon story")
    chapter = Chapter.objects.create(story=story, slug="abandon-m1", number=1, title="Module 1")
    level = AdventureLevel.objects.create(chapter=chapter, slug="abandon-level", title="Level")
    tier = AdventureLevelTier.objects.create(adventure_level=level, difficulty="easy")
    wave = AdventureLevelTierWave.objects.create(tier=tier, slug="abandon-wave")
    for key in ("a", "b"):
        AdventureLevelTierWaveVariant.objects.create(
            wave=wave,
            slug=f"abandon-{key}",
            label=key,
            semantic_key=f"abandon-{key}",
            initial_state={"repository_initialized": True, "variant": key},
        )
    return tier


@pytest.fixture
def learner(db, django_user_model):
    user = django_user_model.objects.create_user(username="abandoner", password="pass12345")
    return user, get_or_create_player(user)


def _start(player, tier, **kwargs):
    return AdventureLevelTierRunService().start_run(
        player=player, tier=tier, source_entry_point="level_page", **kwargs
    )


def _submit_command(run):
    CommandStep.objects.create(
        adventure_tier_run=run,
        command_text="git status",
        normalized_command="git status",
        result_category=CommandStep.ResultCategory.TARGET_MATCHED,
        command_classification=CommandStep.CommandClassification.DIAGNOSTIC,
        was_processable=True,
        attempt_number=run.steps.count() + 1,
    )


def _status(run):
    row = AdventureLevelTierRun.objects.filter(pk=run.pk).first()
    return row.status if row else None


def test_exit_keeps_a_run_with_commands_as_abandoned(tier, learner):
    user, player = learner
    run = _start(player, tier)
    _submit_command(run)
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.delete(f"/api/adventure-tier-runs/{run.id}/")

    assert response.status_code == 204
    run.refresh_from_db()
    assert run.status == SESSION_STATUS_ABANDONED
    assert run.ended_at is not None
    assert run.completed_at is None
    # Its commands are kept with it.
    assert run.steps.count() == 1


def test_exit_still_deletes_a_run_without_commands(tier, learner):
    user, player = learner
    run = _start(player, tier)
    client = APIClient()
    client.force_authenticate(user=user)

    client.delete(f"/api/adventure-tier-runs/{run.id}/")

    assert _status(run) is None


def test_start_over_mid_run_abandons_the_old_run_and_does_not_chain_to_it(tier, learner):
    user, player = learner
    run = _start(player, tier)
    _submit_command(run)
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(f"/api/adventure-tier-runs/{run.id}/retry/")

    assert response.status_code == 201
    assert _status(run) == SESSION_STATUS_ABANDONED
    fresh = AdventureLevelTierRun.objects.get(pk=response.json()["id"])
    assert fresh.status == SESSION_STATUS_STARTED
    # Same chain shape as when the old run was deleted.
    assert fresh.prior_run_id is None
    assert fresh.retry_index == 1


def test_start_over_without_commands_still_deletes_the_old_run(tier, learner):
    _, player = learner
    run = _start(player, tier)

    _start(player, tier, prior_run=run)

    assert _status(run) is None


def test_closed_tab_run_is_abandoned_by_the_next_start_on_the_tier(tier, learner):
    """A closed tab leaves the run started; the next start replaces it."""
    _, player = learner
    left_open = _start(player, tier)
    _submit_command(left_open)

    replacement = _start(player, tier)

    assert _status(left_open) == SESSION_STATUS_ABANDONED
    assert replacement.status == SESSION_STATUS_STARTED
    assert replacement.prior_run_id is None


def test_closed_tab_run_without_commands_is_deleted_by_the_next_start(tier, learner):
    _, player = learner
    left_open = _start(player, tier)

    _start(player, tier)

    assert _status(left_open) is None


def test_abandoned_run_is_never_resumable(tier, learner):
    _, player = learner
    run = _start(player, tier)
    _submit_command(run)
    service = AdventureLevelTierRunService()
    service.discard(run=run)

    assert service._active_run(player=player, tier=tier) is None
    # Discarding again is a no-op, not a second transition.
    assert service.discard(run=run) is False
    # A new start is a fresh run, not the abandoned one.
    fresh = _start(player, tier)
    assert fresh.id != run.id
    assert fresh.status == SESSION_STATUS_STARTED


def test_retry_from_an_abandoned_run_does_not_chain_to_it(tier, learner):
    _, player = learner
    run = _start(player, tier)
    _submit_command(run)
    AdventureLevelTierRunService().discard(run=run)
    run.refresh_from_db()

    fresh = _start(player, tier, prior_run=run)

    assert fresh.prior_run_id is None


def test_abandoned_runs_do_not_count_as_tried_variants(tier, learner):
    _, player = learner
    run = _start(player, tier)
    _submit_command(run)
    AdventureLevelTierRunService().discard(run=run)
    selector = TierVariantSelectionService()

    assert selector._tried_variant_keys(player=player, tier=tier) == set()

    AdventureLevelTierRun.objects.create(
        player=player,
        tier=tier,
        current_wave=run.current_wave,
        selected_variant=run.selected_variant,
        status=SESSION_STATUS_FAILED,
    )
    assert selector._tried_variant_keys(player=player, tier=tier) == {
        run.selected_variant.semantic_key
    }
