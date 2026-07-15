from django.core.management import call_command
from rest_framework.test import APIClient

from adventures.models import AdventureLevel
from players.services import get_or_create_player
from progress.wallet import WalletService


def make_user(django_user_model, username: str = "adventurer"):
    return django_user_model.objects.create_user(
        username=username,
        email=f"{username}@example.com",
        password="pass12345",
    )


def first_level():
    return (
        AdventureLevel.objects.filter(is_published=True, waves__variants__is_published=True)
        .select_related("chapter")
        .order_by("chapter__sort_order", "sort_order", "id")
        .distinct()
        .first()
    )


def two_levels_in_one_adventure():
    """The first two sequential levels of whichever published adventure has
    at least two playable levels (used to test level-order gating without
    depending on the exact shape of the seeded curriculum)."""
    adventures = AdventureLevel.objects.filter(
        is_published=True, chapter__is_published=True
    ).order_by("chapter__sort_order", "sort_order", "id")
    for adventure in adventures:
        levels = list(
            AdventureLevel.objects.filter(
                chapter_id=adventure.chapter_id,
                is_published=True,
                waves__variants__is_published=True,
            )
            .order_by("sort_order", "id")
            .distinct()
        )
        if len(levels) >= 2:
            return levels[0], levels[1]
    return None, None


def _authenticated_client_with_companion(django_user_model, username: str = "adventurer"):
    user = make_user(django_user_model, username)
    player = get_or_create_player(user)
    WalletService().award(player=player, amount=150, reason="test_seed", award_key=f"test-seed:{username}")
    client = APIClient()
    client.force_authenticate(user=user)
    client.post("/api/shop/catalog/purchase/", {"kind": "companion", "slug": "blue"}, format="json")
    return client, player


def test_starting_an_adventure_without_a_companion_is_locked(db, django_user_model):
    call_command("seed_curriculum")
    user = make_user(django_user_model)
    level = first_level()
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(f"/api/adventure-levels/{level.id}/runs/")

    assert response.status_code == 423


def test_buying_a_companion_unlocks_adventure_start(db, django_user_model):
    call_command("seed_curriculum")
    user = make_user(django_user_model)
    player = get_or_create_player(user)
    WalletService().award(player=player, amount=150, reason="test_seed", award_key="test-seed:blue")
    level = first_level()
    client = APIClient()
    client.force_authenticate(user=user)

    client.post(
        "/api/shop/catalog/purchase/", {"kind": "companion", "slug": "blue"}, format="json"
    )
    response = client.post(f"/api/adventure-levels/{level.id}/runs/")

    assert response.status_code == 201


def test_starting_a_later_level_before_the_previous_one_is_locked(db, django_user_model):
    call_command("seed_curriculum")
    first, second = two_levels_in_one_adventure()
    assert first is not None and second is not None
    client, _player = _authenticated_client_with_companion(django_user_model)

    response = client.post(f"/api/adventure-levels/{second.id}/runs/")

    assert response.status_code == 423


def test_completing_the_previous_level_unlocks_the_next_one(db, django_user_model):
    call_command("seed_curriculum")
    first, second = two_levels_in_one_adventure()
    assert first is not None and second is not None
    client, player = _authenticated_client_with_companion(django_user_model)

    from progress.models import AdventureLevelCompletion

    AdventureLevelCompletion.objects.create(player=player, adventure_level=first)

    response = client.post(f"/api/adventure-levels/{second.id}/runs/")

    assert response.status_code == 201
