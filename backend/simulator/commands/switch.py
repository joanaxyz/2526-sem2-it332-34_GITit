from __future__ import annotations

from simulator.commands.base import BaseCommandHandler, SimulatorCommandError
from simulator.commands.checkout import create_and_switch, switch_to_ref
from simulator.intents import CommandIntent


class SwitchCommandHandler(BaseCommandHandler):
    command = "switch"

    def apply(self, runtime, state: dict, intent: CommandIntent):
        operation = intent.operations[0]
        if operation.name == "CreateAndSwitchBranch":
            outcome = create_and_switch(runtime, state, operation.params)
            outcome.command = "switch"
            return outcome
        if operation.name == "SwitchBranch":
            outcome = switch_to_ref(runtime, state, operation.params["name"])
            outcome.command = "switch"
            return outcome
        raise SimulatorCommandError("fatal: unsupported switch operation", exit_code=129)
