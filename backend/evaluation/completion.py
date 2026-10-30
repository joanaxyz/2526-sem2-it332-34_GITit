from dataclasses import dataclass, field
from typing import Any

from evaluation.compiler import CompiledEvaluationSpecCache, compile_evaluation_spec
from evaluation.engine import EvaluationEngine
from evaluation.services import EvaluationOutcome


@dataclass
class CompletionEvaluationContext:
    variant: Any
    next_state: dict
    level_evaluation_spec: dict | None = None
    executed_commands: list[str] = field(default_factory=list)
    next_state_hash: str | None = None
    expected_state_hash: str | None = None
    next_state_already_normalized: bool = False
    initial_state_already_normalized: bool = False
    required_techniques: list[str] = field(default_factory=list)
    verified_techniques: list[str] = field(default_factory=list)


class PracticeCompletionEvaluator:
    def evaluate(self, context: CompletionEvaluationContext) -> EvaluationOutcome:
        variant = context.variant
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
            # Level fallback is rare and not keyed by a stable cache id, so
            # compile it directly.
            spec = compile_evaluation_spec(context.level_evaluation_spec)
        outcome = EvaluationEngine().evaluate(
            spec=spec,
            next_state=context.next_state,
            initial_state=getattr(variant, "initial_state", None),
            executed_commands=context.executed_commands,
            next_state_hash=context.next_state_hash,
            expected_state_hash=context.expected_state_hash,
            next_state_already_normalized=context.next_state_already_normalized,
            initial_state_already_normalized=context.initial_state_already_normalized,
        )

        if not context.required_techniques:
            return outcome
        from common.constants import RESULT_TARGET_MATCHED, RESULT_TARGET_NOT_YET_MATCHED
        from curriculum.services.techniques import technique_label

        missing = sorted(set(context.required_techniques) - set(context.verified_techniques))
        passed = tuple(
            {
                "type": "required_technique",
                "rule": {"technique": t},
                "reason": "Technique verified.",
            }
            for t in context.required_techniques
            if t not in missing
        )
        failed = tuple(
            {
                "type": "required_technique",
                "rule": {"technique": t},
                "reason": f"Use the required technique: {technique_label(t)}.",
            }
            for t in missing
        )
        matched = outcome.target_matched and not missing
        return EvaluationOutcome(
            result_category=RESULT_TARGET_MATCHED if matched else RESULT_TARGET_NOT_YET_MATCHED,
            target_matched=matched,
            passed_rules=outcome.passed_rules + passed,
            failed_rules=outcome.failed_rules + failed,
            summary=outcome.summary
            if not missing
            else "Required technique has not been demonstrated.",
        )
