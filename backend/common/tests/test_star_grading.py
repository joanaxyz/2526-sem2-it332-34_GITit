from types import SimpleNamespace

import pytest

from adventures.models import (
    AdventureLevelTier,
    AdventureLevelTierProgress,
    AdventureLevelTierWave,
    AdventureLevelTierWaveVariant,
)
from adventures.scoring import stars
from adventures.services import AdventureLevelTierRunService, AdventureRunService
from challenges.services import ChallengeRunService
from progress.models import (
    AdventureLevelCompletion,
    AdventureLevelTierCompletion,
    ChallengeTrialCompletion,
    CoinTransaction,
)
from testing.frontend_execution import frontend_execution_payload
from testing.runtime_factories import (
    api_client_for,
    create_stage_readme_adventure_run,
    create_stage_readme_challenge_run,
)


@pytest.mark.parametrize(
    "solved,counted,budget,first_try,expected",
    [
        (False, 0, 2, True, 0),
        (True, 1, 2, True, 3),
        (True, 2, 2, True, 3),
        (True, 2, 2, False, 2),
        (True, 3, 2, True, 1),
        (True, 3, 2, False, 1),
    ],
)
def test_star_grades_follow_the_command_target(solved, counted, budget, first_try, expected):
    assert (
        stars(solved=solved, counted_commands=counted, budget=budget, first_try=first_try)
        == expected
    )


@pytest.fixture(params=["adventure", "tier", "challenge"])
def grading_lane(request, db, django_user_model):
    lane = request.param
    factory = (
        create_stage_readme_challenge_run
        if lane == "challenge"
        else create_stage_readme_adventure_run
    )
    fixture = factory(django_user_model, reward_coins=25)
    if lane == "challenge":
        owner = fixture.trial
        run = fixture.run
        completion_model = ChallengeTrialCompletion
        endpoint = "challenge-runs"

        def start(prior=None):
            return ChallengeRunService().start_run(
                player=fixture.player, trial=owner, source_entry_point="level_page", prior_run=prior
            )

    elif lane == "tier":
        fixture.run.delete()
        owner = AdventureLevelTier.objects.create(adventure_level=fixture.level, difficulty="easy")
        wave = AdventureLevelTierWave.objects.create(
            tier=owner, slug="grading", min_counted_commands=1, max_counted_commands=3
        )
        AdventureLevelTierWaveVariant.objects.create(
            wave=wave,
            slug="grading",
            initial_state=fixture.states.initial,
            target_state=fixture.states.target,
            evaluation_spec={"completion_policy": {"mode": "state_hash"}},
            solution_commands=["git add README.md"],
        )
        completion_model = AdventureLevelTierCompletion
        endpoint = "adventure-tier-runs"

        def start(prior=None):
            return AdventureLevelTierRunService().start_run(
                player=fixture.player, tier=owner, source_entry_point="level_page", prior_run=prior
            )

        run = start()
    else:
        owner = fixture.level
        run = fixture.run
        completion_model = AdventureLevelCompletion
        endpoint = "adventure-runs"

        def start(prior=None):
            return AdventureRunService().start_run(player=fixture.player, level=owner)

    return SimpleNamespace(
        lane=lane,
        fixture=fixture,
        owner=owner,
        run=run,
        start=start,
        endpoint=endpoint,
        completion_model=completion_model,
        client=api_client_for(fixture.user),
    )


def _submit(context, run, command):
    solving = command == "git add README.md"
    diagnostic = command == "git status"
    response = context.client.post(
        f"/api/{context.endpoint}/{run.id}/submit-command/",
        {
            "command": command,
            "execution": frontend_execution_payload(
                command,
                context.fixture.states.target if solving else run.repository_state,
                processed=solving or diagnostic,
                diagnostic=diagnostic,
                exit_code=0 if solving or diagnostic else 129,
                client_run_revision=(
                    run.command_count if context.lane == "adventure" else run.total_attempts
                ),
            ),
        },
        format="json",
    )
    assert response.status_code == 200, response.content
    run.refresh_from_db()
    return response.json()


def _score_snapshot(context):
    completion = context.completion_model.objects.get(player=context.fixture.player)
    return completion.stars, completion.counted_action_total, completion.completed_at


@pytest.mark.parametrize("use_play_again", [False, True])
def test_better_replay_updates_saved_grade_without_repeating_rewards(grading_lane, use_play_again):
    context = grading_lane
    _submit(context, context.run, "git nope")
    _submit(context, context.run, "git add README.md")
    assert context.run.stars == 1
    assert _score_snapshot(context)[:2] == (1, 2)
    transactions = list(CoinTransaction.objects.values_list("id", "amount", "award_key"))
    assert transactions

    replay = context.start(context.run if use_play_again else None)
    assert replay.is_replay is True
    _submit(context, replay, "git status")
    _submit(context, replay, "git add README.md")

    assert replay.stars == 3
    assert _score_snapshot(context)[:2] == (3, 1)
    assert list(CoinTransaction.objects.values_list("id", "amount", "award_key")) == transactions
    if context.lane == "tier":
        assert AdventureLevelTierProgress.objects.get(tier=context.owner).successful_clears == 1


def test_worse_replay_keeps_the_best_saved_grade(grading_lane):
    context = grading_lane
    _submit(context, context.run, "git add README.md")
    best = _score_snapshot(context)
    assert best[:2] == (3, 1)

    replay = context.start()
    _submit(context, replay, "git nope")
    _submit(context, replay, "git add README.md")

    assert replay.stars == 1
    assert _score_snapshot(context) == best


def test_retry_after_failure_earns_two_stars_then_play_again_can_improve_it(grading_lane):
    context = grading_lane
    for _ in range(3):
        _submit(context, context.run, "git nope")
    assert context.run.status == "failed"

    retry = context.start(context.run)
    _submit(context, retry, "git add README.md")
    assert retry.stars == 2
    assert _score_snapshot(context)[:2] == (2, 1)

    replay = context.start(retry)
    _submit(context, replay, "git add README.md")
    assert replay.stars == 3
    assert _score_snapshot(context)[:2] == (3, 1)


@pytest.mark.parametrize("grading_lane", ["tier", "challenge"], indirect=True)
def test_same_grade_replay_keeps_the_lower_command_total(grading_lane):
    context = grading_lane
    _submit(context, context.run, "git nope")
    _submit(context, context.run, "git nope")
    _submit(context, context.run, "git add README.md")
    assert _score_snapshot(context)[:2] == (1, 3)

    replay = context.start(context.run)
    _submit(context, replay, "git nope")
    _submit(context, replay, "git add README.md")

    assert _score_snapshot(context)[:2] == (1, 2)
