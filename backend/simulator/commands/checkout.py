from __future__ import annotations

from simulator.commands.base import BaseCommandHandler, CommandOutcome, SimulatorCommandError
from simulator.intents import CommandIntent


class CheckoutCommandHandler(BaseCommandHandler):
    command = "checkout"

    def apply(self, runtime, state: dict, intent: CommandIntent) -> CommandOutcome:
        operation = intent.operations[0]
        if operation.name == "CreateAndSwitchBranch":
            return create_and_switch(runtime, state, operation.params)
        if operation.name == "SwitchBranch":
            return switch_to_ref(runtime, state, operation.params["name"])
        raise SimulatorCommandError("fatal: unsupported checkout operation", exit_code=129)


def create_and_switch(runtime, state: dict, params: dict) -> CommandOutcome:
    name = params["name"]
    branches = state.setdefault("branches", {})
    if name in branches:
        raise SimulatorCommandError(f"fatal: a branch named '{name}' already exists", exit_code=128)
    start_point = params.get("start_point")
    branches[name] = (
        runtime._resolve_ref(state, start_point) if start_point else runtime._head_commit(state)
    )
    state["head"] = {"type": "branch", "name": name, "target": branches[name]}
    runtime.normalizer.normalize_head(state)
    return CommandOutcome(
        command="checkout", details={"created": name, "switched": name, "new": True}
    )


def switch_to_ref(runtime, state: dict, name: str) -> CommandOutcome:
    branches = state.setdefault("branches", {})
    if name in branches:
        state["head"] = {"type": "branch", "name": name, "target": branches[name]}
        runtime.normalizer.normalize_head(state)
        return CommandOutcome(command="checkout", details={"switched": name, "new": False})
    try:
        target = runtime._resolve_ref(state, name)
    except ValueError as exc:
        raise SimulatorCommandError(
            f"error: pathspec '{name}' did not match any file(s) known to git", exit_code=1
        ) from exc
    state["head"] = {"type": "detached", "target": target}
    return CommandOutcome(command="checkout", details={"detached": target})
