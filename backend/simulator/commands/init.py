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
        quiet = bool(params.get("quiet"))
        reinitialized = bool(state.get("repository_initialized"))

        state["repository_initialized"] = True
        if reinitialized:
            branches = state.setdefault("branches", {})
            head = state.setdefault("head", {"type": "branch", "name": initial_branch})
            if not branches:
                branches[initial_branch] = None
            if head.get("type") != "branch" or not head.get("name"):
                state["head"] = {"type": "branch", "name": next(iter(branches)), "target": None}
        else:
            state["remotes"] = {}
            state["remote_branches"] = {}
            state["upstream_tracking"] = {}
            state["branches"] = {initial_branch: None}
            state["head"] = {"type": "branch", "name": initial_branch, "target": None}
        runtime._set_operation_metadata(
            state,
            last_init_current_directory=directory is None,
            last_init_directory=directory,
            last_init_initial_branch=initial_branch,
            last_init_quiet=quiet,
            last_init_reinitialized=reinitialized,
        )
        return CommandOutcome(
            command="init",
            details={
                "initial_branch": initial_branch,
                "directory": directory,
                "quiet": quiet,
                "reinitialized": reinitialized,
            },
        )
