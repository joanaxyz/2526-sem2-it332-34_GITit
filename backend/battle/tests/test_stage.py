"""Battle-stage dressing resolution (stage_payload).

Resolves a chapter's authored `battle_stage` config into render-ready data
(sprite URLs + normalized positions). Uses the cached descriptor map, so the
positive case primes the cache directly rather than seeding sprite files.
"""

from types import SimpleNamespace

import pytest
from django.core.cache import cache

from assets.descriptors import _cache_key, clear_descriptor_cache
from assets.models import KIND_RELIC
from battle.payloads import stage_payload


def _chapter(battle_stage):
    return SimpleNamespace(battle_stage=battle_stage)


def test_returns_none_when_unauthored():
    assert stage_payload(_chapter({}), user=None) is None
    assert stage_payload(_chapter(None), user=None) is None


@pytest.mark.django_db
def test_returns_none_when_nothing_resolves():
    clear_descriptor_cache()
    # A slug with no matching published artifact resolves to no URL -> dropped.
    config = {"background": "missing", "artifacts": [{"slug": "also-missing", "x": 0.5, "y": 0.5}]}
    assert stage_payload(_chapter(config), user=None) is None


@pytest.mark.django_db
def test_resolves_background_and_artifacts():
    # Prime the cached tower-artifact descriptor map so resolution is file-free.
    cache.set(
        _cache_key(KIND_RELIC),
        {
            "backdrop": {"sprites": {"default": {"url": "/media/backdrop.png"}}},
            "banner": {"sprites": {"default": {"url": "/media/banner.png"}}},
        },
        timeout=None,
    )
    try:
        config = {
            "background": "backdrop",
            "artifacts": [
                {"slug": "banner", "x": 1.5, "y": -0.2, "scale": 0, "rotation": 30, "z": 2},
                {"slug": "ghost", "x": 0.3, "y": 0.3},  # unresolved -> dropped
            ],
        }
        payload = stage_payload(_chapter(config), user=None)
        assert payload is not None
        assert payload["background"] == {"slug": "backdrop", "url": "/media/backdrop.png"}
        assert len(payload["artifacts"]) == 1
        prop = payload["artifacts"][0]
        assert prop["slug"] == "banner"
        assert prop["url"] == "/media/banner.png"
        # Coordinates clamp to 0..1; a non-positive scale falls back to 1.0.
        assert prop["x"] == 1.0
        assert prop["y"] == 0.0
        assert prop["scale"] == 1.0
        assert prop["rotation"] == 30.0
        assert prop["z"] == 2
    finally:
        clear_descriptor_cache()
