"""Phase 3: private official fork + share-link behavior."""

import pytest
from rest_framework.test import APIClient

from assets.models import (
    KIND_MONSTER,
    KIND_TOWER_PIECE,
    TOWER_PIECE_ADVENTURE_SECTION,
    Asset,
    TowerPieceAsset,
)
from authoring.models import ContentDefinition
from tower_designs.models import ORIGIN_OFFICIAL_FORK, ORIGIN_PERSONAL, TowerDesign


def make_user(django_user_model, username="builder"):
    return django_user_model.objects.create_user(
        username=username, email=f"{username}@example.com", password="pass12345"
    )


def make_section_asset() -> Asset:
    # A non-"official-*" slug so the default skeleton stays empty and the test
    # controls exactly one (bound) interactive piece.
    asset = Asset.objects.create(
        kind=KIND_TOWER_PIECE, slug="custom-adventure-section", label="Adventure Section"
    )
    TowerPieceAsset.objects.create(asset=asset, piece_type=TOWER_PIECE_ADVENTURE_SECTION)
    return asset


@pytest.mark.django_db
def test_official_fork_is_idempotent_and_coexists_with_personal(django_user_model):
    user = make_user(django_user_model)
    client = APIClient()
    client.force_authenticate(user=user)

    first = client.post("/api/tower-designs/official-fork/")
    assert first.status_code == 201
    fork_id = first.json()["design"]["id"]
    assert first.json()["design"]["origin"] == ORIGIN_OFFICIAL_FORK

    again = client.post("/api/tower-designs/official-fork/")
    assert again.json()["design"]["id"] == fork_id  # idempotent

    # A personal tower can still be created alongside the fork (per-origin cap).
    personal = client.post("/api/tower-designs/", {"slug": "mine", "title": "Mine"}, format="json")
    assert personal.status_code == 201
    assert personal.json()["origin"] == ORIGIN_PERSONAL
    assert TowerDesign.objects.filter(owner=user).count() == 2


@pytest.mark.django_db
def test_official_fork_cannot_be_published_or_shared(django_user_model):
    user = make_user(django_user_model)
    client = APIClient()
    client.force_authenticate(user=user)
    fork_id = client.post("/api/tower-designs/official-fork/").json()["design"]["id"]

    publish = client.post(f"/api/tower-designs/{fork_id}/publish/")
    assert publish.status_code == 400
    share = client.post(f"/api/tower-designs/{fork_id}/share/")
    assert share.status_code == 400


@pytest.mark.django_db
def test_share_publishes_monster_and_serves_public_overview(django_user_model):
    author = make_user(django_user_model, "author")
    section = make_section_asset()
    monster = Asset.objects.create(
        kind=KIND_MONSTER, owner=author, slug="pet-slime", label="Pet Slime", is_published=False
    )
    content = ContentDefinition.objects.create(
        owner=author,
        kind="adventure",
        status="published",
        slug="pet-adventure",
        title="Pet Adventure",
        definition={
            "levels": [
                {
                    "slug": "s",
                    "title": "S",
                    "solution_commands": ["git status"],
                    "encounter_spec": [{"species": "pet-slime", "hp": 1}],
                }
            ]
        },
    )

    client = APIClient()
    client.force_authenticate(user=author)
    design_id = client.post("/api/tower-designs/", {"slug": "mine", "title": "Mine"}, format="json").json()["id"]
    piece = client.post(
        f"/api/tower-designs/{design_id}/pieces/",
        {"piece_asset_id": section.id, "piece_type": "adventure_section"},
        format="json",
    )
    client.post(
        f"/api/tower-designs/{design_id}/bindings/",
        {"piece_instance_id": piece.json()["id"], "content_definition_id": content.id},
        format="json",
    )

    share = client.post(f"/api/tower-designs/{design_id}/share/")
    assert share.status_code == 200, share.content
    assert share.json()["visibility"] == "public"
    assert share.json()["share_path"] == f"/tower/shared/{design_id}"

    monster.refresh_from_db()
    assert monster.is_published is True
    assert monster.visibility == "public"

    # Anyone (even anonymous) can read the shared overview.
    anon = APIClient()
    overview = anon.get(f"/api/tower-designs/shared/{design_id}/")
    assert overview.status_code == 200
    assert overview.json()["design"]["id"] == design_id


@pytest.mark.django_db
def test_unshared_tower_is_not_publicly_visible(django_user_model):
    author = make_user(django_user_model, "author")
    design = TowerDesign.objects.create(owner=author, slug="secret", title="Secret")

    anon = APIClient()
    response = anon.get(f"/api/tower-designs/shared/{design.id}/")
    assert response.status_code == 404
