import copy
from dataclasses import dataclass
from typing import Any

from common.constants import RESULT_TARGET_MATCHED, RESULT_TARGET_NOT_YET_MATCHED
from simulator.ignore import matching_gitignore_rule
from simulator.services import normalize_command
from simulator.state import RepositoryStateNormalizer


@dataclass(frozen=True)
class EvaluationOutcome:
    result_category: str
    target_matched: bool
    passed_rules: tuple[dict, ...] = ()
    failed_rules: tuple[dict, ...] = ()
    summary: str = ""


def _canonical_form(command: str) -> str:
    """Return the canonical normalized form of a command for comparison.

    git checkout -b <branch> [<start>] is semantically identical to
    git switch -c <branch> [<start>]; normalize both to the switch form so
    command_matches() accepts either spelling.
    """
    normalized = normalize_command(command).lower()
    # "git checkout -b <branch>" is equivalent to "git switch -c <branch>".
    parts = normalized.split()
    if len(parts) >= 3 and parts[1] == "checkout" and parts[2] == "-b":
        parts[1] = "switch"
        parts[2] = "-c"
        return " ".join(parts)
    return normalized


def command_matches(executed: str, required: str) -> bool:
    executed = _canonical_form(executed)
    required = _canonical_form(required)
    return executed == required or executed.startswith(f"{required} ")


def _each(spec: dict, key: str, rule_type: str, field: str) -> list[dict]:
    """One rule per item of a list-valued spec key."""
    return [{"type": rule_type, field: item} for item in spec.get(key, [])]


def _pairs(spec: dict, key: str, rule_type: str, left: str, right: str) -> list[dict]:
    """One rule per entry of a mapping-valued spec key."""
    return [{"type": rule_type, left: k, right: v} for k, v in spec.get(key, {}).items()]


def _flag(spec: dict, key: str, rule_type: str) -> list[dict]:
    """A bare rule when a boolean spec key is truthy."""
    return [{"type": rule_type}] if spec.get(key) else []


def _presence_bool(spec: dict, key: str, rule_type: str) -> list[dict]:
    """A valued rule whenever the key is present - False is a real requirement."""
    return [{"type": rule_type, "value": bool(spec[key])}] if key in spec else []


def _command_rules(spec: dict) -> list[dict]:
    return [
        *_each(spec, "required_commands", "required_command", "command"),
        *_each(spec, "forbidden_commands", "forbidden_command", "command"),
    ]


def _branch_rules(spec: dict) -> list[dict]:
    return [
        *_presence_bool(spec, "repository_initialized", "repository_initialized"),
        *_each(spec, "branch_exists", "branch_exists", "branch"),
        *_each(spec, "branch_absent", "branch_absent", "branch"),
        *_pairs(spec, "branch_points_to", "branch_points_to", "branch", "commit"),
        *_pairs(
            spec, "remote_branch_points_to", "remote_branch_points_to", "remote_branch", "commit"
        ),
        *(
            [{"type": "head_branch_equals", "branch": spec["head_branch"]}]
            if spec.get("head_branch")
            else []
        ),
    ]


def _remote_rules(spec: dict) -> list[dict]:
    return [
        *_each(spec, "remote_exists", "remote_exists", "remote"),
        *_each(spec, "remote_branch_exists", "remote_branch_exists", "remote_branch"),
        *_each(spec, "remote_branch_absent", "remote_branch_absent", "remote_branch"),
        *_each(spec, "upstream_tracking_set", "upstream_tracking_set", "branch"),
        *_pairs(spec, "remote_url_matches", "remote_url_matches", "remote", "url"),
        *_pairs(spec, "upstream_tracking", "upstream_tracking_equals", "branch", "upstream"),
        *_presence_bool(spec, "remote_tracking_updated", "remote_tracking_updated"),
        *_pairs(
            spec,
            "remote_branch_matches_local",
            "remote_branch_matches_local",
            "remote_branch",
            "branch",
        ),
    ]


def _cleanliness_rules(spec: dict) -> list[dict]:
    stash_required = spec.get("stash_stack_empty") or spec.get("stash_stack_empty_after_pop")
    return [
        *_flag(spec, "working_tree_clean", "working_tree_clean"),
        *_flag(spec, "staging_empty", "index_empty"),
        *_flag(spec, "conflict_free", "conflict_free"),
        *([{"type": "stash_stack_empty"}] if stash_required else []),
    ]


