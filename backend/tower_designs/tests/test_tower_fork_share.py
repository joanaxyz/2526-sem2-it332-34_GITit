"""Phase 3: private official fork + share-link behavior."""

import pytest
from django.core.management import call_command
from rest_framework.test import APIClient

from assets.models import (
    KIND_MONSTER,
    KIND_TOWER_ARTIFACT,
    KIND_TOWER_PIECE,
    TOWER_PIECE_SECTION,
    Asset,
    TowerPieceAsset,
)
from authoring.models import ContentDefinition
from command_adventures.models import CommandAdventure
from curriculum.models import Storey, Tome
from tower_designs.models import (
    ORIGIN_OFFICIAL_FORK,
    ORIGIN_PERSONAL,
    ArtifactPlacement,
    TowerDesign,
)


def make_user(django_user_model, username="builder"):
    return django_user_model.objects.create_user(
        username=username, email=f"{username}@example.com", password="pass12345"
    )


def make_section_asset() -> Asset:
    # A non-"official-*" slug so the default skeleton stays empty and the test
    # controls exactly one (bound) interactive piece.
    asset = Asset.objects.create(
        kind=KIND_TOWER_PIECE, slug="custom-section", label="Tower Section"
    )
    TowerPieceAsset.objects.create(asset=asset, piece_type=TOWER_PIECE_SECTION)
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
def test_official_fork_seeds_and_refreshes_authored_artifacts(
    django_user_model,
    settings,
    tmp_path,
):
    settings.MEDIA_ROOT = tmp_path
    call_command("seed_assets", "--skip-grant", verbosity=0)

    storey = Storey.objects.create(
        slug="official-storey",
        number=1,
        title="Official Storey",
        description="Seeded",
        is_published=True,
    )
    CommandAdventure.objects.create(
        storey=storey,
        slug="official-storey-adventure",
        title="Adventure",
        description="Seeded",
        is_published=True,
    )
    Tome.objects.create(
        storey=storey,
        slug="official-storey-tome",
        title="Tome",
        placement="above_adventure",
        pages=[],
        is_published=True,
    )
    user = make_user(django_user_model)
    client = APIClient()
    client.force_authenticate(user=user)

    first = client.post("/api/tower-designs/official-fork/")
    assert first.status_code == 201, first.content
    fork_id = first.json()["design"]["id"]
    assert {artifact["role"] for artifact in first.json()["artifacts"]} == {"adventure", "tome"}
    assert ArtifactPlacement.objects.filter(tower_design_id=fork_id).count() == 2

    ArtifactPlacement.objects.filter(tower_design_id=fork_id).delete()
    refreshed = client.post("/api/tower-designs/official-fork/")

    assert refreshed.status_code == 201, refreshed.content
    assert refreshed.json()["design"]["id"] == fork_id
    assert {artifact["role"] for artifact in refreshed.json()["artifacts"]} == {
        "adventure",
        "tome",
    }


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
    artifact = Asset.objects.create(
        kind=KIND_TOWER_ARTIFACT,
        owner=author,
        slug="custom-adventure-artifact",
        label="Adventure Artifact",
        is_published=False,
    )
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
        {"piece_asset_id": section.id, "piece_type": "section"},
        format="json",
    )
    client.post(
        f"/api/tower-designs/{design_id}/artifacts/",
        {
            "target_piece_instance_id": piece.json()["id"],
            "artifact_asset_id": artifact.id,
            "role": "adventure",
            "content_definition_id": content.id,
            "x": 20,
            "y": 12,
            "width": 40,
            "height": 64,
        },
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
