import pytest
from django.core.management import call_command

from assets.models import KIND_TOWER_ARTIFACT, KIND_TOWER_PIECE, Asset, AssetSprite, TowerPieceAsset
from assets.seed_data.tower_pieces import OFFICIAL_TOWER_ARTIFACT_SPECS, OFFICIAL_TOWER_PIECE_SPECS


@pytest.mark.django_db
def test_seed_assets_registers_tower_assets_from_archives(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path

    call_command("seed_assets", "--skip-grant", verbosity=0)

    piece_slugs = {spec["slug"] for spec in OFFICIAL_TOWER_PIECE_SPECS}
    artifact_slugs = {spec["slug"] for spec in OFFICIAL_TOWER_ARTIFACT_SPECS}

    assert set(
        Asset.objects.filter(kind=KIND_TOWER_PIECE).values_list("slug", flat=True)
    ) == piece_slugs
    assert set(
        Asset.objects.filter(kind=KIND_TOWER_ARTIFACT).values_list("slug", flat=True)
    ) == artifact_slugs
    assert TowerPieceAsset.objects.filter(asset__slug__in=piece_slugs).count() == len(piece_slugs)
    assert AssetSprite.objects.filter(asset__slug__in=piece_slugs | artifact_slugs).count() == (
        len(piece_slugs) + len(artifact_slugs)
    )
    hall_piece = TowerPieceAsset.objects.get(asset__slug="official-hall-section")
    hall_sprite = AssetSprite.objects.get(asset__slug="official-hall-section", action="default")
    assert hall_piece.view_box == "-23.25 -2 414.5 224"
    assert f'viewBox="{hall_piece.view_box}"'.encode() in hall_sprite.image.read()


@pytest.mark.django_db
def test_seed_assets_overwrites_stale_seed_sprite_without_suffix(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    stale_sprite = tmp_path / "assets" / "sprites" / "blue__idle.png"
    stale_sprite.parent.mkdir(parents=True)
    stale_sprite.write_bytes(b"stale")

    call_command("seed_assets", "--skip-grant", verbosity=0)

    sprite = AssetSprite.objects.get(asset__slug="blue", action="idle")
    assert sprite.image.name == "assets/sprites/blue__idle.png"
    assert not list(stale_sprite.parent.glob("blue__idle_*.png"))
