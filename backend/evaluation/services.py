import copy
from dataclasses import dataclass

from common.constants import RESULT_TARGET_MATCHED, RESULT_TARGET_NOT_YET_MATCHED
from simulator.services import normalize_command


@dataclass(frozen=True)
class EvaluationOutcome:
    result_category: str
    target_matched: bool


def command_matches(executed: str, required: str) -> bool:
    executed = normalize_command(executed).lower()
    required = normalize_command(required).lower()
    return executed == required or executed.startswith(f"{required} ")


class StateBasedEvaluator:
    def evaluate(
        self,
        state: dict,
        target_rule: dict,
        *,
        initial_state: dict | None = None,
        executed_commands: list[str] | None = None,
    ) -> EvaluationOutcome:
        matched = True
        executed_commands = executed_commands or []
        branches = state.get("branches", {})
        remote_branches = state.get("remote_branches", {})
        head = state.get("head", {})

        for required in target_rule.get("required_commands", []):
            matched = matched and any(
                command_matches(executed, required) for executed in executed_commands
            )
        for forbidden in target_rule.get("forbidden_commands", []):
            matched = matched and not any(
                command_matches(executed, forbidden) for executed in executed_commands
            )

        if "repository_initialized" in target_rule:
            matched = matched and bool(state.get("repository_initialized", True)) == bool(
                target_rule["repository_initialized"]
            )

        for name in target_rule.get("branch_exists", []):
            matched = matched and name in branches
        for name in target_rule.get("branch_absent", []):
            matched = matched and name not in branches
        for name, commit_id in target_rule.get("branch_points_to", {}).items():
            matched = matched and branches.get(name) == commit_id
        if target_rule.get("head_branch"):
            matched = (
                matched
                and head.get("type") == "branch"
                and head.get("name") == target_rule["head_branch"]
            )

        if target_rule.get("remote_exists"):
            matched = matched and all(name in state.get("remotes", {}) for name in target_rule["remote_exists"])
        for name in target_rule.get("remote_branch_exists", []):
            matched = matched and name in remote_branches
        for name, url in target_rule.get("remote_url_matches", {}).items():
            matched = matched and state.get("remotes", {}).get(name) == url
        for branch, upstream in target_rule.get("upstream_tracking", {}).items():
            matched = matched and state.get("upstream_tracking", {}).get(branch) == upstream
        if "remote_tracking_updated" in target_rule:
            matched = matched and bool(state.get("remote_tracking_updated", False)) == bool(
                target_rule["remote_tracking_updated"]
            )
        for remote_branch, local_branch in target_rule.get("remote_branch_matches_local", {}).items():
            matched = matched and remote_branches.get(remote_branch) == branches.get(local_branch)

        if target_rule.get("working_tree_clean"):
            matched = matched and not state.get("working_tree") and not state.get("conflicts")
        if target_rule.get("staging_empty"):
            matched = matched and not state.get("staging")
        if target_rule.get("conflict_free"):
            matched = matched and not state.get("conflicts")
        if target_rule.get("stash_stack_empty") or target_rule.get("stash_stack_empty_after_pop"):
            matched = matched and not state.get("stash_stack")

        for branch, minimum in target_rule.get("min_commits_on_branch", {}).items():
            matched = matched and self._commit_depth(state, self._ref_target(state, branch)) >= minimum
        for left, right in target_rule.get("branches_equal", []):
            matched = matched and self._ref_target(state, left) == self._ref_target(state, right)

        for path in target_rule.get("working_tree_contains", []):
            matched = matched and path in state.get("working_tree", {})
        for path in target_rule.get("working_tree_absent", []):
            matched = matched and path not in state.get("working_tree", {})
        for path in target_rule.get("staging_contains", []):
            matched = matched and path in state.get("staging", {})

        latest_commit_rule = target_rule.get("latest_commit", {})
        if latest_commit_rule:
            commit = self._branch_tip_commit(state, self._ref_target(state, latest_commit_rule.get("branch")))
            matched = matched and commit is not None
            files = commit.get("files", {}) if commit else {}
            message = commit.get("message", "").lower() if commit else ""
            for path in latest_commit_rule.get("contains_paths", []):
                matched = matched and path in files
            for path in latest_commit_rule.get("excludes_paths", []):
                matched = matched and path not in files
            for required_text in latest_commit_rule.get("message_contains", []):
                matched = matched and required_text.lower() in message

        for expected in target_rule.get("reflog_contains", []):
            matched = matched and self._reflog_contains(state, expected)

        if target_rule.get("repository_state_unchanged") and initial_state is not None:
            matched = matched and self._states_equal(state, initial_state)
        if target_rule.get("repository_state_unchanged_except") and initial_state is not None:
            matched = matched and self._states_equal(
                state,
                initial_state,
                exclude=set(target_rule["repository_state_unchanged_except"]),
            )

        result = RESULT_TARGET_MATCHED if matched else RESULT_TARGET_NOT_YET_MATCHED
        return EvaluationOutcome(result_category=result, target_matched=matched)

    def _commit_depth(self, state: dict, commit_id: str | None) -> int:
        if not commit_id:
            return 0
        commits = {commit["id"]: commit for commit in state.get("commits", [])}
        seen: set[str] = set()
        stack = [commit_id]
        while stack:
            current = stack.pop()
            if current in seen or current not in commits:
                continue
            seen.add(current)
            stack.extend(commits[current].get("parents", []))
        return len(seen)

    def _branch_tip_commit(self, state: dict, commit_id: str | None) -> dict | None:
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

    def _reflog_contains(self, state: dict, expected: dict | str) -> bool:
        entries = state.get("reflog", [])
        if isinstance(expected, str):
            return any(
                expected in str(entry.get("target", "")) or expected in str(entry.get("message", ""))
                for entry in entries
            )
        return any(
            all(str(entry.get(key)) == str(value) for key, value in expected.items())
            for entry in entries
        )

    def _states_equal(self, left: dict, right: dict, *, exclude: set[str] | None = None) -> bool:
        exclude = exclude or set()
        left_copy = copy.deepcopy(left)
        right_copy = copy.deepcopy(right)
        for key in exclude:
            left_copy.pop(key, None)
            right_copy.pop(key, None)
        return left_copy == right_copy


class InspectionEvaluator:
    def evaluate(
        self,
        *,
        initial_state: dict,
        current_state: dict,
        expected_observations: dict,
        executed_commands: list[str],
    ) -> EvaluationOutcome:
        required_commands = expected_observations.get("required_commands", [])
        checks = expected_observations.get("checks", {})
        matched = True

        for required in required_commands:
            matched = matched and any(
                self._command_matches(executed, required) for executed in executed_commands
            )

        if expected_observations.get("repository_state_unchanged", True):
            matched = matched and current_state == initial_state

        observed = self.observations_for(initial_state)
        for key, expected in checks.items():
            matched = matched and observed.get(key) == expected

        result = RESULT_TARGET_MATCHED if matched else RESULT_TARGET_NOT_YET_MATCHED
        return EvaluationOutcome(result_category=result, target_matched=matched)

    def observations_for(self, state: dict) -> dict:
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
        latest_changed_paths = sorted((latest_commit or {}).get("files", {}))

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
