import pytest
from django.core.exceptions import ValidationError
from rest_framework.test import APIClient

from assets.models import (
    KIND_TOWER_ARTIFACT,
    KIND_TOWER_PIECE,
    TOWER_PIECE_SECTION,
    Asset,
    TowerPieceAsset,
)
from authoring.models import ContentDefinition
from tower_designs.models import ArtifactPlacement, TowerDesign, TowerPieceInstance


def make_user(django_user_model, username="student"):
    return django_user_model.objects.create_user(
        username=username,
        email=f"{username}@example.com",
        password="pass12345",
    )


@pytest.mark.django_db
def test_user_can_create_bind_and_fetch_active_tower(django_user_model):
    user = make_user(django_user_model)
    piece_asset = Asset.objects.create(
        kind=KIND_TOWER_PIECE,
        slug="official-section-test",
        label="Tower Section",
    )
    TowerPieceAsset.objects.create(asset=piece_asset, piece_type=TOWER_PIECE_SECTION)
    artifact_asset = Asset.objects.create(
        kind=KIND_TOWER_ARTIFACT,
        slug="official-adventure-artifact-test",
        label="Adventure Artifact",
    )
    content = ContentDefinition.objects.create(
        owner=user,
        kind="adventure",
        status="published",
        slug="adventure",
        title="Adventure",
        definition={"levels": []},
    )
    client = APIClient()
    client.force_authenticate(user=user)

    created = client.post(
        "/api/tower-designs/",
        {"slug": "my-tower", "title": "My Tower"},
        format="json",
    )
    assert created.status_code == 201
    design_id = created.json()["id"]

    piece = client.post(
        f"/api/tower-designs/{design_id}/pieces/",
        {"piece_asset_id": piece_asset.id, "piece_type": "section"},
        format="json",
    )
    assert piece.status_code == 201

    placement = client.post(
        f"/api/tower-designs/{design_id}/artifacts/",
        {
            "target_piece_instance_id": piece.json()["id"],
            "artifact_asset_id": artifact_asset.id,
            "role": "adventure",
            "content_definition_id": content.id,
            "x": 24,
            "y": 12,
            "width": 32,
            "height": 48,
        },
        format="json",
    )
    assert placement.status_code == 201, placement.content
    assert ArtifactPlacement.objects.count() == 1

    active = client.post(f"/api/tower-designs/{design_id}/set-active/")
    assert active.status_code == 200

    overview = client.get("/api/my-tower/overview/")
    assert overview.status_code == 200
    body = overview.json()
    assert body["design"]["id"] == design_id
    assert body["tower_layout"]["pieces"][0]["pieceType"] == "section"
    assert body["artifacts"][0]["role"] == "adventure"
    assert body["artifacts"][0]["contentBinding"] == {
        "kind": "adventure",
        "id": content.id,
    }
    assert body["artifacts"][0]["width"] == 32
    assert body["artifacts"][0]["height"] == 48


@pytest.mark.django_db
def test_raise_tower_is_idempotent(django_user_model):
    """"Raise your Tower" is get-or-create: a second call returns the existing
    personal tower instead of erroring, so the one-per-user cap reads as a fact
    of the world rather than a validation error."""
    user = make_user(django_user_model)
    client = APIClient()
    client.force_authenticate(user=user)

    first = client.post("/api/tower-designs/", {"slug": "spire-a", "title": "Spire A"}, format="json")
    assert first.status_code == 201

    second = client.post("/api/tower-designs/", {"slug": "spire-b", "title": "Spire B"}, format="json")
    assert second.status_code == 201
    # Same tower returned, not a second one.
    assert second.json()["id"] == first.json()["id"]
    assert TowerDesign.objects.filter(owner=user, origin="personal").count() == 1


@pytest.mark.django_db
def test_tower_piece_rejects_non_piece_asset(django_user_model):
    user = make_user(django_user_model)
    design = TowerDesign.objects.create(owner=user, slug="tower", title="Tower")
    artifact = Asset.objects.create(kind=KIND_TOWER_ARTIFACT, slug="banner", label="Banner")

    with pytest.raises(ValidationError):
        TowerPieceInstance.objects.create(
            tower_design=design,
            piece_asset=artifact,
            piece_type="section",
        )
