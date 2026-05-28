from __future__ import annotations

from simulator.commands.base import BaseCommandHandler, CommandOutcome, SimulatorCommandError
from simulator.intents import CommandIntent


class BranchCommandHandler(BaseCommandHandler):
    command = "branch"

    def apply(self, runtime, state: dict, intent: CommandIntent) -> CommandOutcome:
        operation = intent.operations[0]
        if operation.name == "InspectBranchList":
            return CommandOutcome(
                command="branch",
                details={
                    "verbose": bool(operation.params.get("verbose")),
                    "all": bool(operation.params.get("all")),
                },
            )
        if operation.name == "CreateBranch":
            return self._create(runtime, state, operation.params)
        if operation.name == "DeleteBranch":
            return self._delete(runtime, state, operation.params["name"], force=bool(operation.params.get("force")))
        raise SimulatorCommandError("fatal: unsupported branch operation", exit_code=129)

    def _create(self, runtime, state: dict, params: dict) -> CommandOutcome:
        name = params["name"]
        start_point = params.get("start_point")
        branches = state.setdefault("branches", {})

        if name in branches:
            raise SimulatorCommandError(
                f"fatal: A branch named '{name}' already exists.",
                exit_code=128,
            )

        if start_point:
            target_id = self._resolve_ref(state, start_point)
            if target_id is None:
                raise SimulatorCommandError(
                    f"fatal: invalid reference: {start_point}",
                    exit_code=128,
                )
        else:
            target_id = runtime._head_commit(state)

        branches[name] = target_id
        runtime._set_operation_metadata(state, last_branch_created=name)
        return CommandOutcome(command="branch", details={"created": name, "target": target_id})

    def _delete(self, runtime, state: dict, name: str, *, force: bool) -> CommandOutcome:
        branches = state.get("branches", {})
        if name not in branches:
            raise SimulatorCommandError(f"error: branch '{name}' not found.", exit_code=1)

        current = runtime._head_branch(state)
        if name == current:
            raise SimulatorCommandError(
                f"error: Cannot delete branch '{name}' checked out locally.", exit_code=1
            )

        target = branches[name]
        if not force:
            from simulator.commands.merge import MergeCommandHandler
            head_commit = runtime._head_commit(state)
            if not MergeCommandHandler()._is_ancestor(state, target, head_commit):
                raise SimulatorCommandError(
                    f"error: The branch '{name}' is not fully merged.\n"
                    f"If you are sure you want to delete it, run 'git branch -D {name}'.",
                    exit_code=1,
                )

        del branches[name]
        runtime._set_operation_metadata(state, last_branch_deleted=name)
        return CommandOutcome(command="branch", details={"deleted": name, "target": target})

    def _resolve_ref(self, state: dict, ref: str) -> str | None:
        if ref in state.get("branches", {}):
            return state["branches"][ref]
        if ref in state.get("remote_branches", {}):
            return state["remote_branches"][ref]
        return ref if any(c.get("id") == ref for c in state.get("commits", [])) else None
