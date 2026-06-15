import pytest
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile

from assets.descriptors import clear_descriptor_cache, descriptor_map
from assets.models import (
    KIND_MONSTER,
    KIND_TOWER_ARTIFACT,
    KIND_TOWER_PIECE,
    TOWER_PIECE_CROWN,
    TOWER_PIECE_LANDING,
    Asset,
    AssetSprite,
    TowerPieceAsset,
)


@pytest.mark.django_db
def test_tower_piece_asset_rejects_non_tower_piece_asset():
    asset = Asset.objects.create(kind=KIND_MONSTER, slug="not-a-piece", label="Not a Piece")

    with pytest.raises(ValidationError):
        TowerPieceAsset.objects.create(asset=asset, piece_type=TOWER_PIECE_LANDING)


@pytest.mark.django_db
def test_tower_artifact_assets_remain_valid_without_piece_metadata():
    asset = Asset(kind=KIND_TOWER_ARTIFACT, slug="banner", label="Banner")

    asset.full_clean()


@pytest.mark.django_db
def test_tower_piece_descriptor_includes_piece_metadata():
    clear_descriptor_cache()
    asset = Asset.objects.create(
        kind=KIND_TOWER_PIECE,
        slug="official-landing",
        label="Official Landing",
    )
    TowerPieceAsset.objects.create(
        asset=asset,
        piece_type=TOWER_PIECE_LANDING,
        view_box="0 0 220 48",
        anchors={"walk_rail": {"x1": 18, "y1": 18, "x2": 202, "y2": 18}},
        bounds={"x": 6, "y": 4, "width": 208, "height": 40},
        svg_sanitized=True,
    )

    descriptor = descriptor_map(KIND_TOWER_PIECE)["official-landing"]

    assert descriptor["kind"] == "tower_piece"
    assert descriptor["piece_type"] == "landing"
    assert descriptor["tower_piece"] == {
        "piece_type": "landing",
        "view_box": "0 0 220 48",
        "anchors": {"walk_rail": {"x1": 18, "y1": 18, "x2": 202, "y2": 18}},
        "bounds": {"x": 6, "y": 4, "width": 208, "height": 40},
        "interaction_zones": {},
        "state_variants": {},
        "svg_sanitized": True,
        "svg": None,
    }


@pytest.mark.django_db
def test_tower_piece_descriptor_serves_inline_svg(tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path
    clear_descriptor_cache()
    asset = Asset.objects.create(
        kind=KIND_TOWER_PIECE,
        slug="official-crown",
        label="Arcane Crown",
    )
    TowerPieceAsset.objects.create(
        asset=asset,
        piece_type=TOWER_PIECE_CROWN,
        view_box="0 0 120 160",
        svg_sanitized=True,
    )
    markup = b'<svg viewBox="0 0 120 160"><path data-role="crown"/></svg>'
    sprite = AssetSprite(asset=asset, action="default", frame_width=120, frame_height=160, fps=1)
    sprite.image.save("official-crown__default.svg", ContentFile(markup), save=True)

    tower_piece = descriptor_map(KIND_TOWER_PIECE)["official-crown"]["tower_piece"]

    # The SVG is served inline so authored asset data can control its own states.
    assert tower_piece["svg"] is not None
    assert 'data-role="crown"' in tower_piece["svg"]


def test_clear_descriptor_cache_tolerates_cache_backend_failure(monkeypatch):
    def fail_delete_many(_keys):
        raise TimeoutError("cache unavailable")

    monkeypatch.setattr("assets.descriptors.cache.delete_many", fail_delete_many)

    clear_descriptor_cache()
