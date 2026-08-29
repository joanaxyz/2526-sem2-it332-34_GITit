from __future__ import annotations

from django.db.models import Sum

from adventures.services import AdventureRunService
from challenges.models import ChallengeRun
from common.constants import SESSION_STATUS_COMPLETED
from progress.models import CoinTransaction, Wallet
from testing.frontend_execution import frontend_execution_payload
from testing.runtime_factories import (
    api_client_for,
    create_stage_readme_adventure_run,
    create_stage_readme_challenge_run,
)


def _submit_challenge_add_readme(*, user, run, target):
    return api_client_for(user).post(
        f"/api/challenge-runs/{run.id}/submit-command/",
        {
            "command": "git add README.md",
            "execution": frontend_execution_payload(
                "git add README.md",
                target,
                client_run_revision=0,
            ),
        },
        format="json",
    )


def _submit_adventure_add_readme(*, user, run, target):
    return api_client_for(user).post(
        f"/api/adventure-runs/{run.id}/submit-command/",
        {
            "command": "git add README.md",
            "execution": frontend_execution_payload(
                "git add README.md",
                target,
                client_run_revision=0,
            ),
        },
        format="json",
    )


def test_challenge_trial_reward_is_paid_once_per_player_and_trial(db, django_user_model):
    fixture = create_stage_readme_challenge_run(
        django_user_model,
        username="challenge-reward",
        reward_coins=40,
    )

    starting_balance = Wallet.objects.get_or_create(player=fixture.player)[0].balance

    response = _submit_challenge_add_readme(
        user=fixture.user,
        run=fixture.run,
        target=fixture.states.target,
    )
    assert response.status_code == 200
    fixture.run.refresh_from_db()
    assert fixture.run.status == SESSION_STATUS_COMPLETED

    retry = ChallengeRun.objects.create(
        player=fixture.player,
        challenge_trial=fixture.trial,
        selected_variant=fixture.variant,
        source_entry_point="reward_idempotency_test",
        min_counted_commands=fixture.trial.min_counted_commands,
        max_counted_commands=fixture.trial.max_counted_commands,
        repository_state=fixture.states.initial,
    )
    response = _submit_challenge_add_readme(
        user=fixture.user,
        run=retry,
        target=fixture.states.target,
    )
    assert response.status_code == 200
    retry.refresh_from_db()
    assert retry.status == SESSION_STATUS_COMPLETED

    award_key = f"trial-reward:{fixture.trial.id}"
    award_transactions = CoinTransaction.objects.filter(player=fixture.player, award_key=award_key)
    assert award_transactions.count() == 1
    assert award_transactions.aggregate(total=Sum("amount"))["total"] == 40
    assert Wallet.objects.get(player=fixture.player).balance >= starting_balance + 40


def test_adventure_level_reward_is_paid_once_even_after_replay(db, django_user_model):
    fixture = create_stage_readme_adventure_run(
        django_user_model,
        username="adventure-reward",
        reward_coins=55,
    )

    starting_balance = Wallet.objects.get_or_create(player=fixture.player)[0].balance

    response = _submit_adventure_add_readme(
        user=fixture.user,
        run=fixture.run,
        target=fixture.states.target,
    )
    assert response.status_code == 200
    fixture.run.refresh_from_db()
    assert fixture.run.status == SESSION_STATUS_COMPLETED

    replay = AdventureRunService().start_run(player=fixture.player, level=fixture.level)
    assert replay.is_replay is True
    response = _submit_adventure_add_readme(
        user=fixture.user,
        run=replay,
        target=fixture.states.target,
    )
    assert response.status_code == 200
    replay.refresh_from_db()
    assert replay.status == SESSION_STATUS_COMPLETED

    award_key = f"adventure-level-reward:{fixture.level.id}"
    award_transactions = CoinTransaction.objects.filter(player=fixture.player, award_key=award_key)
    assert award_transactions.count() == 1
    assert award_transactions.aggregate(total=Sum("amount"))["total"] == 55
    assert Wallet.objects.get(player=fixture.player).balance >= starting_balance + 55
