from django.core.management import call_command
from rest_framework.test import APIClient

from challenges.models import ChallengeTrial
from challenges.services import ChallengeRunService
from shop.models import Entitlement


def test_starting_a_challenge_does_not_require_a_companion(
    db,
    django_user_model,
    monkeypatch,
):
    call_command("seed_curriculum")
    monkeypatch.setattr(ChallengeRunService, "_ensure_unlocked", lambda self, **kwargs: None)
    user = django_user_model.objects.create_user(
        username="repository-puzzler",
        email="repository-puzzler@example.com",
        password="pass12345",
    )
    trial = (
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
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(f"/api/challenge-trials/{trial.id}/runs/")

    assert not Entitlement.objects.filter(player__user=user, kind="companion").exists()
    assert response.status_code == 201
