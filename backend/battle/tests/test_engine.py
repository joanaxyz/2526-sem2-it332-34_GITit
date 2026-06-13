"""Pure-turn matrix for the battle engine (no Django)."""

import pytest

from assets.descriptors import clear_descriptor_cache
from assets.models import KIND_MONSTER, Asset
from battle.engine import BattleEngine, TurnInput
from battle.payloads import battle_block


def _state(monsters, passing_rules=0):
    return {
        "schema_version": 1,
        "monsters": monsters,
        "passing_rules": passing_rules,
    }


def _mob(idx, hp=1, alive=True, species="slime", tier="mob"):
    return {"id": idx, "species": species, "tier": tier, "hp": hp, "max_hp": hp, "alive": alive}


def _turn(state, **overrides):
    defaults = dict(
        battle_state=state,
        counted=True,
        processed=True,
        solved=False,
        rules_passing=None,
        skill="commit",
        defeated=False,
    )
    defaults.update(overrides)
    return TurnInput(**defaults)


def test_diagnostic_is_a_free_action():
    state = _state([_mob(0)])
    outcome = BattleEngine().resolve_turn(_turn(state, counted=False, rules_passing=2))
    assert outcome.events == []
    assert outcome.battle_state["monsters"][0]["alive"] is True
    # The measurement still advances so the next real turn diffs correctly.
    assert outcome.battle_state["passing_rules"] == 2


def test_progress_hits_the_front_monster():
    state = _state([_mob(0, hp=2), _mob(1, hp=1)], passing_rules=1)
    outcome = BattleEngine().resolve_turn(_turn(state, rules_passing=2))
    assert [e["type"] for e in outcome.events] == ["player_attack"]
    attack = outcome.events[0]
    assert attack["target"] == 0
    assert attack["damage"] == 1
    assert attack["target_hp_after"] == 1
    assert attack["skill"] == "commit"
    assert outcome.battle_state["passing_rules"] == 2


def test_lethal_hit_appends_death():
    state = _state([_mob(0, hp=1), _mob(1, hp=1)])
    outcome = BattleEngine().resolve_turn(_turn(state, rules_passing=1))
    assert [e["type"] for e in outcome.events] == ["player_attack", "monster_death"]
    assert outcome.battle_state["monsters"][0]["alive"] is False
    assert outcome.battle_state["monsters"][1]["alive"] is True


def test_multi_rule_progress_cascades_damage_across_monsters():
    # A command that satisfies several rules at once deals that many points of
    # damage, spilling front-to-back so it can fell more than one monster.
    state = _state([_mob(0, hp=1), _mob(1, hp=2)], passing_rules=0)
    outcome = BattleEngine().resolve_turn(_turn(state, rules_passing=3))
    types = [e["type"] for e in outcome.events]
    assert types == ["player_attack", "monster_death", "player_attack", "monster_death"]
    assert outcome.events[0]["damage"] == 1
    assert outcome.events[2]["damage"] == 2
    assert all(not m["alive"] for m in outcome.battle_state["monsters"])


def test_no_progress_is_a_miss_and_the_rear_monster_attacks():
    state = _state([_mob(0), _mob(1, species="knight", tier="elite")], passing_rules=2)
    outcome = BattleEngine().resolve_turn(_turn(state, rules_passing=2))
    assert [e["type"] for e in outcome.events] == ["monster_attack"]
    assert outcome.events[0]["monster"] == 1
    assert outcome.events[0]["cause"] == "miss"


def test_failed_command_is_a_miss_and_keeps_the_measurement():
    state = _state([_mob(0)], passing_rules=3)
    outcome = BattleEngine().resolve_turn(_turn(state, processed=False, rules_passing=None))
    assert [e["type"] for e in outcome.events] == ["monster_attack"]
    # A failed command didn't change the repo; the measurement must not reset.
    assert outcome.battle_state["passing_rules"] == 3


def test_non_counted_noise_is_silent():
    # Non-git garbage is unprocessable and not counted: not a git mistake, so
    # the roster stays quiet (only counted git attempts draw an attack).
    state = _state([_mob(0)], passing_rules=1)
    outcome = BattleEngine().resolve_turn(
        _turn(state, counted=False, processed=False, rules_passing=None)
    )
    assert outcome.events == []
    assert outcome.battle_state["monsters"][0]["alive"] is True


def test_solve_is_a_finishing_blow_never_a_miss():
    state = _state([_mob(0, hp=3), _mob(1, hp=2)], passing_rules=5)
    outcome = BattleEngine().resolve_turn(_turn(state, solved=True, rules_passing=5))
    types = [e["type"] for e in outcome.events]
    assert types == [
        "player_attack",
        "monster_death",
        "player_attack",
        "monster_death",
        "encounter_cleared",
    ]
    assert outcome.events[0]["damage"] == 3
    assert all(not m["alive"] for m in outcome.battle_state["monsters"])


def test_defeat_event_rides_the_final_turn():
    state = _state([_mob(0, hp=2)])
    outcome = BattleEngine().resolve_turn(_turn(state, rules_passing=0, defeated=True))
    assert [e["type"] for e in outcome.events] == ["monster_attack", "player_defeat"]


def test_dead_roster_yields_no_combat_events():
    state = _state([_mob(0, hp=0, alive=False)])
    outcome = BattleEngine().resolve_turn(_turn(state, rules_passing=1))
    assert outcome.events == []


def test_input_state_is_never_mutated():
    state = _state([_mob(0, hp=1)])
    BattleEngine().resolve_turn(_turn(state, rules_passing=1))
    assert state["monsters"][0]["hp"] == 1
    assert state["monsters"][0]["alive"] is True


@pytest.mark.django_db
def test_battle_block_shape():
    clear_descriptor_cache()
    state = _state([_mob(0)])
    block = battle_block(state, [{"type": "player_defeat"}])
    assert block == {
        "schema_version": 1,
        "monsters": state["monsters"],
        "events": [{"type": "player_defeat"}],
    }
    assert battle_block({}) is None
    assert battle_block(None) is None


@pytest.mark.django_db
def test_battle_block_merges_asset_descriptor():
    clear_descriptor_cache()
    Asset.objects.create(
        kind=KIND_MONSTER,
        slug="slime",
        label="Slime",
        default_scale=1.2,
        config={"tier": "mob", "attack": {"kind": "melee", "hit_frame": 3}},
    )

    block = battle_block(_state([_mob(0, species="slime")]))

    descriptor = block["monsters"][0]["descriptor"]
    assert descriptor["slug"] == "slime"
    assert descriptor["label"] == "Slime"
    assert descriptor["scale"] == 1.2
    assert descriptor["attack"] == {"kind": "melee", "hit_frame": 3}
