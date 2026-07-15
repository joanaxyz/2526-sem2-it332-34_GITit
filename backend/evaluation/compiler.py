from collections import OrderedDict
from typing import Any

from common.schemas.schema_validation import validate_evaluation_spec_payload
from evaluation.types import CompletionPolicy, EvaluationSpec, ProcessRequirements

VALID_COMPLETION_MODES = {"rules", "state_hash", "rules_then_hash"}


class CompiledEvaluationSpecCache:
    """Compile authored evaluation specs once per variant/problem.

    The compiled EvaluationSpec is an immutable dataclass derived purely from
    authored JSON, and the evaluator only reads it (``as_rule_payload`` returns a
    fresh shallow copy each call), so it is safe to memoize across requests. The
    key mirrors VariantTargetStateHashCache (``id`` + ``semantic_key``) so
    re-authoring transparently recompiles; any miss falls back to a fresh compile.
    """

    _cache: "OrderedDict[tuple, EvaluationSpec]" = OrderedDict()
    _max_entries = 512

    def spec_for(self, *, key: tuple, raw_spec: dict[str, Any] | None) -> EvaluationSpec:
        cached = self._cache.get(key)
        if cached is not None:
            self._cache.move_to_end(key)
            return cached
        spec = compile_evaluation_spec(raw_spec)
        self._cache[key] = spec
        self._cache.move_to_end(key)
        while len(self._cache) > self._max_entries:
            self._cache.popitem(last=False)
        return spec


def compile_evaluation_spec(raw_spec: dict[str, Any] | None) -> EvaluationSpec:
    """Compile authored evaluation data into the normalized evaluator contract."""
    if raw_spec in (None, ""):
        raise ValueError("missing evaluation_spec")
    validate_evaluation_spec_payload(raw_spec)
    raw_spec = dict(raw_spec)
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
