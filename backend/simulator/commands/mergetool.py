from __future__ import annotations

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
            raise SimulatorCommandError(
                "No conflicted files match the requested pathspec.",
                exit_code=1,
            )

        configured_tool = (
            operation.params.get("tool")
            or state.get("config", {}).get("merge.tool")
            or state.get("operation_metadata", {}).get("configured_merge_tool")
            or "vimdiff"
        )
        runtime._set_operation_metadata(
            state,
            last_mergetool_tool=configured_tool,
            last_mergetool_paths=selected,
            last_mergetool_requested=True,
            last_mergetool_opened=True,
        )
        joined_paths = ", ".join(selected)
        return CommandOutcome(
            command="mergetool",
            stdout=(
                f"Opened {configured_tool} for {joined_paths}.\n"
                "The workspace conflict editor is ready with ours, theirs, base, and the merged file.\n"
                "No files were staged; save the resolved file, then use git add and git merge --continue or git commit."
            ),
        )
