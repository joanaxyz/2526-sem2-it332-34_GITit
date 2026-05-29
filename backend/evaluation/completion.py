from dataclasses import dataclass, field
from typing import Any

from common.constants import RESULT_TARGET_MATCHED
from evaluation.services import EvaluationOutcome, StateBasedEvaluator


@dataclass
class CompletionEvaluationContext:
    session: Any
    previous_state: dict
    next_state: dict
    executed_commands: list[str] = field(default_factory=list)
    next_state_hash: str | None = None
    expected_state_hash: str | None = None


class StateRuleCompletionEvaluator:
    def evaluate(self, context: CompletionEvaluationContext) -> EvaluationOutcome:
        target_rule = context.session.variant.target_rule
        if not target_rule:
            raise ValueError("missing target_rule")

        module_number = getattr(
            getattr(context.session, "learning_unit", None), "number", None
        )

        if module_number == 4:
            # Fast path: precomputed hash comparison skips full evaluation
            if (
                context.next_state_hash is not None
                and context.expected_state_hash is not None
                and context.next_state_hash == context.expected_state_hash
            ):
                return EvaluationOutcome(
                    result_category=RESULT_TARGET_MATCHED,
                    target_matched=True,
                    summary="State hash matched target state.",
                )
            # Module 4 checks state shape only — required_commands are not enforced
            effective_rule = {k: v for k, v in target_rule.items() if k != "required_commands"}
        else:
            effective_rule = target_rule

        return StateBasedEvaluator().evaluate(
            context.next_state,
            effective_rule,
            initial_state=getattr(context.session.variant, "initial_state", None),
            executed_commands=context.executed_commands,
        )


# Production alias used by the scenario session service
ScenarioCompletionEvaluator = StateRuleCompletionEvaluator
