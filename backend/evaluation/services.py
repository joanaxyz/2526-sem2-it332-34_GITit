import copy
from dataclasses import dataclass
from typing import Any

from common.constants import RESULT_TARGET_MATCHED, RESULT_TARGET_NOT_YET_MATCHED
from simulator.services import normalize_command
from simulator.state import RepositoryStateNormalizer


@dataclass(frozen=True)
class EvaluationOutcome:
    result_category: str
    target_matched: bool
    passed_rules: tuple[dict, ...] = ()
    failed_rules: tuple[dict, ...] = ()
    summary: str = ""


def command_matches(executed: str, required: str) -> bool:
    executed = normalize_command(executed).lower()
    required = normalize_command(required).lower()
    return executed == required or executed.startswith(f"{required} ")


class StateBasedEvaluator:
    def __init__(self) -> None:
        self.normalizer = RepositoryStateNormalizer()

    def evaluate(
        self,
        state: dict,
        target_rule: dict,
        *,
        initial_state: dict | None = None,
        executed_commands: list[str] | None = None,
    ) -> EvaluationOutcome:
        state = self.normalizer.normalize(state)
        initial_state = self.normalizer.normalize(initial_state) if initial_state is not None else None
        executed_commands = executed_commands or []
        rules = self._rules_from_target_rule(target_rule or {})
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

    def _rules_from_target_rule(self, target_rule: dict) -> list[dict]:
        rules = [dict(rule) for rule in target_rule.get("rules", [])]

        for required in target_rule.get("required_commands", []):
            rules.append({"type": "required_command", "command": required})
        for forbidden in target_rule.get("forbidden_commands", []):
            rules.append({"type": "forbidden_command", "command": forbidden})

        if "repository_initialized" in target_rule:
            rules.append(
                {
                    "type": "repository_initialized",
                    "value": bool(target_rule["repository_initialized"]),
                }
            )
        for name in target_rule.get("branch_exists", []):
            rules.append({"type": "branch_exists", "branch": name})
        for name in target_rule.get("branch_absent", []):
            rules.append({"type": "branch_absent", "branch": name})
        for name, commit_id in target_rule.get("branch_points_to", {}).items():
            rules.append({"type": "branch_points_to", "branch": name, "commit": commit_id})
        if target_rule.get("head_branch"):
            rules.append({"type": "head_branch_equals", "branch": target_rule["head_branch"]})

        for name in target_rule.get("remote_exists", []):
            rules.append({"type": "remote_exists", "remote": name})
        for name in target_rule.get("remote_branch_exists", []):
            rules.append({"type": "remote_branch_exists", "remote_branch": name})
        for name, url in target_rule.get("remote_url_matches", {}).items():
            rules.append({"type": "remote_url_matches", "remote": name, "url": url})
        for branch, upstream in target_rule.get("upstream_tracking", {}).items():
            rules.append(
                {
                    "type": "upstream_tracking_equals",
                    "branch": branch,
                    "upstream": upstream,
                }
            )
        if "remote_tracking_updated" in target_rule:
            rules.append(
                {
                    "type": "remote_tracking_updated",
                    "value": bool(target_rule["remote_tracking_updated"]),
                }
            )
        for remote_branch, local_branch in target_rule.get("remote_branch_matches_local", {}).items():
            rules.append(
                {
                    "type": "remote_branch_matches_local",
                    "remote_branch": remote_branch,
                    "branch": local_branch,
                }
            )

        if target_rule.get("working_tree_clean"):
            rules.append({"type": "working_tree_clean"})
        if target_rule.get("staging_empty"):
            rules.append({"type": "index_empty"})
        if target_rule.get("conflict_free"):
            rules.append({"type": "conflict_free"})
        if target_rule.get("stash_stack_empty") or target_rule.get("stash_stack_empty_after_pop"):
            rules.append({"type": "stash_stack_empty"})

        for branch, minimum in target_rule.get("min_commits_on_branch", {}).items():
            rules.append({"type": "min_commits_on_branch", "branch": branch, "minimum": minimum})
        for left, right in target_rule.get("branches_equal", []):
            rules.append({"type": "branches_equal", "left": left, "right": right})

        for path in target_rule.get("working_tree_contains", []):
            rules.append({"type": "working_tree_contains", "path": path})
        for path in target_rule.get("working_tree_absent", []):
            rules.append({"type": "working_tree_absent", "path": path})
        for path in target_rule.get("staging_contains", []):
            rules.append({"type": "staging_contains", "path": path})

        latest_commit_rule = target_rule.get("latest_commit", {})
        if latest_commit_rule:
            rules.append(
                {
                    "type": "branch_tip_commit",
                    "branch": latest_commit_rule.get("branch"),
                    "changes_include": latest_commit_rule.get("contains_paths", []),
                    "changes_exclude": latest_commit_rule.get("excludes_paths", []),
                    "message_contains": latest_commit_rule.get("message_contains", []),
                }
            )

        for expected in target_rule.get("reflog_contains", []):
            rules.append({"type": "reflog_contains", "expected": expected})

        if target_rule.get("repository_state_unchanged"):
            rules.append({"type": "repository_state_unchanged"})
        if target_rule.get("repository_state_unchanged_except"):
            rules.append(
                {
                    "type": "repository_state_unchanged_except",
                    "except": target_rule["repository_state_unchanged_except"],
                }
            )

        return rules

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
            return passed, "Required command was executed." if passed else f"Required command {required!r} was not executed."
        if rule_type == "forbidden_command":
            forbidden = rule.get("command", "")
            passed = not any(command_matches(executed, forbidden) for executed in executed_commands)
            return passed, "Forbidden command was not used." if passed else f"Forbidden command {forbidden!r} was used."
        if rule_type == "repository_initialized":
            expected = bool(rule.get("value", True))
            passed = bool(state.get("repository_initialized", True)) == expected
            return passed, f"repository_initialized is {state.get('repository_initialized', True)!r}."

        if rule_type == "head_branch_equals":
            branch = rule.get("branch")
            passed = state.get("head", {}).get("type") == "branch" and state.get("head", {}).get("name") == branch
            return passed, "HEAD is on the expected branch." if passed else f"HEAD is not on branch {branch!r}."
        if rule_type == "head_detached_at":
            target = self._resolve_expected(rule.get("commit") or rule.get("target"), state, initial_state)
            passed = state.get("head", {}).get("type") == "detached" and state.get("head", {}).get("target") == target
            return passed, "Detached HEAD points to the expected commit." if passed else f"Detached HEAD is not at {target!r}."
        if rule_type == "head_points_to":
            target = self._resolve_expected(rule.get("commit") or rule.get("target"), state, initial_state)
            passed = self._head_commit(state) == target
            return passed, "HEAD points to the expected commit." if passed else f"HEAD does not point to {target!r}."

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
            target = self._resolve_expected(rule.get("commit") or rule.get("target"), state, initial_state)
            passed = state.get("branches", {}).get(branch) == target
            return passed, f"Branch {branch!r} points to {state.get('branches', {}).get(branch)!r}, expected {target!r}."
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
            return self._check_commit_conditions(commit, rule, state=state, initial_state=initial_state)
        if rule_type == "remote_branch_exists":
            name = rule.get("remote_branch")
            passed = name in state.get("remote_branches", {})
            return passed, f"Remote branch {name!r} {'exists' if passed else 'does not exist'}."
        if rule_type == "remote_branch_points_to":
            name = rule.get("remote_branch")
            target = self._resolve_expected(rule.get("commit") or rule.get("target"), state, initial_state)
            passed = state.get("remote_branches", {}).get(name) == target
            return passed, f"Remote branch {name!r} points to {state.get('remote_branches', {}).get(name)!r}, expected {target!r}."
        if rule_type == "remote_branch_matches_local":
            remote_branch = rule.get("remote_branch")
            branch = rule.get("branch")
            passed = state.get("remote_branches", {}).get(remote_branch) == state.get("branches", {}).get(branch)
            return passed, f"{remote_branch!r} and {branch!r} do not match." if not passed else "Remote branch matches local branch."
        if rule_type == "upstream_tracking_equals":
            branch = rule.get("branch")
            upstream = rule.get("upstream")
            passed = state.get("upstream_tracking", {}).get(branch) == upstream
            return passed, f"Upstream for {branch!r} is {state.get('upstream_tracking', {}).get(branch)!r}."

        if rule_type == "commit_exists":
            commit_id = self._resolve_expected(rule.get("commit") or rule.get("id"), state, initial_state)
            passed = self._commit_by_id(state, commit_id) is not None
            return passed, f"Commit {commit_id!r} {'exists' if passed else 'does not exist'}."
        if rule_type in {"latest_commit_message_equals", "latest_commit_message_contains"}:
            commit = self._latest_commit_for_rule(state, rule)
            expected = rule.get("message") or rule.get("text")
            if not commit:
                return False, "Latest commit was not found."
            message = commit.get("message", "")
            passed = message == expected if rule_type.endswith("equals") else str(expected).lower() in message.lower()
            return passed, f"Latest commit message was {message!r}."
        if rule_type in {
            "commit_message_contains",
            "commit_changes_include",
            "commit_changes_exclude",
            "commit_tree_contains",
            "commit_tree_excludes",
            "commit_has_parent",
            "commit_parent_equals",
            "commit_parent_count_equals",
            "commit_is_merge",
            "commit_is_not_merge",
        }:
            commit = self._commit_for_rule(state, rule, initial_state=initial_state)
            if not commit:
                return False, "Commit was not found."
            return self._check_commit_rule(rule_type, commit, rule, state=state, initial_state=initial_state)
        if rule_type == "branch_history_contains":
            branch = rule.get("branch")
            expected = self._expected_commits(rule, state, initial_state)
            history = self._branch_history(state, branch)
            missing = [commit_id for commit_id in expected if commit_id not in history]
            return not missing, "Branch history contains expected commits." if not missing else f"Missing commits in history: {missing}."
        if rule_type == "branch_history_excludes":
            branch = rule.get("branch")
            excluded = self._expected_commits(rule, state, initial_state)
            history = self._branch_history(state, branch)
            present = [commit_id for commit_id in excluded if commit_id in history]
            return not present, "Branch history excludes forbidden commits." if not present else f"Unexpected commits in history: {present}."

        if rule_type in {"index_empty", "staging_empty"}:
            passed = not state.get("staging")
            return passed, "Index is empty." if passed else f"Index still has {sorted(state.get('staging', {}))}."
        if rule_type == "staging_contains":
            paths = set(self._as_list(rule.get("path") or rule.get("paths")))
            missing = sorted(paths - set(state.get("staging", {})))
            return not missing, "Staging contains expected paths." if not missing else f"Staging is missing {missing}."
        if rule_type == "staging_excludes":
            paths = set(self._as_list(rule.get("path") or rule.get("paths")))
            present = sorted(paths & set(state.get("staging", {})))
            return not present, "Staging excludes expected paths." if not present else f"Staging still contains {present}."
        if rule_type == "staging_matches_exact_paths":
            expected = sorted(rule.get("paths", []))
            actual = sorted(state.get("staging", {}))
            return actual == expected, f"Staged paths were {actual}, expected {expected}."

        if rule_type == "working_tree_clean":
            passed = not state.get("working_tree") and not state.get("conflicts")
            return passed, "Working tree is clean." if passed else "Working tree still has changes or conflicts."
        if rule_type == "working_tree_contains":
            paths = set(self._as_list(rule.get("path") or rule.get("paths")))
            missing = sorted(paths - set(state.get("working_tree", {})))
            return not missing, "Working tree contains expected paths." if not missing else f"Working tree is missing {missing}."
        if rule_type == "working_tree_absent":
            paths = set(self._as_list(rule.get("path") or rule.get("paths")))
            present = sorted(paths & set(state.get("working_tree", {})))
            return not present, "Working tree excludes expected paths." if not present else f"Working tree still contains {present}."
        if rule_type == "working_tree_matches_exact_paths":
            expected = sorted(rule.get("paths", []))
            actual = sorted(state.get("working_tree", {}))
            return actual == expected, f"Working tree paths were {actual}, expected {expected}."
        if rule_type == "working_tree_clean_except":
            allowed = set(rule.get("paths", []))
            actual = set(state.get("working_tree", {}))
            extra = sorted(actual - allowed)
            return not extra and not state.get("conflicts"), "Working tree only has allowed paths." if not extra else f"Unexpected working tree paths: {extra}."

        if rule_type in {"conflict_free", "conflicts_empty", "conflicts_resolved"}:
            passed = not state.get("conflicts")
            return passed, "No conflicts remain." if passed else f"Conflicts remain: {state.get('conflicts')}."
        if rule_type == "conflicts_contain_paths":
            paths = set(rule.get("paths", []))
            actual = set(state.get("conflicts", []))
            missing = sorted(paths - actual)
            return not missing, "Expected conflict paths are present." if not missing else f"Missing conflict paths: {missing}."
        if rule_type == "conflict_resolution_contains":
            path = rule.get("path")
            token = str(rule.get("token", ""))
            value = str(state.get("staging", {}).get(path) or state.get("working_tree", {}).get(path) or "")
            passed = token in value
            return passed, f"Conflict resolution for {path!r} {'contains' if passed else 'does not contain'} {token!r}."

        if rule_type == "remote_exists":
            remote = rule.get("remote")
            passed = remote in state.get("remotes", {})
            return passed, f"Remote {remote!r} {'exists' if passed else 'does not exist'}."
        if rule_type == "remote_url_matches":
            remote = rule.get("remote")
            url = rule.get("url")
            passed = state.get("remotes", {}).get(remote) == url
            return passed, f"Remote URL for {remote!r} was {state.get('remotes', {}).get(remote)!r}."
        if rule_type == "remote_tracking_updated":
            expected = bool(rule.get("value", True))
            passed = bool(self._operation_value(state, "remote_tracking_updated")) == expected
            return passed, f"remote_tracking_updated is {self._operation_value(state, 'remote_tracking_updated')!r}."
        if rule_type == "fetch_updated_remote_tracking_without_moving_local":
            branch = rule.get("branch") or self._head_branch(state)
            local_unchanged = True
            if initial_state and branch:
                local_unchanged = state.get("branches", {}).get(branch) == initial_state.get("branches", {}).get(branch)
            passed = bool(self._operation_value(state, "remote_tracking_updated")) and local_unchanged
            return passed, "Fetch updated remote tracking without moving the local branch." if passed else "Fetch/local branch state did not match."
        if rule_type == "pull_moved_local_to_upstream":
            branch = rule.get("branch") or self._head_branch(state)
            upstream = rule.get("upstream") or state.get("upstream_tracking", {}).get(branch)
            passed = bool(branch and upstream and state.get("branches", {}).get(branch) == state.get("remote_branches", {}).get(upstream))
            return passed, "Local branch matches upstream after pull." if passed else "Local branch does not match upstream."
        if rule_type == "push_moved_remote_to_local_tip":
            branch = rule.get("branch") or self._head_branch(state)
            remote_branch = rule.get("remote_branch") or state.get("upstream_tracking", {}).get(branch)
            passed = bool(remote_branch and state.get("remote_branches", {}).get(remote_branch) == state.get("branches", {}).get(branch))
            return passed, "Remote branch matches local tip after push." if passed else "Remote branch does not match local tip."

        if rule_type == "stash_stack_empty":
            passed = not state.get("stash_stack")
            return passed, "Stash stack is empty." if passed else "Stash stack is not empty."
        if rule_type == "stash_stack_contains_paths":
            paths = set(rule.get("paths", []))
            available = self._stash_paths(state)
            missing = sorted(paths - available)
            return not missing, "Stash contains expected paths." if not missing else f"Stash is missing paths: {missing}."
        if rule_type == "stash_top_contains":
            paths = set(rule.get("paths", []))
            available = self._stash_paths(state, top_only=True)
            missing = sorted(paths - available)
            return not missing, "Top stash contains expected paths." if not missing else f"Top stash is missing paths: {missing}."
        if rule_type == "stash_pop_restored_paths":
            paths = set(rule.get("paths", []))
            restored = set(self._operation_value(state, "last_stash_pop_restored_paths") or [])
            actual = set(state.get("working_tree", {})) | set(state.get("staging", {}))
            missing = sorted(paths - (restored | actual))
            return not missing, "Stash pop restored expected paths." if not missing else f"Stash pop did not restore: {missing}."

        if rule_type == "reflog_contains":
            passed = self._reflog_contains(state, rule.get("expected"))
            return passed, "Reflog contains expected entry." if passed else f"Reflog did not contain {rule.get('expected')!r}."
        if rule_type == "branch_moved_to":
            branch = rule.get("branch") or self._head_branch(state)
            target = self._resolve_expected(rule.get("commit") or rule.get("target"), state, initial_state)
            passed = state.get("branches", {}).get(branch) == target
            return passed, f"Branch {branch!r} points to {state.get('branches', {}).get(branch)!r}, expected {target!r}."
        if rule_type == "branch_moved_back_from_initial":
            branch = rule.get("branch") or self._head_branch(state)
            if not initial_state:
                return False, "Initial state is required."
            initial_target = initial_state.get("branches", {}).get(branch)
            passed = state.get("branches", {}).get(branch) != initial_target
            return passed, f"Branch {branch!r} target compared with initial {initial_target!r}."
        if rule_type == "new_revert_commit_exists":
            passed = any(str(commit.get("message", "")).lower().startswith("revert") for commit in state.get("commits", []))
            return passed, "A revert commit exists." if passed else "No revert commit exists."
        if rule_type == "revert_preserves_history":
            target = self._resolve_expected(rule.get("commit"), state, initial_state)
            branch = rule.get("branch") or self._head_branch(state)
            history = self._branch_history(state, branch)
            passed = target in history
            return passed, "Reverted commit remains in history." if passed else f"{target!r} is missing from history."
        if rule_type == "cherry_pick_created_new_commit":
            source = self._commit_by_id(state, self._resolve_expected(rule.get("source"), state, initial_state))
            tip = self._latest_commit_for_rule(state, rule)
            passed = bool(source and tip and tip.get("id") != source.get("id") and tip.get("message") == source.get("message"))
            return passed, "Cherry-pick created a new commit." if passed else "Cherry-pick commit was not found."
        if rule_type == "cherry_pick_copied_changes_from":
            source = self._commit_by_id(state, self._resolve_expected(rule.get("source"), state, initial_state))
            tip = self._latest_commit_for_rule(state, rule)
            passed = bool(source and tip and set(self._changed_paths(source)) <= set(self._changed_paths(tip)))
            return passed, "Cherry-pick copied expected changes." if passed else "Cherry-pick did not copy expected changes."

        if rule_type == "repository_state_unchanged":
            if initial_state is None:
                return False, "Initial state is required."
            passed = self._states_equal(state, initial_state)
            return passed, "Repository state is unchanged." if passed else "Repository state changed."
        if rule_type == "repository_state_unchanged_except":
            if initial_state is None:
                return False, "Initial state is required."
            exclude = set(rule.get("except", []))
            passed = self._states_equal(state, initial_state, exclude=exclude)
            return passed, "Repository state changed only in allowed areas." if passed else "Repository state changed outside allowed areas."

        if rule_type == "min_commits_on_branch":
            branch = rule.get("branch")
            minimum = int(rule.get("minimum", 0))
            depth = self._commit_depth(state, self._ref_target(state, branch))
            return depth >= minimum, f"Branch {branch!r} has depth {depth}, expected at least {minimum}."

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
            ("commit_tree_contains", {"tree": rule.get("tree_contains"), "paths": rule.get("tree_contains")}),
            ("commit_tree_excludes", {"paths": rule.get("tree_excludes")}),
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
            return not missing, "Commit message contains expected text." if not missing else f"Commit message did not contain {missing}."
        if rule_type == "commit_changes_include":
            paths = set(rule.get("paths") or rule.get("changes_include") or [])
            changed = set(self._changed_paths(commit))
            missing = sorted(paths - changed)
            return not missing, "Commit changes include expected paths." if not missing else f"Commit changes were missing {missing}."
        if rule_type == "commit_changes_exclude":
            paths = set(rule.get("paths") or rule.get("changes_exclude") or [])
            changed = set(self._changed_paths(commit))
            present = sorted(paths & changed)
            return not present, "Commit changes exclude forbidden paths." if not present else f"Commit unexpectedly changed {present}."
        if rule_type == "commit_tree_contains":
            tree = commit.get("tree") or {}
            expected_tree = rule.get("tree")
            if isinstance(expected_tree, dict):
                mismatched = [
                    path
                    for path, value in expected_tree.items()
                    if tree.get(path) != value
                ]
                return not mismatched, "Commit tree contains expected file contents." if not mismatched else f"Tree mismatched paths: {mismatched}."
            paths = set(rule.get("paths") or rule.get("tree_contains") or [])
            missing = sorted(path for path in paths if path not in tree)
            return not missing, "Commit tree contains expected paths." if not missing else f"Tree missing paths: {missing}."
        if rule_type == "commit_tree_excludes":
            tree = commit.get("tree") or {}
            paths = set(rule.get("paths") or rule.get("tree_excludes") or [])
            present = sorted(path for path in paths if path in tree)
            return not present, "Commit tree excludes expected paths." if not present else f"Tree unexpectedly contains paths: {present}."
        if rule_type in {"commit_has_parent", "commit_parent_equals"}:
            parent = self._resolve_expected(
                rule.get("parent") or rule.get("parent_equals") or rule.get("expected"),
                state,
                initial_state,
            )
            passed = parent in commit.get("parents", [])
            return passed, "Commit has expected parent." if passed else f"Commit parents were {commit.get('parents', [])}, expected {parent!r}."
        if rule_type == "commit_parent_count_equals":
            expected = int(rule.get("count", rule.get("parent_count", 0)))
            actual = len(commit.get("parents", []))
            return actual == expected, f"Commit parent count was {actual}, expected {expected}."
        if rule_type == "commit_is_merge":
            passed = len(commit.get("parents", [])) > 1
            return passed, "Commit is a merge commit." if passed else "Commit is not a merge commit."
        if rule_type == "commit_is_not_merge":
            passed = len(commit.get("parents", [])) <= 1
            return passed, "Commit is not a merge commit." if passed else "Commit is a merge commit."
        return False, f"Unsupported commit rule type: {rule_type!r}."

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
            for resolved in (self._resolve_expected(value, state, initial_state) for value in values)
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
        return next((commit for commit in state.get("commits", []) if commit["id"] == commit_id), None)

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
                expected in str(entry.get("target", "")) or expected in str(entry.get("message", ""))
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
            return {key: self._resolve_expected(item, state, initial_state) for key, item in value.items()}
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


