from __future__ import annotations

import copy

from simulator.commands.base import BaseCommandHandler, CommandOutcome, SimulatorCommandError
from simulator.intents import CommandIntent


class RevertCommandHandler(BaseCommandHandler):
    command = "revert"

    def apply(self, runtime, state: dict, intent: CommandIntent) -> CommandOutcome:
        operation = intent.first("RevertCommit")
        if operation is None:
            raise SimulatorCommandError("fatal: unsupported revert operation", exit_code=129)
        source_id = str(operation.params.get("commit") or "")
        source_commit = runtime._commit_by_id(state, source_id)
        if not source_commit:
            raise SimulatorCommandError(f"fatal: bad revision '{source_id}'", exit_code=128)
        if state.get("conflicts"):
            raise SimulatorCommandError(
                "error: Reverting is not possible because you have unmerged files.",
                exit_code=128,
            )

        head_id = runtime._head_commit(state)
        head_tree = runtime._head_tree(state)
        reverted_changes = {}
        for path, payload in (source_commit.get("changes") or {}).items():
            reverted_changes[path] = {
                "change_type": runtime.normalizer.change_type(
                    head_tree.get(path), copy.deepcopy(payload.get("before"))
                ),
                "before": head_tree.get(path),
                "after": copy.deepcopy(payload.get("before")),
            }
        next_tree = runtime._apply_changes(head_tree, reverted_changes)
        net_changes = runtime._diff_trees(head_tree, next_tree)
        commit_id = runtime._next_commit_id(state)
        message = f"Revert \"{source_commit.get('message', source_id)}\""
        state.setdefault("commits", []).append(
            runtime._commit_payload(
                state=state,
                commit_id=commit_id,
                message=message,
                parents=[head_id] if head_id else [],
                tree=next_tree,
                changes=net_changes,
            )
        )
        runtime._set_head_commit(state, commit_id)
        runtime._set_operation_metadata(
            state,
            last_revert_source=source_id,
            last_revert_created_commit=commit_id,
            last_revert_no_edit=bool(operation.params.get("no_edit")),
        )
        runtime._record_reflog(state, commit_id, f"revert: {source_id}")
        return CommandOutcome(
            command="revert",
            stdout=f"[{runtime._head_branch(state) or 'HEAD'} {commit_id}] {message}",
        )