def _commit_graph_rules(spec: dict) -> list[dict]:
    return [
        *_pairs(spec, "min_commits_on_branch", "min_commits_on_branch", "branch", "minimum"),
        *(
            {"type": "branches_equal", "left": left, "right": right}
            for left, right in spec.get("branches_equal", [])
        ),
    ]


def _path_rules(spec: dict) -> list[dict]:
    return [
        *_each(spec, "working_tree_contains", "working_tree_contains", "path"),
        *_each(spec, "working_tree_absent", "working_tree_absent", "path"),
        *_each(spec, "staging_contains", "staging_contains", "path"),
    ]


def _history_rules(spec: dict) -> list[dict]:
    latest_commit = spec.get("latest_commit", {})
    return [
        *(
            [
                {
                    "type": "branch_tip_commit",
                    "branch": latest_commit.get("branch"),
                    "changes_include": latest_commit.get("contains_paths", []),
                    "changes_exclude": latest_commit.get("excludes_paths", []),
                    "message_contains": latest_commit.get("message_contains", []),
                }
            ]
            if latest_commit
            else []
        ),
        *_each(spec, "reflog_contains", "reflog_contains", "expected"),
    ]


def _invariance_rules(spec: dict) -> list[dict]:
    return [
        *_flag(spec, "repository_state_unchanged", "repository_state_unchanged"),
        *(
            [
                {
                    "type": "repository_state_unchanged_except",
                    "except": spec["repository_state_unchanged_except"],
                }
            ]
            if spec.get("repository_state_unchanged_except")
            else []
        ),
    ]


def rules_from_state_requirements(state_requirements: dict | None) -> list[dict]:
    """Expand a seed-authored state_requirements spec into flat rule dicts.

    Module-level so non-evaluation callers (e.g. the battle layer deriving
    monster HP from "distance to target") can count rules without instantiating
    an evaluator. Group order is part of the contract (pinned by
    test_rule_builders): the failed-rules list surfaces to learners in spec order.
    """
    spec = state_requirements or {}
    return [
        *(dict(rule) for rule in spec.get("rules", [])),
        *_command_rules(spec),
        *_branch_rules(spec),
        *_remote_rules(spec),
        *_cleanliness_rules(spec),
        *_commit_graph_rules(spec),
        *_path_rules(spec),
        *_history_rules(spec),
        *_invariance_rules(spec),
    ]


