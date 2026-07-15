from django.core.management import call_command
from rest_framework.test import APIClient

from challenges.models import ChallengeTrial
from challenges.services import ChallengeRunService
from players.services import get_or_create_player
from progress.wallet import WalletService


def make_user(django_user_model, username: str = "challenger"):
    return django_user_model.objects.create_user(
        username=username,
        email=f"{username}@example.com",
        password="pass12345",
    )


def first_trial():
    return (
        ChallengeTrial.objects.filter(
            is_published=True,
            challenge_level__is_published=True,
            variants__is_published=True,
        )
        .order_by(
            "challenge_level__chapter__sort_order",
            "challenge_level__sort_order",
            "difficulty",
        )
        .distinct()
        .first()
    )


def test_starting_a_challenge_without_a_companion_is_locked(db, django_user_model, monkeypatch):
    call_command("seed_curriculum")
    monkeypatch.setattr(ChallengeRunService, "_ensure_unlocked", lambda self, **kwargs: None)
    user = make_user(django_user_model)
    trial = first_trial()
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(f"/api/challenge-trials/{trial.id}/runs/")

    assert response.status_code == 423


def test_buying_a_companion_unlocks_challenge_start(db, django_user_model, monkeypatch):
    call_command("seed_curriculum")
    monkeypatch.setattr(ChallengeRunService, "_ensure_unlocked", lambda self, **kwargs: None)
    user = make_user(django_user_model)
    player = get_or_create_player(user)
    WalletService().award(player=player, amount=150, reason="test_seed", award_key="test-seed:blue")
    trial = first_trial()
    client = APIClient()
    client.force_authenticate(user=user)

    client.post(
        "/api/shop/catalog/purchase/", {"kind": "companion", "slug": "blue"}, format="json"
    )
    response = client.post(f"/api/challenge-trials/{trial.id}/runs/")

    assert response.status_code == 201
