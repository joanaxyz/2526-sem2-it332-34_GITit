from io import BytesIO

import pytest
from django.core.files.base import ContentFile
from PIL import Image

from assets.models import KIND_MONSTER, Asset, AssetSprite


def _png(width: int, height: int) -> bytes:
    buffer = BytesIO()
    Image.new("RGBA", (width, height), (0, 0, 0, 0)).save(buffer, format="PNG")
    return buffer.getvalue()


@pytest.mark.django_db
def test_sprite_save_counts_horizontal_square_strip(tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path
    asset = Asset.objects.create(kind=KIND_MONSTER, slug="test-slime", label="Test Slime")
    sprite = AssetSprite(asset=asset, action="idle", fps=8)

    sprite.image.save("idle.png", ContentFile(_png(48, 16)), save=True)

    assert sprite.frame_width == 16
    assert sprite.frame_height == 16
    assert sprite.columns == 3
    assert sprite.rows == 1
    assert sprite.frame_count == 3


@pytest.mark.django_db
def test_sprite_save_counts_explicit_grid(tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path
    asset = Asset.objects.create(kind=KIND_MONSTER, slug="test-grid", label="Test Grid")
    sprite = AssetSprite(
        asset=asset,
        action="walk",
        frame_width=16,
        frame_height=16,
        fps=10,
    )

    sprite.image.save("walk.png", ContentFile(_png(48, 32)), save=True)

    assert sprite.columns == 3
    assert sprite.rows == 2
    assert sprite.frame_count == 6