class StateBasedEvaluator:
    def __init__(self) -> None:
        self.normalizer = RepositoryStateNormalizer()

    def evaluate(
        self,
        state: dict,
        state_requirements: dict,
        *,
        initial_state: dict | None = None,
        executed_commands: list[str] | None = None,
    ) -> EvaluationOutcome:
        state = self.normalizer.normalize(state)
        initial_state = (
            self.normalizer.normalize(initial_state) if initial_state is not None else None
        )
        executed_commands = executed_commands or []
        rules = self._rules_from_state_requirements(state_requirements or {})
        passed_rules: list[dict] = []
        failed_rules: list[dict] = []

        for rule in rules:
            passed, reason = self._check_rule(
                state,
                rule,
                initial_state=initial_state,
                executed_commands=executed_commands,
            )
            detail = {"type": rule.get("type", "unknown"), "rule": rule, "reason": reason}
            if passed:
                passed_rules.append(detail)
            else:
                failed_rules.append(detail)

        matched = not failed_rules
        result = RESULT_TARGET_MATCHED if matched else RESULT_TARGET_NOT_YET_MATCHED
        summary = (
            f"{len(passed_rules)} rules passed."
            if matched
            else f"{len(failed_rules)} of {len(rules)} rules failed."
        )
        return EvaluationOutcome(
            result_category=result,
            target_matched=matched,
            passed_rules=tuple(passed_rules),
            failed_rules=tuple(failed_rules),
            summary=summary,
        )

    def _rules_from_state_requirements(self, state_requirements: dict) -> list[dict]:
        return rules_from_state_requirements(state_requirements)

    def _check_rule(
        self,
        state: dict,
        rule: dict,
        *,
        initial_state: dict | None,
        executed_commands: list[str],
    ) -> tuple[bool, str]:
        rule_type = rule.get("type")
        if rule_type == "required_command":
            required = rule.get("command", "")
            passed = any(command_matches(executed, required) for executed in executed_commands)
            return (
                passed,
                "Required command was executed."
                if passed
                else f"Required command {required!r} was not executed.",
            )
        if rule_type == "forbidden_command":
            forbidden = rule.get("command", "")
            passed = not any(command_matches(executed, forbidden) for executed in executed_commands)
            return (
                passed,
                "Forbidden command was not used."
                if passed
                else f"Forbidden command {forbidden!r} was used.",
            )
        if rule_type == "repository_initialized":
            expected = bool(rule.get("value", True))
            passed = bool(state.get("repository_initialized", True)) == expected
            return (
                passed,
                f"repository_initialized is {state.get('repository_initialized', True)!r}.",
            )

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

        if rule_type in {"index_empty", "staging_empty"}:
            passed = not state.get("staging")
            return (
                passed,
                "Index is empty."
                if passed
                else f"Index still has {sorted(state.get('staging', {}))}.",
            )
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

        return False, f"Unsupported rule type: {rule_type!r}."

    def _check_commit_conditions(
        self,
        commit: dict,
        rule: dict,
        *,
        state: dict,
        initial_state: dict | None,
    ) -> tuple[bool, str]:
        checks = [
            ("commit_message_contains", {"text": rule.get("message_contains")}),
            ("commit_changes_include", {"paths": rule.get("changes_include")}),
            ("commit_changes_exclude", {"paths": rule.get("changes_exclude")}),
            ("commit_changes_include_tokens", {"tokens": rule.get("changes_include_tokens")}),
            ("commit_changes_exclude_tokens", {"tokens": rule.get("changes_exclude_tokens")}),
            (
                "commit_tree_contains",
                {"tree": rule.get("tree_contains"), "paths": rule.get("tree_contains")},
            ),
            ("commit_tree_excludes", {"paths": rule.get("tree_excludes")}),
            ("commit_tree_contains_tokens", {"tokens": rule.get("tree_contains_tokens")}),
            ("commit_tree_excludes_tokens", {"tokens": rule.get("tree_excludes_tokens")}),
            ("commit_parent_equals", {"parent": rule.get("parent_equals")}),
            ("commit_parent_count_equals", {"count": rule.get("parent_count_equals")}),
        ]
        if "message_equals" in rule and commit.get("message") != rule.get("message_equals"):
            return False, f"Commit message was {commit.get('message')!r}."
        if rule.get("is_merge") is True and len(commit.get("parents", [])) <= 1:
            return False, "Commit is not a merge commit."
        if rule.get("is_not_merge") is True and len(commit.get("parents", [])) > 1:
            return False, "Commit is a merge commit."
        for rule_type, payload in checks:
            if all(value in (None, [], {}) for value in payload.values()):
                continue
            passed, reason = self._check_commit_rule(
                rule_type,
                commit,
                payload,
                state=state,
                initial_state=initial_state,
            )
            if not passed:
                return passed, reason
        return True, f"Commit {commit.get('id')} matched expected details."

    def _check_commit_rule(
        self,
        rule_type: str,
        commit: dict,
        rule: dict,
        *,
        state: dict,
        initial_state: dict | None,
    ) -> tuple[bool, str]:
        if rule_type == "commit_message_contains":
            texts = self._as_list(rule.get("text") or rule.get("message_contains"))
            message = commit.get("message", "")
            missing = [text for text in texts if str(text).lower() not in message.lower()]
            return (
                not missing,
                "Commit message contains expected text."
                if not missing
                else f"Commit message did not contain {missing}.",
            )
        if rule_type == "commit_changes_include":
            paths = set(rule.get("paths") or rule.get("changes_include") or [])
            changed = set(self._changed_paths(commit))
            missing = sorted(paths - changed)
            return (
                not missing,
                "Commit changes include expected paths."
                if not missing
                else f"Commit changes were missing {missing}.",
            )
        if rule_type == "commit_changes_exclude":
            paths = set(rule.get("paths") or rule.get("changes_exclude") or [])
            changed = set(self._changed_paths(commit))
            present = sorted(paths & changed)
            return (
                not present,
                "Commit changes exclude forbidden paths."
                if not present
                else f"Commit unexpectedly changed {present}.",
            )
        if rule_type == "commit_changes_include_tokens":
            return self._token_rule_for_payload(
                commit.get("changes") or {},
                rule.get("tokens") or rule.get("changes_include_tokens") or [],
                should_contain=True,
                label="Commit changes",
            )
        if rule_type == "commit_changes_exclude_tokens":
            return self._token_rule_for_payload(
                commit.get("changes") or {},
                rule.get("tokens") or rule.get("changes_exclude_tokens") or [],
                should_contain=False,
                label="Commit changes",
            )
        if rule_type == "commit_tree_contains":
            tree = commit.get("tree") or {}
            expected_tree = rule.get("tree")
            if isinstance(expected_tree, dict):
                mismatched = [
                    path for path, value in expected_tree.items() if tree.get(path) != value
                ]
                return (
                    not mismatched,
                    "Commit tree contains expected file contents."
                    if not mismatched
                    else f"Tree mismatched paths: {mismatched}.",
                )
            paths = set(rule.get("paths") or rule.get("tree_contains") or [])
            missing = sorted(path for path in paths if path not in tree)
            return (
                not missing,
                "Commit tree contains expected paths."
                if not missing
                else f"Tree missing paths: {missing}.",
            )
        if rule_type == "commit_tree_excludes":
            tree = commit.get("tree") or {}
            paths = set(rule.get("paths") or rule.get("tree_excludes") or [])
            present = sorted(path for path in paths if path in tree)
            return (
                not present,
                "Commit tree excludes expected paths."
                if not present
                else f"Tree unexpectedly contains paths: {present}.",
            )
        if rule_type == "commit_tree_contains_tokens":
            return self._token_rule_for_payload(
                commit.get("tree") or {},
                rule.get("tokens") or rule.get("tree_contains_tokens") or [],
                should_contain=True,
                label="Commit tree",
            )
        if rule_type == "commit_tree_excludes_tokens":
            return self._token_rule_for_payload(
                commit.get("tree") or {},
                rule.get("tokens") or rule.get("tree_excludes_tokens") or [],
                should_contain=False,
                label="Commit tree",
            )
        if rule_type in {"commit_has_parent", "commit_parent_equals"}:
            parent = self._resolve_expected(
                rule.get("parent") or rule.get("parent_equals") or rule.get("expected"),
                state,
                initial_state,
            )
            passed = parent in commit.get("parents", [])
            return (
                passed,
                "Commit has expected parent."
                if passed
                else f"Commit parents were {commit.get('parents', [])}, expected {parent!r}.",
            )
        if rule_type == "commit_parent_count_equals":
            expected = int(rule.get("count", rule.get("parent_count", 0)))
            actual = len(commit.get("parents", []))
            return actual == expected, f"Commit parent count was {actual}, expected {expected}."
        if rule_type == "commit_is_merge":
            passed = len(commit.get("parents", [])) > 1
            return (
                passed,
                "Commit is a merge commit." if passed else "Commit is not a merge commit.",
            )
        if rule_type == "commit_is_not_merge":
            passed = len(commit.get("parents", [])) <= 1
            return (
                passed,
                "Commit is not a merge commit." if passed else "Commit is a merge commit.",
            )
        return False, f"Unsupported commit rule type: {rule_type!r}."

    def _check_operation_metadata(
        self, rule_type: str, state: dict, rule: dict
    ) -> tuple[bool, str]:
        key = rule.get("key")
        metadata = state.get("operation_metadata", {})
        present = key in metadata or key in state
        actual = self._operation_value(state, key)
        expected = rule.get("value")
        if rule_type == "operation_metadata_absent":
            return (
                not present,
                f"Operation metadata {key!r} {'is absent' if not present else 'is present'}.",
            )
        if rule_type == "operation_metadata_equals":
            passed = actual == expected
            return passed, f"Operation metadata {key!r} was {actual!r}, expected {expected!r}."
        if rule_type == "operation_metadata_not_equals":
            passed = actual != expected
            return passed, f"Operation metadata {key!r} was {actual!r}."
        if rule_type == "operation_metadata_contains":
            needle = rule.get("value")
            if isinstance(actual, dict) and isinstance(needle, dict):
                passed = all(
                    actual.get(item_key) == item_value for item_key, item_value in needle.items()
                )
            elif isinstance(actual, (list, tuple, set)):
                passed = needle in actual
            else:
                passed = str(needle) in str(actual)
            return passed, f"Operation metadata {key!r} was {actual!r}."
        return False, f"Unsupported operation metadata rule: {rule_type!r}."

    def _check_commit_replaced_by_amend(
        self,
        state: dict,
        rule: dict,
        initial_state: dict | None,
    ) -> tuple[bool, str]:
        old_commit = self._resolve_expected(
            rule.get("old")
            or rule.get("replaced")
            or rule.get("commit")
            or self._operation_value(state, "last_amend_replaced_commit"),
            state,
            initial_state,
        )
        new_commit = self._resolve_expected(
            rule.get("new")
            or rule.get("created")
            or self._operation_value(state, "last_amend_created_commit"),
            state,
            initial_state,
        )
        replaced = state.get("replaced_commits", {}).get(old_commit)
        passed = bool(old_commit and new_commit and replaced == new_commit)
        return (
            passed,
            "Amend replacement metadata matched."
            if passed
            else f"Amend metadata was {old_commit!r} -> {replaced!r}, expected {new_commit!r}.",
        )

    def _check_commit_not_followed_by_extra_commit(
        self,
        state: dict,
        rule: dict,
        initial_state: dict | None,
    ) -> tuple[bool, str]:
        branch = rule.get("branch") or self._head_branch(state)
        expected_tip = self._resolve_expected(
            rule.get("commit")
            or rule.get("tip")
            or self._operation_value(state, "last_amend_created_commit"),
            state,
            initial_state,
        )
        actual_tip = self._ref_target(state, branch)
        passed = bool(expected_tip and actual_tip == expected_tip)
        return (
            passed,
            f"Branch {branch!r} tip is {actual_tip!r}, expected amended tip {expected_tip!r}.",
        )

    def _check_branch_tip_replaces_commit(
        self,
        state: dict,
        rule: dict,
        initial_state: dict | None,
    ) -> tuple[bool, str]:
        branch = rule.get("branch") or self._head_branch(state)
        old_id = self._resolve_expected(
            rule.get("old")
            or rule.get("replaced")
            or rule.get("commit")
            or self._operation_value(state, "last_amend_replaced_commit"),
            state,
            initial_state,
        )
        tip_id = self._ref_target(state, branch)
        old_commit = self._commit_by_id(state, old_id)
        tip_commit = self._commit_by_id(state, tip_id)
        passed = bool(
            old_commit
            and tip_commit
            and tip_id != old_id
            and tip_commit.get("parents", []) == old_commit.get("parents", [])
        )
        return passed, f"Branch {branch!r} tip {tip_id!r} compared with replaced commit {old_id!r}."

    def _token_rule_for_entries(
        self,
        entries: dict,
        rule: dict,
        *,
        should_contain: bool,
        label: str,
    ) -> tuple[bool, str]:
        path_map = rule.get("paths")
        if isinstance(path_map, dict):
            for path, tokens in path_map.items():
                missing = self._missing_tokens(entries.get(path), self._as_list(tokens))
                if should_contain and missing:
                    return False, f"{label} entry {path!r} is missing tokens {missing}."
                if not should_contain and len(missing) != len(self._as_list(tokens)):
                    present = sorted(set(map(str, self._as_list(tokens))) - set(missing))
                    return False, f"{label} entry {path!r} still contains tokens {present}."
            return True, f"{label} token rule matched."
        return self._token_rule_for_payload(
            entries,
            rule.get("tokens", []),
            should_contain=should_contain,
            label=label,
        )

    def _token_rule_for_payload(
        self,
        payload: object,
        tokens: object,
        *,
        should_contain: bool,
        label: str,
    ) -> tuple[bool, str]:
        token_list = self._as_list(tokens)
        missing = self._missing_tokens(payload, token_list)
        if should_contain:
            return (
                not missing,
                f"{label} contains expected tokens."
                if not missing
                else f"{label} is missing tokens {missing}.",
            )
        present = sorted(set(map(str, token_list)) - set(missing))
        return (
            not present,
            f"{label} excludes expected tokens."
            if not present
            else f"{label} still contains tokens {present}.",
        )

    def _path_token_map_rule(
        self, entries: dict, path_map: dict, *, label: str
    ) -> tuple[bool, str]:
        for path, tokens in (path_map or {}).items():
            missing = self._missing_tokens(entries.get(path), self._as_list(tokens))
            if missing:
                return False, f"{label} for {path!r} is missing tokens {missing}."
        return True, f"{label} matched expected tokens."

    def _missing_tokens(self, payload: object, tokens: list) -> list[str]:
        haystack = self.normalizer.token_haystack(payload).lower()
        return [str(token) for token in tokens if str(token).lower() not in haystack]

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
