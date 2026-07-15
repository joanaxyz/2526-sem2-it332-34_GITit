"""Cheap backend-side verification for client-submitted Git transitions.

The browser simulator still owns instant UI feedback. This verifier mirrors the
supported mutating command transitions that can affect persisted progress/rewards
without shelling out to Git, so a forged client next_state cannot silently earn
completion.
"""

from __future__ import annotations

import copy

from common.exceptions import BadRequest
from simulator.services import parse_git_command


class RefVerificationMixin:
    def _verify_branch(self, *, command: str, previous_state: dict, next_state: dict) -> None:
        for key in self.REF_ONLY_IMMUTABLE_KEYS:
            self._require_same_key(key, previous_state, next_state)
        parts = parse_git_command(command) or []
        args = self._pathspecs(parts)
        # Plain `git branch` is diagnostic and should not reach this mutating verifier.
        if not args:
            return
        expected_branches = copy.deepcopy(previous_state.get("branches") or {})
        expected_head = copy.deepcopy(previous_state.get("head") or {})
        expected_upstream = copy.deepcopy(previous_state.get("upstream_tracking") or {})
        if "-m" in parts or "--move" in parts:
            old_name = args[0] if len(args) > 1 else self._head_branch(previous_state)
            new_name = args[1] if len(args) > 1 else args[0]
            if not old_name or not new_name or old_name not in expected_branches or new_name in expected_branches:
                raise BadRequest("execution.next_state does not match the submitted git branch command.")
            expected_branches[new_name] = expected_branches.pop(old_name)
            if expected_head.get("type") == "branch" and expected_head.get("name") == old_name:
                expected_head = {"type": "branch", "name": new_name, "target": expected_branches.get(new_name)}
            if old_name in expected_upstream:
                expected_upstream[new_name] = expected_upstream.pop(old_name)
            if next_state.get("branches") != expected_branches or next_state.get("head") != expected_head or next_state.get("upstream_tracking") != expected_upstream:
                raise BadRequest("execution.next_state does not match the submitted git branch command.")
            return
        if "-d" in parts or "-D" in parts or "--delete" in parts:
            name = args[0]
            target = expected_branches.get(name)
            if name not in expected_branches or self._head_branch(previous_state) == name:
                raise BadRequest("execution.next_state does not match the submitted git branch command.")
            if "-D" not in parts and not self._is_ancestor(previous_state, target, self.normalizer.head_commit_id(previous_state)):
                raise BadRequest("execution.next_state does not match the submitted git branch command.")
            expected_branches.pop(name, None)
            if next_state.get("branches") != expected_branches:
                raise BadRequest("execution.next_state does not match the submitted git branch command.")
            return
        name = args[0]
        start = args[1] if len(args) > 1 else None
        target = self._resolve_ref(previous_state, start) if start else self.normalizer.head_commit_id(previous_state)
        if name in expected_branches or (start and not target):
            raise BadRequest("execution.next_state does not match the submitted git branch command.")
        expected_branches[name] = target
        if next_state.get("branches") != expected_branches:
            raise BadRequest("execution.next_state does not match the submitted git branch command.")
        if next_state.get("head") != previous_state.get("head"):
            raise BadRequest("git branch must not move HEAD unless renaming the current branch.")
    def _verify_switch(self, *, command: str, previous_state: dict, next_state: dict) -> None:
        for key in self.REF_ONLY_IMMUTABLE_KEYS:
            self._require_same_key(key, previous_state, next_state)
        parts = parse_git_command(command) or []
        args = self._pathspecs(parts)
        if "--detach" in parts:
            target = self._resolve_ref(previous_state, args[0] if args else "HEAD")
            if not target:
                raise BadRequest("execution.next_state does not match the submitted git switch command.")
            if next_state.get("head") != {"type": "detached", "target": target}:
                raise BadRequest("execution.next_state does not match the submitted git switch command.")
            self._require_same_key("branches", previous_state, next_state)
            return
        create = "-c" in parts or "--create" in parts
        if create:
            name = args[0] if args else ""
            start = args[1] if len(args) > 1 else None
            target = self._resolve_ref(previous_state, start) if start else self.normalizer.head_commit_id(previous_state)
            if start and not target:
                raise BadRequest("execution.next_state does not match the submitted git switch command.")
            expected_branches = copy.deepcopy(previous_state.get("branches") or {})
            expected_branches[name] = target
            if next_state.get("branches") != expected_branches:
                raise BadRequest("execution.next_state does not match the submitted git switch command.")
            if next_state.get("head") != {"type": "branch", "name": name, "target": target}:
                raise BadRequest("execution.next_state does not match the submitted git switch command.")
            return
        name = args[0] if args else ""
        expected_branches = copy.deepcopy(previous_state.get("branches") or {})
        expected_upstream = copy.deepcopy(previous_state.get("upstream_tracking") or {})
        if name not in expected_branches:
            remote_key = f"origin/{name}"
            if remote_key not in (previous_state.get("remote_branches") or {}):
                raise BadRequest("execution.next_state does not match the submitted git switch command.")
            expected_branches[name] = (previous_state.get("remote_branches") or {}).get(remote_key)
            expected_upstream[name] = remote_key
        target = expected_branches.get(name)
        if next_state.get("branches") != expected_branches:
            raise BadRequest("execution.next_state does not match the submitted git switch command.")
        if next_state.get("upstream_tracking") != expected_upstream:
            raise BadRequest("execution.next_state does not match the submitted git switch command.")
        if next_state.get("head") != {"type": "branch", "name": name, "target": target}:
            raise BadRequest("execution.next_state does not match the submitted git switch command.")
    def _verify_checkout(self, *, command: str, previous_state: dict, next_state: dict) -> None:
        parts = parse_git_command(command) or []
        if "-b" in parts:
            for key in self.REF_ONLY_IMMUTABLE_KEYS:
                self._require_same_key(key, previous_state, next_state)
            args = self._pathspecs(parts)
            name = args[0] if args else ""
            start = args[1] if len(args) > 1 else None
            target = self._resolve_ref(previous_state, start) if start else self.normalizer.head_commit_id(previous_state)
            if start and not target:
                raise BadRequest("execution.next_state does not match the submitted git checkout command.")
            expected_branches = copy.deepcopy(previous_state.get("branches") or {})
            expected_branches[name] = target
            if next_state.get("branches") != expected_branches:
                raise BadRequest("execution.next_state does not match the submitted git checkout command.")
            if next_state.get("head") != {"type": "branch", "name": name, "target": target}:
                raise BadRequest("execution.next_state does not match the submitted git checkout command.")
            return

        for key in self.INDEX_WORKTREE_IMMUTABLE_KEYS:
            self._require_same_key(key, previous_state, next_state)
        side = "ours" if "--ours" in parts else "theirs"
        paths = self._pathspecs(parts)
        conflicts = set(previous_state.get("conflicts") or [])
        if not conflicts:
            raise BadRequest("execution.next_state does not match the submitted git checkout command.")
        expected_working = copy.deepcopy(previous_state.get("working_tree") or {})
        for path in paths:
            if path not in conflicts:
                raise BadRequest("execution.next_state does not match the submitted git checkout command.")
            detail = (previous_state.get("conflict_details") or {}).get(path) or {}
            expected_working[path] = {
                "status": "modified",
                "content": copy.deepcopy(detail.get(side)),
                "resolution_side": side,
            }
        if next_state.get("working_tree") != expected_working:
            raise BadRequest("execution.next_state does not match the submitted git checkout command.")
        self._require_same_key("staging", previous_state, next_state)
        self._require_same_key("conflicts", previous_state, next_state)
        self._require_same_key("conflict_details", previous_state, next_state)
    def _verify_tag(self, *, command: str, previous_state: dict, next_state: dict) -> None:
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
            "remote_tags",
            "stash_stack",
            "reflog",
            "replaced_commits",
            "config",
        }:
            self._require_same_key(key, previous_state, next_state)
        parts = parse_git_command(command) or []
        args = self._pathspecs(parts, value_options={"-m", "--message"})
        expected = copy.deepcopy(previous_state.get("tags") or {})
        if "-d" in parts or "--delete" in parts:
            for name in args:
                expected.pop(name, None)
        elif not args:
            self._require_same_state(previous_state, next_state, "git tag without arguments cannot mutate repository state.")
            return
        else:
            name = args[0]
            target_ref = args[1] if len(args) > 1 else "HEAD"
            target = self._resolve_revision(previous_state, target_ref)
            if not target:
                raise BadRequest("execution.next_state does not match the submitted git tag command.")
            message = self._commit_message(parts) or ""
            expected[name] = {
                "target": target,
                "annotated": "-a" in parts or "--annotate" in parts or bool(message),
                "message": message,
            }
        if next_state.get("tags") != expected:
            raise BadRequest("execution.next_state does not match the submitted git tag command.")
    def _verify_config(self, *, command: str, previous_state: dict, next_state: dict) -> None:
        parts = parse_git_command(command) or []
        if "--list" in parts or "-l" in parts:
            self._require_same_state(previous_state, next_state, "git config --list cannot mutate repository state.")
            return
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
        }:
            self._require_same_key(key, previous_state, next_state)
        args = self._pathspecs(parts)
        if len(args) < 2:
            raise BadRequest("execution.next_state does not match the submitted git config command.")
        expected = copy.deepcopy(previous_state.get("config") or {})
        expected[args[0]] = args[1]
        if next_state.get("config") != expected:
            raise BadRequest("execution.next_state does not match the submitted git config command.")
    def _resolve_revision(self, state: dict, revision: str | None) -> str | None:
        if not revision or revision == "HEAD":
            return self.normalizer.head_commit_id(state)
        if revision.startswith("HEAD~"):
            try:
                depth = int(revision[5:])
            except ValueError:
                return None
            current = self.normalizer.head_commit_id(state)
            for _ in range(depth):
                commit = self.normalizer.commit_by_id(state, current)
                current = (commit or {}).get("parents", [None])[0] if commit else None
                if not current:
                    return None
            return current
        if revision.startswith("HEAD@{") and revision.endswith("}"):
            try:
                index = int(revision[6:-1])
            except ValueError:
                return None
            entry = (state.get("reflog") or [None])[index] if index < len(state.get("reflog") or []) else None
            target = entry.get("target") if isinstance(entry, dict) else None
            return target if isinstance(target, str) else None
        return self._resolve_ref(state, revision)
    def _resolve_ref(self, state: dict, ref: str | None) -> str | None:
        if not ref or ref == "HEAD":
            return self.normalizer.head_commit_id(state)
        if ref in (state.get("branches") or {}):
            return (state.get("branches") or {}).get(ref)
        if ref in (state.get("remote_branches") or {}):
            return (state.get("remote_branches") or {}).get(ref)
        tag = (state.get("tags") or {}).get(ref)
        if isinstance(tag, dict):
            return str(tag.get("target") or "") or None
        if tag:
            return str(tag)
        if self.normalizer.commit_by_id(state, ref):
            return ref
        return None
    def _tree_for_commit(self, state: dict, commit_id: str | None) -> dict:
        commit = self.normalizer.commit_by_id(state, commit_id)
        return copy.deepcopy((commit or {}).get("tree") or {})
    def _set_head_commit(self, state: dict, commit_id: str | None) -> None:
        head = state.get("head") or {}
        if head.get("type") == "branch":
            branch = head.get("name")
            if branch:
                state.setdefault("branches", {})[branch] = commit_id
        else:
            head["target"] = commit_id
        self.normalizer.normalize_head(state)
        if commit_id:
            state.setdefault("reflog", []).append(
                {"ref": f"HEAD@{{{len(state.get('reflog', []))}}}", "target": commit_id, "message": "move HEAD"}
            )
    def _head_branch(self, state: dict) -> str | None:
        head = state.get("head") or {}
        return head.get("name") if head.get("type") == "branch" else None
