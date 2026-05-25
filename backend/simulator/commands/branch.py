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
        raise SimulatorCommandError(
            "fatal: only branch listing is supported in Module 1",
            exit_code=129,
        )
