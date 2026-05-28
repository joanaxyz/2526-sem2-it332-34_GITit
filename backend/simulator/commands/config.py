from __future__ import annotations

from simulator.commands.base import BaseCommandHandler, CommandOutcome
from simulator.intents import CommandIntent


class ConfigCommandHandler(BaseCommandHandler):
    command = "config"

    def apply(self, runtime, state: dict, intent: CommandIntent) -> CommandOutcome:
        list_operation = intent.first("ListConfig")
        if list_operation:
            config = state.get("config", {})
            lines = [f"{key}={value}" for key, value in sorted(config.items())]
            return CommandOutcome(command="config", stdout="\n".join(lines))

        operation = intent.first("SetConfig")
        key = operation.params["key"]
        value = operation.params["value"]
        state.setdefault("config", {})[key] = value
        metadata = {
            "last_config_scope": operation.params.get("scope", "global"),
            "last_config_key": key,
            "last_config_value": value,
        }
        if key == "merge.tool":
            metadata["configured_merge_tool"] = value
        runtime._set_operation_metadata(state, **metadata)
        return CommandOutcome(command="config", stdout="")
