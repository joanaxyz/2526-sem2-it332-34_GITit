from __future__ import annotations

from simulator.commands.base import BaseCommandHandler, CommandOutcome, SimulatorCommandError
from simulator.intents import CommandIntent


class BranchCommandHandler(BaseCommandHandler):
    command = "branch"

    def apply(self, runtime, state: dict, intent: CommandIntent) -> CommandOutcome:
        operation = intent.operations[0]
        if operation.name == "InspectBranchList":
            return CommandOutcome(
                command="branch", details={"verbose": bool(operation.params.get("verbose"))}
            )
        if operation.name == "DeleteBranch":
            return self._delete(runtime, state, operation.params)
        if operation.name == "CreateBranch":
            return self._create(runtime, state, operation.params)
        raise SimulatorCommandError("fatal: unsupported branch operation", exit_code=129)

    def _create(self, runtime, state: dict, params: dict) -> CommandOutcome:
        name = params["name"]
        branches = state.setdefault("branches", {})
        if name in branches:
            raise SimulatorCommandError(
                f"fatal: a branch named '{name}' already exists", exit_code=128
            )
        start_point = params.get("start_point")
        branches[name] = (
            runtime._resolve_ref(state, start_point) if start_point else runtime._head_commit(state)
        )
        return CommandOutcome(command="branch", details={"created": name})

    def _delete(self, runtime, state: dict, params: dict) -> CommandOutcome:
        name = params["name"]
        branches = state.setdefault("branches", {})
        if name == runtime._head_branch(state):
            raise SimulatorCommandError(
                f"error: Cannot delete branch '{name}' checked out", exit_code=1
            )
        if name not in branches:
            raise SimulatorCommandError(f"error: branch '{name}' not found.", exit_code=1)
        target = branches.pop(name)
        return CommandOutcome(
            command="branch",
            details={"deleted": name, "target": target, "force": params.get("force")},
        )
