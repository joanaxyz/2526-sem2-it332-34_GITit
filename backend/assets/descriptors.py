"""Frontend-facing asset descriptors, cached so hot paths never query.

The battle payload merges these into each `battle_state` monster. The descriptor
map for a kind is tiny and changes only when an admin/user edits an asset, so we
build it once and cache it; :mod:`assets.signals` busts the cache on write. The
per-command submit path therefore adds **zero** asset queries (latency budget is
SQL round trips - see backend/scripts/profile_command_latency.py).
"""

from __future__ import annotations

import logging

from django.core.cache import cache

from assets.models import KIND_CHARACTER, KIND_MONSTER, KIND_TOWER_PIECE, Asset, TowerPieceAsset

_CACHE_VERSION = 5
logger = logging.getLogger(__name__)


def _inline_svg(asset) -> str | None:
    """The piece's default SVG markup, read inline so the frontend can animate it
    (vs. a flat ``<img>``). Returns ``None`` for non-SVG sprites or read errors.
    Cached with the descriptor, so this file read happens only on cache rebuild.
    """
    sprite = next((s for s in asset.sprites.all() if s.action == "default"), None)
    if sprite is None or not sprite.image:
        return None
    if not str(sprite.image.name or "").lower().endswith(".svg"):
        return None
    try:
        with sprite.image.open("rb") as handle:
            return handle.read().decode("utf-8")
    except Exception as exc:  # pragma: no cover - storage/encoding edge cases
        logger.warning("Could not inline SVG for %s: %s", asset.slug, exc)
        return None


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
        "id": asset.id,
        "slug": asset.slug,
        "label": asset.label,
        "kind": asset.kind,
        "scale": asset.default_scale,
        "owner_id": asset.owner_id,
        "visibility": asset.visibility,
        "price": asset.price,
        "tags": list(asset.tags or []),
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
                # Inline SVG + safe animation preset drive the data-driven
                # renderer (PieceSvg): the art is styled/animated, not a flat img.
                "svg": _inline_svg(asset),
                "animation": config.get("animation"),
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


def owned_descriptor_map(user, kind: str) -> dict[str, dict]:
    """Official published assets PLUS the user's own AND purchased assets of `kind`.

    Used by the editor/private tower (and owner-aware battle resolution) so a
    user's uploaded private assets and store purchases are visible to them
    without ever entering the global (cross-user) cached map. Each descriptor is
    stamped with a ``source`` (``official`` | ``owned`` | ``purchased``) for
    frontend filtering. The official entries are copied before stamping so the
    shared cached map is never mutated.
    """
    base: dict[str, dict] = {}
    for slug, descriptor in descriptor_map(kind).items():
        base[slug] = {**descriptor, "source": "official"}
    if not getattr(user, "is_authenticated", False):
        return base

    owned = (
        Asset.objects.filter(owner=user, kind=kind)
        .select_related("tower_piece")
        .prefetch_related("sprites")
    )
    for asset in owned:
        base[asset.slug] = {**asset_descriptor(asset), "source": "owned"}

    for asset in _entitled_assets(user, kind):
        # Don't override an asset the user also owns; ownership wins.
        if asset.owner_id == getattr(user, "id", None):
            continue
        # Default-granted official assets (the Arcane Spire starter kit) are
        # entitled too, but they are not purchases — keep them labelled official
        # rather than downgrading the source the palette/shop filters on. Key off
        # the asset's real owner (None == official), not the base source label,
        # since the base map also carries other users' published store assets.
        if asset.owner_id is None and asset.slug in base:
            continue
        base[asset.slug] = {**asset_descriptor(asset), "source": "purchased"}
    return base


def _entitled_assets(user, kind: str):
    """Assets of `kind` the user has purchased (via marketplace entitlements).

    Imported locally to avoid an app-load import cycle (marketplace imports
    assets). Returns an empty list if the marketplace app is unavailable.
    """
    try:
        from marketplace.models import Entitlement
    except Exception:  # pragma: no cover - marketplace app optional at import time
        return []
    return list(
        Asset.objects.filter(
            kind=kind,
            entitlement__user=user,
        )
        .select_related("tower_piece")
        .prefetch_related("sprites")
        .distinct()
    )


def clear_descriptor_cache() -> None:
    # Clear every kind regardless of which changed; the map is tiny to rebuild.
    from assets.models import ASSET_KINDS

    try:
        cache.delete_many([_cache_key(kind) for kind, _label in ASSET_KINDS])
    except Exception as exc:  # pragma: no cover - depends on cache backend/network.
        logger.warning("Could not clear asset descriptor cache: %s", exc)
