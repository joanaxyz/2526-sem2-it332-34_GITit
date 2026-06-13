"""Frontend-facing asset descriptors, cached so hot paths never query.

The battle payload merges these into each `battle_state` monster. The descriptor
map for a kind is tiny and changes only when an admin/user edits an asset, so we
build it once and cache it; :mod:`assets.signals` busts the cache on write. The
per-command submit path therefore adds **zero** asset queries (latency budget is
SQL round trips — see backend/scripts/profile_command_latency.py).
"""

from __future__ import annotations

import logging

from django.core.cache import cache

from assets.models import KIND_CHARACTER, KIND_MONSTER, KIND_TOWER_PIECE, Asset, TowerPieceAsset

_CACHE_VERSION = 2
logger = logging.getLogger(__name__)


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
    payload = {
        "slug": asset.slug,
        "label": asset.label,
        "kind": asset.kind,
        "scale": asset.default_scale,
        "config": config,
        "sprites": {s.action: sprite_descriptor(s) for s in asset.sprites.all()},
    }
    if asset.kind == KIND_MONSTER:
        payload.update(
            {
                "tier": config.get("tier"),
                "attack": config.get("attack", {}),
                "metrics": config.get("metrics", {}),
            }
        )
    elif asset.kind == KIND_CHARACTER:
        payload["metrics"] = config.get("metrics", {})
        payload["random_actions"] = config.get("random_actions", [])
    elif asset.kind == KIND_TOWER_PIECE:
        try:
            tower_piece = asset.tower_piece
        except TowerPieceAsset.DoesNotExist:
            tower_piece = None
        if tower_piece:
            payload["piece_type"] = tower_piece.piece_type
            payload["tower_piece"] = {
                "piece_type": tower_piece.piece_type,
                "view_box": tower_piece.view_box,
                "anchors": tower_piece.anchors or {},
                "bounds": tower_piece.bounds or {},
                "interaction_zones": tower_piece.interaction_zones or {},
                "state_variants": tower_piece.state_variants or {},
                "svg_sanitized": tower_piece.svg_sanitized,
            }
    return payload


def descriptor_map(kind: str = KIND_MONSTER) -> dict[str, dict]:
    """`{slug: descriptor}` for every published asset of `kind`, cached."""
    key = _cache_key(kind)
    cached = cache.get(key)
    if cached is not None:
        return cached
    assets = Asset.objects.filter(kind=kind, is_published=True).select_related(
        "tower_piece"
    ).prefetch_related("sprites")
    built = {asset.slug: asset_descriptor(asset) for asset in assets}
    cache.set(key, built, timeout=None)
    return built


def clear_descriptor_cache() -> None:
    # Clear every kind regardless of which changed; the map is tiny to rebuild.
    from assets.models import ASSET_KINDS

    try:
        cache.delete_many([_cache_key(kind) for kind, _label in ASSET_KINDS])
    except Exception as exc:  # pragma: no cover - depends on cache backend/network.
        logger.warning("Could not clear asset descriptor cache: %s", exc)
