from __future__ import annotations

import copy

from simulator.commands.base import BaseCommandHandler, CommandOutcome, SimulatorCommandError
from simulator.intents import CommandIntent


class RebaseCommandHandler(BaseCommandHandler):
    command = "rebase"

    def apply(self, runtime, state: dict, intent: CommandIntent) -> CommandOutcome:
        if intent.first("AbortRebase"):
            return self._abort(runtime, state)
        if intent.first("ContinueRebase"):
            return self._continue(runtime, state)
        operation = intent.first("StartRebase")
        if operation is None:
            raise SimulatorCommandError("fatal: unsupported rebase operation", exit_code=129)
        return self._start(runtime, state, operation.params)

    def _start(self, runtime, state: dict, params: dict) -> CommandOutcome:
        if state.get("conflicts"):
            raise SimulatorCommandError(
                "error: cannot rebase: You have unstaged changes.",
                exit_code=128,
            )
        target_ref = str(params.get("target") or "")
        target_commit = self._resolve_ref(runtime, state, target_ref)
        if not target_commit:
            raise SimulatorCommandError(f"fatal: invalid upstream '{target_ref}'", exit_code=128)
        head_commit = runtime._head_commit(state)
        current_branch = runtime._head_branch(state)
        if not current_branch:
            raise SimulatorCommandError("fatal: rebase requires a branch checkout", exit_code=128)
        if head_commit == target_commit:
            return CommandOutcome(command="rebase", stdout="Current branch is up to date.")

        base = self._common_ancestor(runtime, state, head_commit, target_commit)
        to_replay = list(reversed(self._commits_since(runtime, state, head_commit, stop_at=base)))
        if not to_replay:
            runtime._set_head_commit(state, target_commit)
            runtime._set_operation_metadata(
                state,
                last_rebase_target=target_ref,
                last_rebase_upstream=target_commit,
                last_rebase_new_head=target_commit,
                last_rebase_interactive=bool(params.get("interactive")),
                last_rebase_replayed_commits=[],
            )
            return CommandOutcome(command="rebase", stdout=f"Successfully rebased and updated {current_branch}.")

        state["rebase_state"] = {
            "branch": current_branch,
            "original_head": head_commit,
            "upstream": target_commit,
            "upstream_ref": target_ref,
            "remaining": to_replay,
            "applied": [],
            "interactive": bool(params.get("interactive")),
            "abort_state": copy.deepcopy(state),
        }
        runtime._set_head_commit(state, target_commit)
        runtime._set_operation_metadata(
            state,
            last_rebase_target=target_ref,
            last_rebase_upstream=target_commit,
            last_rebase_interactive=bool(params.get("interactive")),
        )
        return self._apply_next(runtime, state)

    def _continue(self, runtime, state: dict) -> CommandOutcome:
        rebase_state = state.get("rebase_state")
        if not isinstance(rebase_state, dict):
            raise SimulatorCommandError("fatal: No rebase in progress?", exit_code=128)
        if state.get("conflicts"):
            raise SimulatorCommandError(
                "You must edit all merge conflicts and then mark them as resolved using git add",
                exit_code=128,
            )
        if state.get("staging"):
            from simulator.commands.commit import CommitCommandHandler

            CommitCommandHandler()._create(
                runtime,
                state,
                {"message": rebase_state.get("pending_message") or "rebase commit"},
                staged_by_all=[],
            )
            created = runtime._head_commit(state)
            if created:
                rebase_state.setdefault("applied", []).append(created)
            rebase_state.pop("pending_message", None)
        return self._apply_next(runtime, state)

    def _abort(self, runtime, state: dict) -> CommandOutcome:
        rebase_state = state.get("rebase_state")
        if not isinstance(rebase_state, dict):
            raise SimulatorCommandError("fatal: No rebase in progress?", exit_code=128)
        abort_state = rebase_state.get("abort_state")
        if isinstance(abort_state, dict):
            restored = copy.deepcopy(abort_state)
            state.clear()
            state.update(restored)
            runtime._set_operation_metadata(state, last_rebase_aborted=True)
            return CommandOutcome(command="rebase", stdout="")
        raise SimulatorCommandError("fatal: unable to abort rebase state", exit_code=128)

    def _apply_next(self, runtime, state: dict) -> CommandOutcome:
        rebase_state = state.get("rebase_state")
        remaining = rebase_state.get("remaining") if isinstance(rebase_state, dict) else None
        if not isinstance(remaining, list):
            raise SimulatorCommandError("fatal: invalid rebase state", exit_code=128)
        if not remaining:
            new_head = runtime._head_commit(state)
            runtime._set_operation_metadata(
                state,
                last_rebase_new_head=new_head,
                last_rebase_replayed_commits=rebase_state.get("applied", []),
            )
            state.pop("rebase_state", None)
            return CommandOutcome(command="rebase", stdout="Successfully rebased and updated current branch.")

        source_id = remaining.pop(0)
        source_commit = runtime._commit_by_id(state, source_id)
        if not source_commit:
            raise SimulatorCommandError(f"fatal: missing commit '{source_id}' during rebase", exit_code=128)
        head_tree = runtime._head_tree(state)
        source_changes = copy.deepcopy(source_commit.get("changes") or {})
        candidate_tree = runtime._apply_changes(head_tree, source_changes)
        conflict_paths = self._detect_conflicts(head_tree, source_changes)
        if conflict_paths:
            state["merge_parent"] = rebase_state.get("upstream")
            state["conflicts"] = sorted(conflict_paths)
            state["conflict_details"] = {
                path: {
                    "base": None,
                    "ours": head_tree.get(path),
                    "theirs": source_changes.get(path, {}).get("after"),
                    "merge_branch": rebase_state.get("upstream_ref"),
                }
                for path in sorted(conflict_paths)
            }
            state["working_tree"] = {
                path: {
                    "status": "conflicted",
                    "content": (
                        f"<<<<<<< HEAD\n{head_tree.get(path, '')}\n=======\n"
                        f"{source_changes.get(path, {}).get('after', '')}\n>>>>>>> rebase\n"
                    ),
                }
                for path in sorted(conflict_paths)
            }
            rebase_state["pending_message"] = source_commit.get("message")
            runtime._set_operation_metadata(
                state,
                last_rebase_conflicted=True,
                last_rebase_conflict_paths=sorted(conflict_paths),
            )
            return CommandOutcome(
                command="rebase",
                exit_code=1,
                stdout=(
                    "CONFLICT (content): Rebase conflict encountered.\n"
                    "Resolve all conflicts manually, mark them as resolved with\n"
                    "\"git add/rm <conflicted_files>\", then run \"git rebase --continue\"."
                ),
            )

        head_id = runtime._head_commit(state)
        commit_id = runtime._next_commit_id(state)
        state.setdefault("commits", []).append(
            runtime._commit_payload(
                state=state,
                commit_id=commit_id,
                message=source_commit.get("message", f"rebase {source_id}"),
                parents=[head_id] if head_id else [],
                tree=candidate_tree,
                changes=runtime._diff_trees(head_tree, candidate_tree),
            )
        )
        runtime._set_head_commit(state, commit_id)
        rebase_state.setdefault("applied", []).append(commit_id)
        return self._apply_next(runtime, state)

    def _resolve_ref(self, runtime, state: dict, ref: str) -> str | None:
        if ref in state.get("branches", {}):
            return state["branches"][ref]
        if ref in state.get("remote_branches", {}):
            return state["remote_branches"][ref]
        if ref.startswith("HEAD~"):
            try:
                depth = int(ref[5:])
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
        if runtime._commit_by_id(state, ref):
            return ref
        return None

    def _common_ancestor(self, runtime, state: dict, left: str | None, right: str | None) -> str | None:
        left_history = self._history(runtime, state, left)
        right_history = set(self._history(runtime, state, right))
        return next((commit_id for commit_id in left_history if commit_id in right_history), None)

    def _history(self, runtime, state: dict, commit_id: str | None) -> list[str]:
        if not commit_id:
            return []
        commits = {commit["id"]: commit for commit in state.get("commits", [])}
        stack = [commit_id]
        seen: list[str] = []
        while stack:
            current = stack.pop()
            if current in seen or current not in commits:
                continue
            seen.append(current)
            stack.extend(commits[current].get("parents", []))
        return seen

    def _commits_since(self, runtime, state: dict, commit_id: str | None, *, stop_at: str | None) -> list[str]:
        commits = []
        current = commit_id
        while current and current != stop_at:
            commits.append(current)
            commit = runtime._commit_by_id(state, current)
            parents = (commit or {}).get("parents", [])
            current = parents[0] if parents else None
        return commits

    def _detect_conflicts(self, head_tree: dict, source_changes: dict) -> set[str]:
        conflicts: set[str] = set()
        for path, payload in source_changes.items():
            before = payload.get("before")
            ours = head_tree.get(path)
            if ours != before and before is not None:
                conflicts.add(path)
        return conflicts
