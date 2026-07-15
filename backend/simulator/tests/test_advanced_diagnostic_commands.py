from simulator.services import is_diagnostic_command

ADVANCED_DIAGNOSTICS = [
    "git shortlog -sn",
    "git rev-parse HEAD",
    "git blame README.md",
    "git grep app HEAD",
    "git describe --tags",
    "git range-diff main~1..main main~1..main",
    "git merge-tree release main",
    "git verify-commit HEAD",
    "git verify-tag v1.0.0",
    "git fsck --full",
    "git count-objects -vH",
    "git cat-file -p HEAD",
    "git ls-tree HEAD",
    "git show-ref",
    "git for-each-ref",
    "git symbolic-ref HEAD",
]


def test_advanced_read_only_commands_are_backend_classified_as_diagnostic():
    assert all(is_diagnostic_command(command) for command in ADVANCED_DIAGNOSTICS)
