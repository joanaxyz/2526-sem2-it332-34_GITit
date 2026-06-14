import pytest
from rest_framework.test import APIClient

from assets.models import KIND_TOWER_ARTIFACT, KIND_TOWER_PIECE, TOWER_PIECE_ADVENTURE_SECTION, Asset, TowerPieceAsset
from authoring.models import ContentDefinition
from towers.models import TowerContentBinding, TowerDesign, TowerPieceInstance


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
        slug="official-adventure-section-test",
        label="Adventure Section",
    )
    TowerPieceAsset.objects.create(asset=piece_asset, piece_type=TOWER_PIECE_ADVENTURE_SECTION)
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
        {"piece_asset_id": piece_asset.id, "piece_type": "adventure_section"},
        format="json",
    )
    assert piece.status_code == 201

    binding = client.post(
        f"/api/tower-designs/{design_id}/bindings/",
        {"piece_instance_id": piece.json()["id"], "content_definition_id": content.id},
        format="json",
    )
    assert binding.status_code == 201
    assert TowerContentBinding.objects.count() == 1

    active = client.post(f"/api/tower-designs/{design_id}/set-active/")
    assert active.status_code == 200

    overview = client.get("/api/my-tower/overview/")
    assert overview.status_code == 200
    body = overview.json()
    assert body["design"]["id"] == design_id
    assert body["tower_layout"]["pieces"][0]["contentBinding"] == {
        "kind": "adventure",
        "id": content.id,
    }


@pytest.mark.django_db
def test_tower_piece_rejects_non_piece_asset(django_user_model):
    user = make_user(django_user_model)
    design = TowerDesign.objects.create(owner=user, slug="tower", title="Tower")
    artifact = Asset.objects.create(kind=KIND_TOWER_ARTIFACT, slug="banner", label="Banner")

    with pytest.raises(Exception):
        TowerPieceInstance.objects.create(
            tower_design=design,
            piece_asset=artifact,
            piece_type="adventure_section",
        )

