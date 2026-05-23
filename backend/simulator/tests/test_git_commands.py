import pytest

from simulator.command_engine import GitCommandEngine
from simulator.git_commands import (
    GitCommandParseError,
    GitCommandParser,
    GitCommandRegistry,
    NonGitCommandError,
)
from simulator.services import RepositoryStateSimulator


def test_parser_handles_quoted_commit_message_and_normalizes_alias():
    parsed = GitCommandParser().parse('git ci --amend -m "Add login form"')

    assert parsed.subcommand == "commit"
    assert parsed.original_subcommand == "ci"
    assert parsed.message == "Add login form"
    assert parsed.executor_args == ["--amend", "-m", "Add login form"]
    assert parsed.normalized_text == "git commit --amend -m 'Add login form'"


def test_parser_allows_amend_no_edit_without_turning_plain_commit_into_amend():
    parser = GitCommandParser()
    registry = GitCommandRegistry()

    amend = parser.parse("git commit --amend --no-edit")
    assert amend.has_option("--amend")
    assert amend.has_option("--no-edit")
    assert amend.executor_args == ["--amend"]

    plain_no_edit = parser.parse("git commit --no-edit")
    assert registry.require("commit").validate(plain_no_edit) == (
        "fatal: options '--no-edit' and '--amend' must be used together"
    )


def test_parser_rejects_non_git_commands():
    with pytest.raises(NonGitCommandError) as exc:
        GitCommandParser().parse("python cleanup.py")

    assert exc.value.exit_code == 127
    assert "python: command not found" in str(exc.value)


def test_parser_reports_invalid_quoting():
    with pytest.raises(GitCommandParseError):
        GitCommandParser().parse('git commit -m "unfinished')


def test_registry_rejects_unsupported_flags_and_classifies_diagnostics():
    parser = GitCommandParser()
    registry = GitCommandRegistry()

    bad = parser.parse("git status --wat")
    assert registry.require("status").validate(bad) == "error: unknown option `--wat`."

    assert registry.is_diagnostic(parser.parse("git status"))
    assert registry.is_diagnostic(parser.parse("git log --oneline --graph --all"))
    assert registry.is_diagnostic(parser.parse("git branch -v"))
    assert registry.is_diagnostic(parser.parse("git remote -v"))
    assert not registry.is_diagnostic(parser.parse("git branch -d stale"))


def test_engine_blocks_shell_and_unsupported_git_without_mutation():
    state = {"commits": [], "branches": {"main": None}, "head": {"type": "branch", "name": "main"}}
    engine = GitCommandEngine()

    shell = engine.process(state, "powershell Remove-Item important.txt")
    unsupported = engine.process(state, "git rebase main")

    assert shell.exit_code == 127
    assert shell.state == state
    assert unsupported.exit_code == 129
    assert "is not a git command" in unsupported.output
    assert unsupported.state == state


def test_engine_mutates_state_for_supported_commit_with_quoted_message():
    state = {
        "commits": [{"id": "c0", "message": "Base", "parents": [], "tree": {"README.md": "v1"}}],
        "branches": {"main": "c0"},
        "head": {"type": "branch", "name": "main"},
        "working_tree": {"src/login.tsx": "login-form-v1"},
        "staging": {},
    }
    engine = GitCommandEngine()

    staged = engine.process(state, "git add src/login.tsx").state
    committed = engine.process(staged, 'git commit -m "Add login form"')

    assert committed.processed is True
    assert committed.state["commits"][-1]["message"] == "Add login form"
    assert committed.state["branches"]["main"] == "c1"


def test_engine_marks_diagnostics_non_mutating():
    state = {
        "commits": [{"id": "c0", "message": "Base", "parents": [], "tree": {"README.md": "v1"}}],
        "branches": {"main": "c0"},
        "head": {"type": "branch", "name": "main"},
        "working_tree": {"README.md": "v2"},
        "staging": {},
    }

    result = GitCommandEngine().process(state, "git diff --staged")

    assert result.processed is True
    assert result.diagnostic is True
    assert result.state == RepositoryStateSimulator().normalize_state(state)
