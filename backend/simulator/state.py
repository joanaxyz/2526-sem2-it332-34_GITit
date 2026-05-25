import copy

DELETE_MARKERS = {"deleted", "removed", "delete", "remove"}


class RepositoryStateNormalizer:
    """Normalize authored repository JSON into the canonical teaching shape.

    Audit note, May 2026:
    - ``repository_state`` already stores commits, branches, HEAD, staging,
      working tree, conflicts, remotes, stash, reflog, and partial hunks.
    - Older commits use ``files`` as an ambiguous "paths changed by this
      commit" map; they usually do not include committed tree contents.
    - Legacy target rules can check broad facts such as current branch, clean
      worktree, staged paths, remotes, and latest commit files/message.
    - Expected-state diagrams are stored separately but are currently just
      shallow snapshots of commits/branches/HEAD for the frontend.
    - The live DAG renders only commit circles, local branch refs, and HEAD, so
      it cannot explain staged files, worktree files, remotes, stash, conflicts,
      or the exact commit details that made a target match.

    This normalizer is the compatibility boundary: old seeded data keeps
    working, while simulator and evaluator code can rely on ``tree`` and
    ``changes`` when they are present or can be inferred.
    """

    TOP_LEVEL_DEFAULTS = {
        "repository_initialized": True,
        "commits": list,
        "branches": dict,
        "head": lambda: {"type": "branch", "name": "main"},
        "staging": dict,
        "working_tree": dict,
        "conflicts": list,
        "remotes": dict,
        "remote_branches": dict,
        "upstream_tracking": dict,
        "stash_stack": list,
        "reflog": list,
        "partial_hunks": dict,
        "replaced_commits": dict,
        "operation_metadata": dict,
    }

    def normalize(self, state: dict | None) -> dict:
        normalized = copy.deepcopy(state or {})
        self.ensure_shape(normalized)
        self.normalize_commits(normalized)
        self.normalize_head(normalized)
        return normalized

    def ensure_shape(self, state: dict) -> dict:
        for key, default in self.TOP_LEVEL_DEFAULTS.items():
            if key in state:
                continue
            state[key] = default() if callable(default) else copy.deepcopy(default)
        if not isinstance(state.get("head"), dict):
            state["head"] = {"type": "branch", "name": "main"}
        return state

    def normalize_head(self, state: dict) -> None:
        head = state.setdefault("head", {"type": "branch", "name": "main"})
        if head.get("type") == "branch":
            head["target"] = state.get("branches", {}).get(head.get("name"))

    def normalize_commits(self, state: dict) -> None:
        commits = state.setdefault("commits", [])
        commits_by_id: dict[str, dict] = {}

        for index, commit in enumerate(commits):
            commit.setdefault("id", f"c{index}")
            commit.setdefault("message", commit["id"])
            commit.setdefault("parents", [])

            parent_tree = self.parent_tree(commit, commits_by_id)
            tree_was_authored = isinstance(commit.get("tree"), dict)
            tree = (
                copy.deepcopy(commit.get("tree"))
                if tree_was_authored
                else copy.deepcopy(parent_tree)
            )

            if tree_was_authored:
                inferred_changes = self.diff_trees(parent_tree, tree)
                authored_changes = self.normalize_changes(commit.get("changes"))
                commit["changes"] = authored_changes or inferred_changes
            elif commit.get("changes"):
                changes = self.normalize_changes(commit.get("changes"))
                tree = self.apply_changes(parent_tree, changes)
                commit["changes"] = changes
            else:
                legacy_files = copy.deepcopy(commit.get("files") or {})
                changes = self.changes_from_entries(parent_tree, legacy_files)
                tree = self.apply_changes(parent_tree, changes)
                commit["changes"] = changes

            commit["tree"] = tree
            commit["is_merge"] = len(commit.get("parents", [])) > 1
            if "files" not in commit:
                commit["files"] = self.files_from_changes(commit.get("changes", {}))
            commits_by_id[commit["id"]] = commit

    def parent_tree(self, commit: dict, commits_by_id: dict[str, dict]) -> dict[str, object]:
        parents = commit.get("parents") or []
        if not parents:
            return {}
        parent = commits_by_id.get(parents[0])
        return copy.deepcopy((parent or {}).get("tree") or {})

    def normalize_changes(self, changes: dict | None) -> dict:
        normalized: dict[str, dict] = {}
        for path, payload in (changes or {}).items():
            if isinstance(payload, dict):
                before = payload.get("before")
                after = payload.get("after")
                change_type = payload.get("change_type") or self.change_type(before, after)
            else:
                before = None
                after = None if self.is_delete_marker(payload) else payload
                change_type = str(payload or self.change_type(before, after))
            normalized[path] = {
                "change_type": change_type,
                "before": before,
                "after": after,
            }
        return normalized

    def changes_from_entries(self, base_tree: dict, entries: dict) -> dict:
        changes: dict[str, dict] = {}
        for path, marker in (entries or {}).items():
            before = base_tree.get(path)
            after = (
                None
                if self.is_delete_marker(marker) or self.is_delete_marker(self.entry_status(marker))
                else self.entry_content(marker)
            )
            changes[path] = {
                "change_type": self.change_type(before, after, marker),
                "before": before,
                "after": after,
            }
        return changes

    def diff_trees(self, before: dict, after: dict) -> dict:
        changes: dict[str, dict] = {}
        for path in sorted(set(before) | set(after)):
            old_value = before.get(path)
            new_value = after.get(path)
            if old_value == new_value:
                continue
            changes[path] = {
                "change_type": self.change_type(old_value, new_value),
                "before": old_value,
                "after": new_value,
            }
        return changes

    def apply_changes(self, base_tree: dict, changes: dict) -> dict:
        tree = copy.deepcopy(base_tree)
        for path, payload in (changes or {}).items():
            if self.is_delete_marker(payload.get("change_type")) or payload.get("after") is None:
                tree.pop(path, None)
            else:
                tree[path] = payload.get("after")
        return tree

    def files_from_changes(self, changes: dict) -> dict:
        files: dict[str, object] = {}
        for path, payload in (changes or {}).items():
            files[path] = payload.get("change_type") or "modified"
        return files

    def change_type(
        self,
        before: object | None,
        after: object | None,
        marker: object | None = None,
    ) -> str:
        if self.is_delete_marker(marker) or after is None:
            return "deleted"
        if before is None:
            return "added"
        return "modified"

    def is_delete_marker(self, value: object | None) -> bool:
        return str(value or "").lower() in DELETE_MARKERS

    def entry_status(self, value: object | None) -> str:
        if isinstance(value, dict):
            status = value.get("status") or value.get("state") or value.get("change_type")
            if status is not None:
                return str(status).lower()
            if value.get("ignored") is True:
                return "ignored"
            if value.get("untracked") is True:
                return "untracked"
        return str(value or "").lower()

    def entry_content(self, value: object | None) -> object:
        if isinstance(value, dict):
            if "content" in value:
                return copy.deepcopy(value.get("content"))
            if "after" in value:
                return copy.deepcopy(value.get("after"))
            if "value" in value:
                return copy.deepcopy(value.get("value"))
        return copy.deepcopy(value)

    def token_haystack(self, value: object | None) -> str:
        if value is None:
            return ""
        if isinstance(value, dict):
            return " ".join(self.token_haystack(item) for item in value.values())
        if isinstance(value, (list, tuple, set)):
            return " ".join(self.token_haystack(item) for item in value)
        return str(value)

    def contains_tokens(self, value: object | None, tokens: list[str]) -> bool:
        haystack = self.token_haystack(value).lower()
        return all(str(token).lower() in haystack for token in tokens)

    def head_commit_id(self, state: dict) -> str | None:
        head = state.get("head", {})
        if head.get("type") == "branch":
            return state.get("branches", {}).get(head.get("name"))
        return head.get("target")

    def commit_by_id(self, state: dict, commit_id: str | None) -> dict | None:
        if not commit_id:
            return None
        return next(
            (commit for commit in state.get("commits", []) if commit.get("id") == commit_id), None
        )

    def head_tree(self, state: dict) -> dict:
        commit = self.commit_by_id(state, self.head_commit_id(state))
        return copy.deepcopy((commit or {}).get("tree") or {})

    def visible_project_tree(self, state: dict) -> dict[str, dict]:
        """Derive the user-visible file set from HEAD, index, and worktree.

        ``working_tree`` in authored scenarios intentionally stores only local
        changes, not every committed file. The Project Structure panel needs the
        merged view students would see in a checkout, so this helper starts with
        the HEAD tree and overlays staged and working-tree entries.
        """

        normalized = self.normalize(state)
        visible: dict[str, dict] = {
            path: {"status": "clean", "source": "head", "content": copy.deepcopy(content)}
            for path, content in self.head_tree(normalized).items()
        }

        for path, value in (normalized.get("staging") or {}).items():
            status = self.entry_status(value) or "modified"
            if self.is_delete_marker(status) or self.is_delete_marker(value):
                visible[path] = {"status": "deleted", "source": "staging", "content": None}
                continue
            visible[path] = {
                "status": self.display_status(value, fallback="modified"),
                "source": "staging",
                "content": self.entry_content(value),
            }

        for path, value in (normalized.get("working_tree") or {}).items():
            status = self.entry_status(value) or "modified"
            if self.is_delete_marker(status) or self.is_delete_marker(value):
                visible[path] = {"status": "deleted", "source": "working_tree", "content": None}
                continue
            visible[path] = {
                "status": self.display_status(value, fallback="modified"),
                "source": "working_tree",
                "content": self.entry_content(value),
            }

        return dict(sorted(visible.items()))

    def display_status(self, value: object | None, *, fallback: str = "changed") -> str:
        status = self.entry_status(value)
        if status in {"", "none"}:
            return fallback
        if status in {"new", "added"}:
            return "added"
        if status in {"remove", "removed"}:
            return "deleted"
        return status
