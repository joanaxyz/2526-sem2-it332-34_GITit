from typing import Any

from evaluation.types import CompletionPolicy, EvaluationSpec, ProcessRequirements

VALID_COMPLETION_MODES = {"rules", "state_hash", "rules_then_hash"}


def compile_evaluation_spec(raw_spec: dict[str, Any] | None) -> EvaluationSpec:
    """Compile authored evaluation data into the normalized evaluator contract."""
    raw_spec = dict(raw_spec or {})
    if not raw_spec:
        raise ValueError("missing evaluation_spec")
    state_requirements = raw_spec.get("state_requirements") or {}
    process = raw_spec.get("process_requirements") or {}
    policy = raw_spec.get("completion_policy") or {}
    return EvaluationSpec(
        state_requirements=dict(state_requirements),
        process_requirements=ProcessRequirements(
            required_commands=tuple(_string_list(process.get("required_commands"))),
            forbidden_commands=tuple(_string_list(process.get("forbidden_commands"))),
        ),
        completion_policy=CompletionPolicy(mode=_completion_mode(policy.get("mode"))),
    )


def _completion_mode(value: Any) -> str:
    mode = str(value or "rules")
    if mode not in VALID_COMPLETION_MODES:
        raise ValueError(f"unsupported completion policy mode: {mode}")
    return mode


def _string_list(value: Any) -> list[str]:
    if value in (None, ""):
        return []
    values = value if isinstance(value, list) else [value]
    return [str(item).strip() for item in values if str(item).strip()]
