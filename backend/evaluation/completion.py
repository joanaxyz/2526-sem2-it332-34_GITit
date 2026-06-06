from dataclasses import dataclass, field
from typing import Any

from evaluation.compiler import compile_evaluation_spec
from evaluation.engine import EvaluationEngine
from evaluation.services import EvaluationOutcome


@dataclass
class CompletionEvaluationContext:
    session: Any
    previous_state: dict
    next_state: dict
    executed_commands: list[str] = field(default_factory=list)
    next_state_hash: str | None = None
    expected_state_hash: str | None = None


class PracticeCompletionEvaluator:
    def evaluate(self, context: CompletionEvaluationContext) -> EvaluationOutcome:
        raw_spec = getattr(context.session.variant, "evaluation_spec", None)
        if not raw_spec:
            raw_spec = getattr(context.session.problem, "evaluation_spec", None)
        spec = compile_evaluation_spec(raw_spec)
        return EvaluationEngine().evaluate(
            spec=spec,
            next_state=context.next_state,
            initial_state=getattr(context.session.variant, "initial_state", None),
            executed_commands=context.executed_commands,
            next_state_hash=context.next_state_hash,
            expected_state_hash=context.expected_state_hash,
        )
