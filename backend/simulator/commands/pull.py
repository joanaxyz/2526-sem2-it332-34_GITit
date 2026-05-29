from __future__ import annotations

import copy

from simulator.commands.base import BaseCommandHandler, CommandOutcome, SimulatorCommandError
from simulator.intents import CommandIntent


class PullCommandHandler(BaseCommandHandler):
    command = "pull"

    def apply(self, runtime, state: dict, intent: CommandIntent) -> CommandOutcome:
        return self._pull(runtime, state, intent.operations[0].params)

    def _pull(self, runtime, state: dict, params: dict) -> CommandOutcome:
        remote = params.get("remote") or "origin"
        branch = params.get("branch")
        rebase = bool(params.get("rebase"))

        head_branch = runtime._head_branch(state)
        if not head_branch:
            raise SimulatorCommandError(
                "fatal: You are not currently on a branch.\n"
                "Please specify which branch you want to rebase against.",
                exit_code=128,
            )

        target_branch = branch or head_branch
        remote_key = f"{remote}/{target_branch}"

        remotes = state.get("remotes", {})
        if remote not in remotes and not state.get("remote_fixtures") and not state.get("remote_updates"):
            raise SimulatorCommandError(
                f"fatal: '{remote}' does not appear to be a git repository"
            )

        updates = state.get("remote_updates") or {}
        if isinstance(updates, dict):
            state.setdefault("remote_branches", {}).update(copy.deepcopy(updates))
        runtime._apply_remote_fixture_branches(state)
        runtime._materialize_remote_commits(state)

        remote_branches = state.get("remote_branches", {})
        if remote_key not in remote_branches:
            raise SimulatorCommandError(
                f"fatal: couldn't find remote ref {target_branch}",
                exit_code=128,
            )

        remote_commit = remote_branches[remote_key]
        local_commit = runtime._head_commit(state)

        if local_commit == remote_commit:
            runtime._set_operation_metadata(
                state,
                remote_tracking_updated=True,
                last_pull_remote=remote,
                last_pull_branch=target_branch,
                pull_already_up_to_date=True,
            )
            return CommandOutcome(command="pull", stdout="Already up to date.")

        runtime._set_operation_metadata(state, remote_tracking_updated=True)

        if rebase:
            return self._rebase(runtime, state, remote, target_branch, local_commit, remote_commit)
        return self._merge(runtime, state, remote, target_branch, remote_key)

    def _merge(self, runtime, state: dict, remote: str, branch: str, remote_key: str) -> CommandOutcome:
        from simulator.commands.merge import MergeCommandHandler
        result = MergeCommandHandler()._merge(runtime, state, remote_key)
        runtime._set_operation_metadata(
            state,
            last_pull_remote=remote,
            last_pull_branch=branch,
            pull_strategy="merge",
        )
        stdout = result.stdout or ""
        stderr = result.stderr or ""
        return CommandOutcome(
            command="pull",
            stdout=stdout,
            stderr=stderr,
            exit_code=result.exit_code,
        )

    def _rebase(
        self,
        runtime,
        state: dict,
        remote: str,
        branch: str,
        local_commit: str | None,
        remote_commit: str | None,
    ) -> CommandOutcome:
        from simulator.commands.merge import MergeCommandHandler
        merge_handler = MergeCommandHandler()
        head_branch = runtime._head_branch(state)

        if merge_handler._is_ancestor(state, local_commit, remote_commit):
            runtime._set_head_commit(state, remote_commit)
            runtime._set_operation_metadata(
                state,
                last_pull_remote=remote,
                last_pull_branch=branch,
                pull_strategy="rebase",
                pull_rebased_onto=remote_commit,
            )
            return CommandOutcome(
                command="pull",
                stdout=f"Successfully rebased and updated refs/heads/{head_branch}.",
            )

        if merge_handler._is_ancestor(state, remote_commit, local_commit):
            runtime._set_operation_metadata(
                state,
                last_pull_remote=remote,
                last_pull_branch=branch,
                pull_strategy="rebase",
            )
            return CommandOutcome(command="pull", stdout="Already up to date.")

        current_tree = runtime._tree_for_commit(state, local_commit)
        remote_tree = runtime._tree_for_commit(state, remote_commit)
        base_id = merge_handler._common_ancestor(state, local_commit, remote_commit)
        base_tree = runtime._tree_for_commit(state, base_id)

        conflict_paths = merge_handler._overlapping_conflicts(base_tree, remote_tree, current_tree)
        if conflict_paths:
            raise SimulatorCommandError(
                "CONFLICT (content): Merge conflict in "
                f"{', '.join(sorted(conflict_paths))}\n"
                "error: could not apply commits\n"
                "hint: Resolve all conflicts manually, then run \"git rebase --continue\"",
                exit_code=1,
            )

        merged_tree = copy.deepcopy(remote_tree)
        for path, value in current_tree.items():
            if value != base_tree.get(path):
                if value is None:
                    merged_tree.pop(path, None)
                else:
                    merged_tree[path] = copy.deepcopy(value)

        commit_id = runtime._next_commit_id(state)
        local_obj = runtime._commit_by_id(state, local_commit)
        message = (local_obj or {}).get("message", f"Rebased onto {branch}")
        changes = runtime._diff_trees(remote_tree, merged_tree)
        state.setdefault("commits", []).append(
            runtime._commit_payload(
                state=state,
                commit_id=commit_id,
                message=message,
                parents=[remote_commit] if remote_commit else [],
                tree=merged_tree,
                changes=changes,
            )
        )
        runtime._set_head_commit(state, commit_id)
        runtime._set_operation_metadata(
            state,
            last_pull_remote=remote,
            last_pull_branch=branch,
            pull_strategy="rebase",
            pull_rebased_onto=remote_commit,
            pull_created_commit=commit_id,
        )
        return CommandOutcome(
            command="pull",
            stdout=f"Successfully rebased and updated refs/heads/{head_branch}.",
        )
