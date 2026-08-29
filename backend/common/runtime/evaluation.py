"""Small helpers shared by challenge/adventure runtime evaluation."""

import json
from collections import Counter


def rule_counts(outcome) -> tuple[int, int]:
    passed = len(getattr(outcome, "passed_rules", ()) or ())
    failed = len(getattr(outcome, "failed_rules", ()) or ())
    return passed, max(1, passed + failed)


def battle_rule_counts(outcome, initial_outcome) -> tuple[int, int]:
    """Count objective progress without rewarding rules true at wave start.

    Final-state contracts often contain invariants such as ``staging_empty``.
    Those are already true before a workflow starts, then temporarily become
    false during a correct ``git add`` step. Raw passed-rule totals therefore
    make that step look like zero progress because one new command rule passes
    while the initial invariant switches off.

    Battle HP should represent progress earned after the initial state, so
    subtract the multiset of initially-passing rules from both the current
    passed set and the total rule set.
    """

    initial_passed = _rule_counter(getattr(initial_outcome, "passed_rules", ()) or ())
    passed = _rule_counter(getattr(outcome, "passed_rules", ()) or ())
    failed = _rule_counter(getattr(outcome, "failed_rules", ()) or ())
    eligible_passed = passed - initial_passed
    eligible_total = (passed + failed) - initial_passed
    return sum(eligible_passed.values()), max(1, sum(eligible_total.values()))


def _rule_counter(details) -> Counter[str]:
    return Counter(
        json.dumps(detail.get("rule", {}), sort_keys=True, separators=(",", ":"))
        for detail in details
    )
