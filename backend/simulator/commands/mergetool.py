from __future__ import annotations

import copy

from simulator.commands.base import BaseCommandHandler, CommandOutcome, SimulatorCommandError
from simulator.intents import CommandIntent


class MergetoolCommandHandler(BaseCommandHandler):
    command = "mergetool"

    def apply(self, runtime, state: dict, intent: CommandIntent) -> CommandOutcome:
        operation = intent.first("RunMergeTool")
        conflicts = list(state.get("conflicts") or [])
        if not conflicts:
            raise SimulatorCommandError("No files need merging", exit_code=1)
        requested = list(operation.params.get("paths") or conflicts)
        selected = [path for path in conflicts if path in requested]
        if not selected:
            raise SimulatorCommandError("No files need merging", exit_code=1)

        configured_tool = (
            operation.params.get("tool")
            or state.get("config", {}).get("merge.tool")
            or state.get("operation_metadata", {}).get("configured_merge_tool")
            or "vimdiff"
        )
        for path in selected:
            resolution = self._resolution_for(runtime, state, path)
            state.setdefault("staging", {})[path] = {
                "status": "modified",
                "content": resolution,
            }
            state.setdefault("working_tree", {}).pop(path, None)
        remaining = sorted(set(conflicts) - set(selected))
        state["conflicts"] = remaining
        runtime._set_operation_metadata(
            state,
            last_mergetool_tool=configured_tool,
            last_mergetool_paths=selected,
        )
        return CommandOutcome(
            command="mergetool",
            stdout=f"Resolved {len(selected)} file(s) with {configured_tool}.",
        )

    def _resolution_for(self, runtime, state: dict, path: str) -> object:
        authored = (state.get("merge_resolutions") or {}).get(path)
        if authored is not None:
            return copy.deepcopy(authored)
        entry = state.get("working_tree", {}).get(path)
        if isinstance(entry, dict) and entry.get("resolution") is not None:
            return copy.deepcopy(entry["resolution"])
        if isinstance(entry, dict) and entry.get("theirs") is not None:
            return copy.deepcopy(entry["theirs"])
        return runtime.normalizer.entry_content(entry)
