from __future__ import annotations

SUPPORTED_RULE_TYPES = frozenset({
    'conflict_free',
    'conflict_resolution_contains',
    'conflicts_contain_paths',
    'conflicts_empty',
    'conflicts_resolved',
    'index_empty',
    'staging_contains',
    'staging_contains_tokens',
    'staging_empty',
    'staging_excludes',
    'staging_excludes_tokens',
    'staging_matches_exact_paths',
    'staging_not_empty',
    'working_tree_absent',
    'working_tree_clean',
    'working_tree_clean_except',
    'working_tree_contains',
    'working_tree_contains_tokens',
    'working_tree_dirty',
    'working_tree_excludes_tokens',
    'working_tree_matches_exact_paths',
})

def check_workspace_state_rule(
    self,
    state: dict,
    rule: dict,
    *,
    initial_state: dict | None,
    executed_commands: list[str],
) -> tuple[bool, str] | None:
    rule_type = rule.get("type")
    if rule_type in {"index_empty", "staging_empty"}:
        passed = not state.get("staging")
        return (
            passed,
            "Index is empty."
            if passed
            else f"Index still has {sorted(state.get('staging', {}))}.",
        )
    if rule_type == "staging_not_empty":
        passed = bool(state.get("staging"))
        return passed, "Something is staged." if passed else "Nothing is staged."
    if rule_type == "staging_contains":
        paths = set(self._as_list(rule.get("path") or rule.get("paths")))
        missing = sorted(paths - set(state.get("staging", {})))
        return (
            not missing,
            "Staging contains expected paths."
            if not missing
            else f"Staging is missing {missing}.",
        )
    if rule_type == "staging_excludes":
        paths = set(self._as_list(rule.get("path") or rule.get("paths")))
        present = sorted(paths & set(state.get("staging", {})))
        return (
            not present,
            "Staging excludes expected paths."
            if not present
            else f"Staging still contains {present}.",
        )
    if rule_type == "staging_matches_exact_paths":
        expected = sorted(rule.get("paths", []))
        actual = sorted(state.get("staging", {}))
        return actual == expected, f"Staged paths were {actual}, expected {expected}."
    if rule_type == "staging_contains_tokens":
        return self._token_rule_for_entries(
            state.get("staging", {}), rule, should_contain=True, label="Staging"
        )
    if rule_type == "staging_excludes_tokens":
        return self._token_rule_for_entries(
            state.get("staging", {}), rule, should_contain=False, label="Staging"
        )

    if rule_type == "working_tree_clean":
        visible_working = {
            path: value
            for path, value in state.get("working_tree", {}).items()
            if self.normalizer.entry_status(value) != "ignored"
        }
        passed = not visible_working and not state.get("conflicts")
        return (
            passed,
            "Working tree is clean."
            if passed
            else "Working tree still has changes or conflicts.",
        )
    if rule_type == "working_tree_dirty":
        visible_working = {
            path: value
            for path, value in state.get("working_tree", {}).items()
            if self.normalizer.entry_status(value) != "ignored"
        }
        passed = bool(visible_working) or bool(state.get("conflicts"))
        return (
            passed,
            "Working tree has uncommitted changes."
            if passed
            else "Working tree has no changes.",
        )
    if rule_type == "working_tree_contains":
        paths = set(self._as_list(rule.get("path") or rule.get("paths")))
        missing = sorted(paths - set(state.get("working_tree", {})))
        return (
            not missing,
            "Working tree contains expected paths."
            if not missing
            else f"Working tree is missing {missing}.",
        )
    if rule_type == "working_tree_absent":
        paths = set(self._as_list(rule.get("path") or rule.get("paths")))
        present = sorted(paths & set(state.get("working_tree", {})))
        return (
            not present,
            "Working tree excludes expected paths."
            if not present
            else f"Working tree still contains {present}.",
        )
    if rule_type == "working_tree_matches_exact_paths":
        expected = sorted(rule.get("paths", []))
        actual = sorted(state.get("working_tree", {}))
        return actual == expected, f"Working tree paths were {actual}, expected {expected}."
    if rule_type == "working_tree_contains_tokens":
        return self._token_rule_for_entries(
            state.get("working_tree", {}), rule, should_contain=True, label="Working tree"
        )
    if rule_type == "working_tree_excludes_tokens":
        return self._token_rule_for_entries(
            state.get("working_tree", {}), rule, should_contain=False, label="Working tree"
        )
    if rule_type == "working_tree_clean_except":
        allowed = set(rule.get("paths", []))
        actual = {
            path
            for path, value in state.get("working_tree", {}).items()
            if self.normalizer.entry_status(value) != "ignored"
        }
        extra = sorted(actual - allowed)
        return (
            not extra and not state.get("conflicts"),
            "Working tree only has allowed paths."
            if not extra
            else f"Unexpected working tree paths: {extra}.",
        )

    if rule_type in {"conflict_free", "conflicts_empty", "conflicts_resolved"}:
        passed = not state.get("conflicts")
        return (
            passed,
            "No conflicts remain."
            if passed
            else f"Conflicts remain: {state.get('conflicts')}.",
        )
    if rule_type == "conflicts_contain_paths":
        paths = set(rule.get("paths", []))
        actual = set(state.get("conflicts", []))
        missing = sorted(paths - actual)
        return (
            not missing,
            "Expected conflict paths are present."
            if not missing
            else f"Missing conflict paths: {missing}.",
        )
    if rule_type == "conflict_resolution_contains":
        path = rule.get("path")
        token = str(rule.get("token", ""))
        value = str(
            state.get("staging", {}).get(path) or state.get("working_tree", {}).get(path) or ""
        )
        passed = token in value
        return (
            passed,
            f"Conflict resolution for {path!r} {'contains' if passed else 'does not contain'} {token!r}.",
        )

    return None
