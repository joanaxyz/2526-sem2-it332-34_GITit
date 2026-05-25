from __future__ import annotations

from simulator.commands.base import BaseCommandHandler, CommandOutcome, SimulatorCommandError
from simulator.intents import CommandIntent


class RemoteCommandHandler(BaseCommandHandler):
    command = "remote"

    def apply(self, runtime, state: dict, intent: CommandIntent) -> CommandOutcome:
        operation = intent.operations[0]
        if operation.name == "InspectRemoteList":
            return CommandOutcome(
                command="remote", details={"verbose": bool(operation.params.get("verbose"))}
            )
        raise SimulatorCommandError("fatal: unsupported remote operation", exit_code=129)
