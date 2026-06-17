from io import BytesIO

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIClient

from assets.models import Asset, AssetSprite, RelicAsset
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
def test_upload_creates_owned_private_relic(django_user_model):
    user = make_user(django_user_model)
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(
        "/api/assets/",
        {
            "kind": "relic",
            "label": "Glow Relic",
            "file": SimpleUploadedFile("relic.svg", SAFE_SVG, content_type="image/svg+xml"),
        },
        format="multipart",
    )

    assert response.status_code == 201, response.content
    asset = Asset.objects.get(owner=user, label="Glow Relic")
    assert asset.kind == "relic"
    assert asset.visibility == "private"
    assert asset.is_published is False
    relic = RelicAsset.objects.get(asset=asset)
    assert relic.view_box == "-2.5 -2.5 15 15"
    # Both regions default from the cropped art.
    assert set(relic.interactive_viewbox) == {"x", "y", "width", "height"}
    assert set(relic.landing_viewbox) == {"x1", "y1", "x2", "y2"}
    sprite = AssetSprite.objects.get(asset=asset, action="default")
    assert (sprite.frame_width, sprite.frame_height) == (15, 15)
    assert b'viewBox="-2.5 -2.5 15 15"' in sprite.image.read()


@pytest.mark.django_db
def test_upload_raster_relic_crops_alpha_and_keeps_png_geometry(django_user_model, settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    from PIL import Image

    user = make_user(django_user_model)
    client = APIClient()
    client.force_authenticate(user=user)
    source = Image.new("RGBA", (12, 10), (0, 0, 0, 0))
    for x in range(3, 9):
        for y in range(2, 7):
            source.putpixel((x, y), (120, 220, 255, 255))
    data = BytesIO()
    source.save(data, format="PNG")

    response = client.post(
        "/api/assets/",
        {
            "kind": "relic",
            "label": "Raster Relic",
            "file": SimpleUploadedFile("relic.png", data.getvalue(), content_type="image/png"),
        },
        format="multipart",
    )

    assert response.status_code == 201, response.content
    asset = Asset.objects.get(owner=user, label="Raster Relic")
    relic = RelicAsset.objects.get(asset=asset)
    assert relic.view_box == "0 0 6 5"
    sprite = AssetSprite.objects.get(asset=asset, action="default")
    assert sprite.image.name.endswith(".png")
    assert (sprite.frame_width, sprite.frame_height, sprite.frame_count) == (6, 5, 1)
    with Image.open(sprite.image) as cropped:
        assert cropped.size == (6, 5)


@pytest.mark.django_db
def test_upload_relic_stores_action_sprites(django_user_model):
    user = make_user(django_user_model)
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(
        "/api/assets/",
        {
            "kind": "relic",
            "label": "Quest Relic",
            "file": SimpleUploadedFile("relic.svg", SAFE_SVG, content_type="image/svg+xml"),
            "file_hover": SimpleUploadedFile("relic-hover.svg", SAFE_SVG, content_type="image/svg+xml"),
            "file_click": SimpleUploadedFile("relic-click.svg", SAFE_SVG, content_type="image/svg+xml"),
        },
        format="multipart",
    )

    assert response.status_code == 201, response.content
    asset = Asset.objects.get(owner=user, label="Quest Relic")
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
            "kind": "relic",
            "label": "Secret Relic",
            "file": SimpleUploadedFile("banner.svg", SAFE_SVG, content_type="image/svg+xml"),
        },
        format="multipart",
    )

    other_client = APIClient()
    other_client.force_authenticate(user=other)
    body = other_client.get("/api/assets/descriptors/?kind=relic&mine=1").json()
    assert all("secret-relic" not in slug for slug in body["results"])
