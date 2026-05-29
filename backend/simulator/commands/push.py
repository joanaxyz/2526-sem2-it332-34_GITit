from __future__ import annotations

from simulator.commands.base import BaseCommandHandler, CommandOutcome, SimulatorCommandError
from simulator.intents import CommandIntent


class PushCommandHandler(BaseCommandHandler):
    command = "push"

    def apply(self, runtime, state: dict, intent: CommandIntent) -> CommandOutcome:
        operation = intent.operations[0]
        if operation.name == "DeleteRemoteBranch":
            return self._delete_remote(runtime, state, operation.params)
        if operation.name == "ForcePushWithLease":
            return self._force_push(runtime, state, operation.params)
        return self._push(runtime, state, operation.params)

    def _push(self, runtime, state: dict, params: dict) -> CommandOutcome:
        remote = params.get("remote") or "origin"
        branch = params.get("branch") or runtime._head_branch(state)
        set_upstream = bool(params.get("set_upstream"))
        force = bool(params.get("force"))

        if not branch:
            raise SimulatorCommandError(
                "fatal: The current branch has no upstream branch.\n"
                "To push the current branch and set the remote as upstream, use\n\n"
                "    git push --set-upstream origin <branch>",
                exit_code=128,
            )

        branches = state.get("branches", {})
        if branch not in branches:
            raise SimulatorCommandError(
                f"error: src refspec {branch} does not match any",
                exit_code=1,
            )

        commit_id = branches[branch]
        remote_key = f"{remote}/{branch}"
        remote_branches = state.setdefault("remote_branches", {})

        if not force and remote_key in remote_branches:
            from simulator.commands.merge import MergeCommandHandler
            remote_commit = remote_branches[remote_key]
            if remote_commit and not MergeCommandHandler()._is_ancestor(state, remote_commit, commit_id):
                raise SimulatorCommandError(
                    f"error: failed to push some refs to '{remote}'\n"
                    "hint: Updates were rejected because the remote contains work that you do\n"
                    "hint: not have locally. Integrate the remote changes (e.g.\n"
                    "hint: 'git pull ...') before pushing again.",
                    exit_code=1,
                )

        remote_branches[remote_key] = commit_id
        state.setdefault("remotes", {}).setdefault(
            remote, f"https://example.test/{remote}.git"
        )

        if set_upstream:
            state.setdefault("upstream_tracking", {})[branch] = remote_key

        runtime._set_operation_metadata(
            state,
            last_push_remote=remote,
            last_push_branch=branch,
            last_push_remote_branch=remote_key,
            last_push_commit=commit_id,
            push_set_upstream=set_upstream,
        )

        url = state["remotes"].get(remote, f"https://example.test/{remote}.git")
        upstream_line = (
            f"\n Branch '{branch}' set up to track remote branch '{branch}' from '{remote}'."
            if set_upstream
            else ""
        )
        return CommandOutcome(
            command="push",
            stdout=f"To {url}\n * [new branch]      {branch} -> {branch}{upstream_line}",
        )

    def _force_push(self, runtime, state: dict, params: dict) -> CommandOutcome:
        remote = params.get("remote") or "origin"
        branch = params.get("branch") or runtime._head_branch(state)

        if not branch:
            raise SimulatorCommandError(
                "fatal: The current branch has no upstream branch.", exit_code=128
            )

        branches = state.get("branches", {})
        if branch not in branches:
            raise SimulatorCommandError(
                f"error: src refspec {branch} does not match any", exit_code=1
            )

        commit_id = branches[branch]
        remote_key = f"{remote}/{branch}"
        state.setdefault("remote_branches", {})[remote_key] = commit_id
        state.setdefault("remotes", {}).setdefault(
            remote, f"https://example.test/{remote}.git"
        )

        runtime._set_operation_metadata(
            state,
            last_push_remote=remote,
            last_push_branch=branch,
            last_push_remote_branch=remote_key,
            last_push_commit=commit_id,
            force_push_with_lease=True,
        )
        url = state["remotes"].get(remote, f"https://example.test/{remote}.git")
        short = (commit_id or "")[:7]
        return CommandOutcome(
            command="push",
            stdout=f"To {url}\n + old..{short}  {branch} -> {branch} (forced update)",
        )

    def _delete_remote(self, runtime, state: dict, params: dict) -> CommandOutcome:
        remote = params.get("remote") or "origin"
        branch = params.get("branch")

        if not branch:
            raise SimulatorCommandError(
                "fatal: --delete doesn't take a refspec", exit_code=128
            )

        remote_key = f"{remote}/{branch}"
        remote_branches = state.setdefault("remote_branches", {})
        if remote_key not in remote_branches:
            raise SimulatorCommandError(
                f"error: unable to delete '{branch}': remote ref does not exist",
                exit_code=1,
            )

        del remote_branches[remote_key]
        upstream = state.get("upstream_tracking", {})
        for local_branch, tracked in list(upstream.items()):
            if tracked == remote_key:
                del upstream[local_branch]

        runtime._set_operation_metadata(
            state,
            last_push_remote=remote,
            last_deleted_remote_branch=branch,
            remote_branch_deleted=branch,
        )
        url = state.get("remotes", {}).get(remote, f"https://example.test/{remote}.git")
        return CommandOutcome(
            command="push",
            stdout=f"To {url}\n - [deleted]         {branch}",
        )
