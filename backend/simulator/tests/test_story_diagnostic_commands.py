from simulator.services import is_diagnostic_command


def test_new_story_read_only_commands_are_backend_diagnostics():
    commands = [
        "git bisect run test-suite",
        "git bisect log",
        "git rerere status",
        "git rerere diff",
        "git worktree list",
        "git sparse-checkout list",
        "git submodule status",
        "git config --get user.name",
        "git config --list",
        "git config -l",
    ]
    assert all(is_diagnostic_command(command) for command in commands)


def test_mutating_future_forms_are_not_misclassified_as_diagnostics():
    commands = [
        "git bisect start",
        "git worktree add ../hotfix hotfix",
        "git sparse-checkout set src",
        "git submodule add https://example.test/ui.git vendor/ui",
        "git config --global user.name Contributor A",
    ]
    assert not any(is_diagnostic_command(command) for command in commands)
