from __future__ import annotations

from simulator.commands.base import BaseCommandHandler, CommandOutcome
from simulator.intents import CommandIntent


class ShowCommandHandler(BaseCommandHandler):
    command = "show"

    def apply(self, runtime, state: dict, intent: CommandIntent) -> CommandOutcome:
        operation = intent.first("InspectObject")
        target = (operation.params if operation else {}).get("target") or "HEAD"
        if target == "HEAD":
            target = runtime._head_commit(state)
        if not runtime._commit_by_id(state, target):
            return CommandOutcome(
                command="show",
                details={"target": target},
                exit_code=128,
                stderr="fatal: bad revision 'HEAD'"
                if target is None
                else f"fatal: bad object {target}",
            )
        return CommandOutcome(
            command="show",
            details={
                "target": target,
                "name_only": bool((operation.params if operation else {}).get("name_only")),
            },
        )
