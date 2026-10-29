from types import SimpleNamespace

import pytest
from adventures.scoring import stars
from curriculum.services.techniques import record_verified_techniques
from evaluation.completion import CompletionEvaluationContext, PracticeCompletionEvaluator
from evaluation.services.rule_builders import command_matches
from testing.frontend_execution import frontend_execution_payload

from common.constants import COMMAND_COUNTED
from common.git.client_command_execution import ClientCommandExecutionService
from common.runtime.scoring_policy import command_comparison, thresholds
from common.tests.test_star_grading import _submit
from common.tests.test_star_grading import grading_lane as lane_fixture

# Register the shared parametrized fixture without shadowing its import.
grading_lane = lane_fixture


@pytest.mark.parametrize("count,expected", [(0, 3), (4, 3), (5, 2), (8, 2), (9, 1), (12, 1)])
@pytest.mark.parametrize("retries", [0, 1, 5, 99])
def test_three_bands_are_independent_of_retries(count, expected, retries):
    assert (
        stars(
            solved=True,
            counted_commands=count,
            budget=4,
            generous_budget=8,
            retry_count=retries,
            policy_version=2,
        )
        == expected
    )
    assert (
        stars(
            solved=False,
            counted_commands=count,
            budget=4,
            generous_budget=8,
            retry_count=retries,
            policy_version=2,
        )
        == 0
    )


def test_target_calibration_and_override_validation():
    assert thresholds(4, 12) == (4, 8, 12)
    assert thresholds(4, 4) == (4, 5, 6)
    assert thresholds(4, 13) == (4, 9, 13)
    assert thresholds(4, 12, 7) == (4, 7, 12)
    for generous in (4, 12):
        with pytest.raises(ValueError):
            thresholds(4, 12, generous)


@pytest.mark.parametrize("count,expected", [(0, "fewer"), (1, "equal"), (2, "more")])
def test_comparison_uses_snapshot_and_hides_unsolved_results(count, expected):
    run = SimpleNamespace(
        status="completed", counted_action_total=count, example_counted_commands=1
    )
    assert command_comparison(run) == {
        "learner_count": count,
        "example_count": 1,
        "relation": expected,
    }
    run.status = "failed"
    assert command_comparison(run) is None


def test_failed_inspection_costs_a_command_under_v2(grading_lane):
    run = grading_lane.run
    execution = ClientCommandExecutionService().from_payload(
        repository_state=run.repository_state,
        command="git status",
        execution=frontend_execution_payload(
            "git status", run.repository_state, diagnostic=True, exit_code=128
        ),
        scoring_policy_version=2,
    )
    assert execution.classification == COMMAND_COUNTED
    assert execution.increment == 1


def test_last_allowed_command_can_complete_for_one_star(grading_lane):
    context = grading_lane
    _submit(context, context.run, "git nope")
    _submit(context, context.run, "git nope")
    result = _submit(context, context.run, "git add README.md")["run"]
    assert result["status"] == "completed"
    assert result["stars"] == 1
    assert result["command_comparison"] == {
        "learner_count": 3,
        "example_count": 1,
        "relation": "more",
    }


def test_unsolved_limit_fails_but_next_attempt_can_earn_three(grading_lane):
    context = grading_lane
    for _ in range(3):
        _submit(context, context.run, "git nope")
    assert context.run.status == "failed"
    retry = context.start(context.run)
    assert retry.scoring_policy_version == 2
    assert retry.min_counted_commands < retry.generous_counted_commands < retry.max_counted_commands
    _submit(context, retry, "git add README.md")
    assert retry.stars == 3


def test_technique_requires_verified_execution_not_typed_text():
    state = {
        "repository_initialized": True,
        "commits": [],
        "branches": {"main": None},
        "head": {"type": "branch", "name": "main"},
        "staging": {},
        "working_tree": {},
        "conflicts": [],
    }
    variant = SimpleNamespace(
        initial_state=state,
        evaluation_spec={
            "state_requirements": {"head_branch": "main"},
            "completion_policy": {"mode": "rules"},
        },
    )
    context = CompletionEvaluationContext(
        variant=variant,
        next_state=state,
        required_techniques=["rebase"],
        executed_commands=["git rebase main"],
    )
    assert not PracticeCompletionEvaluator().evaluate(context).target_matched
    context.verified_techniques = ["rebase"]
    assert PracticeCompletionEvaluator().evaluate(context).target_matched


def test_noop_and_failed_commands_do_not_produce_technique_evidence():
    run = SimpleNamespace(scoring_policy_version=2, verified_techniques=[])
    execution = SimpleNamespace(
        state_mutated=False,
        result=SimpleNamespace(processed=True, normalized_command="git rebase main"),
    )
    record_verified_techniques(run, execution)
    assert run.verified_techniques == []
    execution.state_mutated = True
    execution.result.processed = False
    record_verified_techniques(run, execution)
    assert run.verified_techniques == []
    execution.result.processed = True
    record_verified_techniques(run, execution)
    assert run.verified_techniques == ["rebase"]


def test_command_matcher_preserves_case_sensitive_arguments():
    assert command_matches("git checkout -b Feature", "git switch -c Feature")
    assert not command_matches("git switch -c feature", "git switch -c Feature")
    assert not command_matches("git add README.md.bak", "git add README.md")


def test_commit_message_cannot_forge_amend_evidence():
    from curriculum.services.techniques import techniques_for_command

    assert techniques_for_command("git commit -m '--amend'") == set()
    assert techniques_for_command("git commit --message=--amend") == set()
    assert techniques_for_command("git commit --amend -m 'Fix a typo'") == {"amend"}
