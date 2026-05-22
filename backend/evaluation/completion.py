from __future__ import annotations

from dataclasses import dataclass

from common.constants import COMPLETION_INSPECTION
from evaluation.services import EvaluationOutcome, InspectionEvaluator, StateBasedEvaluator
from scenarios.models import ScenarioSession


@dataclass(frozen=True)
class CompletionEvaluationContext:
    session: ScenarioSession
    previous_state: dict
    next_state: dict
    executed_commands: list[str]
    inspection_answer: dict | None = None


class ScenarioCompletionEvaluator:
    """Routes completion checks by scenario type.

    Command execution and terminal output happen before this boundary. This class
    only decides whether the resulting structured state satisfies the learning
    target.
    """

    def evaluate(self, context: CompletionEvaluationContext) -> EvaluationOutcome:
        completion_type = context.session.difficulty_instance.completion_type
        if completion_type == COMPLETION_INSPECTION:
            return InspectionCompletionEvaluator().evaluate(context)
        return StateRuleCompletionEvaluator().evaluate(context)


class StateRuleCompletionEvaluator:
    def evaluate(self, context: CompletionEvaluationContext) -> EvaluationOutcome:
        rule = context.session.variant.target_rule or context.session.difficulty_instance.target_rule.rule
        return StateBasedEvaluator().evaluate(
            context.next_state,
            rule,
            initial_state=context.session.variant.initial_state,
            executed_commands=context.executed_commands,
        )


class InspectionCompletionEvaluator:
    def evaluate(self, context: CompletionEvaluationContext) -> EvaluationOutcome:
        return InspectionEvaluator().evaluate(
            initial_state=context.session.variant.initial_state,
            current_state=context.next_state,
            expected_observations=context.session.variant.expected_observations,
            executed_commands=context.executed_commands,
            submitted_answer=context.inspection_answer,
        )
