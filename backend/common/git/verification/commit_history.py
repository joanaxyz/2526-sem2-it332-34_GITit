"""Cheap backend-side verification for client-submitted Git transitions.

The browser simulator still owns instant UI feedback. This verifier mirrors the
supported mutating command transitions that can affect persisted progress/rewards
without shelling out to Git, so a forged client next_state cannot silently earn
completion.
"""

from __future__ import annotations

import copy
from typing import Any

from common.exceptions import BadRequest
from simulator.services import parse_git_command


class CommitHistoryVerificationMixin:
    def verified_diagnostic_state(
        self,
        *,
        command: str,
        previous_state: dict,
        command_family: str,
        exit_code: int,
    ) -> dict:
        """Return authoritative evidence metadata for supported diagnostics.

        The browser's submitted diagnostic state is never trusted. Evidence is
        derived from the normalized command and the backend-owned previous
        repository state, then limited to the same operation metadata keys the
        frontend simulator records.
        """

        expected = copy.deepcopy(previous_state)
        if exit_code != 0:
            return expected

        parts = parse_git_command(command) or []
        raw_args = parts[2:]
        if (
            command_family == "merge-base"
            and len(raw_args) == 2
            and all(not value.startswith("-") for value in raw_args)
        ):
            left = self._resolve_ref(expected, raw_args[0])
            right = self._resolve_ref(expected, raw_args[1])
            base = self._common_ancestor(expected, left, right)
            if base:
                self._set_operation_metadata(expected, {"last_merge_base": base})
        elif command_family == "rev-list" and len(raw_args) == 2 and raw_args.count("--count") == 1:
            range_arg = next(value for value in raw_args if value != "--count")
            range_parts = range_arg.split("..", 1)
            if len(range_parts) == 2 and all(range_parts):
                left = self._resolve_ref(expected, range_parts[0])
                right = self._resolve_ref(expected, range_parts[1])
                if left and right:
                    count = len(self._commits_since(expected, right, left))
                    self._set_operation_metadata(expected, {"last_rev_list_count": count})

        return self.tools.normalize_state(expected)

    def _verify_commit(self, *, command: str, previous_state: dict, next_state: dict) -> None:
        parts = parse_git_command(command) or []
        expected = copy.deepcopy(previous_state)
        staged_by_all: list[str] = []
        if "-a" in parts or "--all" in parts:
            staged_by_all = self._selected_add_paths(expected, [], include_tracked=True, include_untracked=False)
            self._stage_selected(expected, staged_by_all)

        if "--amend" in parts:
            self._verify_commit_amend(parts=parts, previous_state=previous_state, staged_state=expected, next_state=next_state)
            return

        staged_entries = expected.get("staging") or {}
        if not staged_entries and not expected.get("merge_parent"):
            self._require_same_state(
                previous_state,
                next_state,
                "git commit without staged changes cannot mutate repository state.",
            )
            return

        previous_commits = previous_state.get("commits") or []
        current = self.normalizer.head_commit_id(expected)
        merge_parent = expected.get("merge_parent")
        merge_branch = str((expected.get("operation_metadata") or {}).get("last_merge_branch") or "branch")
        message = self._commit_message(parts) or (f"Merge branch '{merge_branch}'" if merge_parent else "commit")
        parents = [value for value in (current, merge_parent) if value]
        commit_id = self._next_commit_id(expected)
        base_tree = self._tree_for_commit(expected, current)
        staged_snapshot = copy.deepcopy(staged_entries)
        staged_changes = self.normalizer.changes_from_entries(base_tree, staged_snapshot)
        tree = self.normalizer.apply_changes(base_tree, staged_changes)
        expected.setdefault("commits", []).append(
            self._commit_payload(
                state=expected,
                commit_id=commit_id,
                message=message,
                parents=parents,
                tree=tree,
                changes=staged_changes,
            )
        )
        expected["staging"] = {}
        expected.pop("merge_parent", None)
        expected.pop("merge_abort_state", None)
        self._cleanup_partial_hunks_after_commit(expected, staged_snapshot)
        self._set_head_commit(expected, commit_id)
        if merge_parent:
            self._set_operation_metadata(expected, {"last_merge_created_commit": commit_id})
        expected = self.tools.normalize_state(expected)

        next_commits = next_state.get("commits") or []
        if len(next_commits) != len(previous_commits) + 1:
            raise BadRequest("execution.next_state does not match the submitted git commit command.")
        self._require_equivalent_expected(expected, next_state, "git commit")
    def _verify_commit_amend(self, *, parts: list[str], previous_state: dict, staged_state: dict, next_state: dict) -> None:
        current = self.normalizer.head_commit_id(staged_state)
        old_commit = self.normalizer.commit_by_id(staged_state, current)
        if not old_commit:
            raise BadRequest("execution.next_state does not match the submitted git commit --amend command.")
        message = self._commit_message(parts)
        if message is None:
            message = old_commit.get("message") or "commit"
        parent_ids = list(old_commit.get("parents") or [])
        parent_id = parent_ids[0] if parent_ids else None
        parent_tree = self._tree_for_commit(staged_state, parent_id)
        current_tree = copy.deepcopy(old_commit.get("tree") or parent_tree)
        staged_entries = copy.deepcopy(staged_state.get("staging") or {})
        if not staged_entries and self._commit_message(parts) is None and "--no-edit" not in parts:
            self._require_same_state(previous_state, next_state, "git commit --amend without changes cannot mutate repository state.")
            return
        staged_changes = self.normalizer.changes_from_entries(current_tree, staged_entries)
        amended_tree = self.normalizer.apply_changes(current_tree, staged_changes)
        commit_id = self._next_commit_id(staged_state)
        changes = self.normalizer.diff_trees(parent_tree, amended_tree)
        expected = copy.deepcopy(staged_state)
        expected.setdefault("commits", []).append(
            self._commit_payload(
                state=expected,
                commit_id=commit_id,
                message=message,
                parents=parent_ids,
                tree=amended_tree,
                changes=changes,
            )
        )
        expected.setdefault("replaced_commits", {})
        if current:
            expected["replaced_commits"][current] = commit_id
        self._set_operation_metadata(expected, {"last_amend_replaced_commit": current, "last_amend_created_commit": commit_id})
        expected["staging"] = {}
        self._cleanup_partial_hunks_after_commit(expected, staged_entries)
        self._set_head_commit(expected, commit_id)
        if commit_id:
            expected.setdefault("reflog", []).append({"ref": f"HEAD@{{{len(expected.get('reflog', []))}}}", "target": commit_id, "message": f"commit --amend: replaced {current}"})
        expected = self.tools.normalize_state(expected)
        self._require_equivalent_expected(expected, next_state, "git commit --amend")
    def _verify_rebase(self, *, command: str, previous_state: dict, next_state: dict) -> None:
        parts = parse_git_command(command) or []
        if "--abort" in parts:
            rebase_state = previous_state.get("rebase_state") if isinstance(previous_state.get("rebase_state"), dict) else None
            abort_state = (rebase_state or {}).get("abort_state")
            if not isinstance(abort_state, dict):
                raise BadRequest("execution.next_state does not match the submitted git rebase --abort command.")
            expected = copy.deepcopy(abort_state)
            self._set_operation_metadata(expected, {"last_rebase_aborted": True})
            expected = self.tools.normalize_state(expected)
            self._require_equivalent_expected(expected, next_state, "git rebase --abort")
            return
        if "--continue" in parts:
            if not isinstance(previous_state.get("rebase_state"), dict) or (previous_state.get("conflicts") or []):
                raise BadRequest("execution.next_state does not match the submitted git rebase --continue command.")
            remaining = [str(item) for item in ((previous_state.get("rebase_state") or {}).get("remaining") or [])]
            if not remaining:
                expected = copy.deepcopy(previous_state)
                self._set_operation_metadata(expected, {"last_rebase_new_head": self.normalizer.head_commit_id(expected), "last_rebase_replayed_commits": copy.deepcopy((expected.get("rebase_state") or {}).get("applied") or [])})
                expected.pop("rebase_state", None)
                expected = self.tools.normalize_state(expected)
                self._require_equivalent_expected(expected, next_state, "git rebase --continue")
                return
            raise BadRequest("execution.next_state does not match the submitted git rebase --continue command.")

        args = self._pathspecs(parts, value_options={"--onto"})
        onto = self._option_value(parts, "--onto")
        has_onto = onto is not None
        if not args:
            raise BadRequest("execution.next_state does not match the submitted git rebase command.")
        new_base_ref = onto if has_onto else args[0]
        upstream_ref = args[0]
        branch_ref = args[1] if has_onto and len(args) > 1 else None
        new_base = self._resolve_ref(previous_state, new_base_ref)
        upstream = self._resolve_ref(previous_state, upstream_ref)
        if not new_base or not upstream:
            raise BadRequest("execution.next_state does not match the submitted git rebase command.")
        expected = copy.deepcopy(previous_state)
        if branch_ref:
            if branch_ref not in (expected.get("branches") or {}):
                raise BadRequest("execution.next_state does not match the submitted git rebase command.")
            expected["head"] = {"type": "branch", "name": branch_ref, "target": (expected.get("branches") or {}).get(branch_ref)}
        current_branch = self._head_branch(expected)
        if not current_branch:
            raise BadRequest("execution.next_state does not match the submitted git rebase command.")
        branch_tip = self.normalizer.head_commit_id(expected)
        if branch_tip == new_base:
            self._require_same_state(previous_state, next_state, "up-to-date git rebase cannot mutate repository state.")
            return
        applied = self._replay_linear_commits(expected, branch_tip, self._common_ancestor(expected, branch_tip, upstream), new_base)
        self._set_operation_metadata(
            expected,
            {
                "last_rebase_target": new_base_ref,
                "last_rebase_onto": new_base if has_onto else None,
                "last_rebase_upstream": upstream,
                "last_rebase_new_head": self.normalizer.head_commit_id(expected),
                "last_rebase_interactive": "-i" in parts or "--interactive" in parts,
                "last_rebase_replayed_commits": applied,
            },
        )
        expected = self.tools.normalize_state(expected)
        self._require_equivalent_expected(expected, next_state, "git rebase")
    def _verify_revert(self, *, command: str, previous_state: dict, next_state: dict) -> None:
        parts = parse_git_command(command) or []
        args = self._pathspecs(parts)
        source_id = self._resolve_revision(previous_state, args[0] if args else None)
        source = self.normalizer.commit_by_id(previous_state, source_id)
        if not source:
            raise BadRequest("execution.next_state does not match the submitted git revert command.")
        head_id = self.normalizer.head_commit_id(previous_state)
        head_tree = self.normalizer.head_tree(previous_state)
        reverted_changes = {}
        for path, change in (source.get("changes") or {}).items():
            reverted_changes[path] = {
                "change_type": self.normalizer.change_type(head_tree.get(path), change.get("before")),
                "before": head_tree.get(path),
                "after": change.get("before"),
            }
        next_tree = self.normalizer.apply_changes(head_tree, reverted_changes)
        commit_id = self._next_commit_id(previous_state)
        expected = copy.deepcopy(previous_state)
        expected.setdefault("commits", []).append(
            self._commit_payload(
                state=previous_state,
                commit_id=commit_id,
                message=f'Revert "{source.get("message") or source.get("id")}"',
                parents=[head_id] if head_id else [],
                tree=next_tree,
                changes=self.normalizer.diff_trees(head_tree, next_tree),
            )
        )
        self._set_head_commit(expected, commit_id)
        self._set_operation_metadata(expected, {"last_revert_source": source_id, "last_revert_created_commit": commit_id, "last_revert_no_edit": "--no-edit" in parts})
        expected.setdefault("reflog", []).append({"ref": f"HEAD@{{{len(expected.get('reflog', []))}}}", "target": commit_id, "message": f"revert: {source_id}"})
        expected = self.tools.normalize_state(expected)
        self._require_equivalent_expected(expected, next_state, "git revert")
    def _verify_cherry_pick(self, *, command: str, previous_state: dict, next_state: dict) -> None:
        parts = parse_git_command(command) or []
        if "--abort" in parts:
            expected = copy.deepcopy(previous_state)
            original = expected.get("cherry_pick_original_head")
            if original:
                self._set_head_commit(expected, original)
            expected["staging"] = {}
            expected["working_tree"] = {}
            expected["conflicts"] = []
            expected.pop("cherry_pick_in_progress", None)
            expected.pop("cherry_pick_original_head", None)
            self._set_operation_metadata(expected, {"last_cherry_pick_aborted": True})
            expected = self.tools.normalize_state(expected)
            self._require_equivalent_expected(expected, next_state, "git cherry-pick --abort")
            return
        args = self._pathspecs(parts)
        source_id = self._resolve_revision(previous_state, args[0] if args else None)
        source = self.normalizer.commit_by_id(previous_state, source_id)
        if not source:
            raise BadRequest("execution.next_state does not match the submitted git cherry-pick command.")
        head_id = self.normalizer.head_commit_id(previous_state)
        head_tree = self.normalizer.head_tree(previous_state)
        next_tree = self.normalizer.apply_changes(head_tree, source.get("changes") or {})
        changes = self.normalizer.diff_trees(head_tree, next_tree)
        expected = copy.deepcopy(previous_state)
        if "--no-commit" in parts or "-n" in parts:
            expected["staging"] = {
                path: "deleted" if change.get("after") is None else {"status": change.get("change_type"), "content": copy.deepcopy(change.get("after"))}
                for path, change in changes.items()
            }
            expected["cherry_pick_in_progress"] = True
            expected["cherry_pick_original_head"] = head_id
            self._set_operation_metadata(expected, {"cherry_pick_in_progress": True, "cherry_pick_original_head": head_id, "last_cherry_pick_source": source_id, "last_cherry_pick_no_commit": True})
        else:
            commit_id = self._next_commit_id(previous_state)
            expected.setdefault("commits", []).append(
                self._commit_payload(
                    state=previous_state,
                    commit_id=commit_id,
                    message=source.get("message") or f"cherry-pick {source_id}",
                    parents=[head_id] if head_id else [],
                    tree=next_tree,
                    changes=changes,
                )
            )
            self._set_head_commit(expected, commit_id)
            self._set_operation_metadata(expected, {"last_cherry_pick_source": source_id, "last_cherry_pick_created_commit": commit_id, "last_cherry_pick_no_commit": False})
        expected = self.tools.normalize_state(expected)
        self._require_equivalent_expected(expected, next_state, "git cherry-pick")
    def _replay_linear_commits(self, state: dict, branch_tip: str | None, stop_at: str | None, new_base: str | None) -> list[str]:
        commits_to_replay = list(reversed(self._commits_since(state, branch_tip, stop_at)))
        new_head = new_base
        applied: list[str] = []
        for source_id in commits_to_replay:
            source = self.normalizer.commit_by_id(state, source_id)
            if not source:
                continue
            base = self._tree_for_commit(state, new_head)
            next_tree = self.normalizer.apply_changes(base, source.get("changes") or {})
            commit_id = self._next_commit_id(state)
            state.setdefault("commits", []).append(
                self._commit_payload(
                    state=state,
                    commit_id=commit_id,
                    message=source.get("message") or f"rebase {source_id}",
                    parents=[new_head] if new_head else [],
                    tree=next_tree,
                    changes=self.normalizer.diff_trees(base, next_tree),
                )
            )
            new_head = commit_id
            applied.append(commit_id)
        self._set_head_commit(state, new_head)
        return applied
    def _commits_since(self, state: dict, commit_id: str | None, stop_at: str | None) -> list[str]:
        result: list[str] = []
        current = commit_id
        while current and current != stop_at:
            result.append(current)
            commit = self.normalizer.commit_by_id(state, current)
            current = (commit.get("parents") or [None])[0] if commit else None
        return result
    def _entries_from_tree_diff(self, before: dict, after: dict) -> dict:
        entries: dict[str, Any] = {}
        for path in sorted(set(before) | set(after)):
            old_value = before.get(path)
            new_value = after.get(path)
            if old_value == new_value:
                continue
            entries[path] = "deleted" if new_value is None else {
                "status": self.normalizer.change_type(old_value, new_value),
                "content": copy.deepcopy(new_value),
            }
        return entries
    def _set_operation_metadata(self, state: dict, metadata: dict[str, Any]) -> None:
        state.setdefault("operation_metadata", {}).update(copy.deepcopy(metadata))
        for key, value in metadata.items():
            state[key] = copy.deepcopy(value)
    def _commit_payload(
        self,
        *,
        state: dict,
        commit_id: str,
        message: str,
        parents: list[str],
        tree: dict,
        changes: dict,
    ) -> dict:
        return {
            "id": commit_id,
            "message": message,
            "parents": copy.deepcopy(parents),
            "tree": copy.deepcopy(tree),
            "changes": copy.deepcopy(changes),
            "files": self.normalizer.files_from_changes(changes),
            "author": "GIT it",
            "order": len(state.get("commits", [])),
            "is_merge": len(parents) > 1,
        }
    def _history(self, state: dict, commit_id: str | None) -> list[str]:
        commits = {commit.get("id"): commit for commit in state.get("commits", [])}
        stack = [commit_id] if commit_id else []
        seen: list[str] = []
        while stack:
            current = stack.pop()
            if not current or current in seen or current not in commits:
                continue
            seen.append(current)
            stack.extend(commits[current].get("parents") or [])
        return seen
    def _is_ancestor(self, state: dict, ancestor: str | None, descendant: str | None) -> bool:
        return bool(ancestor and ancestor in self._history(state, descendant))
    def _common_ancestor(self, state: dict, left: str | None, right: str | None) -> str | None:
        right_history = set(self._history(state, right))
        return next((commit_id for commit_id in self._history(state, left) if commit_id in right_history), None)
    def _next_commit_id(self, state: dict) -> str:
        existing = {commit.get("id") for commit in state.get("commits", [])}
        index = 0
        while f"c{index}" in existing:
            index += 1
        return f"c{index}"
    def _commit_message(self, parts: list[str]) -> str | None:
        for index, part in enumerate(parts):
            if part in {"-m", "--message"} and index + 1 < len(parts):
                return parts[index + 1]
            if part.startswith("--message="):
                return part.split("=", 1)[1]
        return None
    def _option_value(self, parts: list[str], *names: str) -> str | None:
        for index, part in enumerate(parts):
            for name in names:
                if part == name and index + 1 < len(parts):
                    return parts[index + 1]
                if name.startswith("--") and part.startswith(f"{name}="):
                    return part.split("=", 1)[1]
        return None
