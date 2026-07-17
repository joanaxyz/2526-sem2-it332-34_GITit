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


class StagingVerificationMixin:
    def _verify_add(self, *, command: str, previous_state: dict, next_state: dict) -> None:
        for key in self.ADD_IMMUTABLE_KEYS:
            self._require_same_key(key, previous_state, next_state)

        parts = parse_git_command(command) or []
        args = self._pathspecs(parts)
        if "-p" in parts or "--patch" in parts:
            expected = copy.deepcopy(previous_state)
            selected = self._selected_patch_paths(expected, args)
            if not selected:
                raise BadRequest("execution.next_state does not match the submitted git add --patch command.")
            for path in selected:
                if path not in (expected.get("working_tree") or {}) and path not in (expected.get("partial_hunks") or {}):
                    continue
                if self.normalizer.entry_status((expected.get("working_tree") or {}).get(path)) == "ignored":
                    continue
                authored = (expected.get("partial_hunks") or {}).get(path)
                target_hunks, leftover_hunks = self._partial_hunk_lists(authored)
                expected.setdefault("staging", {})[path] = {"status": "partial", "hunks": target_hunks or self._entry_tokens((expected.get("working_tree") or {}).get(path))}
                if target_hunks or leftover_hunks:
                    if leftover_hunks:
                        expected.setdefault("working_tree", {})[path] = {"status": "modified", "hunks": leftover_hunks}
                    else:
                        expected.setdefault("working_tree", {}).pop(path, None)
                else:
                    expected.setdefault("working_tree", {})[path] = "modified"
            expected = self.tools.normalize_state(expected)
            self._require_equivalent_expected(expected, next_state, "git add --patch")
            return

        include_untracked = "-u" not in parts and "--update" not in parts
        selected = self._selected_add_paths(previous_state, args, include_untracked=include_untracked)
        if not selected:
            # Empty add is a no-op in authored scenarios. It cannot rewrite index
            # or worktree wholesale.
            self._require_same_key("staging", previous_state, next_state)
            self._require_same_key("working_tree", previous_state, next_state)
            return

        expected_staging = copy.deepcopy(previous_state.get("staging") or {})
        expected_working = copy.deepcopy(previous_state.get("working_tree") or {})
        expected_conflicts = set(previous_state.get("conflicts") or [])
        expected_details = copy.deepcopy(previous_state.get("conflict_details") or {})
        for path in selected:
            if self.normalizer.entry_status(expected_working.get(path)) == "ignored":
                continue
            expected_staging[path] = copy.deepcopy(expected_working.get(path, "updated"))
            expected_working.pop(path, None)
            expected_conflicts.discard(path)
            expected_details.pop(path, None)

        if next_state.get("staging") != expected_staging:
            raise BadRequest("execution.next_state does not match the submitted git add command.")
        if next_state.get("working_tree") != expected_working:
            raise BadRequest("execution.next_state does not match the submitted git add command.")
        if sorted(next_state.get("conflicts") or []) != sorted(expected_conflicts):
            raise BadRequest("execution.next_state does not match the submitted git add command.")
        if next_state.get("conflict_details") != expected_details:
            raise BadRequest("execution.next_state does not match the submitted git add command.")
    def _verify_rm(self, *, command: str, previous_state: dict, next_state: dict) -> None:
        for key in self.INDEX_WORKTREE_IMMUTABLE_KEYS:
            self._require_same_key(key, previous_state, next_state)
        parts = parse_git_command(command) or []
        cached = "--cached" in parts
        paths = self._expand_pathspecs(self.normalizer.head_tree(previous_state), self._pathspecs(parts))
        if not paths:
            self._require_same_key("staging", previous_state, next_state)
            self._require_same_key("working_tree", previous_state, next_state)
            return
        base_tree = self.normalizer.head_tree(previous_state)
        expected_staging = copy.deepcopy(previous_state.get("staging") or {})
        expected_working = copy.deepcopy(previous_state.get("working_tree") or {})
        for path in paths:
            if path not in base_tree and path not in expected_staging:
                raise BadRequest("execution.next_state does not match the submitted git rm command.")
            expected_staging[path] = "deleted"
            if cached:
                expected_working[path] = {"status": "untracked", "content": base_tree.get(path, "")}
            else:
                expected_working.pop(path, None)
        if next_state.get("staging") != expected_staging or next_state.get("working_tree") != expected_working:
            raise BadRequest("execution.next_state does not match the submitted git rm command.")
    def _verify_restore(self, *, command: str, previous_state: dict, next_state: dict) -> None:
        for key in self.INDEX_WORKTREE_IMMUTABLE_KEYS:
            self._require_same_key(key, previous_state, next_state)
        parts = parse_git_command(command) or []
        paths = self._pathspecs(parts, value_options={"--source"})
        source = self._option_value(parts, "--source")
        if "--staged" in parts:
            if source:
                return
            if "." in paths:
                paths = sorted(previous_state.get("staging") or {})
            expected_staging = copy.deepcopy(previous_state.get("staging") or {})
            expected_working = copy.deepcopy(previous_state.get("working_tree") or {})
            for path in paths:
                if path in expected_staging:
                    expected_working[path] = copy.deepcopy(expected_staging.get(path, "modified"))
                    expected_staging.pop(path, None)
            if next_state.get("staging") != expected_staging or next_state.get("working_tree") != expected_working:
                raise BadRequest("execution.next_state does not match the submitted git restore command.")
            return

        expected_working = copy.deepcopy(previous_state.get("working_tree") or {})
        expected_conflicts = set(previous_state.get("conflicts") or [])
        expected_details = copy.deepcopy(previous_state.get("conflict_details") or {})
        if source:
            source_commit = self._resolve_revision(previous_state, source)
            if not source_commit:
                raise BadRequest("execution.next_state does not match the submitted git restore command.")
            source_tree = self._tree_for_commit(previous_state, source_commit)
            head_tree = self.normalizer.head_tree(previous_state)
            for path in paths:
                if path not in source_tree:
                    expected_working[path] = "deleted"
                else:
                    expected_working[path] = {
                        "status": self.normalizer.change_type(head_tree.get(path), source_tree[path]),
                        "content": copy.deepcopy(source_tree[path]),
                    }
        else:
            if "." in paths:
                paths = sorted(
                    path
                    for path, value in (previous_state.get("working_tree") or {}).items()
                    if self.normalizer.entry_status(value) not in {"ignored", "untracked"}
                )
            head_tree = self.normalizer.head_tree(previous_state)
            for path in paths:
                if path not in expected_working and path not in head_tree:
                    raise BadRequest("execution.next_state does not match the submitted git restore command.")
                expected_working.pop(path, None)
                expected_conflicts.discard(path)
                expected_details.pop(path, None)
        if next_state.get("working_tree") != expected_working:
            raise BadRequest("execution.next_state does not match the submitted git restore command.")
        if sorted(next_state.get("conflicts") or []) != sorted(expected_conflicts):
            raise BadRequest("execution.next_state does not match the submitted git restore command.")
        if next_state.get("conflict_details") != expected_details:
            raise BadRequest("execution.next_state does not match the submitted git restore command.")
    def _verify_reset(self, *, command: str, previous_state: dict, next_state: dict) -> None:
        parts = parse_git_command(command) or []
        args = self._pathspecs(parts)
        target_expr = args[0] if args else "HEAD"
        target = self._resolve_revision(previous_state, target_expr)
        if not target:
            raise BadRequest("execution.next_state does not match the submitted git reset command.")
        mode = "soft" if "--soft" in parts else "mixed" if "--mixed" in parts else "hard"
        expected = copy.deepcopy(previous_state)
        expected["merge_abort_state"] = copy.deepcopy(previous_state)
        old_head = self.normalizer.head_commit_id(previous_state)
        old_tree = self.normalizer.head_tree(previous_state)
        target_tree = self._tree_for_commit(previous_state, target)
        self._set_head_commit(expected, target)
        if mode == "soft":
            expected["staging"] = self._entries_from_tree_diff(target_tree, old_tree)
        elif mode == "mixed":
            expected["staging"] = {}
            expected["working_tree"] = self._entries_from_tree_diff(target_tree, old_tree)
        else:
            expected["staging"] = {}
            expected["working_tree"] = {}
            expected["conflicts"] = []
            expected.pop("conflict_details", None)
            expected.pop("merge_parent", None)
            expected.pop("cherry_pick_in_progress", None)
            expected.pop("cherry_pick_original_head", None)
        self._set_operation_metadata(
            expected,
            {
                "last_reset_mode": mode,
                "last_reset_target": target,
                "last_reset_target_expr": target_expr,
                "last_reset_previous_head": old_head,
            },
        )
        if target:
            expected.setdefault("reflog", []).append(
                {
                    "ref": f"HEAD@{{{len(expected.get('reflog', []))}}}",
                    "target": target,
                    "message": f"reset: moving to {target_expr}",
                }
            )
        expected = self.tools.normalize_state(expected)
        self._require_equivalent_expected(expected, next_state, "git reset")
    def _stage_selected(self, state: dict, paths: list[str]) -> None:
        state.setdefault("working_tree", {})
        state.setdefault("staging", {})
        conflicts = set(state.get("conflicts") or [])
        details = state.setdefault("conflict_details", {})
        for path in paths:
            if self.normalizer.entry_status((state.get("working_tree") or {}).get(path)) == "ignored":
                continue
            state["staging"][path] = copy.deepcopy((state.get("working_tree") or {}).get(path, "updated"))
            state["working_tree"].pop(path, None)
            conflicts.discard(path)
            details.pop(path, None)
        state["conflicts"] = sorted(conflicts)
    def _cleanup_partial_hunks_after_commit(self, state: dict, staged_entries: dict) -> None:
        state.setdefault("partial_hunks", {})
        for path, staged_value in (staged_entries or {}).items():
            if self.normalizer.entry_status(staged_value) != "partial":
                continue
            authored = (state.get("partial_hunks") or {}).get(path)
            if not isinstance(authored, dict):
                continue
            leftover = self._as_list(authored.get("leftover_hunks") or authored.get("remaining_hunks") or authored.get("leftover"))
            if leftover:
                state["partial_hunks"][path] = {"target_hunks": [], "leftover_hunks": leftover}
            else:
                state["partial_hunks"].pop(path, None)
    def _selected_patch_paths(self, state: dict, args: list[str]) -> list[str]:
        if args:
            return args
        if state.get("partial_hunks"):
            return list((state.get("partial_hunks") or {}).keys())
        return [
            path
            for path, value in (state.get("working_tree") or {}).items()
            if self.normalizer.entry_status(value) not in {"ignored", "untracked"}
        ]
    def _partial_hunk_lists(self, authored: Any) -> tuple[list[Any], list[Any]]:
        if isinstance(authored, dict):
            target = self._as_list(authored.get("target_hunks") or authored.get("staged_hunks") or authored.get("stage"))
            leftover = self._as_list(authored.get("leftover_hunks") or authored.get("remaining_hunks") or authored.get("leftover"))
            return target, leftover
        hunks = self._as_list(authored)
        return hunks[:1], hunks[1:]
    def _as_list(self, value: Any) -> list[Any]:
        if value is None or value == "":
            return []
        return list(value) if isinstance(value, list) else [value]
    def _entry_tokens(self, value: Any) -> list[str]:
        if value is None:
            return []
        if isinstance(value, dict):
            for key in ("hunks", "tokens", "target_hunks", "leftover_hunks"):
                if key in value:
                    return [str(item) for item in self._as_list(value.get(key))]
        haystack = self.normalizer.token_haystack(value)
        return [haystack] if haystack else []
    def _selected_add_paths(self, state: dict, args: list[str], *, include_tracked: bool = True, include_untracked: bool = True) -> list[str]:
        working_tree = state.get("working_tree") or {}
        base_tree = self.normalizer.head_tree(state)
        requested = [arg for arg in args if arg != "--"] or sorted(working_tree)
        if "." in requested:
            requested = sorted(working_tree)
        selected: list[str] = []
        for requested_path in requested:
            matches = self._matching_paths(working_tree, requested_path)
            for path in matches:
                value = working_tree.get(path)
                status = self.normalizer.entry_status(value)
                if status == "ignored":
                    continue
                tracked = path in base_tree or status in {"modified", "deleted", "removed"}
                untracked = not tracked or status == "untracked"
                if (tracked and include_tracked) or (untracked and include_untracked):
                    selected.append(path)
        return sorted(set(selected))
    def _matching_paths(self, working_tree: dict, requested_path: str) -> list[str]:
        if requested_path.endswith("/"):
            return sorted(path for path in working_tree if path.startswith(requested_path))
        if requested_path in working_tree:
            return [requested_path]
        prefix = f"{requested_path.rstrip('/')}/"
        return sorted(path for path in working_tree if path.startswith(prefix))
    def _expand_pathspecs(self, base_tree: dict, paths: list[str]) -> list[str]:
        expanded: list[str] = []
        for spec in paths:
            if spec.endswith("/"):
                expanded.extend(path for path in base_tree if path.startswith(spec))
                continue
            prefix = f"{spec.rstrip('/')}/"
            matches = [path for path in base_tree if path.startswith(prefix)]
            expanded.extend(matches or [spec])
        return sorted(set(expanded))
    def _pathspecs(self, parts: list[str], *, value_options: set[str] | None = None) -> list[str]:
        value_options = value_options or set()
        paths: list[str] = []
        positional_only = False
        index = 2
        while index < len(parts):
            part = parts[index]
            if not positional_only and part == "--":
                positional_only = True
                index += 1
                continue
            if not positional_only:
                option_name = part.split("=", 1)[0] if part.startswith("--") and "=" in part else part
                if option_name in value_options:
                    index += 1 if "=" in part else 2
                    continue
                if part.startswith("-"):
                    index += 1
                    continue
            paths.append(part)
            index += 1
        return paths
