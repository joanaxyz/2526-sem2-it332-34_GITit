"""Response builder for the `battle` block.

Attached to attempt/run payloads (events empty — initial roster state) and to
per-command responses (with the turn's ordered events). The player's bar is
the command budget, already present in the counts payloads, so it never
appears here.
"""

from __future__ import annotations

from assets.descriptors import descriptor_map
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


def _monster_payloads(monsters: list[dict]) -> list[dict]:
    descriptors = descriptor_map()
    payloads = []
    for monster in monsters:
        payload = dict(monster)
        descriptor = _effective_descriptor(payload, descriptors)
        if descriptor:
            payload["descriptor"] = descriptor
        payloads.append(payload)
    return payloads


def battle_block(battle_state: dict | None, events: list[dict] | None = None) -> dict | None:
    if not battle_state:
        return None
    monsters = list(battle_state.get("monsters") or [])
    return {
        "schema_version": battle_state.get("schema_version", BATTLE_SCHEMA_VERSION),
        "monsters": _monster_payloads(monsters),
        "events": list(events or []),
    }
