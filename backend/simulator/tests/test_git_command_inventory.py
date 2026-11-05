import pytest

from common.git.client_command_execution import ClientCommandExecutionService
from simulator.services import is_diagnostic_command
from testing.frontend_execution import frontend_execution_payload


def test_unsupported_inventory_commands_are_not_backend_diagnostics():
    commands = [
        "git clean -f",
        "git mv README.md docs/README.md",
        "git update-ref refs/heads/release HEAD",
        "git credential fill",
        "git cli",
    ]

    assert not any(is_diagnostic_command(command) for command in commands)


def test_supported_read_only_commands_stay_backend_diagnostics():
    commands = [
        "git status",
        "git log --oneline",
        "git show HEAD",
        "git diff",
        "git merge-base main feature",
        "git fsck --full",
        "git worktree list",
    ]

    assert all(is_diagnostic_command(command) for command in commands)


def test_unknown_git_subcommands_still_count_as_unknown():
    assert not is_diagnostic_command("git frobnicate")


@pytest.mark.parametrize("command", [
    "git -h", "git commit -h", "git switch --help", "git config -h",
    "git help switch", "git config user.name", "git config --global user.name",
])
def test_help_and_config_queries_are_accepted_as_read_only(command):
    state = {"repository_initialized": True, "branches": {"main": None}}
    service = ClientCommandExecutionService()
    execution = service.from_payload(
        repository_state=state,
        command=command,
        execution=frontend_execution_payload(command, state, diagnostic=True),
    )
    assert is_diagnostic_command(command)
    assert execution.increment == 0
    assert not execution.state_mutated
    assert execution.next_state == service.state_tools.normalize_state(state)


@pytest.mark.parametrize("command", [
    'git commit -m "--help"', 'git commit --message "-h"',
    'git commit -am "--help"', 'git tag -m "--help" v1',
    'git stash push -m "--help"', "git add -- -h",
    'git config user.name Learner',
])
def test_help_looking_values_and_paths_do_not_bypass_mutation_checks(command):
    assert not is_diagnostic_command(command)
