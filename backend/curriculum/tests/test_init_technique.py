from types import SimpleNamespace

import pytest

from curriculum.services.techniques import (
    record_verified_techniques,
    required_techniques,
    technique_label,
    techniques_for_command,
)

UNINITIALIZED = {"repository_initialized": False}
TECHNIQUE = "init:initial-branch:main"


@pytest.mark.parametrize(
    "command",
    [
        "git init -b main",
        "git init --initial-branch main",
        "git init --initial-branch=main",
        "git init --quiet -b main .",
        "git init . -b main",
    ],
)
def test_explicit_initial_branch_syntax_earns_value_bound_evidence(command):
    assert techniques_for_command(command, previous_state=UNINITIALIZED) == {TECHNIQUE}


@pytest.mark.parametrize(
    "command",
    [
        "git init",
        "git init .",
        "git init -- -b main",
        "git init 'folder -b main'",
        "git init -b",
        "git init --initial-branch=",
        "git init --initial-branch --quiet",
        "git init 'unclosed",
        "git branch -m main",
    ],
)
def test_default_branch_and_option_like_operands_do_not_earn_evidence(command):
    assert techniques_for_command(command, previous_state=UNINITIALIZED) == set()


def test_initial_branch_evidence_requires_verified_creation_and_the_correct_value():
    assert techniques_for_command("git init -b main") == set()
    assert techniques_for_command("git init -b main", previous_state={}) == set()
    assert (
        techniques_for_command("git init -b main", previous_state={"repository_initialized": True})
        == set()
    )
    assert techniques_for_command("git init -b trunk", previous_state=UNINITIALIZED) == {
        "init:initial-branch:trunk"
    }
    assert techniques_for_command("git init -b Main", previous_state=UNINITIALIZED) == {
        "init:initial-branch:Main"
    }


def test_initial_branch_requirement_is_scoped_to_the_teaching_variant():
    assert required_techniques("init-easy-current-empty") == [TECHNIQUE]
    assert required_techniques("init-easy-plain-notes") == []
    assert required_techniques("init-easy-trunk-branch") == []
    assert technique_label(TECHNIQUE) == "git init -b main"


def test_initial_branch_evidence_requires_successful_verified_execution():
    run = SimpleNamespace(scoring_policy_version=2, verified_techniques=[])
    execution = SimpleNamespace(
        previous_state=UNINITIALIZED,
        state_mutated=False,
        result=SimpleNamespace(processed=True, normalized_command="git init -b main"),
    )
    record_verified_techniques(run, execution)
    assert run.verified_techniques == []
    execution.state_mutated = True
    execution.result.processed = False
    record_verified_techniques(run, execution)
    assert run.verified_techniques == []
    execution.result.processed = True
    record_verified_techniques(run, execution)
    assert run.verified_techniques == [TECHNIQUE]
