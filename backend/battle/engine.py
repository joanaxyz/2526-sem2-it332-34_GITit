"""Pure turn resolution: no I/O, no ORM.

A battle turn is a function over signals the submit paths already compute:
command classification (counted?), execution success (processed?), the
evaluation outcome (solved? how many rules pass now?). The damage signal is
the count of passing evaluation rules - "distance to target" - which credits
intermediate progress (e.g. the `git add` before the `git commit`).

Turn rules:
- Diagnostics / non-git noise: free, no turn, no events.
- Solved: finishing blow - every living monster dies, never a miss.
- HIT (counted + processed + more rules passing than last turn): damage equal
  to the number of newly satisfied rules, dealt front-to-back across the roster.
  Total HP equals the rule count, so a clean run kills everything exactly as the
  repo reaches target.
- MISS (counted but failed, or no new progress): one monster attacks. Pure
  drama - the real cost was the counted command (the player's mana).
- Defeat (budget exhausted, decided by the caller): `player_defeat` appended.

The player has no HP field anywhere; see battle/constants.py.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field

from battle.constants import (
    CAUSE_MISS,
    EVENT_ENCOUNTER_CLEARED,
    EVENT_MONSTER_ATTACK,
    EVENT_MONSTER_DEATH,
    EVENT_PLAYER_ATTACK,
    EVENT_PLAYER_DEFEAT,
)


@dataclass(frozen=True)
class TurnInput:
    battle_state: dict
    counted: bool
    processed: bool
    solved: bool
    # len(EvaluationOutcome.passed_rules); None when the command never reached
    # evaluation (unprocessable input) - treated as "no new progress".
    rules_passing: int | None
    # Command family for the frontend effect registry ("commit", "merge", ).
    skill: str = "default"
    # Budget exhausted by this command (the caller owns that decision).
    defeated: bool = False


@dataclass(frozen=True)
class TurnOutcome:
    battle_state: dict
    events: list[dict] = field(default_factory=list)

    @property
    def changed(self) -> bool:
        return bool(self.events)


class BattleEngine:
    def resolve_turn(self, turn: TurnInput) -> TurnOutcome:
        # deepcopy keeps the turn pure; the helpers below mutate the copied
        # monster dicts in place (they live inside `state["monsters"]`).
        state = deepcopy(turn.battle_state)
        living = [m for m in state.get("monsters", []) if m.get("alive")]

        if turn.solved:
            events = _finishing_blow(living, turn.skill)
        elif living:
            events = _combat(living, turn, int(state.get("passing_rules", 0)))
        else:
            events = []

        # Remember the measurement for the next turn's progress delta. Only
        # processed commands move it: a failed command didn't change the repo.
        if turn.processed and turn.rules_passing is not None:
            state["passing_rules"] = turn.rules_passing

        if turn.defeated:
            events.append({"type": EVENT_PLAYER_DEFEAT})

        return TurnOutcome(battle_state=state, events=events)


def _finishing_blow(living: list[dict], skill: str) -> list[dict]:
    """Solve: every living monster dies, never a miss."""
    events: list[dict] = []
    for monster in living:
        remaining = int(monster.get("hp", 0))
        monster["hp"] = 0
        monster["alive"] = False
        events.append(
            {
                "type": EVENT_PLAYER_ATTACK,
                "skill": skill,
                "target": monster["id"],
                "damage": remaining,
                "target_hp_after": 0,
            }
        )
        events.append({"type": EVENT_MONSTER_DEATH, "monster": monster["id"]})
    events.append({"type": EVENT_ENCOUNTER_CLEARED})
    return events


def _combat(living: list[dict], turn: TurnInput, previous_rules: int) -> list[dict]:
    """One unsolved turn against a living roster. Only counted commands engage:
    diagnostics and non-git noise are free and silent. A counted command hits
    the front monster(s) by the number of newly satisfied rules, else draws a
    miss from the rear (a failed/invalid git command still counts, so mistakes
    always get attacked)."""
    if not turn.counted:
        return []
    delta = 0
    if turn.processed and turn.rules_passing is not None:
        delta = turn.rules_passing - previous_rules
    if delta > 0:
        return _hit(living, delta, turn.skill)
    return _miss(living[-1])


def _hit(living: list[dict], damage: int, skill: str) -> list[dict]:
    """Progress: `damage` (newly satisfied rule count) spread front-to-back, so
    a command that clears several rules can fell more than one monster."""
    events: list[dict] = []
    remaining = damage
    for target in living:
        if remaining <= 0:
            break
        dealt = min(remaining, int(target.get("hp", 0)))
        if dealt <= 0:
            continue
        target["hp"] = int(target.get("hp", 0)) - dealt
        remaining -= dealt
        events.append(
            {
                "type": EVENT_PLAYER_ATTACK,
                "skill": skill,
                "target": target["id"],
                "damage": dealt,
                "target_hp_after": target["hp"],
            }
        )
        if target["hp"] == 0:
            target["alive"] = False
            events.append({"type": EVENT_MONSTER_DEATH, "monster": target["id"]})
    return events


def _miss(attacker: dict) -> list[dict]:
    """No new progress: the roster's rear (an elite/boss when present) takes the
    shot. Pure drama - the real cost was the counted command (the mana)."""
    return [{"type": EVENT_MONSTER_ATTACK, "monster": attacker["id"], "cause": CAUSE_MISS}]
