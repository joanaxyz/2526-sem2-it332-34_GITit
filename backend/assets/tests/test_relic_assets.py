import pytest
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile

from assets.descriptors import clear_descriptor_cache, descriptor_map
from assets.models import KIND_MONSTER, KIND_RELIC, Asset, AssetSprite, RelicAsset


@pytest.mark.django_db
def test_relic_asset_rejects_non_relic_asset():
    asset = Asset.objects.create(kind=KIND_MONSTER, slug="not-a-relic", label="Not a Relic")

    with pytest.raises(ValidationError):
        RelicAsset.objects.create(asset=asset)


@pytest.mark.django_db
def test_relic_descriptor_includes_relic_metadata():
    clear_descriptor_cache()
    asset = Asset.objects.create(
        kind=KIND_RELIC,
        slug="official-relic",
        label="Official Relic",
    )
    RelicAsset.objects.create(
        asset=asset,
        view_box="0 0 220 48",
        interactive_viewbox={"x": 30, "y": 8, "width": 160, "height": 32},
        landing_viewbox={"x1": 18, "y1": 44, "x2": 202, "y2": 44},
        svg_sanitized=True,
    )

    descriptor = descriptor_map(KIND_RELIC)["official-relic"]

    assert descriptor["kind"] == "relic"
    assert descriptor["relic"] == {
        "view_box": "0 0 220 48",
        "interactive_viewbox": {"x": 30, "y": 8, "width": 160, "height": 32},
        "landing_viewbox": {"x1": 18, "y1": 44, "x2": 202, "y2": 44},
        "svg_sanitized": True,
        "svg": None,
        "content_type": None,
        "natural_width": None,
        "natural_height": None,
        "is_raster": False,
    }


@pytest.mark.django_db
def test_relic_descriptor_serves_inline_svg(tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path
    clear_descriptor_cache()
    asset = Asset.objects.create(
        kind=KIND_RELIC,
        slug="official-relic",
        label="Arcane Relic",
    )
    RelicAsset.objects.create(
        asset=asset,
        view_box="0 0 120 160",
        svg_sanitized=True,
    )
    markup = b'<svg viewBox="0 0 120 160"><path data-role="relic"/></svg>'
    sprite = AssetSprite(asset=asset, action="default", frame_width=120, frame_height=160, fps=1)
    sprite.image.save("official-relic__default.svg", ContentFile(markup), save=True)

    relic = descriptor_map(KIND_RELIC)["official-relic"]["relic"]

    # The SVG is served inline so authored asset data can control its own states.
    assert relic["svg"] is not None
    assert 'data-role="relic"' in relic["svg"]


def test_clear_descriptor_cache_tolerates_cache_backend_failure(monkeypatch):
    def fail_delete_many(_keys):
        raise TimeoutError("cache unavailable")

    monkeypatch.setattr("assets.descriptors.cache.delete_many", fail_delete_many)

    clear_descriptor_cache()
