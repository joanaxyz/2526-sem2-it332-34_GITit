from types import SimpleNamespace

import pytest
from adventures.models import AdventureLevelTierProgress
from adventures.scoring import star_breakdown, stars
from adventures.services import AdventureLevelTierRunService
from challenges.services import ChallengeRunService
from progress.models import (
    AdventureLevelTierCompletion,
    ChallengeTrialCompletion,
    CoinTransaction,
)
from testing.frontend_execution import frontend_execution_payload
from testing.runtime_factories import (
    api_client_for,
    create_stage_readme_challenge_run,
    create_stage_readme_tier_run,
)


@pytest.mark.parametrize(
    "solved,counted,budget,retry_count,expected",
    [
        (False, 0, 2, 0, 0),
        (True, 1, 2, 0, 3),
        (True, 2, 2, 1, 3),
        (True, 2, 2, 2, 2),
        (True, 2, 2, 3, 2),
        (True, 3, 2, 0, 1),
        (True, 3, 2, 1, 1),
        (True, 3, 2, 2, 1),
    ],
)
def test_star_grades_follow_the_command_target(solved, counted, budget, retry_count, expected):
    assert (
        stars(solved=solved, counted_commands=counted, budget=budget, retry_count=retry_count)
        == expected
    )


@pytest.mark.parametrize(
    "status,counted,retries,grade,available,states,reasons",
    [
        ("started", 0, 0, 0, 3, ["pending"] * 3, [None] * 3),
        (
            "started",
            3,
            0,
            0,
            1,
            ["pending", "missed", "missed"],
            [None, "command_target_exceeded", "command_target_exceeded"],
        ),
        ("completed", 2, 1, 3, 3, ["earned"] * 3, [None] * 3),
        (
            "completed",
            2,
            2,
            2,
            2,
            ["earned", "earned", "missed"],
            [None, None, "retry_allowance_exceeded"],
        ),
        (
            "completed",
            3,
            0,
            1,
            1,
            ["earned", "missed", "missed"],
            [None, "command_target_exceeded", "command_target_exceeded"],
        ),
        ("failed", 0, 0, 0, 0, ["missed"] * 3, ["not_cleared"] * 3),
        ("abandoned", 1, 0, 0, 0, ["missed"] * 3, ["not_cleared"] * 3),
    ],
)
def test_breakdown_explains_every_awarded_and_available_star(
    status, counted, retries, grade, available, states, reasons
):
    run = SimpleNamespace(
        status=status,
        stars=grade,
        counted_action_total=counted,
        min_counted_commands=2,
        retry_index=retries,
    )
    result = star_breakdown(run)
    assert result == {
        "stars": grade,
        "available_stars": available,
        "counted_commands": counted,
        "command_target": 2,
        "retry_count": retries,
        "graded_under_previous_rules": False,
        "criteria": [
            {"key": key, "state": state, "reason": reason}
            for key, state, reason in zip(
                ("clear", "command_target", "retry_allowance"), states, reasons, strict=True
            )
        ],
    }


def test_transfer_checkpoints_have_no_star_breakdown():
    assert star_breakdown(SimpleNamespace(is_transfer=True)) is None


def test_historical_grade_does_not_fabricate_a_retry_penalty():
    result = star_breakdown(
        SimpleNamespace(
            status="completed",
            stars=2,
            counted_action_total=2,
            min_counted_commands=2,
            retry_index=1,
        )
    )
    assert result["stars"] == 2
    assert result["graded_under_previous_rules"] is True
    assert result["criteria"][-1]["reason"] == "previous_scoring_rules"


@pytest.fixture(params=["tier", "challenge"])
def grading_lane(request, db, django_user_model):
    lane = request.param
    if lane == "challenge":
        fixture = create_stage_readme_challenge_run(django_user_model, reward_coins=25)
        owner = fixture.trial
        run = fixture.run
        completion_model = ChallengeTrialCompletion
        endpoint = "challenge-runs"

        def start(prior=None):
            return ChallengeRunService().start_run(
                player=fixture.player, trial=owner, source_entry_point="level_page", prior_run=prior
            )

    else:
        fixture = create_stage_readme_tier_run(django_user_model)
        owner = fixture.tier
        run = fixture.run
        completion_model = AdventureLevelTierCompletion
        endpoint = "adventure-tier-runs"

        def start(prior=None):
            return AdventureLevelTierRunService().start_run(
                player=fixture.player, tier=owner, source_entry_point="level_page", prior_run=prior
            )

    run.scoring_policy_version = 2
    run.generous_counted_commands = 2
    run.example_counted_commands = 1
    run.save(
        update_fields=[
            "scoring_policy_version",
            "generous_counted_commands",
            "example_counted_commands",
        ]
    )
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
                client_run_revision=run.total_attempts,
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
    assert context.run.stars == 2
    assert _score_snapshot(context)[:2] == (2, 2)
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

    assert replay.stars == 2
    assert _score_snapshot(context) == best


