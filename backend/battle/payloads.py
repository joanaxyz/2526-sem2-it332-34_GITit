"""Response builder for the `battle` block.

Attached to attempt/run payloads (events empty - initial roster state) and to
per-command responses (with the turn's ordered events). The player's bar is
the command budget, already present in the counts payloads, so it never
appears here.
"""

from __future__ import annotations

from assets.descriptors import descriptor_map, owned_descriptor_map
from assets.models import KIND_BATTLE_ARTIFACT, KIND_MONSTER, KIND_RELIC
from battle.constants import BATTLE_SCHEMA_VERSION

# Artifact assets that can dress a battle stage (backdrop + scattered props).
_STAGE_ARTIFACT_KINDS = (KIND_RELIC, KIND_BATTLE_ARTIFACT)


def _effective_descriptor(monster: dict, descriptors: dict[str, dict]) -> dict | None:
    slug = str(monster.get("species") or "")
    descriptor = descriptors.get(slug)
    if not descriptor:
        return None
    payload = {
        **descriptor,
        "attack": dict(descriptor.get("attack") or {}),
        "metrics": dict(descriptor.get("metrics") or {}),
        "sprites": {
            action: dict(sprite) for action, sprite in (descriptor.get("sprites") or {}).items()
        },
    }
    scale = monster.get("scale")
    if scale not in (None, ""):
        try:
            payload["scale"] = float(scale)
        except (TypeError, ValueError):
            pass
    return payload


def _monster_payloads(monsters: list[dict], user=None) -> list[dict]:
    # Official monsters resolve from the global cached map with zero queries.
    # Only when a species is missing (a user's uploaded/purchased monster) do we
    # lazily build the owner-aware map, so the official hot path is untouched.
    descriptors = descriptor_map()
    owned: dict[str, dict] | None = None
    payloads = []
    for monster in monsters:
        payload = dict(monster)
        descriptor = _effective_descriptor(payload, descriptors)
        if descriptor is None and getattr(user, "is_authenticated", False):
            if owned is None:
                owned = owned_descriptor_map(user, KIND_MONSTER)
            descriptor = _effective_descriptor(payload, owned)
        if descriptor:
            payload["descriptor"] = descriptor
        payloads.append(payload)
    return payloads


def _sprite_url(descriptor: dict | None) -> str | None:
    sprites = (descriptor or {}).get("sprites") or {}
    sprite = sprites.get("default") or next(iter(sprites.values()), None)
    url = (sprite or {}).get("url")
    return url or None


def _resolve_stage_artifact(slug: str, user, caches: dict) -> str | None:
    """Resolve an artifact slug to its sprite URL via the cached descriptor maps
    (official = zero query). Only falls back to the owner-aware map for a user's
    own/purchased artifact, mirroring the monster resolution above."""
    for kind in _STAGE_ARTIFACT_KINDS:
        cache = caches.setdefault(kind, descriptor_map(kind))
        url = _sprite_url(cache.get(slug))
        if url:
            return url
    if getattr(user, "is_authenticated", False):
        for kind in _STAGE_ARTIFACT_KINDS:
            key = ("owned", kind)
            cache = caches.get(key)
            if cache is None:
                cache = caches[key] = owned_descriptor_map(user, kind)
            url = _sprite_url(cache.get(slug))
            if url:
                return url
    return None


def stage_payload(chapter, *, user=None) -> dict | None:
    """Resolve a chapter's authored battle-stage dressing into render-ready data
    (sprite URLs + normalized positions). Returns None when nothing is authored
    so the client falls back to the default sky + ledge. Built off the run-detail
    payload only (never the per-command hot path)."""
    config = getattr(chapter, "battle_stage", None) or {}
    if not isinstance(config, dict) or not config:
        return None
    caches: dict = {}

    background = None
    bg_slug = config.get("background")
    if bg_slug:
        url = _resolve_stage_artifact(str(bg_slug), user, caches)
        if url:
            background = {"slug": str(bg_slug), "url": url}

    artifacts = []
    for row in config.get("artifacts") or []:
        if not isinstance(row, dict):
            continue
        slug = str(row.get("slug") or "")
        url = _resolve_stage_artifact(slug, user, caches) if slug else None
        if not url:
            continue
        artifacts.append(
            {
                "slug": slug,
                "url": url,
                "x": _clamp01(row.get("x")),
                "y": _clamp01(row.get("y")),
                "scale": _positive(row.get("scale"), 1.0),
                "rotation": _number(row.get("rotation"), 0.0),
                "z": int(_number(row.get("z"), 0)),
            }
        )

    if not background and not artifacts:
        return None
    return {"background": background, "artifacts": artifacts}


def _number(value, fallback: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback


def _positive(value, fallback: float) -> float:
    result = _number(value, fallback)
    return result if result > 0 else fallback


def _clamp01(value) -> float:
    return min(1.0, max(0.0, _number(value, 0.0)))


def battle_block(
    battle_state: dict | None, events: list[dict] | None = None, *, user=None
) -> dict | None:
    if not battle_state:
        return None
    monsters = list(battle_state.get("monsters") or [])
    return {
        "schema_version": battle_state.get("schema_version", BATTLE_SCHEMA_VERSION),
        "monsters": _monster_payloads(monsters, user=user),
        "events": list(events or []),
    }
