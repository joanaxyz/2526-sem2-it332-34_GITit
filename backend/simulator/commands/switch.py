from __future__ import annotations

from simulator.commands.base import BaseCommandHandler, CommandOutcome, SimulatorCommandError
from simulator.intents import CommandIntent


class SwitchCommandHandler(BaseCommandHandler):
    command = "switch"

    def apply(self, runtime, state: dict, intent: CommandIntent) -> CommandOutcome:
        operation = intent.operations[0]
        if operation.name == "CreateAndSwitchBranch":
            return self._create_and_switch(runtime, state, operation.params)
        if operation.name == "DetachHead":
            return self._detach(runtime, state, operation.params)
        return self._switch(runtime, state, operation.params["name"])

    def _switch(self, runtime, state: dict, name: str) -> CommandOutcome:
        branches = state.setdefault("branches", {})
        if name not in branches:
            remote_key = f"origin/{name}"
            if remote_key in state.get("remote_branches", {}):
                branches[name] = state["remote_branches"][remote_key]
                state.setdefault("upstream_tracking", {})[name] = remote_key
            else:
                raise SimulatorCommandError(
                    f"error: pathspec '{name}' did not match any file(s) known to git",
                    exit_code=1,
                )

        if state.get("staging") or state.get("working_tree"):
            raise SimulatorCommandError(
                "error: Your local changes to the following files would be overwritten by checkout.\n"
                "Please commit your changes or stash them before you switch branches.",
                exit_code=1,
            )

        old_branch = runtime._head_branch(state)
        state["head"] = {"type": "branch", "name": name}
        target = branches.get(name)
        runtime._record_reflog(state, target, f"switch: moving from {old_branch or 'HEAD'} to {name}")
        runtime._set_operation_metadata(state, last_switch_branch=name, last_switched_to=name)
        return CommandOutcome(command="switch", stdout=f"Switched to branch '{name}'")

    def _create_and_switch(self, runtime, state: dict, params: dict) -> CommandOutcome:
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

        old_branch = runtime._head_branch(state)
        branches[name] = target_id
        state["head"] = {"type": "branch", "name": name}
        runtime._record_reflog(state, target_id, f"switch: moving from {old_branch or 'HEAD'} to {name}")
        runtime._set_operation_metadata(
            state,
            last_switch_branch=name,
            last_branch_created=name,
            last_switched_to=name,
        )
        return CommandOutcome(command="switch", stdout=f"Switched to a new branch '{name}'")

    def _detach(self, runtime, state: dict, params: dict) -> CommandOutcome:
        target = params.get("target", "HEAD")
        target_id = self._resolve_ref(state, target)
        if target_id is None:
            raise SimulatorCommandError(f"fatal: invalid reference: {target}", exit_code=128)
        state["head"] = {"type": "detached", "target": target_id}
        runtime._record_reflog(state, target_id, f"switch: moving to {target}")
        runtime._set_operation_metadata(state, detached_head=True, last_detached_to=target_id)
        short = target_id[:7] if target_id else target
        return CommandOutcome(command="switch", stdout=f"HEAD is now at {short}")

    def _resolve_ref(self, state: dict, ref: str) -> str | None:
        if ref in state.get("branches", {}):
            return state["branches"][ref]
        if ref in state.get("remote_branches", {}):
            return state["remote_branches"][ref]
        return ref if any(c.get("id") == ref for c in state.get("commits", [])) else None
