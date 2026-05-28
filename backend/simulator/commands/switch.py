from __future__ import annotations

from simulator.commands.base import BaseCommandHandler, CommandOutcome, SimulatorCommandError
from simulator.intents import CommandIntent


class SwitchCommandHandler(BaseCommandHandler):
    command = "switch"

    def apply(self, runtime, state: dict, intent: CommandIntent) -> CommandOutcome:
        create = intent.first("CreateAndSwitchBranch")
        if create:
            name = str(create.params.get("branch") or "")
            if not name:
                raise SimulatorCommandError("fatal: branch name required", exit_code=128)
            start_point = create.params.get("start_point")
            head_commit = self._resolve_start_point(runtime, state, start_point) if start_point else runtime._head_commit(state)
            if start_point and not head_commit:
                raise SimulatorCommandError(f"fatal: invalid reference: {start_point}", exit_code=128)
            state.setdefault("branches", {})[name] = head_commit
            state["head"] = {"type": "branch", "name": name, "target": head_commit}
            runtime._set_operation_metadata(
                state,
                last_switch_branch=name,
                last_switch_created=True,
            )
            runtime._record_reflog(state, head_commit, f"switch: create {name}")
            return CommandOutcome(command="switch", stdout=f"Switched to a new branch '{name}'")

        move = intent.first("SwitchBranch")
        if move is None:
            raise SimulatorCommandError("fatal: unsupported switch operation", exit_code=129)
        name = str(move.params.get("branch") or "")
        if name not in state.get("branches", {}):
            raise SimulatorCommandError(f"fatal: invalid reference: {name}", exit_code=128)
        state["head"] = {
            "type": "branch",
            "name": name,
            "target": state["branches"][name],
        }
        runtime._set_operation_metadata(
            state,
            last_switch_branch=name,
            last_switch_created=False,
        )
        runtime._record_reflog(state, state["branches"][name], f"switch: {name}")
        return CommandOutcome(command="switch", stdout=f"Switched to branch '{name}'")

    def _resolve_start_point(self, runtime, state: dict, start_point: str | None) -> str | None:
        if not start_point:
            return runtime._head_commit(state)
        if start_point in state.get("branches", {}):
            return state["branches"][start_point]
        if start_point in state.get("remote_branches", {}):
            return state["remote_branches"][start_point]
        if isinstance(start_point, str) and start_point.startswith("HEAD@{") and start_point.endswith("}"):
            try:
                index = int(start_point[6:-1])
            except ValueError:
                return None
            reflog = state.get("reflog", [])
            if 0 <= index < len(reflog):
                return reflog[-(index + 1)].get("target")
            return None
        if runtime._commit_by_id(state, start_point):
            return start_point
        return None
