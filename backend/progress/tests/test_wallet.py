from django.core.management import call_command
from rest_framework.test import APIClient

from challenges.models import ChallengeLevel, ChallengeRun
from progress.models import CoinTransaction, Wallet
from progress.wallet import WalletService


def make_user(django_user_model, username: str = "student"):
    return django_user_model.objects.create_user(
        username=username,
        email=f"{username}@example.com",
        password="pass12345",
    )


def test_award_credits_balance_once_per_key(db, django_user_model):
    user = make_user(django_user_model)
    service = WalletService()

    assert service.award(user=user, amount=25, reason="challenge_clear", award_key="challenge-clear:1") is True
    assert service.award(user=user, amount=25, reason="challenge_clear", award_key="challenge-clear:1") is False
    assert service.award(user=user, amount=10, reason="first_attempt_star", award_key="challenge-star:1") is True

    wallet = Wallet.objects.get(user=user)
    assert wallet.balance == 35
    assert CoinTransaction.objects.filter(user=user).count() == 2


def test_award_rejects_non_positive_amounts(db, django_user_model):
    user = make_user(django_user_model)

    assert WalletService().award(user=user, amount=0, reason="noop", award_key="noop:0") is False
    assert not Wallet.objects.filter(user=user).exists()


def test_spend_debits_balance_once_per_key(db, django_user_model):
    user = make_user(django_user_model)
    service = WalletService()
    service.award(user=user, amount=75, reason="seed", award_key="seed:spend")

    assert service.spend(user=user, amount=25, reason="store_purchase", award_key="purchase:1") is True
    assert service.spend(user=user, amount=25, reason="store_purchase", award_key="purchase:1") is False

    assert Wallet.objects.get(user=user).balance == 50
    assert CoinTransaction.objects.filter(user=user, amount=-25, reason="store_purchase").count() == 1


def test_wallet_endpoint_returns_balance_and_recent(db, django_user_model):
    user = make_user(django_user_model)
    WalletService().award(user=user, amount=30, reason="adventure_pass", award_key="adventure-pass:1")
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.get("/api/progress/wallet/")

    assert response.status_code == 200
    body = response.json()
    assert body["balance"] == 30
    assert body["recent"][0]["reason"] == "adventure_pass"
    assert body["recent"][0]["amount"] == 30


def test_storey_chest_awards_gitcoins_when_progress_crosses_threshold(db, django_user_model):
    call_command("seed_curriculum_v2")
    user = make_user(django_user_model)
    level = ChallengeLevel.objects.filter(difficulty="easy", is_published=True).select_related("challenge").first()
    assert level is not None
    level.required_successful_attempts = 1
    level.save(update_fields=["required_successful_attempts"])
    storey = level.storey
    # A tiny threshold guarantees the first progress tick crosses it.
    storey.chest_rewards = [{"threshold": 1, "coins": 60}]
    storey.save(update_fields=["chest_rewards"])
    client = APIClient()
    client.force_authenticate(user=user)

    # Challenge entry is gated on passing the storey's adventure first.
    from django.utils import timezone

    from command_adventures.models import AdventureRun, CommandAdventure

    adventure = CommandAdventure.objects.filter(storey=storey, is_published=True).first()
    if adventure is not None:
        AdventureRun.objects.create(
            user=user, command_adventure=adventure, mode="primary", passed_at=timezone.now()
        )

    start = client.post(
        f"/api/challenge-levels/{level.id}/runs/",
        {"source_entry_point": "tower_page"},
        format="json",
    )
    assert start.status_code == 201
    run = ChallengeRun.objects.get(id=start.json()["id"])
    for command in run.variant.solution_commands:
        response = client.post(
            f"/api/challenge-runs/{run.id}/submit-command/",
            {"command": command},
            format="json",
        )
        assert response.status_code == 200
    run.refresh_from_db()
    assert run.status == "completed"

    transactions = CoinTransaction.objects.filter(user=user, award_key=f"storey-chest:{storey.id}:1")
    assert transactions.count() == 1
    assert transactions.first().amount == 60
    assert transactions.first().reason == "storey_chest"
    assert Wallet.objects.get(user=user).balance == 60


def test_chest_thresholds_are_seed_customizable(db):
    call_command("seed_curriculum_v2")
    from curriculum.models import DEFAULT_CHEST_REWARDS, Storey

    storey = Storey.objects.filter(is_published=True).first()
    assert storey.chest_rewards == DEFAULT_CHEST_REWARDS
