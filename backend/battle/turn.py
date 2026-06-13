"""Battle integration seam for the command submit paths.

The pure engine (battle.engine) and the initial-state builders (battle.state)
know nothing about runs or attempts. Both submit paths, however, share the same
three-step wiring: lazily initialize `battle_state` on the row, resolve one
turn, and write the new state back. That wiring lives here, once, so the
challenge and adventure paths can never drift.
"""

from __future__ import annotations

from typing import Callable

from battle.engine import BattleEngine, TurnInput


def apply_battle_turn(
    holder,
    build_initial: Callable[[], dict],
    *,
    counted: bool,
    processed: bool,
    solved: bool,
    rules_passing: int | None,
    skill: str,
    defeated: bool,
) -> tuple[list[dict], bool]:
    """Resolve one battle turn for `holder` (a ChallengeRun / AdventureLevelAttempt).

    Lazily builds `holder.battle_state` for pre-battle rows, runs the engine,
    writes the new state back, and returns ``(events, changed)``. The state
    rides the save the submit path already performs — no extra query.
    """
    if not holder.battle_state:
        holder.battle_state = build_initial()
    outcome = BattleEngine().resolve_turn(
        TurnInput(
            battle_state=holder.battle_state,
            counted=counted,
            processed=processed,
            solved=solved,
            rules_passing=rules_passing,
            skill=skill,
            defeated=defeated,
        )
    )
    holder.battle_state = outcome.battle_state
    return outcome.events, outcome.changed
