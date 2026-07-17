import copy
import hashlib
import json
import shlex

from simulator.state import RepositoryStateNormalizer


def normalize_command(command: str) -> str:
    try:
        parts = shlex.split(command.strip())
    except ValueError:
        return _normalized_fallback(command)
    if not parts or parts[0] != "git":
        return _normalized_fallback(command)
    aliases = {"st": "status", "ci": "commit", "co": "checkout", "br": "branch"}
    if len(parts) > 1:
        parts[1] = aliases.get(parts[1], parts[1])
    return " ".join(
        shlex.quote(part) if any(ch.isspace() for ch in part) else part for part in parts
    )


def _normalized_fallback(command: str) -> str:
    return " ".join(command.strip().split())


def parse_git_command(command: str) -> list[str] | None:
    try:
        parts = shlex.split(command.strip())
    except ValueError:
        return None
    if not parts or parts[0] != "git":
        return None
    return parts


def is_diagnostic_command(command: str) -> bool:
    parts = parse_git_command(command)
    if not parts or len(parts) < 2:
        return False
    subcommand = parts[1]
    if subcommand in {"--help", "--version", "help", "version"}:
        return True
    if subcommand in {
        "status",
        "log",
        "show",
        "diff",
        "reflog",
        "check-ignore",
        "ls-files",
        "merge-base",
        "rev-list",
        "shortlog",
        "rev-parse",
        "blame",
        "grep",
        "describe",
        "range-diff",
        "merge-tree",
        "verify-commit",
        "verify-tag",
        "fsck",
        "count-objects",
        "cat-file",
        "ls-tree",
        "show-ref",
        "for-each-ref",
        "symbolic-ref",
    }:
        return True
    args = parts[2:]
    if subcommand == "bisect":
        return bool(args) and args[0] in {"run", "log"}
    if subcommand == "rerere":
        return bool(args) and args[0] in {"status", "diff"}
    if subcommand == "worktree":
        return args == ["list"]
    if subcommand == "sparse-checkout":
        return args == ["list"]
    if subcommand == "submodule":
        return args == ["status"]
    if subcommand == "config":
        return any(option in args for option in {"--get", "--list", "-l"})
    if subcommand == "branch":
        return len([part for part in args if not part.startswith("-")]) == 0
    if subcommand == "remote":
        return len([part for part in parts[2:] if not part.startswith("-")]) == 0
    if subcommand == "stash":
        return len(parts) > 2 and parts[2] in {"list", "show"}
    if subcommand == "tag" and len(parts) == 2:
        return True
    return False


