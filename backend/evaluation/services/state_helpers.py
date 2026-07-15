import copy
from typing import Any


class StateHelperMixin:
    def _commit_depth(self, state: dict, commit_id: str | None) -> int:
        return len(self._branch_history_from_commit(state, commit_id))

    def _branch_history(self, state: dict, branch: str | None) -> list[str]:
        return self._branch_history_from_commit(state, self._ref_target(state, branch))

    def _branch_history_from_commit(self, state: dict, commit_id: str | None) -> list[str]:
        if not commit_id:
            return []
        commits = {commit["id"]: commit for commit in state.get("commits", [])}
        seen: list[str] = []
        stack = [commit_id]
        while stack:
            current = stack.pop()
            if current in seen or current not in commits:
                continue
            seen.append(current)
            stack.extend(commits[current].get("parents", []))
        return seen

    def _latest_commit_for_rule(self, state: dict, rule: dict) -> dict | None:
        ref = rule.get("branch") or rule.get("ref")
        commit_id = self._ref_target(state, ref) if ref else self._head_commit(state)
        return self._commit_by_id(state, commit_id)

    def _commit_for_rule(
        self,
        state: dict,
        rule: dict,
        *,
        initial_state: dict | None = None,
    ) -> dict | None:
        commit_id = self._resolve_expected(
            rule.get("commit") or rule.get("id") or rule.get("ref"),
            state,
            initial_state,
        )
        if commit_id is None and rule.get("branch"):
            commit_id = self._ref_target(state, rule.get("branch"))
        return self._commit_by_id(state, commit_id)

    def _expected_commits(
        self,
        rule: dict,
        state: dict,
        initial_state: dict | None,
    ) -> list[str]:
        values = rule.get("commits")
        if values is None:
            values = [rule.get("commit")]
        return [
            resolved
            for resolved in (
                self._resolve_expected(value, state, initial_state) for value in values
            )
            if resolved
        ]

    def _head_branch(self, state: dict) -> str | None:
        head = state.get("head", {})
        return head.get("name") if head.get("type") == "branch" else None

    def _head_commit(self, state: dict) -> str | None:
        head = state.get("head", {})
        if head.get("type") == "branch":
            return state.get("branches", {}).get(head.get("name"))
        return head.get("target")

    def _commit_by_id(self, state: dict, commit_id: str | None) -> dict | None:
        if not commit_id:
            return None
        return next(
            (commit for commit in state.get("commits", []) if commit["id"] == commit_id), None
        )

    def _ref_target(self, state: dict, ref: str | None) -> str | None:
        if not ref:
            return None
        if ref in state.get("branches", {}):
            return state["branches"][ref]
        if ref in state.get("remote_branches", {}):
            return state["remote_branches"][ref]
        return ref

    def _changed_paths(self, commit: dict) -> list[str]:
        return sorted((commit.get("changes") or commit.get("files") or {}).keys())

    def _reflog_contains(self, state: dict, expected: dict | str | None) -> bool:
        entries = state.get("reflog", [])
        if isinstance(expected, str):
            return any(
                expected in str(entry.get("target", ""))
                or expected in str(entry.get("message", ""))
                for entry in entries
            )
        if isinstance(expected, dict):
            return any(
                all(str(entry.get(key)) == str(value) for key, value in expected.items())
                for entry in entries
            )
        return False

    def _states_equal(self, left: dict, right: dict, *, exclude: set[str] | None = None) -> bool:
        exclude = exclude or set()
        left_copy = copy.deepcopy(left)
        right_copy = copy.deepcopy(right)
        for key in exclude:
            left_copy.pop(key, None)
            right_copy.pop(key, None)
        return left_copy == right_copy

    def _stash_paths(self, state: dict, *, top_only: bool = False) -> set[str]:
        stack = state.get("stash_stack", [])
        entries = stack[-1:] if top_only and stack else stack
        paths: set[str] = set()
        for entry in entries:
            paths.update(entry.get("working_tree", {}))
            paths.update(entry.get("staging", {}))
            paths.update(entry.get("conflicts", []))
        return paths

    def _operation_value(self, state: dict, key: str) -> Any:
        return state.get("operation_metadata", {}).get(key, state.get(key))

    def _resolve_expected(
        self,
        value: Any,
        state: dict,
        initial_state: dict | None,
    ) -> Any:
        if isinstance(value, list):
            return [self._resolve_expected(item, state, initial_state) for item in value]
        if isinstance(value, dict):
            return {
                key: self._resolve_expected(item, state, initial_state)
                for key, item in value.items()
            }
        if not isinstance(value, str) or not value.startswith("$"):
            return value
        if value == "$initial.head_commit":
            return self._head_commit(initial_state or {})
        if value == "$initial.head_branch":
            return self._head_branch(initial_state or {})
        if value.startswith("$initial.branches.") and initial_state is not None:
            branch = value.removeprefix("$initial.branches.")
            return initial_state.get("branches", {}).get(branch)
        if value == "$head_commit":
            return self._head_commit(state)
        return value

    def _as_list(self, value: Any) -> list:
        if value in (None, ""):
            return []
        return value if isinstance(value, list) else [value]
