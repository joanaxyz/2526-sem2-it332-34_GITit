from common.constants import RESULT_TARGET_MATCHED, RESULT_TARGET_NOT_YET_MATCHED
from evaluation.services import EvaluationOutcome, StateBasedEvaluator
from evaluation.types import EvaluationSpec


class EvaluationEngine:
    def evaluate(
        self,
        *,
        spec: EvaluationSpec,
        next_state: dict,
        initial_state: dict | None = None,
        executed_commands: list[str] | None = None,
        next_state_hash: str | None = None,
        expected_state_hash: str | None = None,
    ) -> EvaluationOutcome:
        mode = spec.completion_policy.mode
        hashes_match = bool(
            next_state_hash
            and expected_state_hash
            and next_state_hash == expected_state_hash
        )

        if mode == "state_hash":
            return self._hash_outcome(hashes_match)

        rules_outcome = StateBasedEvaluator().evaluate(
            next_state,
            spec.as_rule_payload(),
            initial_state=initial_state,
            executed_commands=executed_commands or [],
        )
        if mode == "rules":
            return rules_outcome

        if not rules_outcome.target_matched:
            return rules_outcome
        if hashes_match:
            return EvaluationOutcome(
                result_category=RESULT_TARGET_MATCHED,
                target_matched=True,
                passed_rules=rules_outcome.passed_rules,
                failed_rules=(),
                summary="Rules passed and state hash matched target state.",
            )
        return EvaluationOutcome(
            result_category=RESULT_TARGET_NOT_YET_MATCHED,
            target_matched=False,
            passed_rules=rules_outcome.passed_rules,
            failed_rules=(
                {
                    "type": "state_hash",
                    "rule": {"type": "state_hash"},
                    "reason": "State hash did not match target state.",
                },
            ),
            summary="Rules passed but state hash did not match target state.",
        )

    def _hash_outcome(self, hashes_match: bool) -> EvaluationOutcome:
        if hashes_match:
            return EvaluationOutcome(
                result_category=RESULT_TARGET_MATCHED,
                target_matched=True,
                summary="State hash matched target state.",
            )
        return EvaluationOutcome(
            result_category=RESULT_TARGET_NOT_YET_MATCHED,
            target_matched=False,
            failed_rules=(
                {
                    "type": "state_hash",
                    "rule": {"type": "state_hash"},
                    "reason": "State hash did not match target state.",
                },
            ),
            summary="State hash did not match target state.",
        )
