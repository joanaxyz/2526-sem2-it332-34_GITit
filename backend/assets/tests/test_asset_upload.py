import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIClient

from assets.models import Asset, AssetSprite, TowerPieceAsset
from assets.sanitize import sanitize_svg

SAFE_SVG = b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"><rect width="10" height="10"/></svg>'


def make_user(django_user_model, username="builder"):
    return django_user_model.objects.create_user(
        username=username, email=f"{username}@example.com", password="pass12345"
    )


def test_sanitize_strips_script_and_handlers():
    dirty = (
        b'<svg xmlns="http://www.w3.org/2000/svg" onload="evil()">'
        b'<script>alert(1)</script><rect onclick="x()" width="5" height="5"/></svg>'
    )
    cleaned = sanitize_svg(dirty).decode("utf-8").lower()
    assert "<script" not in cleaned
    assert "onload" not in cleaned
    assert "onclick" not in cleaned


def test_sanitize_rejects_doctype():
    with pytest.raises(ValidationError):
        sanitize_svg(b'<!DOCTYPE svg [<!ENTITY x "y">]><svg></svg>')


@pytest.mark.django_db
def test_upload_creates_owned_private_tower_piece(django_user_model):
    user = make_user(django_user_model)
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(
        "/api/assets/",
        {
            "kind": "tower_piece",
            "label": "Glow Landing",
            "piece_type": "landing",
            "file": SimpleUploadedFile("landing.svg", SAFE_SVG, content_type="image/svg+xml"),
        },
        format="multipart",
    )

    assert response.status_code == 201, response.content
    asset = Asset.objects.get(owner=user, label="Glow Landing")
    assert asset.visibility == "private"
    assert asset.is_published is False
    piece = TowerPieceAsset.objects.get(asset=asset)
    assert piece.view_box == "-2.5 -2.5 15 15"
    assert piece.anchors == {}
    sprite = AssetSprite.objects.get(asset=asset, action="default")
    assert b'viewBox="-2.5 -2.5 15 15"' in sprite.image.read()


@pytest.mark.django_db
def test_upload_tower_artifact_stores_cropped_bounds_and_action_sprites(django_user_model):
    user = make_user(django_user_model)
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(
        "/api/assets/",
        {
            "kind": "tower_artifact",
            "label": "Quest Relic",
            "file": SimpleUploadedFile("relic.svg", SAFE_SVG, content_type="image/svg+xml"),
            "file_hover": SimpleUploadedFile("relic-hover.svg", SAFE_SVG, content_type="image/svg+xml"),
            "file_click": SimpleUploadedFile("relic-click.svg", SAFE_SVG, content_type="image/svg+xml"),
        },
        format="multipart",
    )

    assert response.status_code == 201, response.content
    asset = Asset.objects.get(owner=user, label="Quest Relic")
    assert asset.config["view_box"] == "-2.5 -2.5 15 15"
    assert asset.config["bounds"] == {"x": -2.5, "y": -2.5, "width": 15.0, "height": 15.0}
    assert set(AssetSprite.objects.filter(asset=asset).values_list("action", flat=True)) == {
        "default",
        "hover",
        "click",
    }


@pytest.mark.django_db
def test_owned_descriptor_map_hides_private_assets_from_others(django_user_model):
    owner = make_user(django_user_model, "owner")
    other = make_user(django_user_model, "other")
    client = APIClient()
    client.force_authenticate(user=owner)
    client.post(
        "/api/assets/",
        {
            "kind": "tower_artifact",
            "label": "Secret Banner",
            "file": SimpleUploadedFile("banner.svg", SAFE_SVG, content_type="image/svg+xml"),
        },
        format="multipart",
    )

    other_client = APIClient()
    other_client.force_authenticate(user=other)
    body = other_client.get("/api/assets/descriptors/?kind=tower_artifact&mine=1").json()
    assert all("secret-banner" not in slug for slug in body["results"])
