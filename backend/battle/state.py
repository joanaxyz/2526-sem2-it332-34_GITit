"""Initial battle-state builders.

`battle_state` lives as JSON on AdventureLevelAttempt / ChallengeRun and is
written inside saves the submit path already performs - never a new query.

Shape (schema 1):
    {
        "schema_version": 1,
        "monsters": [
            {"id": 0, "species": "slime", "tier": "mob",
             "hp": 1, "max_hp": 1, "alive": true},
        ],
        "passing_rules": 0,          # evaluation rules satisfied last turn
    }

Total HP is derived from the variant's evaluation spec: it equals the number of
rules that must pass to reach `target_state`. Each newly satisfied rule is one
hit and the solve lands the finishing blow, so HP tracks the repository state
actually being achieved rather than an authored magic number. The species cycle
is still deterministic per level slug, so every environment agrees on the
roster. Authored `encounter_spec` / `boss_spec` win when present.
"""

from __future__ import annotations

import zlib

from battle.constants import (
    BATTLE_SCHEMA_VERSION,
    BOSS_SPECIES_CYCLE,
    MAX_DEFAULT_MONSTERS,
    MOB_SPECIES_CYCLE,
    TIER_BOSS,
    TIER_MOB,
)
from evaluation.compiler import compile_evaluation_spec
from evaluation.services import rules_from_state_requirements


def _target_hp(evaluation_spec) -> int:
    """Monster/boss HP = number of evaluation rules to reach `target_state`.

    State-hash variants expose no granular rules (progress is invisible until
    the hash matches), so they fall back to 1 - the solve is the only blow.
    """
    try:
        spec = compile_evaluation_spec(evaluation_spec)
    except ValueError:
        return 1
    if spec.completion_policy.mode == "state_hash":
        return 1
    return max(1, len(rules_from_state_requirements(spec.as_rule_payload())))


def _stable_offset(slug: str) -> int:
    return zlib.crc32(slug.encode("utf-8"))


def _roster_for(level, attr: str, fallback: tuple[str, ...]) -> tuple[str, ...]:
    """Species cycle for this level's chapter, or the global fallback.

    Reads `level.chapter.<attr>` (mob_roster / boss_roster); a missing chapter or
    an empty roster falls back to the shared default cycle. Chapter access is
    resolved once at run/attempt creation - callers select_related the chain -
    so this never adds a per-command round trip.
    """
    chapter = getattr(level, "chapter", None)
    roster = list(getattr(chapter, attr, None) or []) if chapter is not None else []
    return tuple(roster) if roster else fallback


def _scale(value) -> float | None:
    if value in (None, ""):
        return None
    try:
        scale = float(value)
    except (TypeError, ValueError):
        return None
    return scale if scale > 0 else None


def _monster(idx: int, species: str, tier: str, hp: int, scale: float | None = None) -> dict:
    monster = {
        "id": idx,
        "species": species,
        "tier": tier,
        "hp": hp,
        "max_hp": hp,
        "alive": hp > 0,
    }
    if scale is not None:
        monster["scale"] = scale
    return monster


def _authored_roster(entries: list) -> list[dict]:
    roster = []
    for idx, entry in enumerate(entries):
        species = str(entry.get("species", "")) or MOB_SPECIES_CYCLE[idx % len(MOB_SPECIES_CYCLE)]
        hp = max(1, int(entry.get("hp", 1)))
        tier = str(entry.get("tier", TIER_MOB))
        roster.append(_monster(idx, species, tier, hp, _scale(entry.get("scale"))))
    return roster


def initial_adventure_battle_state(level, variant) -> dict:
    """Roster for one adventure level (= one encounter).

    Default: up to 3 mobs whose total HP equals the variant's rule count, so
    each rule-advancing command visibly chips a monster and the solve lands the
    finishing blow. Authored `encounter_spec` rows ({species, hp, tier}) override.
    """
    authored = getattr(level, "encounter_spec", None) or []
    if authored:
        monsters = _authored_roster(authored)
    else:
        total_hp = _target_hp(getattr(variant, "evaluation_spec", None))
        count = min(total_hp, MAX_DEFAULT_MONSTERS)
        base_hp, extra = divmod(total_hp, count)
        offset = _stable_offset(level.slug)
        cycle = _roster_for(level, "mob_roster", MOB_SPECIES_CYCLE)
        monsters = [
            _monster(
                i,
                cycle[(offset + i) % len(cycle)],
                TIER_MOB,
                base_hp + (1 if i < extra else 0),
            )
            for i in range(count)
        ]
    return {
        "schema_version": BATTLE_SCHEMA_VERSION,
        "monsters": monsters,
        "passing_rules": 0,
    }


def initial_challenge_battle_state(level, variant) -> dict:
    """Single boss for one challenge level's level. Boss HP = the variant's
    rule count (distance to target). Authored `boss_spec` ({species, hp})
    overrides the derived default."""
    authored = getattr(level, "boss_spec", None) or {}
    offset = _stable_offset(getattr(level.challenge, "slug", "") or str(level.pk))
    cycle = _roster_for(level, "boss_roster", BOSS_SPECIES_CYCLE)
    species = str(authored.get("species", "")) or cycle[offset % len(cycle)]
    default_hp = _target_hp(getattr(variant, "evaluation_spec", None))
    hp = max(1, int(authored.get("hp", default_hp)))
    return {
        "schema_version": BATTLE_SCHEMA_VERSION,
        "monsters": [_monster(0, species, TIER_BOSS, hp, _scale(authored.get("scale")))],
        "passing_rules": 0,
    }
