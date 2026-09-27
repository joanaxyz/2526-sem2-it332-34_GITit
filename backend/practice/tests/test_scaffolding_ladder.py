"""The fading-scaffold ladder is a constant, not authored content.

Easy shows everything, medium drops the Expected State diagram, hard drops the
contextual feedback as well. These assertions are the contract: the ladder is
owned in one place and every gameplay surface reads it from there.
"""

from __future__ import annotations

import pytest

from challenges.payloads import challenge_run_payload
from challenges.services.command_processing import (
    _uses_contextual_feedback,
    _visible_target_state,
)
from common.constants import DIFFICULTY_EASY, DIFFICULTY_HARD, DIFFICULTY_MEDIUM
from practice.services.scaffolding import ScaffoldingService
from testing.runtime_factories import create_stage_readme_challenge_run

EXPECTED_LADDER = {
    DIFFICULTY_EASY: {"live_dag": True, "expected_state": True, "contextual_feedback": True},
    DIFFICULTY_MEDIUM: {"live_dag": True, "expected_state": False, "contextual_feedback": True},
    DIFFICULTY_HARD: {"live_dag": True, "expected_state": False, "contextual_feedback": False},
}


@pytest.mark.parametrize("difficulty", sorted(EXPECTED_LADDER))
def test_supports_follow_the_constant_ladder(difficulty):
    assert ScaffoldingService().supports_for(difficulty) == EXPECTED_LADDER[difficulty]


def test_unknown_difficulty_falls_back_to_the_least_support():
    assert ScaffoldingService().supports_for("") == EXPECTED_LADDER[DIFFICULTY_HARD]


def test_guided_adventure_runs_sit_outside_the_ladder():
    supports = ScaffoldingService().guided_supports()
    assert supports == {
        "live_dag": True,
        "expected_state": False,
        "contextual_feedback": False,
    }


@pytest.mark.parametrize("difficulty", sorted(EXPECTED_LADDER))
def test_command_processing_reads_the_same_ladder(db, django_user_model, difficulty):
    fixture = create_stage_readme_challenge_run(
        django_user_model, username=f"ladder-processing-{difficulty}"
    )
    run = fixture.run
    run.challenge_trial.difficulty = difficulty
    run.challenge_trial.save(update_fields=["difficulty"])
    run.refresh_from_db()

    expected = EXPECTED_LADDER[difficulty]
    assert _uses_contextual_feedback(run) is expected["contextual_feedback"]
    assert (_visible_target_state(run) is not None) is expected["expected_state"]


@pytest.mark.parametrize("difficulty", sorted(EXPECTED_LADDER))
def test_run_payload_exposes_the_expected_state_only_where_the_ladder_allows(
    db, django_user_model, difficulty
):
    fixture = create_stage_readme_challenge_run(
        django_user_model, username=f"ladder-payload-{difficulty}"
    )
    run = fixture.run
    run.challenge_trial.difficulty = difficulty
    run.challenge_trial.save(update_fields=["difficulty"])
    run.refresh_from_db()

    payload = challenge_run_payload(run, include_steps=False)
    expected = EXPECTED_LADDER[difficulty]

    assert payload["scaffolding"] == expected
    # The frontend renders the Expected State panel only when the flag and the
    # snapshot are both present, so a populated target is part of the contract.
    assert (payload["expected_state"] is not None) is expected["expected_state"]


def _tier_run(django_user_model, difficulty: str):
    """Minimal published tier run with a populated target state."""
    from adventures.models import (
        AdventureLevel,
        AdventureLevelTier,
        AdventureLevelTierRun,
        AdventureLevelTierWave,
        AdventureLevelTierWaveVariant,
    )
    from curriculum.models import Chapter, Story
    from players.services import get_or_create_player
    from testing.runtime_factories import stage_readme_states

    user = django_user_model.objects.create_user(
        username=f"ladder-tier-{difficulty}", password="test-pass"
    )
    player = get_or_create_player(user)
    story = Story.objects.create(slug=f"ladder-{difficulty}", title="Ladder")
    chapter = Chapter.objects.create(
        story=story, slug=f"ladder-{difficulty}", number=1, title="Ladder"
    )
    level = AdventureLevel.objects.create(
        chapter=chapter, slug=f"ladder-{difficulty}", title="Ladder"
    )
    tier = AdventureLevelTier.objects.create(adventure_level=level, difficulty=difficulty)
    wave = AdventureLevelTierWave.objects.create(
        tier=tier, slug=f"ladder-{difficulty}", max_counted_commands=8
    )
    states = stage_readme_states()
    variant = AdventureLevelTierWaveVariant.objects.create(
        wave=wave,
        slug=f"ladder-{difficulty}",
        label="Ladder",
        initial_state=states.initial,
        target_state=states.target,
        evaluation_spec={"completion_policy": {"mode": "state_hash"}},
        solution_commands=["git add README.md"],
    )
    return AdventureLevelTierRun.objects.create(
        player=player,
        tier=tier,
        current_wave=wave,
        selected_variant=variant,
        repository_state=states.initial,
        max_counted_commands=8,
    )


@pytest.mark.parametrize("difficulty", sorted(EXPECTED_LADDER))
def test_tier_payload_follows_the_same_ladder(db, django_user_model, difficulty):
    from adventures.services.tier_command_processing import (
        _uses_contextual_feedback as tier_uses_contextual_feedback,
    )
    from adventures.services.tier_command_processing import (
        _visible_target_state as tier_visible_target_state,
    )
    from adventures.tier_payloads import tier_run_payload

    run = _tier_run(django_user_model, difficulty)
    expected = EXPECTED_LADDER[difficulty]

    payload = tier_run_payload(run, include_steps=False)
    assert payload["scaffolding"] == expected
    assert (payload["expected_state"] is not None) is expected["expected_state"]
    assert tier_uses_contextual_feedback(run) is expected["contextual_feedback"]
    assert (tier_visible_target_state(run) is not None) is expected["expected_state"]


def test_guided_adventure_payload_is_not_difficulty_tiered(db, django_user_model):
    from adventures.payloads import attempt_payload
    from testing.runtime_factories import create_stage_readme_adventure_run

    fixture = create_stage_readme_adventure_run(django_user_model, username="ladder-guided")
    payload = attempt_payload(fixture.run, include_steps=False)
    assert payload["scaffolding"] == ScaffoldingService().guided_supports()
