from __future__ import annotations

from dataclasses import dataclass

from evaluation.services import EvaluationOutcome, StateBasedEvaluator
from scenarios.models import ScenarioSession


@dataclass(frozen=True)
class CompletionEvaluationContext:
    session: ScenarioSession
    previous_state: dict
    next_state: dict
    executed_commands: list[str]


class ScenarioCompletionEvaluator:
    """Evaluate scenario completion from repository state.

    Command execution and terminal output happen before this boundary. This class
    only decides whether the resulting structured state satisfies the learning
    target. ``expanded_state_based`` uses the same evaluator with more detailed
    target rules.
    """

    def evaluate(self, context: CompletionEvaluationContext) -> EvaluationOutcome:
        return StateRuleCompletionEvaluator().evaluate(context)


class StateRuleCompletionEvaluator:
    def evaluate(self, context: CompletionEvaluationContext) -> EvaluationOutcome:
        rule = context.session.variant.target_rule
        if not rule:
            raise ValueError("Scenario variant is missing target_rule.")
        return StateBasedEvaluator().evaluate(
            context.next_state,
            rule,
            initial_state=context.session.variant.initial_state,
            executed_commands=context.executed_commands,
        )

