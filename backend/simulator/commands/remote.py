from __future__ import annotations

from simulator.commands.base import BaseCommandHandler, CommandOutcome, SimulatorCommandError
from simulator.intents import CommandIntent


class RemoteCommandHandler(BaseCommandHandler):
    command = "remote"

    def apply(self, runtime, state: dict, intent: CommandIntent) -> CommandOutcome:
        operation = intent.operations[0]
        remotes = state.setdefault("remotes", {})
        if operation.name == "InspectRemoteList":
            return CommandOutcome(
                command="remote", details={"verbose": bool(operation.params.get("verbose"))}
            )
        if operation.name == "AddRemote":
            name = operation.params["name"]
            if name in remotes:
                raise SimulatorCommandError(f"error: remote {name} already exists.", exit_code=3)
            remotes[name] = operation.params["url"]
            return CommandOutcome(command="remote", details={"added": name, "url": remotes[name]})
        if operation.name == "RemoveRemote":
            name = operation.params["name"]
            if name not in remotes:
                raise SimulatorCommandError(f"error: No such remote: '{name}'", exit_code=2)
            remotes.pop(name)
            for key in list(state.setdefault("upstream_tracking", {})):
                if state["upstream_tracking"][key].startswith(f"{name}/"):
                    state["upstream_tracking"].pop(key)
            for key in list(state.setdefault("remote_branches", {})):
                if key.startswith(f"{name}/"):
                    state["remote_branches"].pop(key)
            return CommandOutcome(command="remote", details={"removed": name})
        if operation.name == "RenameRemote":
            old = operation.params["old"]
            new = operation.params["new"]
            if old not in remotes:
                raise SimulatorCommandError(f"error: No such remote: '{old}'", exit_code=2)
            if new in remotes:
                raise SimulatorCommandError(f"error: remote {new} already exists.", exit_code=3)
            remotes[new] = remotes.pop(old)
            remote_branches = state.setdefault("remote_branches", {})
            for key in list(remote_branches):
                if key.startswith(f"{old}/"):
                    remote_branches[f"{new}/{key.split('/', 1)[1]}"] = remote_branches.pop(key)
            upstream = state.setdefault("upstream_tracking", {})
            for branch, value in list(upstream.items()):
                if value.startswith(f"{old}/"):
                    upstream[branch] = f"{new}/{value.split('/', 1)[1]}"
            return CommandOutcome(command="remote", details={"renamed": old, "new": new})
        raise SimulatorCommandError("fatal: unsupported remote operation", exit_code=129)
