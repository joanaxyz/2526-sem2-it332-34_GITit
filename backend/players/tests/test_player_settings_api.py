from rest_framework import status
from rest_framework.test import APIClient

from players.models import PlayerPreferences
from players.services import get_or_create_player
from shop.models import Entitlement, PlayerLoadout


def make_user(django_user_model, username="settingsuser"):
    return django_user_model.objects.create_user(
        username=username,
        email=f"{username}@example.com",
        password="Password123!",
    )


def authenticated_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def test_preferences_are_created_with_defaults_and_can_be_updated(db, django_user_model):
    user = make_user(django_user_model)
    client = authenticated_client(user)

    response = client.get("/api/player/preferences/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"motion_mode": "system"}
    player = get_or_create_player(user)
    assert PlayerPreferences.objects.filter(player=player).exists()

    updated = client.patch(
        "/api/player/preferences/",
        {"motion_mode": "reduced"},
        format="json",
    )

    assert updated.status_code == status.HTTP_200_OK
    assert updated.json() == {"motion_mode": "reduced"}
    record = PlayerPreferences.objects.get(player=player)
    assert record.motion_mode == "reduced"


def test_preferences_reject_unknown_choice(db, django_user_model):
    user = make_user(django_user_model, username="badpreference")
    client = authenticated_client(user)

    response = client.patch(
        "/api/player/preferences/",
        {"motion_mode": "fast"},
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_owned_companion_can_be_equipped_from_player_loadout_endpoint(db, django_user_model):
    user = make_user(django_user_model, username="loadoutuser")
    player = get_or_create_player(user)
    Entitlement.objects.create(player=player, kind="companion", slug="black")
    client = authenticated_client(user)

    response = client.post(
        "/api/player/loadout/companion/",
        {"kind": "companion", "slug": "black"},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["active_companion"] == "black"
    assert response.json()["shop"]["active_companion"] == "black"
    assert PlayerLoadout.objects.get(player=player).active_companion_slug == "black"


def test_unowned_companion_cannot_be_equipped_from_player_loadout_endpoint(db, django_user_model):
    user = make_user(django_user_model, username="unownedloadout")
    client = authenticated_client(user)

    response = client.post(
        "/api/player/loadout/companion/",
        {"kind": "companion", "slug": "black"},
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
