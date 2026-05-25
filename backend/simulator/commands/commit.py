from __future__ import annotations

import copy

from simulator.commands.add import AddCommandHandler
from simulator.commands.base import BaseCommandHandler, CommandOutcome, SimulatorCommandError
from simulator.intents import CommandIntent


class CommitCommandHandler(BaseCommandHandler):
    command = "commit"

    def apply(self, runtime, state: dict, intent: CommandIntent) -> CommandOutcome:
        staged_by_all: list[str] = []
        for operation in intent.operations:
            if operation.name == "StageTrackedChangesOnly":
                staged_by_all = AddCommandHandler().stage_tracked(
                    runtime,
                    state,
                    tuple(operation.params.get("paths") or ()),
                )

        commit_operation = intent.first("AmendCommit") or intent.first("CreateCommit")
        if commit_operation is None:
            raise SimulatorCommandError("fatal: unsupported commit operation", exit_code=129)
        if commit_operation.name == "AmendCommit":
            return self._amend(runtime, state, commit_operation.params, staged_by_all=staged_by_all)
        return self._create(runtime, state, commit_operation.params, staged_by_all=staged_by_all)

    def _create(
        self, runtime, state: dict, params: dict, *, staged_by_all: list[str]
    ) -> CommandOutcome:
        if state.get("conflicts"):
            raise SimulatorCommandError(
                "Committing is not possible because you have unmerged files.",
                exit_code=128,
            )
        if not state.get("staging") and not state.get("merge_parent"):
            raise SimulatorCommandError("nothing to commit, working tree clean", exit_code=1)

        merge_parent = state.pop("merge_parent", None)
        merge_branch = state.get("operation_metadata", {}).get("last_merge_branch", "branch")
        message = params.get("message") or (
            f"Merge branch '{merge_branch}'" if merge_parent else "commit"
        )
        current = runtime._head_commit(state)
        parents = [parent for parent in [current, merge_parent] if parent]
        commit_id = runtime._next_commit_id(state)
        base_tree = runtime._tree_for_commit(state, current)
        staged_entries = copy.deepcopy(state.get("staging", {}))
        staged_changes = runtime._changes_from_entries(base_tree, staged_entries)
        tree = runtime._apply_changes(base_tree, staged_changes)
        state.setdefault("commits", []).append(
            runtime._commit_payload(
                state=state,
                commit_id=commit_id,
                message=message,
                parents=parents,
                tree=tree,
                changes=staged_changes,
            )
        )
        state["staging"] = {}
        state.pop("merge_abort_state", None)
        runtime._cleanup_partial_hunks_after_commit(state, staged_entries)
        runtime._set_head_commit(state, commit_id)
        if merge_parent:
            runtime._set_operation_metadata(state, last_merge_created_commit=commit_id)
        return CommandOutcome(
            command="commit",
            details={
                "commit_id": commit_id,
                "message": message,
                "changes": staged_changes,
                "branch": runtime._head_branch(state) or "HEAD",
                "amend": False,
                "staged_by_all": staged_by_all,
            },
        )

    def _amend(
        self, runtime, state: dict, params: dict, *, staged_by_all: list[str]
    ) -> CommandOutcome:
        current = runtime._head_commit(state)
        old_commit = runtime._commit_by_id(state, current)
        if not old_commit:
            raise SimulatorCommandError("fatal: You have nothing to amend.", exit_code=128)

        message = old_commit.get("message", "commit")
        if params.get("message") is not None:
            message = params["message"]
        parent_ids = list(old_commit.get("parents", []))
        parent_id = (parent_ids or [None])[0]
        parent_tree = runtime._tree_for_commit(state, parent_id)
        current_tree = copy.deepcopy(old_commit.get("tree") or parent_tree)
        staged_entries = copy.deepcopy(state.get("staging", {}))
        if not staged_entries and params.get("message") is None and not params.get("no_edit"):
            raise SimulatorCommandError("No changes", exit_code=1)
        staged_changes = runtime._changes_from_entries(current_tree, staged_entries)
        amended_tree = runtime._apply_changes(current_tree, staged_changes)
        commit_id = runtime._next_commit_id(state)
        changes = runtime._diff_trees(parent_tree, amended_tree)
        state.setdefault("commits", []).append(
            runtime._commit_payload(
                state=state,
                commit_id=commit_id,
                message=message,
                parents=parent_ids,
                tree=amended_tree,
                changes=changes,
            )
        )
        state.setdefault("replaced_commits", {})[current] = commit_id
        runtime._set_operation_metadata(
            state,
            last_amend_replaced_commit=current,
            last_amend_created_commit=commit_id,
        )
        state["staging"] = {}
        runtime._cleanup_partial_hunks_after_commit(state, staged_entries)
        runtime._set_head_commit(state, commit_id)
        runtime._record_reflog(state, commit_id, f"commit --amend: replaced {current}")
        return CommandOutcome(
            command="commit",
            details={
                "commit_id": commit_id,
                "message": message,
                "changes": changes,
                "branch": runtime._head_branch(state) or "HEAD",
                "amend": True,
                "replaced": current,
                "staged_by_all": staged_by_all,
            },
        )
