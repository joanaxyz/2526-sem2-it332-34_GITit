from __future__ import annotations

from simulator.commands.base import BaseCommandHandler, CommandOutcome
from simulator.intents import CommandIntent


class CheckIgnoreCommandHandler(BaseCommandHandler):
    command = "check-ignore"

    def apply(self, runtime, state: dict, intent: CommandIntent) -> CommandOutcome:
        operation = intent.first("InspectIgnoredPath")
        return CommandOutcome(
            command="check-ignore",
            details={"path": (operation.params if operation else {}).get("path")},
        )
