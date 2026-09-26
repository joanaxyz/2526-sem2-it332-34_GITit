"""An abandoned tier run is a started session that did not succeed.

It counts in SCR's and HLCR's started totals, its submitted commands count in
CAR, and an abandoned eligible retry is an unsuccessful RTA session. ARC
(completed runs only) and the learner retry success rate leave it out.
"""

import pytest

from adventures.models import (
    AdventureLevel,
    AdventureLevelTier,
    AdventureLevelTierRun,
    AdventureLevelTierWave,
    AdventureLevelTierWaveVariant,
)
from common.constants import (
    DIFFICULTY_HARD,
    SESSION_STATUS_ABANDONED,
    SESSION_STATUS_COMPLETED,
    SESSION_STATUS_FAILED,
)
from curriculum.models import Chapter, Story
from players.services import get_or_create_player
from practice.models import CommandStep
from progress.services import MetricsService


@pytest.fixture
def hard_tier(db):
    """Module 3 hard tier with two structurally different variants."""
    story = Story.objects.create(slug=MetricsService.PERFORMANCE_STORY_SLUG, title="Legacy")
    chapter = Chapter.objects.create(story=story, slug="m3", number=3, title="Module 3")
    level = AdventureLevel.objects.create(chapter=chapter, slug="m3-level", title="Level")
    tier = AdventureLevelTier.objects.create(adventure_level=level, difficulty=DIFFICULTY_HARD)
    wave = AdventureLevelTierWave.objects.create(tier=tier, slug="m3-hard")
    variants = {
        key: AdventureLevelTierWaveVariant.objects.create(
            wave=wave,
            slug=f"m3-{key}",
            label=key,
            semantic_key=f"m3-{key}",
            initial_state={"files": {f"{key}.txt": key}},
            target_state={"files": {f"{key}.txt": f"{key}-done"}},
        )
        for key in ("a", "b")
    }
    return tier, wave, variants


@pytest.fixture
def player(db, django_user_model):
    return get_or_create_player(
        django_user_model.objects.create_user(username="abandon-kpi", password="pass12345")
    )


def _run(player, bundle, variant, status, *, prior=None, processable=0, invalid=0):
    tier, wave, variants = bundle
    run = AdventureLevelTierRun.objects.create(
        player=player,
        tier=tier,
        current_wave=wave,
        selected_variant=variants[variant],
        prior_run=prior,
        status=status,
        retry_index=(prior.retry_index + 1) if prior else 0,
    )
    for index, ok in enumerate([True] * processable + [False] * invalid, start=1):
        CommandStep.objects.create(
            adventure_tier_run=run,
            command_text="git status" if ok else "git nonsense",
            normalized_command="git status" if ok else "git nonsense",
            result_category=(
                CommandStep.ResultCategory.TARGET_MATCHED
                if ok
                else CommandStep.ResultCategory.INVALID
            ),
            command_classification=(
                CommandStep.CommandClassification.DIAGNOSTIC
                if ok
                else CommandStep.CommandClassification.UNPROCESSABLE
            ),
            was_processable=ok,
            attempt_number=index,
        )
    return run


def _kpis(player):
    return MetricsService().performance_summary(player=player)["kpis"]


def test_abandoned_run_counts_in_scr_hlcr_and_car_but_not_arc(hard_tier, player):
    _run(player, hard_tier, "a", SESSION_STATUS_COMPLETED, processable=1)
    before = _kpis(player)

    _run(player, hard_tier, "a", SESSION_STATUS_ABANDONED, processable=1, invalid=1)
    after = _kpis(player)

    assert before["scr"] == {"value": 100.0, "numerator": 1, "denominator": 1}
    assert after["scr"] == {"value": 50.0, "numerator": 1, "denominator": 2}
    assert after["hlcr"] == {"value": 50.0, "numerator": 1, "denominator": 2}
    # Its two commands join the completed run's one: 2 processable of 3.
    assert after["car"] == {"value": 66.7, "numerator": 2, "denominator": 3}
    assert after["arc"] == before["arc"]


def test_abandoned_eligible_retry_lowers_rta_but_not_retry_success_rate(hard_tier, player):
    # One eligible retry that completed.
    failed = _run(player, hard_tier, "a", SESSION_STATUS_FAILED, processable=1)
    _run(player, hard_tier, "b", SESSION_STATUS_COMPLETED, prior=failed, processable=1)
    before = _kpis(player)

    # A second eligible retry (after a failure, structurally changed) that the
    # learner abandoned.
    failed_again = _run(player, hard_tier, "a", SESSION_STATUS_FAILED, processable=1)
    _run(player, hard_tier, "b", SESSION_STATUS_ABANDONED, prior=failed_again, processable=1)
    after = _kpis(player)

    assert before["rta"] == {"value": 100.0, "numerator": 1, "denominator": 1}
    assert after["rta"] == {"value": 50.0, "numerator": 1, "denominator": 2}
    # The learner-facing retry success rate ignores abandoned runs.
    assert before["retry_success_rate"] == {"value": 100.0, "numerator": 1, "denominator": 1}
    assert after["retry_success_rate"] == before["retry_success_rate"]
    assert after["rtr"] == after["retry_success_rate"]
