from dataclasses import dataclass, field
from typing import Any

from evaluation.compiler import CompiledEvaluationSpecCache, compile_evaluation_spec
from evaluation.engine import EvaluationEngine
from evaluation.services import EvaluationOutcome


@dataclass
class CompletionEvaluationContext:
    run: Any
    previous_state: dict
    next_state: dict
    executed_commands: list[str] = field(default_factory=list)
    next_state_hash: str | None = None
    expected_state_hash: str | None = None


class PracticeCompletionEvaluator:
    def evaluate(self, context: CompletionEvaluationContext) -> EvaluationOutcome:
        variant = context.run.variant
        raw_spec = getattr(variant, "evaluation_spec", None)
        variant_id = getattr(variant, "id", None)
        if raw_spec and variant_id is not None:
            # Cached compile keyed on the variant; the spec is recompiled only if
            # the variant is re-authored (new semantic_key).
            spec = CompiledEvaluationSpecCache().spec_for(
                key=("variant", variant_id, getattr(variant, "semantic_key", "") or ""),
                raw_spec=raw_spec,
            )
        elif raw_spec:
            spec = compile_evaluation_spec(raw_spec)
        else:
            # Quest-level fallback is rare and not keyed by a stable cache id, so
            # compile it directly.
            spec = compile_evaluation_spec(
                getattr(context.run.quest, "evaluation_spec", None)
            )
        return EvaluationEngine().evaluate(
            spec=spec,
            next_state=context.next_state,
            initial_state=getattr(context.run.variant, "initial_state", None),
            executed_commands=context.executed_commands,
            next_state_hash=context.next_state_hash,
            expected_state_hash=context.expected_state_hash,
        )
