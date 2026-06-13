"""Frontend-facing asset descriptors, cached so hot paths never query.

The battle payload merges these into each `battle_state` monster. The descriptor
map for a kind is tiny and changes only when an admin/user edits an asset, so we
build it once and cache it; :mod:`assets.signals` busts the cache on write. The
per-command submit path therefore adds **zero** asset queries (latency budget is
SQL round trips — see backend/scripts/profile_command_latency.py).
"""

from __future__ import annotations

from django.core.cache import cache

from assets.models import KIND_MONSTER, Asset

_CACHE_VERSION = 1


def _cache_key(kind: str) -> str:
    return f"assets:descriptors:{_CACHE_VERSION}:{kind}"


def sprite_descriptor(sprite) -> dict:
    return {
        "url": sprite.image.url if sprite.image else "",
        "frame_count": sprite.frame_count,
        "columns": sprite.columns,
        "rows": sprite.rows,
        "frame_width": sprite.frame_width,
        "frame_height": sprite.frame_height,
        "fps": sprite.fps,
        "loops": sprite.loops,
    }


def asset_descriptor(asset: Asset) -> dict:
    config = asset.config or {}
    return {
        "slug": asset.slug,
        "label": asset.label,
        "kind": asset.kind,
        "scale": asset.default_scale,
        "tier": config.get("tier"),
        "attack": config.get("attack", {}),
        "metrics": config.get("metrics", {}),
        "sprites": {s.action: sprite_descriptor(s) for s in asset.sprites.all()},
    }


def descriptor_map(kind: str = KIND_MONSTER) -> dict[str, dict]:
    """`{slug: descriptor}` for every published asset of `kind`, cached."""
    key = _cache_key(kind)
    cached = cache.get(key)
    if cached is not None:
        return cached
    assets = (
        Asset.objects.filter(kind=kind, is_published=True).prefetch_related("sprites")
    )
    built = {asset.slug: asset_descriptor(asset) for asset in assets}
    cache.set(key, built, timeout=None)
    return built


def clear_descriptor_cache() -> None:
    # Clear every kind regardless of which changed; the map is tiny to rebuild.
    from assets.models import ASSET_KINDS

    for kind, _label in ASSET_KINDS:
        cache.delete(_cache_key(kind))
