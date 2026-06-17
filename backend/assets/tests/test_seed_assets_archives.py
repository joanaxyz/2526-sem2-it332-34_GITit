import pytest
from django.core.management import call_command

from assets.models import KIND_RELIC, Asset, AssetSprite, RelicAsset
from assets.seed_data.relics import OFFICIAL_RELIC_SPECS


@pytest.mark.django_db
def test_seed_assets_registers_relics_from_archives(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path

    call_command("seed_assets", "--skip-grant", verbosity=0)

    relic_slugs = {spec["slug"] for spec in OFFICIAL_RELIC_SPECS}

    assert set(
        Asset.objects.filter(kind=KIND_RELIC).values_list("slug", flat=True)
    ) == relic_slugs
    assert RelicAsset.objects.filter(asset__slug__in=relic_slugs).count() == len(relic_slugs)
    assert AssetSprite.objects.filter(asset__slug__in=relic_slugs).count() == len(relic_slugs)

    relic = RelicAsset.objects.get(asset__slug="official-relic")
    relic_sprite = AssetSprite.objects.get(asset__slug="official-relic", action="default")
    # The relic art is built from the hall section SVG, auto-cropped at seed.
    assert relic.view_box == "-23.25 -2 414.5 224"
    assert f'viewBox="{relic.view_box}"'.encode() in relic_sprite.image.read()
    assert relic.interactive_viewbox
    assert relic.landing_viewbox


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
