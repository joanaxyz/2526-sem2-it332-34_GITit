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


class MergeStashVerificationMixin:
    def _verify_stash(self, *, command: str, previous_state: dict, next_state: dict) -> None:
        for key in {
            "repository_initialized",
            "commits",
            "branches",
            "head",
            "remotes",
            "remote_branches",
            "upstream_tracking",
            "tags",
            "remote_tags",
            "reflog",
            "replaced_commits",
            "config",
        }:
            self._require_same_key(key, previous_state, next_state)
        parts = parse_git_command(command) or []
        raw_args = parts[2:]
        known_subcommands = {"push", "save", "apply", "pop", "drop", "list", "show"}
        subcommand = next((part for part in raw_args if part in known_subcommands), "push")
        if subcommand in {"list", "show"}:
            self._require_same_state(previous_state, next_state, f"git stash {subcommand} cannot mutate repository state.")
            return
        expected = copy.deepcopy(previous_state)
        if subcommand in {"push", "save"}:
            include_untracked = "-u" in parts or "--include-untracked" in parts
            working_tree = {
                path: copy.deepcopy(value)
                for path, value in (previous_state.get("working_tree") or {}).items()
                if include_untracked or self.normalizer.entry_status(value) != "untracked"
            }
            if not working_tree and not (previous_state.get("staging") or {}) and not (previous_state.get("conflicts") or []):
                self._require_same_state(previous_state, next_state, "empty git stash cannot mutate repository state.")
                return
            message = self._option_value(parts, "-m", "--message") or f"WIP on {self._head_branch(previous_state) or 'HEAD'}"
            expected.setdefault("stash_stack", []).append(
                {
                    "working_tree": copy.deepcopy(working_tree),
                    "staging": copy.deepcopy(previous_state.get("staging") or {}),
                    "conflicts": copy.deepcopy(previous_state.get("conflicts") or []),
                    "message": message,
                }
            )
            expected["working_tree"] = copy.deepcopy(previous_state.get("working_tree") or {})
            for path in working_tree:
                expected["working_tree"].pop(path, None)
            expected["staging"] = {}
            expected["conflicts"] = []
            self._set_operation_metadata(expected, {"last_stash_action": "push", "last_stash_operation": "push", "stash_count": len(expected.get("stash_stack") or [])})
        elif subcommand in {"apply", "pop"}:
            index = self._stash_index(raw_args[1] if len(raw_args) > 1 else None)
            real_index = len(expected.get("stash_stack") or []) - 1 - index
            entry = (expected.get("stash_stack") or [])[real_index] if 0 <= real_index < len(expected.get("stash_stack") or []) else None
            if not entry:
                raise BadRequest("execution.next_state does not match the submitted git stash command.")
            expected.setdefault("working_tree", {}).update(copy.deepcopy(entry.get("working_tree") or {}))
            expected.setdefault("staging", {}).update(copy.deepcopy(entry.get("staging") or {}))
            expected["conflicts"] = copy.deepcopy(entry.get("conflicts") or [])
            if subcommand == "pop":
                expected["stash_stack"].pop(real_index)
            self._set_operation_metadata(expected, {"last_stash_action": subcommand, "last_stash_operation": subcommand, "stash_count": len(expected.get("stash_stack") or [])})
        elif subcommand == "drop":
            index = self._stash_index(raw_args[1] if len(raw_args) > 1 else None)
            real_index = len(expected.get("stash_stack") or []) - 1 - index
            if not (0 <= real_index < len(expected.get("stash_stack") or [])):
                raise BadRequest("execution.next_state does not match the submitted git stash command.")
            expected["stash_stack"].pop(real_index)
            self._set_operation_metadata(expected, {"last_stash_action": "drop", "last_stash_operation": "drop", "stash_count": len(expected.get("stash_stack") or [])})
        else:
            raise BadRequest("execution.next_state does not match the submitted git stash command.")
        expected = self.tools.normalize_state(expected)
        self._require_equivalent_expected(expected, next_state, "git stash")
    def _verify_merge(self, *, command: str, previous_state: dict, next_state: dict) -> None:
        expected = self._expected_merge_state(command=command, previous_state=previous_state)
        expected = self.tools.normalize_state(expected)
        self._require_equivalent_expected(expected, next_state, "git merge")
    def _expected_merge_state(self, *, command: str, previous_state: dict) -> dict:
        parts = parse_git_command(command) or []
        if "--abort" in parts:
            expected = copy.deepcopy(previous_state.get("merge_abort_state") or {})
            if expected:
                self._set_operation_metadata(expected, {"last_merge_aborted": True})
            else:
                expected = copy.deepcopy(previous_state)
                expected["conflicts"] = []
                expected["staging"] = {}
                expected["working_tree"] = {}
                expected.pop("conflict_details", None)
                expected.pop("merge_parent", None)
                self._set_operation_metadata(expected, {"last_merge_aborted": True})
            return expected
        if "--continue" in parts:
            # Reuse the commit verifier semantics by building the same expected
            # merge commit that `git commit` creates while merge_parent is set.
            if not previous_state.get("merge_parent") or (previous_state.get("conflicts") or []):
                raise BadRequest("execution.next_state does not match the submitted git merge --continue command.")
            expected = copy.deepcopy(previous_state)
            staged_entries = expected.get("staging") or {}
            current = self.normalizer.head_commit_id(expected)
            merge_parent = expected.get("merge_parent")
            merge_branch = str((expected.get("operation_metadata") or {}).get("last_merge_branch") or "branch")
            commit_id = self._next_commit_id(expected)
            base_tree = self._tree_for_commit(expected, current)
            staged_changes = self.normalizer.changes_from_entries(base_tree, staged_entries)
            tree = self.normalizer.apply_changes(base_tree, staged_changes)
            expected.setdefault("commits", []).append(
                self._commit_payload(
                    state=expected,
                    commit_id=commit_id,
                    message=f"Merge branch '{merge_branch}'",
                    parents=[value for value in (current, merge_parent) if value],
                    tree=tree,
                    changes=staged_changes,
                )
            )
            expected["staging"] = {}
            expected.pop("merge_parent", None)
            expected.pop("merge_abort_state", None)
            self._set_head_commit(expected, commit_id)
            self._set_operation_metadata(expected, {"last_merge_created_commit": commit_id})
            return expected

        args = self._pathspecs(parts)
        branch = args[0] if args else ""
        target_id = self._resolve_ref(previous_state, branch)
        if not target_id:
            raise BadRequest("execution.next_state does not match the submitted git merge command.")
        current_id = self.normalizer.head_commit_id(previous_state)
        if current_id == target_id:
            return copy.deepcopy(previous_state)

        current_tree = self.normalizer.head_tree(previous_state)
        target_tree = self._tree_for_commit(previous_state, target_id)
        base_id = self._common_ancestor(previous_state, current_id, target_id)
        base_tree = self._tree_for_commit(previous_state, base_id)

        if "--squash" in parts:
            expected = copy.deepcopy(previous_state)
            expected_staging = copy.deepcopy(previous_state.get("staging") or {})
            for path, value in target_tree.items():
                if value != current_tree.get(path):
                    expected_staging[path] = {"status": self.normalizer.change_type(current_tree.get(path), value), "content": copy.deepcopy(value)}
            for path in current_tree:
                if path not in target_tree:
                    expected_staging[path] = "deleted"
            expected["staging"] = expected_staging
            return expected

        conflict_paths = set(self._authored_conflict_paths(previous_state))
        conflict_paths.update(self._overlapping_conflicts(base_tree, current_tree, target_tree))
        if conflict_paths:
            expected = copy.deepcopy(previous_state)
            expected["merge_parent"] = target_id
            expected["merge_abort_state"] = copy.deepcopy(previous_state)
            expected["conflicts"] = sorted(conflict_paths)
            expected.setdefault("conflict_details", {})
            expected.setdefault("working_tree", {})
            for path in expected["conflicts"]:
                resolution = ((previous_state.get("merge_resolutions") or {}).get(path))
                expected["conflict_details"][path] = {
                    "base": copy.deepcopy(base_tree.get(path)),
                    "ours": copy.deepcopy(current_tree.get(path)),
                    "theirs": copy.deepcopy(target_tree.get(path)),
                    "resolution": copy.deepcopy(resolution),
                    "merge_branch": branch,
                }
                expected["working_tree"][path] = self._conflict_entry(
                    branch,
                    base_tree.get(path),
                    current_tree.get(path),
                    target_tree.get(path),
                    resolution,
                )
            for path in sorted(set(current_tree) | set(target_tree)):
                if path in conflict_paths or current_tree.get(path) == target_tree.get(path):
                    continue
                after = target_tree.get(path)
                expected.setdefault("staging", {})[path] = "deleted" if after is None else {
                    "status": self.normalizer.change_type(current_tree.get(path), after),
                    "content": copy.deepcopy(after),
                }
            self._set_operation_metadata(expected, {"last_merge_branch": branch, "last_merge_target": target_id, "last_merge_conflicted": True, "last_merge_conflict_paths": sorted(conflict_paths)})
            return expected

        no_ff = "--no-ff" in parts
        if not no_ff and self._is_ancestor(previous_state, current_id, target_id):
            expected = copy.deepcopy(previous_state)
            self._set_head_commit(expected, target_id)
            self._set_operation_metadata(expected, {"last_merge_branch": branch, "last_merge_target": target_id, "last_merge_fast_forward": True})
            return expected

        staged_paths = [
            path
            for path in sorted(set(current_tree) | set(target_tree))
            if current_tree.get(path) != target_tree.get(path)
        ]
        expected = copy.deepcopy(previous_state)
        commit_id = self._next_commit_id(previous_state)
        changes = self.normalizer.diff_trees(current_tree, target_tree)
        expected.setdefault("commits", []).append(
            self._commit_payload(
                state=previous_state,
                commit_id=commit_id,
                message=f"Merge branch '{branch}'",
                parents=[value for value in (current_id, target_id) if value],
                tree=target_tree,
                changes=changes,
            )
        )
        expected["staging"] = {}
        self._set_head_commit(expected, commit_id)
        self._set_operation_metadata(expected, {"last_merge_branch": branch, "last_merge_target": target_id, "last_merge_created_commit": commit_id, "last_merge_auto_staged_paths": staged_paths, "last_merge_no_ff": no_ff})
        return expected
    def _verify_mergetool(self, *, command: str, previous_state: dict, next_state: dict) -> None:
        for key in {
            "repository_initialized",
            "commits",
            "branches",
            "head",
            "staging",
            "working_tree",
            "conflicts",
            "conflict_details",
            "partial_hunks",
            "remotes",
            "remote_branches",
            "upstream_tracking",
            "tags",
            "remote_tags",
            "stash_stack",
            "reflog",
            "replaced_commits",
            "config",
        }:
            self._require_same_key(key, previous_state, next_state)
        parts = parse_git_command(command) or []
        paths = self._pathspecs(parts, value_options={"--tool"})
        conflicts = list(previous_state.get("conflicts") or [])
        if not conflicts:
            raise BadRequest("execution.next_state does not match the submitted git mergetool command.")
        selected = [path for path in conflicts if not paths or path in paths]
        if not selected:
            raise BadRequest("execution.next_state does not match the submitted git mergetool command.")
        tool = self._option_value(parts, "--tool") or (previous_state.get("config") or {}).get("merge.tool") or (previous_state.get("operation_metadata") or {}).get("configured_merge_tool") or "tool"
        expected_metadata = copy.deepcopy(previous_state.get("operation_metadata") or {})
        expected_metadata.update({"last_mergetool_tool": tool, "last_mergetool_paths": selected, "last_mergetool_opened": True})
        if next_state.get("operation_metadata") != expected_metadata:
            raise BadRequest("execution.next_state does not match the submitted git mergetool command.")
        for key, value in {"last_mergetool_tool": tool, "last_mergetool_paths": selected, "last_mergetool_opened": True}.items():
            if next_state.get(key) != value:
                raise BadRequest("execution.next_state does not match the submitted git mergetool command.")
    def _stash_index(self, raw: str | None) -> int:
        if not raw:
            return 0
        if raw.startswith("stash@{") and raw.endswith("}"):
            try:
                return int(raw[7:-1])
            except ValueError:
                return 0
        try:
            return int(raw)
        except ValueError:
            return 0
    def _authored_conflict_paths(self, state: dict) -> list[str]:
        if not state.get("conflict_on_merge") and not state.get("merge_conflicts"):
            return []
        paths = list(state.get("conflict_files") or []) + list(state.get("merge_conflict_files") or [])
        merge_conflicts = state.get("merge_conflicts") or {}
        if isinstance(merge_conflicts, dict):
            paths.extend(merge_conflicts.keys())
        return sorted({str(path) for path in paths})
    def _overlapping_conflicts(self, base_tree: dict, current_tree: dict, target_tree: dict) -> list[str]:
        conflicts: list[str] = []
        for path in sorted(set(base_tree) | set(current_tree) | set(target_tree)):
            base = base_tree.get(path)
            ours = current_tree.get(path)
            theirs = target_tree.get(path)
            if ours != base and theirs != base and ours != theirs:
                conflicts.append(path)
        return conflicts
    def _conflict_entry(self, branch: str, base: Any, ours: Any, theirs: Any, resolution: Any) -> dict:
        return {
            "status": "conflicted",
            "content": f"<<<<<<< HEAD\n{ours or ''}\n=======\n{theirs or ''}\n>>>>>>> {branch}\n",
            "base": copy.deepcopy(base),
            "ours": copy.deepcopy(ours),
            "theirs": copy.deepcopy(theirs),
            "resolution": copy.deepcopy(resolution),
        }
