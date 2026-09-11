from curriculum.management.commands.seed_legacy_modules import (
    MODULE_1_LEVELS,
    required_case_details,
)
from curriculum.seed_data.spec_helpers import required_commit_message_details


def _module_one_cases():
    for level in MODULE_1_LEVELS:
        for tier in level["tiers"].values():
            yield from tier["cases"]


def test_every_module_one_clone_exposes_its_repository_url():
    checked = 0
    for case in _module_one_cases():
        if not any(command.startswith("git clone") for command in case["solution_commands"]):
            continue

        checked += 1
        url = case["initial_state"]["remote_fixtures"]["url"]
        assert {"label": "Repository URL", "value": url} in required_case_details(case)

    assert checked == 13


def test_every_module_one_evaluated_commit_message_is_exposed():
    checked = 0
    for case in _module_one_cases():
        expected = required_commit_message_details(
            case["solution_commands"],
            {"state_requirements": case["state_requirements"]},
        )
        if not expected:
            continue

        checked += 1
        assert all(detail in required_case_details(case) for detail in expected)

    assert checked > 20
