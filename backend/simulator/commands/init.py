from __future__ import annotations

from simulator.commands.base import BaseCommandHandler, CommandOutcome
from simulator.intents import CommandIntent


class InitCommandHandler(BaseCommandHandler):
    command = "init"

    def apply(self, runtime, state: dict, intent: CommandIntent) -> CommandOutcome:
        operation = intent.first("InitializeRepository")
        params = operation.params if operation else {}
        initial_branch = params.get("initial_branch") or "main"
        directory = params.get("directory")

        state["repository_initialized"] = True
        state["remotes"] = {}
        state["remote_branches"] = {}
        state["upstream_tracking"] = {}
        state["branches"] = {initial_branch: None}
        state["head"] = {"type": "branch", "name": initial_branch, "target": None}
        runtime._set_operation_metadata(
            state,
            last_init_current_directory=directory is None,
            last_init_initial_branch=initial_branch,
        )
        if directory:
            runtime._set_operation_metadata(state, last_init_directory=directory)
        else:
            runtime._clear_operation_metadata(state, "last_init_directory")
        return CommandOutcome(
            command="init",
            details={
                "initial_branch": initial_branch,
                "directory": directory,
                "quiet": bool(params.get("quiet")),
            },
        )
