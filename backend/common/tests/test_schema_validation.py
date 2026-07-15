import pytest

from common.exceptions import BadRequest
from common.git.command_outcomes import command_outcome_payload
from common.schemas.schema_validation import (
    SchemaValidationError,
    validate_command_outcome_payload,
    validate_evaluation_spec_payload,
    validate_repository_state_payload,
)
from evaluation.compiler import compile_evaluation_spec


def test_repository_state_validator_accepts_minimal_state():
    assert validate_repository_state_payload({"working_tree": {"README.md": "draft"}})["working_tree"]


def test_repository_state_validator_accepts_uninitialized_head():
    payload = validate_repository_state_payload({"head": {"type": "none"}})
    assert payload["head"]["type"] == "none"


@pytest.mark.parametrize(
    "payload, message",
    [
        ([], "repository_state must be an object"),
        ({"branches": []}, "repository_state.branches must be an object"),
        ({"commits": {}}, "repository_state.commits must be a list"),
        ({"commits": [{"id": "c0"}, {"id": "c0"}]}, "duplicate commit id"),
        ({"head": {"type": "floating"}}, "repository_state.head.type"),
        ({"conflicts": ["README.md", 7]}, r"repository_state.conflicts\[1\]"),
    ],
)
def test_repository_state_validator_rejects_bad_shapes(payload, message):
    with pytest.raises(BadRequest, match=message):
        validate_repository_state_payload(payload)


def test_command_outcome_helper_returns_valid_payload():
    payload = command_outcome_payload(
        processed=True,
        counted=True,
        solved=False,
        failed=False,
        command_family="add",
        previous_rules_passing=1,
        rules_passing=2,
        total_rules=3,
        max_counted_commands=4,
        counted_command_count=2,
    )
    assert validate_command_outcome_payload(payload) is payload
    assert payload["rules_delta"] == 1
    assert payload["remaining_counted_commands"] == 2


@pytest.mark.parametrize(
    "payload, message",
    [
        ({}, "missing required field"),
        (
            {
                "processed": True,
                "counted": True,
                "solved": False,
                "failed": False,
                "command_family": "add",
                "previous_rules_passing": 2,
                "rules_passing": 1,
                "rules_delta": 99,
                "total_rules": 3,
                "max_counted_commands": 4,
                "counted_command_count": 1,
                "remaining_counted_commands": 3,
            },
            "rules_delta is inconsistent",
        ),
        (
            {
                "processed": True,
                "counted": True,
                "solved": False,
                "failed": False,
                "command_family": "add",
                "previous_rules_passing": 0,
                "rules_passing": 4,
                "rules_delta": 4,
                "total_rules": 3,
                "max_counted_commands": 4,
                "counted_command_count": 1,
                "remaining_counted_commands": 3,
            },
            "rules_passing cannot exceed total_rules",
        ),
    ],
)
def test_command_outcome_validator_rejects_inconsistent_payloads(payload, message):
    with pytest.raises(SchemaValidationError, match=message):
        validate_command_outcome_payload(payload)


def test_evaluation_spec_validator_accepts_current_contract():
    spec = validate_evaluation_spec_payload(
        {
            "state_requirements": {"repository_initialized": True},
            "process_requirements": {"required_commands": ["git init"]},
            "completion_policy": {"mode": "rules_then_hash"},
        }
    )
    assert spec["completion_policy"]["mode"] == "rules_then_hash"


@pytest.mark.parametrize(
    "payload, message",
    [
        ([], "evaluation_spec must be an object"),
        ({"state_requirements": []}, "state_requirements must be an object"),
        ({"process_requirements": []}, "process_requirements must be an object"),
        ({"process_requirements": {"required_commands": ["git init", 3]}}, r"required_commands\[1\]"),
        ({"completion_policy": {"mode": "magic"}}, "unsupported completion policy mode"),
    ],
)
def test_evaluation_spec_validator_rejects_bad_shapes(payload, message):
    with pytest.raises(SchemaValidationError, match=message):
        validate_evaluation_spec_payload(payload)


def test_compile_evaluation_spec_uses_validator():
    with pytest.raises(SchemaValidationError, match="state_requirements must be an object"):
        compile_evaluation_spec({"state_requirements": []})
