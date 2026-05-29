from __future__ import annotations

import copy

from simulator.commands.base import BaseCommandHandler, CommandOutcome, SimulatorCommandError
from simulator.intents import CommandIntent


class CheckoutCommandHandler(BaseCommandHandler):
    command = "checkout"

    def apply(self, runtime, state: dict, intent: CommandIntent) -> CommandOutcome:
        create_op = intent.first("CreateAndSwitchBranch")
        if create_op is not None:
            from simulator.commands.switch import SwitchCommandHandler
            return SwitchCommandHandler()._create_and_switch(runtime, state, create_op.params)

        operation = intent.first("CheckoutConflictSide")
        if operation is None:
            raise SimulatorCommandError(
                "git checkout in this simulator supports -b to create a branch, or --ours/--theirs for conflicted files.",
                exit_code=129,
            )

        side = operation.params["side"]
        paths = list(operation.params.get("paths") or [])
        if not state.get("conflicts"):
            raise SimulatorCommandError(
                "fatal: --ours/--theirs can only be used while resolving merge conflicts.",
                exit_code=128,
            )

        conflicts = set(state.get("conflicts") or [])
        updated: list[str] = []
        for path in paths:
            if path not in conflicts:
                raise SimulatorCommandError(
                    f"error: path '{path}' is not an unmerged file.",
                    exit_code=1,
                )
            content = self._conflict_side(state, path, side)
            state.setdefault("working_tree", {})[path] = (
                "deleted"
                if content is None
                else {
                    "status": "modified",
                    "content": copy.deepcopy(content),
                }
            )
            updated.append(path)

        runtime._set_operation_metadata(
            state,
            last_checkout_conflict_side=side,
            last_checkout_conflict_paths=updated,
        )
        return CommandOutcome(
            command="checkout",
            stdout=(
                f"Updated {len(updated)} path(s) from {side}.\n"
                "The paths are still unmerged until you stage the resolved file."
            ),
        )

    def _conflict_side(self, state: dict, path: str, side: str) -> object:
        details = state.get("conflict_details") or {}
        detail = details.get(path)
        if isinstance(detail, dict) and side in detail:
            return copy.deepcopy(detail.get(side))

        entry = (state.get("working_tree") or {}).get(path)
        if isinstance(entry, dict) and side in entry:
            return copy.deepcopy(entry.get(side))

        raise SimulatorCommandError(
            f"error: conflict side '{side}' is not available for {path}.",
            exit_code=1,
        )
