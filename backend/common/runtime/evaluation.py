"""Small helpers shared by challenge/adventure runtime evaluation."""


def rule_counts(outcome) -> tuple[int, int]:
    passed = len(getattr(outcome, "passed_rules", ()) or ())
    failed = len(getattr(outcome, "failed_rules", ()) or ())
    return passed, max(1, passed + failed)
