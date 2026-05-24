from __future__ import annotations

from simulator.commands.base import BaseCommandHandler, CommandOutcome
from simulator.intents import CommandIntent


class StatusCommandHandler(BaseCommandHandler):
    command = "status"

    def apply(self, runtime, state: dict, intent: CommandIntent) -> CommandOutcome:
        operation = intent.first("InspectStatus")
        return CommandOutcome(
            command="status",
            details={"short": bool((operation.params if operation else {}).get("short"))},
        )
