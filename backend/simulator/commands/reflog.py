from __future__ import annotations

from simulator.commands.base import BaseCommandHandler, CommandOutcome
from simulator.intents import CommandIntent


class ReflogCommandHandler(BaseCommandHandler):
    command = "reflog"

    def apply(self, runtime, state: dict, intent: CommandIntent) -> CommandOutcome:
        return CommandOutcome(command="reflog")
