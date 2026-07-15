"""Objective-checklist soundness gate for authored adventure levels.

A learner-facing objective check is only meaningful when it is *false on the
variant's initial state* (otherwise it shows as already-done before the learner
acts - a premature pass) and *true on the variant's target state* (otherwise it
can never tick off, even when the problem is solved). This mirrors the manual
verification that caught three premature-pass bugs in Chapter 1, and protects
every level flipped to the modular ``workflow=True`` checklist.

Read-only inspection levels intentionally keep a command-based check
(``workflow=False``): those are exercised here too and pass because their
requirement is satisfied by the executed solution, not by a state change.
"""

import pytest

from curriculum.seed_data.adventure_levels import ADVENTURE_LEVELS
from evaluation.checklist import ObjectiveChecklistEvaluator


def _variant_cases():
    for level in ADVENTURE_LEVELS:
        for variant in level.get("variants") or []:
            yield level, variant


@pytest.mark.parametrize(
    "level,variant",
    list(_variant_cases()),
    ids=[f"{lvl['slug']}::{v['case_id']}" for lvl, v in _variant_cases()],
)
def test_objective_checks_are_false_on_initial_and_true_on_target(level, variant):
    checks = level.get("objective_checks") or []
    assert checks, f"{level['slug']} has no objective checks."

    initial = variant.get("initial_state_template") or {}
    target = variant.get("target_state_template") or {}
    solution = variant.get("solution_commands_template") or []
    assert target, f"{level['slug']}::{variant['case_id']} has no target state."

    evaluator = ObjectiveChecklistEvaluator()
    on_initial = evaluator.evaluate(checks, state=initial, initial_state=initial, executed_commands=[])
    on_target = evaluator.evaluate(
        checks, state=target, initial_state=initial, executed_commands=solution
    )

    for initial_row, target_row in zip(on_initial, on_target, strict=True):
        label = initial_row["label"]
        assert not initial_row["satisfied"], (
            f"Premature pass: {level['slug']}::{variant['case_id']} objective "
            f"{label!r} is already satisfied on the initial state."
        )
        assert target_row["satisfied"], (
            f"Never true: {level['slug']}::{variant['case_id']} objective "
            f"{label!r} is not satisfied on the solved target state."
        )
