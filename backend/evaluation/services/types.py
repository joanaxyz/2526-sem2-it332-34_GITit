from dataclasses import dataclass


@dataclass(frozen=True)
class EvaluationOutcome:
    result_category: str
    target_matched: bool
    passed_rules: tuple[dict, ...] = ()
    failed_rules: tuple[dict, ...] = ()
    summary: str = ""
