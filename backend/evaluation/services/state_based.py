from common.constants import RESULT_TARGET_MATCHED, RESULT_TARGET_NOT_YET_MATCHED
from simulator.state import RepositoryStateNormalizer

from .commit_rules import StateCommitRuleMixin
from .payload_rules import StatePayloadRuleMixin
from .rule_builders import rules_from_state_requirements
from .state_helpers import StateHelperMixin
from .state_requirements import StateRequirementRuleMixin
from .types import EvaluationOutcome


class StateBasedEvaluator(
    StateRequirementRuleMixin,
    StateCommitRuleMixin,
    StatePayloadRuleMixin,
    StateHelperMixin,
):
    def __init__(self) -> None:
        self.normalizer = RepositoryStateNormalizer()

    def evaluate(
        self,
        state: dict,
        state_requirements: dict,
        *,
        initial_state: dict | None = None,
        executed_commands: list[str] | None = None,
        state_already_normalized: bool = False,
        initial_state_already_normalized: bool = False,
    ) -> EvaluationOutcome:
        state = state if state_already_normalized else self.normalizer.normalize(state)
        initial_state = (
            initial_state
            if initial_state is not None and initial_state_already_normalized
            else self.normalizer.normalize(initial_state)
            if initial_state is not None
            else None
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
