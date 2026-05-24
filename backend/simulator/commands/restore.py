from __future__ import annotations

from simulator.commands.base import BaseCommandHandler, CommandOutcome, SimulatorCommandError
from simulator.intents import CommandIntent


class RestoreCommandHandler(BaseCommandHandler):
    command = "restore"

    def apply(self, runtime, state: dict, intent: CommandIntent) -> CommandOutcome:
        operation = intent.operations[0]
        paths = list(operation.params.get("paths") or [])
        if not paths:
            raise SimulatorCommandError("fatal: you must specify path(s) to restore", exit_code=128)
        if operation.name == "RestoreStaged":
            if "." in paths:
                paths = sorted(state.setdefault("staging", {}))
            unstaged: list[str] = []
            for path in paths:
                if path not in state.setdefault("staging", {}):
                    raise SimulatorCommandError(
                        f"error: pathspec '{path}' did not match any file(s) known to git",
                        exit_code=1,
                    )
                value = state["staging"].pop(path)
                state.setdefault("working_tree", {})[path] = value
                unstaged.append(path)
            return CommandOutcome(command="restore", details={"unstaged": unstaged})

        restored: list[str] = []
        if "." in paths:
            paths = sorted(
                path
                for path, value in state.setdefault("working_tree", {}).items()
                if runtime.normalizer.entry_status(value) != "ignored"
            )
        for path in paths:
            if path not in state.setdefault("working_tree", {}) and path not in runtime._head_tree(
                state
            ):
                raise SimulatorCommandError(
                    f"error: pathspec '{path}' did not match any file(s) known to git", exit_code=1
                )
            state["working_tree"].pop(path, None)
            conflicts = set(state.get("conflicts", []))
            conflicts.discard(path)
            state["conflicts"] = sorted(conflicts)
            restored.append(path)
        return CommandOutcome(command="restore", details={"restored": restored})
