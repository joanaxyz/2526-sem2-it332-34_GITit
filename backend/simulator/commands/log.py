from __future__ import annotations

from simulator.commands.base import BaseCommandHandler, CommandOutcome
from simulator.intents import CommandIntent


class LogCommandHandler(BaseCommandHandler):
    command = "log"

    def apply(self, runtime, state: dict, intent: CommandIntent) -> CommandOutcome:
        operation = intent.first("InspectLog")
        if not state.get("commits"):
            return CommandOutcome(
                command="log",
                details=operation.params if operation else {},
                exit_code=128,
                stderr=f"fatal: your current branch '{runtime._head_branch(state) or 'HEAD'}' does not have any commits yet",
            )
        return CommandOutcome(command="log", details=operation.params if operation else {})
