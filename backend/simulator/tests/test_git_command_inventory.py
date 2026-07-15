from simulator.services import is_diagnostic_command


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
