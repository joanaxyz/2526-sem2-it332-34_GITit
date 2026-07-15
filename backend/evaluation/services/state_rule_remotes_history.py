from __future__ import annotations

SUPPORTED_RULE_TYPES = frozenset({
    'branch_moved_back_from_initial',
    'branch_moved_to',
    'cherry_pick_copied_changes_from',
    'cherry_pick_created_new_commit',
    'fetch_updated_remote_tracking_without_moving_local',
    'new_revert_commit_exists',
    'operation_metadata_absent',
    'operation_metadata_contains',
    'operation_metadata_equals',
    'operation_metadata_not_equals',
    'pull_moved_local_to_upstream',
    'push_moved_remote_to_local_tip',
    'reflog_contains',
    'remote_exists',
    'remote_tracking_updated',
    'remote_url_matches',
    'revert_preserves_history',
    'stash_pop_restored_paths',
    'stash_stack_contains_paths',
    'stash_stack_empty',
    'stash_top_contains',
})

def check_remote_history_state_rule(
    self,
    state: dict,
    rule: dict,
    *,
    initial_state: dict | None,
    executed_commands: list[str],
) -> tuple[bool, str] | None:
    rule_type = rule.get("type")
    if rule_type == "remote_exists":
        remote = rule.get("remote")
        passed = remote in state.get("remotes", {})
        return passed, f"Remote {remote!r} {'exists' if passed else 'does not exist'}."
    if rule_type == "remote_url_matches":
        remote = rule.get("remote")
        url = rule.get("url")
        passed = state.get("remotes", {}).get(remote) == url
        return (
            passed,
            f"Remote URL for {remote!r} was {state.get('remotes', {}).get(remote)!r}.",
        )
    if rule_type == "remote_tracking_updated":
        expected = bool(rule.get("value", True))
        passed = bool(self._operation_value(state, "remote_tracking_updated")) == expected
        return (
            passed,
            f"remote_tracking_updated is {self._operation_value(state, 'remote_tracking_updated')!r}.",
        )
    if rule_type in {
        "operation_metadata_equals",
        "operation_metadata_not_equals",
        "operation_metadata_absent",
        "operation_metadata_contains",
    }:
        return self._check_operation_metadata(rule_type, state, rule)
    if rule_type == "fetch_updated_remote_tracking_without_moving_local":
        branch = rule.get("branch") or self._head_branch(state)
        local_unchanged = True
        if initial_state and branch:
            local_unchanged = state.get("branches", {}).get(branch) == initial_state.get(
                "branches", {}
            ).get(branch)
        passed = (
            bool(self._operation_value(state, "remote_tracking_updated")) and local_unchanged
        )
        return (
            passed,
            "Fetch updated remote tracking without moving the local branch."
            if passed
            else "Fetch/local branch state did not match.",
        )
    if rule_type == "pull_moved_local_to_upstream":
        branch = rule.get("branch") or self._head_branch(state)
        upstream = rule.get("upstream") or state.get("upstream_tracking", {}).get(branch)
        passed = bool(
            branch
            and upstream
            and state.get("branches", {}).get(branch)
            == state.get("remote_branches", {}).get(upstream)
        )
        return (
            passed,
            "Local branch matches upstream after pull."
            if passed
            else "Local branch does not match upstream.",
        )
    if rule_type == "push_moved_remote_to_local_tip":
        branch = rule.get("branch") or self._head_branch(state)
        remote_branch = rule.get("remote_branch") or state.get("upstream_tracking", {}).get(
            branch
        )
        passed = bool(
            remote_branch
            and state.get("remote_branches", {}).get(remote_branch)
            == state.get("branches", {}).get(branch)
        )
        return (
            passed,
            "Remote branch matches local tip after push."
            if passed
            else "Remote branch does not match local tip.",
        )

    if rule_type == "stash_stack_empty":
        passed = not state.get("stash_stack")
        return passed, "Stash stack is empty." if passed else "Stash stack is not empty."
    if rule_type == "stash_stack_contains_paths":
        paths = set(rule.get("paths", []))
        available = self._stash_paths(state)
        missing = sorted(paths - available)
        return (
            not missing,
            "Stash contains expected paths."
            if not missing
            else f"Stash is missing paths: {missing}.",
        )
    if rule_type == "stash_top_contains":
        paths = set(rule.get("paths", []))
        available = self._stash_paths(state, top_only=True)
        missing = sorted(paths - available)
        return (
            not missing,
            "Top stash contains expected paths."
            if not missing
            else f"Top stash is missing paths: {missing}.",
        )
    if rule_type == "stash_pop_restored_paths":
        paths = set(rule.get("paths", []))
        restored = set(self._operation_value(state, "last_stash_pop_restored_paths") or [])
        actual = set(state.get("working_tree", {})) | set(state.get("staging", {}))
        missing = sorted(paths - (restored | actual))
        return (
            not missing,
            "Stash pop restored expected paths."
            if not missing
            else f"Stash pop did not restore: {missing}.",
        )

    if rule_type == "reflog_contains":
        passed = self._reflog_contains(state, rule.get("expected"))
        return (
            passed,
            "Reflog contains expected entry."
            if passed
            else f"Reflog did not contain {rule.get('expected')!r}.",
        )
    if rule_type == "branch_moved_to":
        branch = rule.get("branch") or self._head_branch(state)
        target = self._resolve_expected(
            rule.get("commit") or rule.get("target"), state, initial_state
        )
        passed = state.get("branches", {}).get(branch) == target
        return (
            passed,
            f"Branch {branch!r} points to {state.get('branches', {}).get(branch)!r}, expected {target!r}.",
        )
    if rule_type == "branch_moved_back_from_initial":
        branch = rule.get("branch") or self._head_branch(state)
        if not initial_state:
            return False, "Initial state is required."
        initial_target = initial_state.get("branches", {}).get(branch)
        passed = state.get("branches", {}).get(branch) != initial_target
        return passed, f"Branch {branch!r} target compared with initial {initial_target!r}."
    if rule_type == "new_revert_commit_exists":
        passed = any(
            str(commit.get("message", "")).lower().startswith("revert")
            for commit in state.get("commits", [])
        )
        return passed, "A revert commit exists." if passed else "No revert commit exists."
    if rule_type == "revert_preserves_history":
        target = self._resolve_expected(rule.get("commit"), state, initial_state)
        branch = rule.get("branch") or self._head_branch(state)
        history = self._branch_history(state, branch)
        passed = target in history
        return (
            passed,
            "Reverted commit remains in history."
            if passed
            else f"{target!r} is missing from history.",
        )
    if rule_type == "cherry_pick_created_new_commit":
        source = self._commit_by_id(
            state, self._resolve_expected(rule.get("source"), state, initial_state)
        )
        tip = self._latest_commit_for_rule(state, rule)
        passed = bool(
            source
            and tip
            and tip.get("id") != source.get("id")
            and tip.get("message") == source.get("message")
        )
        return (
            passed,
            "Cherry-pick created a new commit."
            if passed
            else "Cherry-pick commit was not found.",
        )
    if rule_type == "cherry_pick_copied_changes_from":
        source = self._commit_by_id(
            state, self._resolve_expected(rule.get("source"), state, initial_state)
        )
        tip = self._latest_commit_for_rule(state, rule)
        passed = bool(
            source and tip and set(self._changed_paths(source)) <= set(self._changed_paths(tip))
        )
        return (
            passed,
            "Cherry-pick copied expected changes."
            if passed
            else "Cherry-pick did not copy expected changes.",
        )

    return None
