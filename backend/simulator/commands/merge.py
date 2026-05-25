from __future__ import annotations

import copy

from simulator.commands.base import BaseCommandHandler, CommandOutcome, SimulatorCommandError
from simulator.intents import CommandIntent


class MergeCommandHandler(BaseCommandHandler):
    command = "merge"

    def apply(self, runtime, state: dict, intent: CommandIntent) -> CommandOutcome:
        operation = intent.operations[0]
        if operation.name == "AbortMerge":
            return self._abort(runtime, state)
        if operation.name == "ContinueMerge":
            return self._continue(runtime, state)
        return self._merge(runtime, state, operation.params["branch"])

    def _abort(self, runtime, state: dict) -> CommandOutcome:
        if not state.get("merge_parent") and not state.get("conflicts"):
            raise SimulatorCommandError("fatal: There is no merge to abort (MERGE_HEAD missing).")
        restored = state.get("merge_abort_state")
        if isinstance(restored, dict) and restored:
            state.clear()
            state.update(copy.deepcopy(restored))
            runtime._set_operation_metadata(state, last_merge_aborted=True)
            return CommandOutcome(command="merge", stdout="")
        state["conflicts"] = []
        state["staging"] = {}
        state["working_tree"] = {}
        state.pop("merge_parent", None)
        runtime._set_operation_metadata(state, last_merge_aborted=True)
        return CommandOutcome(command="merge", stdout="")

    def _continue(self, runtime, state: dict) -> CommandOutcome:
        if not state.get("merge_parent"):
            raise SimulatorCommandError("fatal: There is no merge in progress (MERGE_HEAD missing).")
        if state.get("conflicts"):
            raise SimulatorCommandError(
                "Committing is not possible because you have unmerged files.",
                exit_code=128,
            )
        from simulator.commands.commit import CommitCommandHandler

        return CommitCommandHandler()._create(runtime, state, {"message": None}, staged_by_all=[])

    def _merge(self, runtime, state: dict, branch: str) -> CommandOutcome:
        if state.get("merge_parent") or state.get("conflicts"):
            raise SimulatorCommandError(
                "error: Merging is not possible because you have unmerged files.",
                exit_code=128,
            )
        target_id = self._resolve_ref(state, branch)
        if not target_id:
            raise SimulatorCommandError(f"merge: {branch} - not something we can merge")
        current_id = runtime._head_commit(state)
        if current_id == target_id:
            return CommandOutcome(command="merge", stdout="Already up to date.")

        before_merge = copy.deepcopy(state)
        current_tree = runtime._tree_for_commit(state, current_id)
        target_tree = runtime._tree_for_commit(state, target_id)
        base_id = self._common_ancestor(state, current_id, target_id)
        base_tree = runtime._tree_for_commit(state, base_id)
        conflict_paths = set(self._authored_conflict_paths(state))
        conflict_paths.update(self._overlapping_conflicts(base_tree, current_tree, target_tree))

        staged_paths: list[str] = []
        for path in sorted(set(current_tree) | set(target_tree)):
            if path in conflict_paths or current_tree.get(path) == target_tree.get(path):
                continue
            after = target_tree.get(path)
            state.setdefault("staging", {})[path] = (
                "deleted"
                if after is None
                else {
                    "status": runtime.normalizer.change_type(current_tree.get(path), after),
                    "content": copy.deepcopy(after),
                }
            )
            staged_paths.append(path)

        if conflict_paths:
            state["merge_parent"] = target_id
            state["merge_abort_state"] = before_merge
            state["conflicts"] = sorted(conflict_paths)
            for path in sorted(conflict_paths):
                state.setdefault("working_tree", {})[path] = self._conflict_entry(
                    path=path,
                    branch=branch,
                    base=base_tree.get(path),
                    ours=current_tree.get(path),
                    theirs=target_tree.get(path),
                    resolution=(state.get("merge_resolutions") or {}).get(path),
                )
            runtime._set_operation_metadata(
                state,
                last_merge_branch=branch,
                last_merge_target=target_id,
                last_merge_conflicted=True,
                last_merge_conflict_paths=sorted(conflict_paths),
            )
            return CommandOutcome(
                command="merge",
                details={"branch": branch, "conflicts": sorted(conflict_paths)},
                exit_code=1,
                stdout=(
                    f"Auto-merging {', '.join(sorted(conflict_paths))}\n"
                    "CONFLICT (content): Merge conflict in "
                    f"{', '.join(sorted(conflict_paths))}\n"
                    "Automatic merge failed; fix conflicts and then commit the result."
                ),
            )

        if self._is_ancestor(state, current_id, target_id):
            runtime._set_head_commit(state, target_id)
            runtime._set_operation_metadata(
                state,
                last_merge_branch=branch,
                last_merge_target=target_id,
                last_merge_fast_forward=True,
            )
            return CommandOutcome(command="merge", stdout=f"Fast-forward\nMerged {branch}.")

        commit_id = runtime._next_commit_id(state)
        changes = runtime._diff_trees(current_tree, target_tree)
        state.setdefault("commits", []).append(
            runtime._commit_payload(
                state=state,
                commit_id=commit_id,
                message=f"Merge branch '{branch}'",
                parents=[item for item in [current_id, target_id] if item],
                tree=target_tree,
                changes=changes,
            )
        )
        state["staging"] = {}
        runtime._set_head_commit(state, commit_id)
        runtime._set_operation_metadata(
            state,
            last_merge_branch=branch,
            last_merge_target=target_id,
            last_merge_created_commit=commit_id,
            last_merge_auto_staged_paths=staged_paths,
        )
        return CommandOutcome(command="merge", stdout=f"Merge made by the 'ort' strategy.\n {len(changes)} file(s) changed")

    def _resolve_ref(self, state: dict, ref: str) -> str | None:
        if ref in state.get("branches", {}):
            return state["branches"][ref]
        if ref in state.get("remote_branches", {}):
            return state["remote_branches"][ref]
        return ref if any(commit.get("id") == ref for commit in state.get("commits", [])) else None

    def _authored_conflict_paths(self, state: dict) -> list[str]:
        if not state.get("conflict_on_merge") and not state.get("merge_conflicts"):
            return []
        paths = state.get("conflict_files") or state.get("merge_conflict_files") or []
        if isinstance(state.get("merge_conflicts"), dict):
            paths = [*paths, *state["merge_conflicts"].keys()]
        return sorted(str(path) for path in paths)

    def _overlapping_conflicts(self, base_tree: dict, current_tree: dict, target_tree: dict) -> set[str]:
        conflicts = set()
        for path in set(base_tree) | set(current_tree) | set(target_tree):
            base = base_tree.get(path)
            ours = current_tree.get(path)
            theirs = target_tree.get(path)
            if ours != base and theirs != base and ours != theirs:
                conflicts.add(path)
        return conflicts

    def _conflict_entry(
        self,
        *,
        path: str,
        branch: str,
        base: object,
        ours: object,
        theirs: object,
        resolution: object,
    ) -> dict:
        ours_text = "" if ours is None else str(ours)
        theirs_text = "" if theirs is None else str(theirs)
        return {
            "status": "conflicted",
            "content": f"<<<<<<< HEAD\n{ours_text}\n=======\n{theirs_text}\n>>>>>>> {branch}\n",
            "base": base,
            "ours": ours,
            "theirs": theirs,
            "resolution": resolution,
        }

    def _common_ancestor(self, state: dict, left: str | None, right: str | None) -> str | None:
        left_history = self._history(state, left)
        right_history = set(self._history(state, right))
        return next((commit_id for commit_id in left_history if commit_id in right_history), None)

    def _is_ancestor(self, state: dict, ancestor: str | None, descendant: str | None) -> bool:
        return bool(ancestor and ancestor in self._history(state, descendant))

    def _history(self, state: dict, commit_id: str | None) -> list[str]:
        commits = {commit["id"]: commit for commit in state.get("commits", [])}
        stack = [commit_id] if commit_id else []
        seen: list[str] = []
        while stack:
            current = stack.pop()
            if current in seen or current not in commits:
                continue
            seen.append(current)
            stack.extend(commits[current].get("parents", []))
        return seen