class RepositoryStateSimulator:
    """Repository-state helper boundary shared by backend evaluators/payloads."""

    def __init__(self) -> None:
        self.normalizer = RepositoryStateNormalizer()

    def clone_state(self, state: dict) -> dict:
        return copy.deepcopy(state)

    def normalize_state(self, state: dict) -> dict:
        return self.normalizer.normalize(state)

    def state_hash(self, state: dict) -> str:
        payload = json.dumps(self.normalize_state(state), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def state_hash_for_normalized(self, state: dict) -> str:
        payload = json.dumps(state, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def _ensure_state_shape(self, state: dict) -> None:
        self.normalizer.ensure_shape(state)
        self.normalizer.normalize_commits(state)
        self.normalizer.normalize_head(state)

    def _head_branch(self, state: dict) -> str | None:
        head = state.get("head", {})
        return head.get("name") if head.get("type") == "branch" else None

    def _head_commit(self, state: dict) -> str | None:
        head = state.get("head", {})
        if head.get("type") == "branch":
            return state.get("branches", {}).get(head.get("name"))
        return head.get("target")

    def _head_tree(self, state: dict) -> dict:
        return self._tree_for_commit(state, self._head_commit(state))

    def _tree_for_commit(self, state: dict, commit_id: str | None) -> dict:
        commit = self._commit_by_id(state, commit_id)
        if not commit:
            return {}
        return copy.deepcopy(commit.get("tree") or {})

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
            "parents": parents,
            "tree": copy.deepcopy(tree),
            "changes": copy.deepcopy(changes),
            "files": self.normalizer.files_from_changes(changes),
            "author": "GIT it",
            "order": len(state.get("commits", [])),
            "is_merge": len(parents) > 1,
        }

    def _changes_from_entries(self, base_tree: dict, entries: dict) -> dict:
        return self.normalizer.changes_from_entries(base_tree, entries)

    def _apply_changes(self, base_tree: dict, changes: dict) -> dict:
        return self.normalizer.apply_changes(base_tree, changes)

    def _diff_trees(self, before: dict, after: dict) -> dict:
        return self.normalizer.diff_trees(before, after)

    def _set_operation_metadata(self, state: dict, **metadata: object) -> None:
        state.setdefault("operation_metadata", {}).update(metadata)
        for key, value in metadata.items():
            state[key] = value

    def _set_head_commit(self, state: dict, commit_id: str | None) -> None:
        branch = self._head_branch(state)
        if branch:
            state.setdefault("branches", {})[branch] = commit_id
        else:
            state.setdefault("head", {})["target"] = commit_id
        self.normalizer.normalize_head(state)
        self._record_reflog(state, commit_id, "move HEAD")

    def _record_reflog(self, state: dict, target: str | None, message: str) -> None:
        if not target:
            return
        state.setdefault("reflog", []).append(
            {
                "ref": f"HEAD@{{{len(state.get('reflog', []))}}}",
                "target": target,
                "message": message,
            }
        )

    def _commit_by_id(self, state: dict, commit_id: str | None) -> dict | None:
        if not commit_id:
            return None
        return next(
            (commit for commit in state.get("commits", []) if commit["id"] == commit_id), None
        )

    def _next_commit_id(self, state: dict) -> str:
        index = 0
        existing = {commit["id"] for commit in state.get("commits", [])}
        while f"c{index}" in existing:
            index += 1
        return f"c{index}"

    def _as_list(self, value: object | None) -> list:
        if value in (None, ""):
            return []
        return value if isinstance(value, list) else [value]

    def _entry_tokens(self, value: object | None) -> list[str]:
        if value is None:
            return []
        if isinstance(value, dict):
            for key in ("hunks", "tokens", "target_hunks", "leftover_hunks"):
                if key in value:
                    return [str(item) for item in self._as_list(value.get(key))]
        return (
            [self.normalizer.token_haystack(value)] if self.normalizer.token_haystack(value) else []
        )

    def _cleanup_partial_hunks_after_commit(self, state: dict, staged_entries: dict) -> None:
        partial_hunks = state.setdefault("partial_hunks", {})
        for path, staged_value in staged_entries.items():
            if self.normalizer.entry_status(staged_value) != "partial":
                continue
            authored = partial_hunks.get(path)
            if not isinstance(authored, dict):
                continue
            leftover = self._as_list(
                authored.get("leftover_hunks")
                or authored.get("remaining_hunks")
                or authored.get("leftover")
            )
            if leftover:
                partial_hunks[path] = {"target_hunks": [], "leftover_hunks": leftover}
            else:
                partial_hunks.pop(path, None)

    def _first_remote_target(self, remote_branches: dict) -> str:
        targets = [target for target in remote_branches.values() if target]
        return sorted(targets)[0] if targets else "r0"

    def _apply_remote_fixture_branches(self, state: dict) -> None:
        fixture = state.get("remote_fixtures") or {}
        if not isinstance(fixture, dict):
            return
        remote_branches = state.setdefault("remote_branches", {})
        branch_targets = {}
        authored_branches = fixture.get("branches")
        if isinstance(authored_branches, dict):
            branch_targets.update(authored_branches)
        for key, value in fixture.items():
            if key in {"commits", "branches", "remote_head", "head", "default_branch"}:
                continue
            if "/" in key and value:
                branch_targets[key] = value
        remote_head = fixture.get("remote_head") or fixture.get("head")
        default_branch = fixture.get("default_branch") or "origin/main"
        if remote_head:
            branch_targets.setdefault(default_branch, remote_head)
        for branch, target in branch_targets.items():
            remote_branches[branch] = target

    def _materialize_remote_commits(self, state: dict) -> None:
        commits = state.setdefault("commits", [])
        existing = {commit["id"] for commit in commits}
        fixture = state.get("remote_fixtures") or {}
        fixture_commits = fixture.get("commits", []) if isinstance(fixture, dict) else []
        for authored_commit in fixture_commits:
            if not isinstance(authored_commit, dict):
                continue
            commit_id = authored_commit.get("id")
            if not commit_id:
                continue
            if commit_id in existing:
                existing_commit = self._commit_by_id(state, commit_id)
                if existing_commit:
                    existing_commit.update(copy.deepcopy(authored_commit))
                continue
            commits.append(copy.deepcopy(authored_commit))
            existing.add(commit_id)
        self.normalizer.normalize_commits(state)
        existing = {commit["id"] for commit in commits}
        remote_ids = sorted(
            {target for target in state.get("remote_branches", {}).values() if target}
        )
        previous = None
        for commit_id in remote_ids:
            if commit_id not in existing:
                commits.append(
                    {
                        "id": commit_id,
                        "message": f"Remote commit {commit_id}",
                        "parents": [previous] if previous else [],
                        "tree": {},
                        "changes": {},
                        "files": {},
                        "is_merge": False,
                    }
                )
                existing.add(commit_id)
            previous = commit_id
        self.normalizer.normalize_commits(state)


class RepositorySnapshotService:
    def _canonical_copy(self, state: dict, *, already_normalized: bool) -> dict:
        normalizer = RepositoryStateNormalizer()
        payload = copy.deepcopy(state) if already_normalized else normalizer.normalize(state)
        payload.pop("project_tree", None)
        payload.pop("visible_tree", None)
        return payload

    def snapshot_for_command(self, state: dict, *, already_normalized: bool = False) -> dict:
        """Return the canonical command state without derived display trees."""
        return self._canonical_copy(state, already_normalized=already_normalized)

    def snapshot(self, state: dict, *, already_normalized: bool = False) -> dict:
        normalizer = RepositoryStateNormalizer()
        state = self._canonical_copy(state, already_normalized=already_normalized)
        visible_tree = normalizer.visible_project_tree(state, assume_normalized=True)
        state["project_tree"] = visible_tree
        state["visible_tree"] = copy.deepcopy(visible_tree)
        return state
