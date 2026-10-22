"""The adventure tier run start owes the full access gate.

The tier flow was written by copying challenges/views.py - which deliberately
requires no companion - so these pin the companion and publication checks.
"""

from django.core.management import call_command
from rest_framework.test import APIClient

from adventures.models import AdventureLevelTier
from players.services import get_or_create_player
from shop.models import Entitlement

TIER_START_BODY = {"source_entry_point": "level_page"}


def make_player(django_user_model, username="adventurer", *, companion=True):
    user = django_user_model.objects.create_user(
        username=username,
        email=f"{username}@example.com",
        password="pass12345",
    )
    player = get_or_create_player(user)
    if companion:
        Entitlement.objects.create(player=player, kind="companion", slug="blue")
    client = APIClient()
    client.force_authenticate(user=user)
    return client, player


def first_easy_tier():
    return (
        AdventureLevelTier.objects.filter(is_published=True, difficulty="easy")
        .select_related("adventure_level", "adventure_level__chapter")
        .order_by("adventure_level__sort_order", "id")
        .first()
    )


def test_tier_start_requires_a_companion(db, django_user_model):
    call_command("seed_curriculum")
    tier = first_easy_tier()
    assert tier is not None
    client, player = make_player(django_user_model, companion=False)

    response = client.post(f"/api/adventure-level-tiers/{tier.id}/runs/", TIER_START_BODY)

    assert not Entitlement.objects.filter(player=player, kind="companion").exists()
    assert response.status_code == 423


def test_tier_start_succeeds_once_a_companion_is_owned(db, django_user_model):
    call_command("seed_curriculum")
    tier = first_easy_tier()
    client, _player = make_player(django_user_model)

    response = client.post(f"/api/adventure-level-tiers/{tier.id}/runs/", TIER_START_BODY)

    assert response.status_code == 201


def test_tier_start_refuses_an_unpublished_level(db, django_user_model):
    call_command("seed_curriculum")
    tier = first_easy_tier()
    level = tier.adventure_level
    level.is_published = False
    level.save(update_fields=["is_published"])
    client, _player = make_player(django_user_model)

    response = client.post(f"/api/adventure-level-tiers/{tier.id}/runs/", TIER_START_BODY)

    assert response.status_code == 404


def test_tier_start_refuses_an_unpublished_chapter(db, django_user_model):
    call_command("seed_curriculum")
    tier = first_easy_tier()
    chapter = tier.adventure_level.chapter
    chapter.is_published = False
    chapter.save(update_fields=["is_published"])
    client, _player = make_player(django_user_model)

    response = client.post(f"/api/adventure-level-tiers/{tier.id}/runs/", TIER_START_BODY)

    assert response.status_code == 404
