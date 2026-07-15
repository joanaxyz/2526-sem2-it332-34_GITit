from __future__ import annotations

from simulator.ignore import matching_gitignore_rule

SUPPORTED_RULE_TYPES = frozenset({
    'branch_tip_replaces_commit',
    'commit_not_followed_by_extra_commit',
    'commit_replaced_by_amend',
    'gitignore_matches_paths',
    'ignored_paths_excluded_from_commit',
    'ignored_paths_present',
    'min_commits_on_branch',
    'partial_hunks_committed',
    'partial_hunks_left_in_working_tree',
    'repository_state_unchanged',
    'repository_state_unchanged_except',
    'tracked_path_removed_from_commit_tree',
})

def check_commit_tree_state_rule(
    self,
    state: dict,
    rule: dict,
    *,
    initial_state: dict | None,
    executed_commands: list[str],
) -> tuple[bool, str] | None:
    rule_type = rule.get("type")
    if rule_type == "commit_replaced_by_amend":
        return self._check_commit_replaced_by_amend(state, rule, initial_state)
    if rule_type == "commit_not_followed_by_extra_commit":
        return self._check_commit_not_followed_by_extra_commit(state, rule, initial_state)
    if rule_type == "branch_tip_replaces_commit":
        return self._check_branch_tip_replaces_commit(state, rule, initial_state)
    if rule_type == "tracked_path_removed_from_commit_tree":
        commit = self._commit_for_rule(
            state, rule, initial_state=initial_state
        ) or self._latest_commit_for_rule(state, rule)
        if not commit:
            return False, "Commit was not found."
        paths = set(self._as_list(rule.get("path") or rule.get("paths")))
        present = sorted(path for path in paths if path in (commit.get("tree") or {}))
        return (
            not present,
            "Tracked paths are absent from the commit tree."
            if not present
            else f"Commit tree still contains {present}.",
        )
    if rule_type == "ignored_paths_present":
        paths = set(self._as_list(rule.get("path") or rule.get("paths")))
        allowed_statuses = set(self._as_list(rule.get("statuses") or ["ignored", "untracked"]))
        working_tree = state.get("working_tree", {})
        missing = [
            path
            for path in sorted(paths)
            if path not in working_tree
            or self.normalizer.entry_status(working_tree.get(path)) not in allowed_statuses
        ]
        return (
            not missing,
            "Ignored/untracked local paths are present."
            if not missing
            else f"Missing ignored/untracked paths: {missing}.",
        )
    if rule_type == "ignored_paths_excluded_from_commit":
        commit = self._commit_for_rule(
            state, rule, initial_state=initial_state
        ) or self._latest_commit_for_rule(state, rule)
        if not commit:
            return False, "Commit was not found."
        paths = set(self._as_list(rule.get("path") or rule.get("paths")))
        changed = set(self._changed_paths(commit))
        tree = commit.get("tree") or {}
        present = sorted(path for path in paths if path in changed or path in tree)
        return (
            not present,
            "Ignored paths are excluded from the commit."
            if not present
            else f"Ignored paths appeared in commit: {present}.",
        )
    if rule_type == "gitignore_matches_paths":
        commit = self._commit_for_rule(
            state, rule, initial_state=initial_state
        ) or self._latest_commit_for_rule(state, rule)
        if not commit:
            return False, "Commit was not found."
        gitignore_path = rule.get("gitignore_path") or rule.get("path") or ".gitignore"
        content = self.normalizer.entry_content((commit.get("tree") or {}).get(gitignore_path))
        paths = set(self._as_list(rule.get("paths") or rule.get("ignored_paths")))
        missing = sorted(
            path for path in paths if not matching_gitignore_rule(content, path)
        )
        return (
            not missing,
            ".gitignore patterns match expected paths."
            if not missing
            else f".gitignore does not match paths: {missing}.",
        )
    if rule_type == "partial_hunks_committed":
        commit = self._commit_for_rule(
            state, rule, initial_state=initial_state
        ) or self._latest_commit_for_rule(state, rule)
        if not commit:
            return False, "Commit was not found."
        return self._path_token_map_rule(
            commit.get("changes") or {}, rule.get("paths", {}), label="Committed hunks"
        )
    if rule_type == "partial_hunks_left_in_working_tree":
        return self._path_token_map_rule(
            state.get("working_tree", {}), rule.get("paths", {}), label="Working tree hunks"
        )
    if rule_type == "repository_state_unchanged":
        if initial_state is None:
            return False, "Initial state is required."
        passed = self._states_equal(state, initial_state)
        return (
            passed,
            "Repository state is unchanged." if passed else "Repository state changed.",
        )
    if rule_type == "repository_state_unchanged_except":
        if initial_state is None:
            return False, "Initial state is required."
        exclude = set(rule.get("except", []))
        passed = self._states_equal(state, initial_state, exclude=exclude)
        return (
            passed,
            "Repository state changed only in allowed areas."
            if passed
            else "Repository state changed outside allowed areas.",
        )

    if rule_type == "min_commits_on_branch":
        branch = rule.get("branch")
        minimum = int(rule.get("minimum", 0))
        depth = self._commit_depth(state, self._ref_target(state, branch))
        return (
            depth >= minimum,
            f"Branch {branch!r} has depth {depth}, expected at least {minimum}.",
        )
    return None
