from __future__ import annotations

import copy

from simulator.commands.base import BaseCommandHandler, CommandOutcome, SimulatorCommandError
from simulator.intents import CommandIntent


class CherryPickCommandHandler(BaseCommandHandler):
    command = "cherry-pick"

    def apply(self, runtime, state: dict, intent: CommandIntent) -> CommandOutcome:
        operation = intent.operations[0]
        if operation.name == "AbortCherryPick":
            return self._abort(runtime, state)
        return self._pick(runtime, state, operation.params)

    def _abort(self, runtime, state: dict) -> CommandOutcome:
        if not state.get("cherry_pick_in_progress") and not state.get("cherry_pick_original_head"):
            raise SimulatorCommandError("error: no cherry-pick or revert in progress", exit_code=128)
        original = state.get("cherry_pick_original_head")
        branch = runtime._head_branch(state)
        if original and branch:
            state.setdefault("branches", {})[branch] = original
        state["staging"] = {}
        state["working_tree"] = {}
        state["conflicts"] = []
        state.pop("cherry_pick_in_progress", None)
        state.pop("cherry_pick_original_head", None)
        runtime._set_operation_metadata(state, last_cherry_pick_aborted=True)
        return CommandOutcome(command="cherry-pick", stdout="")

    def _pick(self, runtime, state: dict, params: dict) -> CommandOutcome:
        source_id = params["commit"]
        source = runtime._commit_by_id(state, source_id)
        if not source:
            raise SimulatorCommandError(f"fatal: bad revision '{source_id}'", exit_code=128)
        if state.get("conflicts"):
            raise SimulatorCommandError(
                "error: Cherry-picking is not possible because you have unmerged files.",
                exit_code=128,
            )

        head_id = runtime._head_commit(state)
        head_tree = runtime._head_tree(state)
        picked_tree = runtime._apply_changes(head_tree, copy.deepcopy(source.get("changes") or {}))
        changes = runtime._diff_trees(head_tree, picked_tree)
        if params.get("no_commit"):
            for path, payload in changes.items():
                after = payload.get("after")
                state.setdefault("staging", {})[path] = (
                    "deleted"
                    if after is None
                    else {
                        "status": payload.get("change_type") or "modified",
                        "content": copy.deepcopy(after),
                    }
                )
            runtime._set_operation_metadata(
                state,
                cherry_pick_in_progress=True,
                cherry_pick_original_head=head_id,
                last_cherry_pick_source=source_id,
                last_cherry_pick_no_commit=True,
            )
            return CommandOutcome(
                command="cherry-pick",
                stdout=f"Applied changes from {source_id} without committing.",
            )

        commit_id = runtime._next_commit_id(state)
        state.setdefault("commits", []).append(
            runtime._commit_payload(
                state=state,
                commit_id=commit_id,
                message=source.get("message", f"cherry-pick {source_id}"),
                parents=[head_id] if head_id else [],
                tree=picked_tree,
                changes=changes,
            )
        )
        runtime._set_head_commit(state, commit_id)
        runtime._set_operation_metadata(
            state,
            last_cherry_pick_source=source_id,
            last_cherry_pick_created_commit=commit_id,
            last_cherry_pick_no_commit=False,
        )
        return CommandOutcome(command="cherry-pick", stdout=f"[{runtime._head_branch(state) or 'HEAD'} {commit_id}] {source.get('message', '')}")
