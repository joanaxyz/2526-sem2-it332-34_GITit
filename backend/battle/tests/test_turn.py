"""Tests for the battle integration seam (no Django)."""

from types import SimpleNamespace

from battle.turn import apply_battle_turn


def _holder(battle_state=None):
    return SimpleNamespace(battle_state=battle_state if battle_state is not None else {})


def _living_state():
    return {
        "schema_version": 1,
        "monsters": [{"id": 0, "species": "slime", "tier": "mob", "hp": 2, "max_hp": 2, "alive": True}],
        "passing_rules": 0,
    }


def test_lazily_initializes_empty_battle_state():
    holder = _holder({})
    calls = []

    def build():
        calls.append(True)
        return _living_state()

    apply_battle_turn(
        holder, build, counted=False, processed=True, solved=False,
        rules_passing=0, skill="default", defeated=False,
    )
    assert calls == [True]
    assert holder.battle_state["monsters"][0]["alive"] is True


def test_existing_state_is_not_rebuilt():
    holder = _holder(_living_state())

    def build():
        raise AssertionError("build_initial must not run when state already exists")

    events, changed = apply_battle_turn(
        holder, build, counted=True, processed=True, solved=False,
        rules_passing=1, skill="commit", defeated=False,
    )
    # A counted command with new progress hits the front monster.
    assert [e["type"] for e in events] == ["player_attack"]
    assert changed is True
    assert holder.battle_state["monsters"][0]["hp"] == 1


def test_free_action_reports_no_change():
    holder = _holder(_living_state())
    events, changed = apply_battle_turn(
        holder, _living_state, counted=False, processed=True, solved=False,
        rules_passing=0, skill="default", defeated=False,
    )
    assert events == []
    assert changed is False
