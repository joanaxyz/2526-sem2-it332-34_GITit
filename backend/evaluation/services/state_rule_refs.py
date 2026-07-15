from __future__ import annotations

SUPPORTED_RULE_TYPES = frozenset({
    'branch_absent',
    'branch_exists',
    'branch_points_to',
    'branch_tip_commit',
    'branches_equal',
    'head_branch_changed',
    'head_branch_equals',
    'head_detached',
    'head_detached_at',
    'head_points_to',
    'local_branches_at_most',
    'local_branches_min',
    'remote_branch_absent',
    'remote_branch_exists',
    'remote_branch_matches_local',
    'remote_branch_points_to',
    'upstream_tracking_equals',
    'upstream_tracking_set',
})

def check_ref_state_rule(
    self,
    state: dict,
    rule: dict,
    *,
    initial_state: dict | None,
    executed_commands: list[str],
) -> tuple[bool, str] | None:
    rule_type = rule.get("type")
    if rule_type == "head_branch_equals":
        branch = rule.get("branch")
        passed = (
            state.get("head", {}).get("type") == "branch"
            and state.get("head", {}).get("name") == branch
        )
        return (
            passed,
            "HEAD is on the expected branch."
            if passed
            else f"HEAD is not on branch {branch!r}.",
        )
    if rule_type == "head_detached":
        passed = state.get("head", {}).get("type") == "detached"
        return passed, "HEAD is detached." if passed else "HEAD is not detached."
    if rule_type == "head_branch_changed":
        if initial_state is None:
            return False, "Initial state is required."
        current = state.get("head", {})
        start = initial_state.get("head", {})
        passed = current.get("type") != start.get("type") or current.get(
            "name"
        ) != start.get("name")
        return (
            passed,
            "HEAD moved off its starting branch."
            if passed
            else "HEAD is still on its starting branch.",
        )
    if rule_type == "local_branches_min":
        minimum = int(rule.get("minimum", 0))
        actual = len(state.get("branches", {}))
        return actual >= minimum, f"There are {actual} local branches, expected >= {minimum}."
    if rule_type == "local_branches_at_most":
        maximum = int(rule.get("maximum", 0))
        actual = len(state.get("branches", {}))
        return actual <= maximum, f"There are {actual} local branches, expected <= {maximum}."
    if rule_type == "head_detached_at":
        target = self._resolve_expected(
            rule.get("commit") or rule.get("target"), state, initial_state
        )
        passed = (
            state.get("head", {}).get("type") == "detached"
            and state.get("head", {}).get("target") == target
        )
        return (
            passed,
            "Detached HEAD points to the expected commit."
            if passed
            else f"Detached HEAD is not at {target!r}.",
        )
    if rule_type == "head_points_to":
        target = self._resolve_expected(
            rule.get("commit") or rule.get("target"), state, initial_state
        )
        passed = self._head_commit(state) == target
        return (
            passed,
            "HEAD points to the expected commit."
            if passed
            else f"HEAD does not point to {target!r}.",
        )

    if rule_type == "branch_exists":
        branch = rule.get("branch")
        passed = branch in state.get("branches", {})
        return passed, f"Branch {branch!r} {'exists' if passed else 'does not exist'}."
    if rule_type == "branch_absent":
        branch = rule.get("branch")
        passed = branch not in state.get("branches", {})
        return passed, f"Branch {branch!r} {'is absent' if passed else 'still exists'}."
    if rule_type == "branch_points_to":
        branch = rule.get("branch")
        target = self._resolve_expected(
            rule.get("commit") or rule.get("target"), state, initial_state
        )
        passed = state.get("branches", {}).get(branch) == target
        return (
            passed,
            f"Branch {branch!r} points to {state.get('branches', {}).get(branch)!r}, expected {target!r}.",
        )
    if rule_type == "branches_equal":
        left = self._ref_target(state, rule.get("left"))
        right = self._ref_target(state, rule.get("right"))
        passed = left == right
        return passed, f"Refs compare as {left!r} and {right!r}."
    if rule_type == "branch_tip_commit":
        branch = rule.get("branch") or self._head_branch(state)
        commit = self._commit_by_id(state, self._ref_target(state, branch))
        if not commit:
            return False, f"Branch {branch!r} does not point to a known commit."
        return self._check_commit_conditions(
            commit, rule, state=state, initial_state=initial_state
        )
    if rule_type == "remote_branch_exists":
        name = rule.get("remote_branch")
        passed = name in state.get("remote_branches", {})
        return passed, f"Remote branch {name!r} {'exists' if passed else 'does not exist'}."
    if rule_type == "remote_branch_absent":
        name = rule.get("remote_branch")
        passed = name not in state.get("remote_branches", {})
        return passed, f"Remote branch {name!r} {'is absent' if passed else 'still exists'}."
    if rule_type == "upstream_tracking_set":
        branch = rule.get("branch")
        passed = branch in state.get("upstream_tracking", {})
        return passed, f"Upstream for {branch!r} is {'set' if passed else 'not set'}."
    if rule_type == "remote_branch_points_to":
        name = rule.get("remote_branch")
        target = self._resolve_expected(
            rule.get("commit") or rule.get("target"), state, initial_state
        )
        passed = state.get("remote_branches", {}).get(name) == target
        return (
            passed,
            f"Remote branch {name!r} points to {state.get('remote_branches', {}).get(name)!r}, expected {target!r}.",
        )
    if rule_type == "remote_branch_matches_local":
        remote_branch = rule.get("remote_branch")
        branch = rule.get("branch")
        passed = state.get("remote_branches", {}).get(remote_branch) == state.get(
            "branches", {}
        ).get(branch)
        return (
            passed,
            f"{remote_branch!r} and {branch!r} do not match."
            if not passed
            else "Remote branch matches local branch.",
        )
    if rule_type == "upstream_tracking_equals":
        branch = rule.get("branch")
        upstream = rule.get("upstream")
        passed = state.get("upstream_tracking", {}).get(branch) == upstream
        return (
            passed,
            f"Upstream for {branch!r} is {state.get('upstream_tracking', {}).get(branch)!r}.",
        )

    return None
