from types import SimpleNamespace

import pytest

from common.constants import RESULT_TARGET_MATCHED, RESULT_TARGET_NOT_YET_MATCHED
from evaluation.compiler import compile_evaluation_spec
from evaluation.completion import CompletionEvaluationContext, PracticeCompletionEvaluator
from evaluation.engine import EvaluationEngine


def test_rules_mode_does_not_inject_required_commands():
    spec = compile_evaluation_spec(
        {
            "state_requirements": {"repository_initialized": True},
            "completion_policy": {"mode": "rules"},
        }
    )
    outcome = EvaluationEngine().evaluate(
        spec=spec,
        next_state={"repository_initialized": True},
        executed_commands=[],
    )
    assert outcome.result_category == RESULT_TARGET_MATCHED


def test_process_requirements_are_enforced_when_explicit():
    spec = compile_evaluation_spec(
        {
            "state_requirements": {"repository_initialized": True},
            "process_requirements": {"required_commands": ["git init"]},
            "completion_policy": {"mode": "rules"},
        }
    )
    outcome = EvaluationEngine().evaluate(
        spec=spec,
        next_state={"repository_initialized": True},
        executed_commands=["git status"],
    )
    assert outcome.result_category == RESULT_TARGET_NOT_YET_MATCHED


def test_required_command_sequence_preserves_order_and_multiplicity():
    spec = compile_evaluation_spec(
        {
            "state_requirements": {
                "rules": [
                    {
                        "type": "required_command_sequence",
                        "commands": [
                            "git status --porcelain",
                            "git cherry-pick --abort",
                            "git status",
                        ],
                    }
                ]
            },
            "completion_policy": {"mode": "rules"},
        }
    )

    incomplete = EvaluationEngine().evaluate(
        spec=spec,
        next_state={},
        executed_commands=["git status --porcelain", "git cherry-pick --abort"],
    )
    wrong_order = EvaluationEngine().evaluate(
        spec=spec,
        next_state={},
        executed_commands=[
            "git status",
            "git cherry-pick --abort",
            "git status --porcelain",
        ],
    )
    complete_with_extra = EvaluationEngine().evaluate(
        spec=spec,
        next_state={},
        executed_commands=[
            "git status --porcelain",
            "git log --oneline",
            "git cherry-pick --abort",
            "git status",
        ],
    )

    assert incomplete.result_category == RESULT_TARGET_NOT_YET_MATCHED
    assert wrong_order.result_category == RESULT_TARGET_NOT_YET_MATCHED
    assert complete_with_extra.result_category == RESULT_TARGET_MATCHED


def test_state_hash_completion_policy_uses_hashes():
    spec = compile_evaluation_spec({"completion_policy": {"mode": "state_hash"}})
    outcome = EvaluationEngine().evaluate(
        spec=spec,
        next_state={},
        next_state_hash="abc",
        expected_state_hash="abc",
    )
    assert outcome.result_category == RESULT_TARGET_MATCHED


def test_completion_evaluator_reads_normalized_variant_spec():
    run = SimpleNamespace(
        variant=SimpleNamespace(
            evaluation_spec={
                "state_requirements": {"repository_initialized": True},
                "completion_policy": {"mode": "rules"},
            },
            initial_state={"repository_initialized": False},
        ),
        level=SimpleNamespace(evaluation_spec={}),
    )
    outcome = PracticeCompletionEvaluator().evaluate(
        CompletionEvaluationContext(
            run=run,
            previous_state={"repository_initialized": False},
            next_state={"repository_initialized": True},
            executed_commands=[],
        )
    )
    assert outcome.result_category == RESULT_TARGET_MATCHED


def test_completion_evaluator_rejects_missing_evaluation_spec():
    run = SimpleNamespace(
        variant=SimpleNamespace(evaluation_spec={}, initial_state={}),
        level=SimpleNamespace(evaluation_spec={}),
    )
    with pytest.raises(ValueError, match="missing evaluation_spec"):
        PracticeCompletionEvaluator().evaluate(
            CompletionEvaluationContext(run=run, previous_state={}, next_state={})
        )
