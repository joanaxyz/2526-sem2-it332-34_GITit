from dataclasses import dataclass

from common.constants import RESULT_TARGET_MATCHED, RESULT_TARGET_NOT_YET_MATCHED


@dataclass(frozen=True)
class EvaluationOutcome:
    result_category: str
    target_matched: bool


class StateBasedEvaluator:
    def evaluate(self, state: dict, target_rule: dict) -> EvaluationOutcome:
        matched = True
        branches = state.get("branches", {})
        head = state.get("head", {})

        for name in target_rule.get("branch_exists", []):
            matched = matched and name in branches
        for name in target_rule.get("branch_absent", []):
            matched = matched and name not in branches
        if target_rule.get("head_branch"):
            matched = matched and head.get("type") == "branch" and head.get("name") == target_rule["head_branch"]
        if target_rule.get("working_tree_clean"):
            matched = matched and not state.get("working_tree")
        if target_rule.get("staging_empty"):
            matched = matched and not state.get("staging")
        if target_rule.get("conflict_free"):
            matched = matched and not state.get("conflicts")

        for branch, minimum in target_rule.get("min_commits_on_branch", {}).items():
            matched = matched and self._commit_depth(state, branches.get(branch)) >= minimum
        for left, right in target_rule.get("branches_equal", []):
            matched = matched and branches.get(left) == branches.get(right)

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
