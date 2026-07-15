from __future__ import annotations

SUPPORTED_RULE_TYPES = frozenset({
    'branch_history_contains',
    'branch_history_excludes',
    'commit_changes_exclude',
    'commit_changes_exclude_tokens',
    'commit_changes_include',
    'commit_changes_include_tokens',
    'commit_count_equals',
    'commit_count_on_branch_equals',
    'commit_exists',
    'commit_has_parent',
    'commit_is_merge',
    'commit_is_not_merge',
    'commit_message_contains',
    'commit_parent_count_equals',
    'commit_parent_equals',
    'commit_tree_contains',
    'commit_tree_contains_tokens',
    'commit_tree_excludes',
    'commit_tree_excludes_tokens',
    'latest_commit_message_contains',
    'latest_commit_message_equals',
})

def check_commit_state_rule(
    self,
    state: dict,
    rule: dict,
    *,
    initial_state: dict | None,
    executed_commands: list[str],
) -> tuple[bool, str] | None:
    rule_type = rule.get("type")
    if rule_type == "commit_exists":
        commit_id = self._resolve_expected(
            rule.get("commit") or rule.get("id"), state, initial_state
        )
        passed = self._commit_by_id(state, commit_id) is not None
        return passed, f"Commit {commit_id!r} {'exists' if passed else 'does not exist'}."
    if rule_type in {"latest_commit_message_equals", "latest_commit_message_contains"}:
        commit = self._latest_commit_for_rule(state, rule)
        expected = rule.get("message") or rule.get("text")
        if not commit:
            return False, "Latest commit was not found."
        message = commit.get("message", "")
        passed = (
            message == expected
            if rule_type.endswith("equals")
            else str(expected).lower() in message.lower()
        )
        return passed, f"Latest commit message was {message!r}."
    if rule_type in {
        "commit_message_contains",
        "commit_changes_include",
        "commit_changes_exclude",
        "commit_changes_include_tokens",
        "commit_changes_exclude_tokens",
        "commit_tree_contains",
        "commit_tree_excludes",
        "commit_tree_contains_tokens",
        "commit_tree_excludes_tokens",
        "commit_has_parent",
        "commit_parent_equals",
        "commit_parent_count_equals",
        "commit_is_merge",
        "commit_is_not_merge",
    }:
        commit = self._commit_for_rule(
            state, rule, initial_state=initial_state
        ) or self._latest_commit_for_rule(state, rule)
        if not commit:
            return False, "Commit was not found."
        return self._check_commit_rule(
            rule_type, commit, rule, state=state, initial_state=initial_state
        )
    if rule_type == "branch_history_contains":
        branch = rule.get("branch")
        expected = self._expected_commits(rule, state, initial_state)
        history = self._branch_history(state, branch)
        missing = [commit_id for commit_id in expected if commit_id not in history]
        return (
            not missing,
            "Branch history contains expected commits."
            if not missing
            else f"Missing commits in history: {missing}.",
        )
    if rule_type == "branch_history_excludes":
        branch = rule.get("branch")
        excluded = self._expected_commits(rule, state, initial_state)
        history = self._branch_history(state, branch)
        present = [commit_id for commit_id in excluded if commit_id in history]
        return (
            not present,
            "Branch history excludes forbidden commits."
            if not present
            else f"Unexpected commits in history: {present}.",
        )

    if rule_type == "commit_count_equals":
        expected = int(rule.get("count", 0))
        actual = len(state.get("commits", []))
        return actual == expected, f"Repository has {actual} commits, expected {expected}."
    if rule_type == "commit_count_on_branch_equals":
        branch = rule.get("branch") or self._head_branch(state)
        expected = int(rule.get("count", 0))
        actual = self._commit_depth(state, self._ref_target(state, branch))
        return (
            actual == expected,
            f"Branch {branch!r} has {actual} commits, expected {expected}.",
        )

    return None
