from django.core.management import call_command
from rest_framework.test import APIClient

from players.services import get_or_create_player
from progress.models import CoinTransaction, Wallet
from progress.wallet import WalletService
from testing.frontend_execution import frontend_execution_payload
from testing.runtime_factories import api_client_for, create_stage_readme_challenge_run


def make_user(django_user_model, username: str = "student"):
    user = django_user_model.objects.create_user(
        username=username,
        email=f"{username}@example.com",
        password="pass12345",
    )
    # Starting a challenge requires an owned companion; grant one directly so
    # these wallet tests don't have to go through the shop purchase flow.
    from shop.models import Entitlement

    Entitlement.objects.get_or_create(player=get_or_create_player(user), kind="companion", slug="blue")
    return user


def test_award_credits_balance_once_per_key(db, django_user_model):
    user = make_user(django_user_model)
    player = get_or_create_player(user)
    service = WalletService()

    assert service.award(player=player, amount=25, reason="challenge_clear", award_key="challenge-clear:1") is True
    assert service.award(player=player, amount=25, reason="challenge_clear", award_key="challenge-clear:1") is False
    assert service.award(player=player, amount=10, reason="perfect_clear", award_key="challenge-star:1") is True

    wallet = Wallet.objects.get(player=player)
    assert wallet.balance == 35
    assert CoinTransaction.objects.filter(player=player).count() == 2


def test_award_rejects_non_positive_amounts(db, django_user_model):
    user = make_user(django_user_model)
    player = get_or_create_player(user)

    assert WalletService().award(player=player, amount=0, reason="noop", award_key="noop:0") is False
    assert not Wallet.objects.filter(player=player).exists()


def test_spend_debits_balance_once_per_key(db, django_user_model):
    user = make_user(django_user_model)
    player = get_or_create_player(user)
    service = WalletService()
    service.award(player=player, amount=75, reason="seed", award_key="seed:spend")

    assert service.spend(player=player, amount=25, reason="store_purchase", award_key="purchase:1") is True
    assert service.spend(player=player, amount=25, reason="store_purchase", award_key="purchase:1") is False

    assert Wallet.objects.get(player=player).balance == 50
    assert CoinTransaction.objects.filter(player=player, amount=-25, reason="store_purchase").count() == 1


def test_wallet_endpoint_returns_balance_without_transaction_history(db, django_user_model):
    user = make_user(django_user_model)
    player = get_or_create_player(user)
    WalletService().award(player=player, amount=30, reason="adventure_pass", award_key="adventure-pass:1")
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.get("/api/progress/wallet/")

    assert response.status_code == 200
    assert response.json() == {"balance": 30}


def test_chapter_chest_awards_gitcoins_when_progress_crosses_threshold(db, django_user_model, monkeypatch):
    fixture = create_stage_readme_challenge_run(
        django_user_model,
        username="chapter-chest",
        reward_coins=0,
    )
    chapter = fixture.chapter

    # A tiny threshold guarantees this trial completion crosses it. The reward
    # schedule is a fixed runtime constant, so the test patches that constant
    # directly instead of authoring per-chapter reward data.
    import progress.chests as chests_module

    monkeypatch.setattr(chests_module, "CHEST_SCHEDULE", [{"threshold": 1, "coins": 60}])

    response = api_client_for(fixture.user).post(
        f"/api/challenge-runs/{fixture.run.id}/submit-command/",
        {
            "command": "git add README.md",
            "execution": frontend_execution_payload(
                "git add README.md",
                fixture.states.target,
                client_run_revision=0,
            ),
        },
        format="json",
    )
    assert response.status_code == 200

    fixture.run.refresh_from_db()
    assert fixture.run.status == "completed"

    transactions = CoinTransaction.objects.filter(
        player=fixture.player,
        award_key=f"chapter-chest:{chapter.id}:1",
    )
    assert transactions.count() == 1
    assert transactions.first().amount == 60
    assert transactions.first().reason == "chapter_chest"
    assert Wallet.objects.get(player=fixture.player).balance == 60


def test_chest_schedule_is_the_same_fixed_runtime_constant_for_every_chapter(db, django_user_model):
    call_command("seed_curriculum")
    from progress.chests import CHEST_SCHEDULE

    user = make_user(django_user_model, "chest-schedule-reader")
    client = APIClient()
    client.force_authenticate(user=user)
    response = client.get("/api/chapters/")

    assert response.status_code == 200
    results = response.json()
    assert results
    for chapter in results:
        assert chapter["chest_schedule"] == CHEST_SCHEDULE
