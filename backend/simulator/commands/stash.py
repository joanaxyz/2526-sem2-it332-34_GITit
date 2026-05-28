from __future__ import annotations

import copy

from simulator.commands.base import BaseCommandHandler, CommandOutcome, SimulatorCommandError
from simulator.intents import CommandIntent


class StashCommandHandler(BaseCommandHandler):
    command = "stash"

    def apply(self, runtime, state: dict, intent: CommandIntent) -> CommandOutcome:
        operation = intent.operations[0]
        if operation.name == "StashChanges":
            return self._push(runtime, state)
        if operation.name == "PopStash":
            return self._pop(runtime, state, operation.params.get("index", 0))
        if operation.name == "ApplyStash":
            return self._apply(runtime, state, operation.params.get("index", 0), remove=False)
        if operation.name == "DropStash":
            return self._drop(runtime, state, operation.params.get("index", 0))
        if operation.name == "ListStash":
            return self._list(state)
        raise SimulatorCommandError("fatal: unsupported stash operation", exit_code=129)

    def _push(self, runtime, state: dict) -> CommandOutcome:
        working_tree = state.get("working_tree", {})
        staging = state.get("staging", {})
        if not working_tree and not staging:
            return CommandOutcome(command="stash", stdout="No local changes to save")

        head_commit = runtime._head_commit(state)
        head_branch = runtime._head_branch(state)
        commit = runtime._commit_by_id(state, head_commit)
        commit_msg = (commit.get("message", "") if commit else "")[:50]
        short_id = (head_commit or "")[:7]
        label = f"WIP on {head_branch or 'HEAD'}: {short_id} {commit_msg}".rstrip()

        entry = {
            "message": label,
            "working_tree": copy.deepcopy(working_tree),
            "staging": copy.deepcopy(staging),
            "head_commit": head_commit,
        }

        stash_stack = state.setdefault("stash_stack", [])
        stash_stack.append(entry)
        state["working_tree"] = {}
        state["staging"] = {}
        runtime._set_operation_metadata(
            state,
            last_stash_operation="push",
            stash_count=len(stash_stack),
        )
        return CommandOutcome(
            command="stash",
            stdout=f"Saved working directory and index state {label}",
        )

    def _pop(self, runtime, state: dict, index: int) -> CommandOutcome:
        return self._apply(runtime, state, index, remove=True)

    def _apply(self, runtime, state: dict, index: int, *, remove: bool) -> CommandOutcome:
        stash_stack = state.get("stash_stack", [])
        if not stash_stack:
            raise SimulatorCommandError(
                "error: refs/stash: No such file or directory", exit_code=1
            )
        real_index = len(stash_stack) - 1 - index
        if real_index < 0:
            raise SimulatorCommandError(
                f"error: refs/stash@{{{index}}}: not a valid reference", exit_code=1
            )

        entry = stash_stack[real_index]
        restored_paths = set(entry.get("working_tree", {})) | set(entry.get("staging", {}))
        state["working_tree"] = copy.deepcopy(entry.get("working_tree", {}))
        state["staging"] = copy.deepcopy(entry.get("staging", {}))

        if remove:
            stash_stack.pop(real_index)

        op = "pop" if remove else "apply"
        branch = runtime._head_branch(state) or "HEAD"
        runtime._set_operation_metadata(
            state,
            last_stash_operation=op,
            stash_count=len(stash_stack),
            last_stash_pop_restored_paths=sorted(restored_paths),
        )
        return CommandOutcome(
            command="stash",
            stdout=f"On branch {branch}\n"
                   f"Changes not staged for commit:\n"
                   f"  (restored from stash@{{{index}}})",
        )

    def _drop(self, runtime, state: dict, index: int) -> CommandOutcome:
        stash_stack = state.get("stash_stack", [])
        if not stash_stack:
            raise SimulatorCommandError(
                "error: refs/stash: No such file or directory", exit_code=1
            )
        real_index = len(stash_stack) - 1 - index
        if real_index < 0:
            raise SimulatorCommandError(
                f"error: refs/stash@{{{index}}}: not a valid reference", exit_code=1
            )
        stash_stack.pop(real_index)
        runtime._set_operation_metadata(
            state,
            last_stash_operation="drop",
            stash_count=len(stash_stack),
        )
        return CommandOutcome(command="stash", stdout=f"Dropped stash@{{{index}}}")

    def _list(self, state: dict) -> CommandOutcome:
        stash_stack = state.get("stash_stack", [])
        if not stash_stack:
            return CommandOutcome(command="stash", stdout="")
        lines = [
            f"stash@{{{i}}}: {entry['message']}"
            for i, entry in enumerate(reversed(stash_stack))
        ]
        return CommandOutcome(command="stash", stdout="\n".join(lines))
