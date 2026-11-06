from types import SimpleNamespace

import pytest

from curriculum.services.techniques import record_verified_techniques, techniques_for_command


@pytest.mark.parametrize(
    "command,expected",
    [
        ("git mergetool", {"mergetool"}),
        ("git push --force-with-lease origin feature/api", {"push:force-with-lease"}),
        ("git push --force-with-lease -u origin feature/api", {"push:force-with-lease"}),
        (
            "git push --force-with-lease=feature/api:c2 origin feature/api",
            {"push:force-with-lease"},
        ),
        ("git push --force origin feature/api", set()),
        ("git push -f --force-with-lease origin feature/api", set()),
        ("git push --force-with-lease --force origin feature/api", set()),
        ("git push origin -- --force-with-lease", set()),
    ],
)
def test_verified_operation_selects_the_actual_tool_or_guard(command, expected):
    assert techniques_for_command(command) == expected


@pytest.mark.parametrize(
    "command", ["git mergetool", "git push --force-with-lease origin feature/api"]
)
@pytest.mark.parametrize("processed,mutated", [(True, False), (False, True), (False, False)])
def test_failed_or_non_mutating_execution_never_earns_assessment_evidence(
    command, processed, mutated
):
    run = SimpleNamespace(scoring_policy_version=2, verified_techniques=[])
    execution = SimpleNamespace(
        previous_state={},
        state_mutated=mutated,
        result=SimpleNamespace(processed=processed, normalized_command=command),
    )
    record_verified_techniques(run, execution)
    assert run.verified_techniques == []


def test_forged_lease_metadata_does_not_override_the_submitted_force_command():
    run = SimpleNamespace(scoring_policy_version=2, verified_techniques=[])
    execution = SimpleNamespace(
        previous_state={"operation_metadata": {"force_with_lease": True}},
        next_state={"operation_metadata": {"force_with_lease": True}},
        state_mutated=True,
        result=SimpleNamespace(
            processed=True, normalized_command="git push --force origin feature/api"
        ),
    )
    record_verified_techniques(run, execution)
    assert run.verified_techniques == []
