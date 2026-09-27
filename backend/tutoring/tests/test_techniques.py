import pytest

from tutoring.services.forms import command_matches_form, command_uses_form, resolve_form
from tutoring.services.techniques import batch_command, techniques_in


def keys(command, state=None):
    return [technique.key for technique in techniques_in(command, state)]


@pytest.mark.parametrize(
    ("command", "expected"),
    [
        ("git add README.md app.py", ["several-paths"]),
        ("git add .", ["current-folder"]),
        ("git add '*.css'", ["path-pattern"]),
        ("git restore --staged -- a.txt b.txt", ["several-paths", "path-separator"]),
        ("git reset --hard HEAD~2", ["relative-commit"]),
        ("git revert HEAD^", ["relative-commit"]),
        ("git log main..feature", ["commit-range"]),
        ("git merge origin/main", ["remote-branch"]),
        ("git rebase @{u}", ["upstream"]),
        ("git restore --source=HEAD~1 app.py", ["relative-commit"]),
    ],
)
def test_detectors_read_the_command_shape(command, expected):
    assert keys(command) == expected


@pytest.mark.parametrize(
    "command",
    [
        "git add README.md",
        "git commit -m 'HEAD~2 fix, see main..dev'",  # message text is never an operand
        "git switch -c feature/login",  # a slash in a branch name is not a remote
        "git diff main...feature",  # symmetric difference is not a range
        "git add -u src",  # -u takes no value, so src stays a single path
    ],
)
def test_ordinary_commands_have_no_technique(command):
    assert keys(command) == []


def test_remote_branch_uses_the_repository_remotes():
    assert keys("git merge team/main", {"remotes": {"team": "https://example.test"}}) == ["remote-branch"]
    assert keys("git merge team/main") == []


def test_one_or_more_forms_match_and_are_only_used_with_several_operands():
    assert command_matches_form("git add a b", "git add <path>...")
    assert command_uses_form("git add a b", "git add <path>...")
    assert not command_uses_form("git add a", "git add <path>...")


def steps(*commands, edits=()):
    return [
        {
            "command": command,
            "diagnostic": command.split()[1] in {"status", "log"},
            "positions": [{}, {}] if index in edits else [{}],
        }
        for index, command in enumerate(commands)
    ]


def test_back_to_back_path_steps_become_one_command():
    route = steps("git add a.txt", "git status", "git add 'b c.txt'", "git commit -m x")
    assert batch_command(route, 0) == ("git add a.txt 'b c.txt'", 2)


@pytest.mark.parametrize(
    "route",
    [
        steps("git add a.txt", "git add -p b.txt"),  # different options
        steps("git add a.txt", "git add b.txt", edits={1}),  # an edit is needed first
        steps("git commit -m a", "git commit -m b"),  # not a path-only command
        steps("git add a.txt", "git add a.txt"),  # nothing new to add
        steps("git add -p a.txt", "git add -p b.txt"),  # interactive, one file at a time
    ],
)
def test_steps_that_cannot_merge_stay_separate(route):
    assert batch_command(route, 0) == (route[0]["command"], 0)


def test_uncatalogued_multi_operand_commands_get_a_one_or_more_shape(db):
    assert resolve_form("git rm a.txt b.txt").usage_form == "git rm <value>..."