class InspectionEvaluator:
    def __init__(self) -> None:
        self.normalizer = RepositoryStateNormalizer()

    def evaluate(
        self,
        *,
        initial_state: dict,
        current_state: dict,
        expected_observations: dict,
        executed_commands: list[str],
    ) -> EvaluationOutcome:
        initial_state = self.normalizer.normalize(initial_state)
        current_state = self.normalizer.normalize(current_state)
        required_commands = expected_observations.get("required_commands", [])
        checks = expected_observations.get("checks", {})
        passed_rules: list[dict] = []
        failed_rules: list[dict] = []

        for required in required_commands:
            passed = any(self._command_matches(executed, required) for executed in executed_commands)
            detail = {"type": "required_command", "rule": {"command": required}}
            if passed:
                passed_rules.append({**detail, "reason": "Required inspection command was executed."})
            else:
                failed_rules.append({**detail, "reason": f"Required inspection command {required!r} was not executed."})

        if expected_observations.get("repository_state_unchanged", True):
            passed = current_state == initial_state
            detail = {"type": "repository_state_unchanged", "rule": {}}
            if passed:
                passed_rules.append({**detail, "reason": "Repository state is unchanged."})
            else:
                failed_rules.append({**detail, "reason": "Repository state changed during inspection."})

        observed = self.observations_for(initial_state)
        for key, expected in checks.items():
            passed = observed.get(key) == expected
            detail = {"type": "observation_equals", "rule": {"key": key, "expected": expected}}
            if passed:
                passed_rules.append({**detail, "reason": f"Observation {key!r} matched."})
            else:
                failed_rules.append(
                    {
                        **detail,
                        "reason": f"Observation {key!r} was {observed.get(key)!r}, expected {expected!r}.",
                    }
                )

        matched = not failed_rules
        result = RESULT_TARGET_MATCHED if matched else RESULT_TARGET_NOT_YET_MATCHED
        return EvaluationOutcome(
            result_category=result,
            target_matched=matched,
            passed_rules=tuple(passed_rules),
            failed_rules=tuple(failed_rules),
            summary=(
                f"{len(passed_rules)} inspection checks passed."
                if matched
                else f"{len(failed_rules)} inspection checks failed."
            ),
        )

    def observations_for(self, state: dict) -> dict:
        state = self.normalizer.normalize(state)
        branches = state.get("branches", {})
        head = state.get("head", {})
        head_branch = head.get("name") if head.get("type") == "branch" else None
        working_tree = state.get("working_tree", {})
        staging = state.get("staging", {})
        commits = state.get("commits", [])
        conflicts = sorted(state.get("conflicts", []))
        unstaged_paths = sorted(
            path for path, value in working_tree.items() if str(value).lower() != "untracked"
        )
        untracked_paths = sorted(
            path for path, value in working_tree.items() if str(value).lower() == "untracked"
        )
        staged_paths = sorted(staging)
        head_target = branches.get(head_branch) if head_branch else head.get("target")
        latest_commit = self._commit_by_id(state, head_target)
        merge_commit = next(
            (commit for commit in reversed(commits) if len(commit.get("parents", [])) > 1),
            None,
        )
        latest_changed_paths = sorted((latest_commit or {}).get("changes") or (latest_commit or {}).get("files", {}))

        return {
            "head_branch": head_branch,
            "current_branch": head_branch,
            "active_branch": head_branch,
            "available_branches": sorted(branches),
            "branch_list": sorted(branches),
            "branch_tips": dict(sorted(branches.items())),
            "active_feature_branch": head_branch if str(head_branch or "").startswith("feature/") else None,
            "stale_branch": self._stale_branch(branches),
            "staged_paths": staged_paths,
            "staged_changes": staged_paths,
            "staging_empty": not staged_paths,
            "staged_diff_paths": staged_paths,
            "unstaged_paths": unstaged_paths,
            "unstaged_changes": unstaged_paths,
            "unstaged_diff_paths": unstaged_paths,
            "untracked_paths": untracked_paths,
            "untracked_files": untracked_paths,
            "conflicted_paths": conflicts,
            "latest_commit": head_target,
            "commit_order": [commit["id"] for commit in commits],
            "commit_history": [commit["id"] for commit in commits],
            "target_commit": head_target,
            "commit_message": (latest_commit or {}).get("message", ""),
            "changed_paths": latest_changed_paths,
            "parent_commit": ((latest_commit or {}).get("parents") or [None])[0],
            "merge_commit": (merge_commit or {}).get("id"),
            "merge_parents": (merge_commit or {}).get("parents", []),
            "divergence_point": self._divergence_point(commits),
            "diff_target": {
                "unstaged": unstaged_paths,
                "staged": staged_paths,
                "conflicted": conflicts,
            },
        }

    def _command_matches(self, executed: str, required: str) -> bool:
        return command_matches(executed, required)

    def _commit_by_id(self, state: dict, commit_id: str | None) -> dict | None:
        if not commit_id:
            return None
        return next((commit for commit in state.get("commits", []) if commit["id"] == commit_id), None)

    def _stale_branch(self, branches: dict) -> str | None:
        for name in sorted(branches):
            if name.endswith(("-old", "-done", "-stale")):
                return name
        return None

    def _divergence_point(self, commits: list[dict]) -> str | None:
        parent_counts: dict[str, int] = {}
        for commit in commits:
            for parent in commit.get("parents", []):
                parent_counts[parent] = parent_counts.get(parent, 0) + 1
        common = [commit_id for commit_id, count in parent_counts.items() if count > 1]
        return common[-1] if common else None
