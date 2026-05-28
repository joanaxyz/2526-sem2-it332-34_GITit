from __future__ import annotations

import copy

from simulator.commands.base import BaseCommandHandler, CommandOutcome, SimulatorCommandError
from simulator.intents import CommandIntent


class ResetCommandHandler(BaseCommandHandler):
    command = "reset"

    def apply(self, runtime, state: dict, intent: CommandIntent) -> CommandOutcome:
        operation = intent.first("ResetHard")
        if operation is None:
            raise SimulatorCommandError("fatal: unsupported reset operation", exit_code=129)
        target_expr = str(operation.params.get("target") or "")
        target = self._resolve_revision(runtime, state, target_expr)
        if not target:
            raise SimulatorCommandError(f"fatal: ambiguous argument '{target_expr}'", exit_code=128)

        state["merge_abort_state"] = copy.deepcopy(state)
        runtime._set_head_commit(state, target)
        state["staging"] = {}
        state["working_tree"] = {}
        state["conflicts"] = []
        state.pop("conflict_details", None)
        state.pop("merge_parent", None)
        state.pop("cherry_pick_in_progress", None)
        state.pop("cherry_pick_original_head", None)
        runtime._set_operation_metadata(
            state,
            last_reset_mode="hard",
            last_reset_target=target,
            last_reset_target_expr=target_expr,
        )
        runtime._record_reflog(state, target, f"reset: moving to {target_expr}")
        return CommandOutcome(
            command="reset",
            stdout=f"HEAD is now at {target}",
        )

    def _resolve_revision(self, runtime, state: dict, revision: str) -> str | None:
        if revision.startswith("HEAD@{") and revision.endswith("}"):
            try:
                index = int(revision[6:-1])
            except ValueError:
                return None
            reflog = state.get("reflog", [])
            if index < 0 or index >= len(reflog):
                return None
            return reflog[-(index + 1)].get("target")
        if revision.startswith("HEAD~"):
            try:
                depth = int(revision[5:])
            except ValueError:
                return None
            current = runtime._head_commit(state)
            for _ in range(depth):
                commit = runtime._commit_by_id(state, current)
                if not commit:
                    return None
                parents = commit.get("parents", [])
                current = parents[0] if parents else None
            return current
        if revision == "HEAD":
            return runtime._head_commit(state)
        if runtime._commit_by_id(state, revision):
            return revision
        return None