@pytest.mark.parametrize("retry_count,expected", [(1, 3), (2, 3), (3, 3)])
def test_retry_allowance_and_fresh_replay_grades(grading_lane, retry_count, expected):
    context = grading_lane
    failed = context.run
    for _ in range(retry_count):
        for _ in range(3):
            _submit(context, failed, "git nope")
        assert failed.status == "failed"
        retry = context.start(failed)
        failed = retry

    _submit(context, retry, "git add README.md")
    assert retry.stars == expected
    assert _score_snapshot(context)[:2] == (expected, 1)
    transactions = list(CoinTransaction.objects.values_list("id", "amount", "award_key"))

    replay = context.start(retry)
    _submit(context, replay, "git add README.md")
    assert replay.stars == 3
    assert _score_snapshot(context)[:2] == (3, 1)
    assert list(CoinTransaction.objects.values_list("id", "amount", "award_key")) == transactions


@pytest.mark.parametrize("grading_lane", ["tier", "challenge"], indirect=True)
def test_better_grade_replay_keeps_the_lower_command_total(grading_lane):
    context = grading_lane
    _submit(context, context.run, "git nope")
    _submit(context, context.run, "git nope")
    _submit(context, context.run, "git add README.md")
    assert _score_snapshot(context)[:2] == (1, 3)

    replay = context.start(context.run)
    _submit(context, replay, "git nope")
    _submit(context, replay, "git add README.md")

    assert _score_snapshot(context)[:2] == (2, 2)


@pytest.mark.parametrize("launch", ["direct", "retry", "stale_prior"])
def test_retry_grading_cannot_be_reset_by_the_launch_path(grading_lane, launch):
    context = grading_lane
    first = failed = context.run
    for _ in range(2):
        for _ in range(3):
            _submit(context, failed, "git nope")
        assert failed.status == "failed"
        prior = None if launch == "direct" else first if launch == "stale_prior" else failed
        failed = context.start(prior)

    assert failed.retry_index == 2
    payload = _submit(context, failed, "git add README.md")["run"]
    assert payload["stars"] == 3
    assert payload["star_breakdown"]["retry_count"] == 2
    assert payload["star_breakdown"]["criteria"][-1] == {
        "key": "efficient_target",
        "state": "earned",
        "reason": None,
    }


def test_full_and_command_payloads_explain_the_same_verified_grade(grading_lane):
    context = grading_lane
    for command in ("git status", "git nope", "git add README.md"):
        submitted = _submit(context, context.run, command)["run"]
        response = context.client.get(f"/api/{context.endpoint}/{context.run.id}/")
        assert response.status_code == 200, response.content
        assert response.json()["star_breakdown"] == submitted["star_breakdown"]
        breakdown = submitted["star_breakdown"]
        assert breakdown["stars"] == submitted["stars"]
        assert sum(c["state"] == "earned" for c in breakdown["criteria"]) == submitted["stars"]
        assert breakdown["counted_commands"] == submitted["counts"]["counted_action_total"]


@pytest.mark.parametrize("exit_first", [False, True])
def test_restarting_a_submitted_attempt_preserves_retry_evidence(grading_lane, exit_first):
    context = grading_lane
    run = context.run
    for _ in range(2):
        _submit(context, run, "git status")
        if exit_first:
            response = context.client.delete(f"/api/{context.endpoint}/{run.id}/")
            assert response.status_code == 204
        next_run = context.start(None if exit_first else run)
        run.refresh_from_db()
        assert run.status == "abandoned"
        run = next_run
    assert run.retry_index == 2
    _submit(context, run, "git add README.md")
    assert run.stars == 3


def test_empty_restarts_do_not_consume_retry_allowance(grading_lane):
    context = grading_lane
    run = context.run
    for _ in range(3):
        run = context.start(run)
    assert run.retry_index == 0


def test_empty_replay_restarts_do_not_consume_retry_allowance(grading_lane):
    context = grading_lane
    _submit(context, context.run, "git add README.md")
    replay = context.start(context.run)
    for _ in range(3):
        replay = context.start(replay)
    assert replay.retry_index == 0
    _submit(context, replay, "git add README.md")
    assert replay.stars == 3


def test_direct_replay_starts_fresh_without_repeating_rewards(grading_lane):
    context = grading_lane
    _submit(context, context.run, "git add README.md")
    best = _score_snapshot(context)
    transactions = list(CoinTransaction.objects.values_list("id", "amount", "award_key"))
    replay = context.start(context.run)
    for _ in range(3):
        _submit(context, replay, "git nope")
    assert replay.status == "failed"
    fresh = context.start()
    assert fresh.retry_index == 0
    _submit(context, fresh, "git add README.md")
    assert fresh.stars == 3
    assert _score_snapshot(context) == best
    assert list(CoinTransaction.objects.values_list("id", "amount", "award_key")) == transactions
