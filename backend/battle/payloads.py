"""Response builder for the `battle` block.

Attached to attempt/run payloads (events empty - initial roster state) and to
per-command responses (with the turn's ordered events). The player's bar is
the command budget, already present in the counts payloads, so it never
appears here.
"""

from __future__ import annotations

from assets.descriptors import descriptor_map, owned_descriptor_map
from assets.models import KIND_MONSTER
from battle.constants import BATTLE_SCHEMA_VERSION


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
