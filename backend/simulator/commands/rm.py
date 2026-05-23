from __future__ import annotations

import copy

from simulator.commands.base import BaseCommandHandler, CommandOutcome, SimulatorCommandError
from simulator.intents import CommandIntent


class RmCommandHandler(BaseCommandHandler):
    command = "rm"

    def apply(self, runtime, state: dict, intent: CommandIntent) -> CommandOutcome:
        operation = intent.operations[0]
        paths = list(operation.params.get("paths") or [])
        cached = bool(operation.params.get("cached"))
        if not paths:
            raise SimulatorCommandError("fatal: No pathspec was given.", exit_code=128)

        staging = state.setdefault("staging", {})
        working_tree = state.setdefault("working_tree", {})
        head_tree = runtime._head_tree(state)
        removed: list[str] = []
        for path in paths:
            if path not in head_tree and path not in staging and path not in working_tree:
                raise SimulatorCommandError(
                    f"fatal: pathspec '{path}' did not match any files", exit_code=128
                )
            staging[path] = "deleted"
            if cached:
                existing = working_tree.get(path)
                working_tree[path] = {
                    "status": "ignored",
                    "content": copy.deepcopy(
                        existing if existing is not None else head_tree.get(path)
                    ),
                    "preserved": True,
                }
            else:
                working_tree.pop(path, None)
            removed.append(path)
        runtime._set_operation_metadata(state, last_rm_cached_paths=removed if cached else [])
        return CommandOutcome(command="rm", details={"paths": removed, "cached": cached})
