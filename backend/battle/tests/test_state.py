"""Deterministic rosters with HP derived from the variant's rule count.

Levels/variants are plain stand-ins (no Django).
"""

from types import SimpleNamespace

from battle.constants import BOSS_SPECIES_CYCLE, MOB_SPECIES_CYCLE
from battle.state import initial_adventure_battle_state, initial_challenge_battle_state


def _variant(rule_count=2, mode="rules"):
    """A variant whose evaluation spec expands to `rule_count` rules."""
    if mode == "state_hash":
        spec = {"completion_policy": {"mode": "state_hash"}}
    else:
        spec = {"state_requirements": {"rules": [{"type": "branch_exists"}] * rule_count}}
    return SimpleNamespace(evaluation_spec=spec)


def _level(slug="stage-files", encounter_spec=None, mob_roster=None):
    return SimpleNamespace(
        slug=slug,
        encounter_spec=encounter_spec or [],
        storey=SimpleNamespace(mob_roster=mob_roster or []) if mob_roster is not None else None,
    )


def _challenge_level(challenge_slug="onboard", boss_spec=None, pk=1, boss_roster=None):
    return SimpleNamespace(
        challenge=SimpleNamespace(slug=challenge_slug),
        boss_spec=boss_spec or {},
        pk=pk,
        storey=SimpleNamespace(boss_roster=boss_roster or []) if boss_roster is not None else None,
    )


def test_adventure_default_roster_hp_tracks_rule_count():
    state = initial_adventure_battle_state(_level(), _variant(rule_count=4))
    monsters = state["monsters"]
    # 4 rules -> 3 monsters totalling 4 HP, so each rule-advancing command chips a monster.
    assert len(monsters) == 3
    assert sum(m["hp"] for m in monsters) == 4
    assert all(m["alive"] for m in monsters)
    assert all(m["species"] in MOB_SPECIES_CYCLE for m in monsters)
    assert state["passing_rules"] == 0


def test_adventure_state_hash_variant_has_one_hp():
    state = initial_adventure_battle_state(_level(), _variant(mode="state_hash"))
    assert sum(m["hp"] for m in state["monsters"]) == 1


def test_adventure_roster_is_deterministic_per_slug():
    a = initial_adventure_battle_state(_level(slug="stage-files"), _variant())
    b = initial_adventure_battle_state(_level(slug="stage-files"), _variant())
    c = initial_adventure_battle_state(_level(slug="inspect-status"), _variant())
    assert a == b
    # Different levels rotate the cycle (same shape, usually other species).
    assert [m["id"] for m in c["monsters"]] == [m["id"] for m in a["monsters"]]


def test_adventure_authored_encounter_wins():
    state = initial_adventure_battle_state(
        _level(encounter_spec=[{"species": "knight", "hp": 3, "tier": "elite", "scale": 1.25}]),
        _variant(rule_count=1),
    )
    assert state["monsters"] == [
        {
            "id": 0,
            "species": "knight",
            "tier": "elite",
            "hp": 3,
            "max_hp": 3,
            "alive": True,
            "scale": 1.25,
        }
    ]


def test_adventure_default_roster_uses_storey_mob_roster():
    roster = ["wizard", "priest"]  # arbitrary species, only the storey list matters
    monsters = initial_adventure_battle_state(_level(mob_roster=roster), _variant(rule_count=4))[
        "monsters"
    ]
    assert {m["species"] for m in monsters} <= set(roster)
    # Authored encounters still win over the storey roster.
    authored = initial_adventure_battle_state(
        _level(mob_roster=roster, encounter_spec=[{"species": "slime", "hp": 1}]),
        _variant(),
    )["monsters"]
    assert authored[0]["species"] == "slime"


def test_challenge_boss_uses_storey_boss_roster():
    (boss,) = initial_challenge_battle_state(_challenge_level(boss_roster=["wizard"]), _variant())[
        "monsters"
    ]
    assert boss["species"] == "wizard"


def test_challenge_boss_hp_tracks_rule_count():
    state = initial_challenge_battle_state(_challenge_level(), _variant(rule_count=3))
    (boss,) = state["monsters"]
    assert boss["tier"] == "boss"
    assert boss["species"] in BOSS_SPECIES_CYCLE
    assert boss["hp"] == 3  # one HP per rule to reach target


def test_challenge_authored_boss():
    state = initial_challenge_battle_state(
        _challenge_level(boss_spec={"species": "wizard", "hp": 7, "scale": 1.7}),
        _variant(rule_count=2),
    )
    (boss,) = state["monsters"]
    assert boss["species"] == "wizard"
    assert boss["hp"] == 7
    assert boss["scale"] == 1.7
