from __future__ import annotations

from simulator.commands.base import BaseCommandHandler, CommandOutcome
from simulator.intents import CommandIntent


class LsFilesCommandHandler(BaseCommandHandler):
    command = "ls-files"

    def apply(self, runtime, state: dict, intent: CommandIntent) -> CommandOutcome:
        return CommandOutcome(command="ls-files")
