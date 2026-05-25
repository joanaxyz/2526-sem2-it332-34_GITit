from __future__ import annotations

import copy

from simulator.commands.base import (
    BaseCommandHandler,
    CommandOutcome,
    SimulatorCommandError,
    selected_paths,
)
from simulator.intents import CommandIntent


class AddCommandHandler(BaseCommandHandler):
    command = "add"

    def apply(self, runtime, state: dict, intent: CommandIntent) -> CommandOutcome:
        operation = intent.operations[0]
        if operation.name == "StagePatch":
            return self._stage_patch(runtime, state, tuple(operation.params.get("paths") or ()))
        if operation.name == "StageTrackedChangesOnly":
            paths = self.stage_tracked(runtime, state, tuple(operation.params.get("paths") or ()))
            return CommandOutcome(command="add", details={"paths": paths, "mode": "tracked"})
        if operation.name == "StageAllChanges":
            paths = self.stage_all(runtime, state, tuple(operation.params.get("paths") or ()))
            return CommandOutcome(command="add", details={"paths": paths, "mode": "all"})
        if operation.name == "UnsupportedCommand":
            raise SimulatorCommandError("fatal: unsupported add operation", exit_code=129)
        paths = self.stage_pathspecs(runtime, state, tuple(operation.params.get("paths") or ()))
        return CommandOutcome(command="add", details={"paths": paths, "mode": "pathspec"})

    def stage_all(self, runtime, state: dict, paths: tuple[str, ...] = ()) -> list[str]:
        selected = selected_paths(
            runtime, state, paths, include_tracked=True, include_untracked=True
        )
        self._stage_selected(runtime, state, selected)
        return selected

    def stage_tracked(self, runtime, state: dict, paths: tuple[str, ...] = ()) -> list[str]:
        selected = selected_paths(
            runtime, state, paths, include_tracked=True, include_untracked=False
        )
        self._stage_selected(runtime, state, selected)
        return selected

    def stage_pathspecs(self, runtime, state: dict, paths: tuple[str, ...]) -> list[str]:
        if not paths:
            raise SimulatorCommandError("Nothing specified, nothing added.", exit_code=128)
        selected = selected_paths(
            runtime, state, paths, include_tracked=True, include_untracked=True
        )
        self._stage_selected(runtime, state, selected)
        return selected

    def _stage_selected(self, runtime, state: dict, paths: list[str]) -> None:
        working_tree = state.setdefault("working_tree", {})
        staging = state.setdefault("staging", {})
        conflicts = set(state.get("conflicts", []))
        for path in paths:
            if runtime.normalizer.entry_status(working_tree.get(path)) == "ignored":
                continue
            staging[path] = copy.deepcopy(working_tree.pop(path, "updated"))
            conflicts.discard(path)
            state.setdefault("conflict_details", {}).pop(path, None)
        state["conflicts"] = sorted(conflicts)

    def _stage_patch(self, runtime, state: dict, paths: tuple[str, ...]) -> CommandOutcome:
        # Keep existing authored partial-hunk behavior intact.
        working_tree = state.setdefault("working_tree", {})
        partial_hunks = state.setdefault("partial_hunks", {})
        selected = (
            list(paths)
            or list(partial_hunks)
            or [
                path
                for path, value in working_tree.items()
                if runtime.normalizer.entry_status(value) not in {"ignored", "untracked"}
            ]
        )
        if not selected:
            raise SimulatorCommandError(
                "No tracked changes available for patch staging.", exit_code=128
            )
        staging = state.setdefault("staging", {})
        staged_paths: list[str] = []
        for path in selected:
            if path not in working_tree and path not in partial_hunks:
                continue
            if runtime.normalizer.entry_status(working_tree.get(path)) == "ignored":
                continue
            authored = partial_hunks.get(path) or {}
            if isinstance(authored, dict):
                target_hunks = runtime._as_list(
                    authored.get("target_hunks")
                    or authored.get("staged_hunks")
                    or authored.get("stage")
                )
                leftover_hunks = runtime._as_list(
                    authored.get("leftover_hunks")
                    or authored.get("remaining_hunks")
                    or authored.get("leftover")
                )
            else:
                authored_hunks = runtime._as_list(authored)
                target_hunks = authored_hunks[:1]
                leftover_hunks = authored_hunks[1:]
            if target_hunks or leftover_hunks:
                staging[path] = {"status": "partial", "hunks": target_hunks}
                if leftover_hunks:
                    working_tree[path] = {"status": "modified", "hunks": leftover_hunks}
                else:
                    working_tree.pop(path, None)
            else:
                staging[path] = {
                    "status": "partial",
                    "hunks": runtime._entry_tokens(working_tree.get(path)),
                }
                working_tree[path] = "modified"
            staged_paths.append(path)
        return CommandOutcome(command="add", details={"paths": staged_paths, "mode": "patch"})
