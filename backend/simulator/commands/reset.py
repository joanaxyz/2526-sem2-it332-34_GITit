from __future__ import annotations

from simulator.commands.base import BaseCommandHandler, CommandOutcome, SimulatorCommandError
from simulator.intents import CommandIntent


class ResetCommandHandler(BaseCommandHandler):
    command = "reset"

    def apply(self, runtime, state: dict, intent: CommandIntent) -> CommandOutcome:
        operation = intent.operations[0]
        if operation.name == "UnstagePaths":
            paths = list(operation.params.get("paths") or [])
            unstaged: list[str] = []
            for path in paths:
                if path not in state.setdefault("staging", {}):
                    raise SimulatorCommandError(
                        f"fatal: ambiguous argument '{path}'", exit_code=128
                    )
                value = state["staging"].pop(path)
                state.setdefault("working_tree", {})[path] = value
                unstaged.append(path)
            return CommandOutcome(command="reset", details={"unstaged": unstaged})

        mode = operation.params.get("mode") or "mixed"
        target = runtime._resolve_reset_target(state, operation.params.get("target"))
        current = runtime._head_commit(state)
        current_tree = runtime._tree_for_commit(state, current)
        target_tree = runtime._tree_for_commit(state, target)
        runtime._set_head_commit(state, target)
        if mode == "hard":
            state["staging"] = {}
            state["working_tree"] = {}
            state["conflicts"] = []
        elif mode == "soft":
            state["staging"] = runtime._diff_trees_as_entries(target_tree, current_tree)
        else:
            state["staging"] = {}
            state.setdefault("working_tree", {}).update(
                runtime._diff_trees_as_entries(target_tree, current_tree)
            )
        runtime._set_operation_metadata(
            state,
            last_reset_mode=mode,
            last_reset_from=current,
            last_reset_to=target,
        )
        return CommandOutcome(
            command="reset", details={"mode": mode, "from": current, "to": target}
        )
