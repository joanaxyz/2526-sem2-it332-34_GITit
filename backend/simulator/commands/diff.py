from __future__ import annotations

from simulator.commands.base import BaseCommandHandler, CommandOutcome
from simulator.intents import CommandIntent


class DiffCommandHandler(BaseCommandHandler):
    command = "diff"

    def apply(self, runtime, state: dict, intent: CommandIntent) -> CommandOutcome:
        operation = intent.first("InspectDiff")
        return CommandOutcome(command="diff", details=operation.params if operation else {})
