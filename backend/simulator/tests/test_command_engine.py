from simulator.command_engine import Pygit2GitCommandEngine


def test_pygit2_command_engine_returns_real_git_status_text():
    state = {
        "commits": [],
        "branches": {"main": None},
        "head": {"type": "branch", "name": "main"},
        "working_tree": {"README.md": "untracked"},
        "staging": {},
        "conflicts": [],
    }

    result = Pygit2GitCommandEngine().process(state, "git status")

    assert result.processed is True
    assert result.exit_code == 0
    assert "On branch main" in result.output
    assert "Untracked files:" in result.output
    assert "README.md" in result.output
    assert "Only simulated" not in result.output


def test_pygit2_command_engine_keeps_real_git_errors_for_invalid_options():
    state = {
        "commits": [],
        "branches": {"main": None},
        "head": {"type": "branch", "name": "main"},
        "working_tree": {},
        "staging": {},
        "conflicts": [],
    }

    result = Pygit2GitCommandEngine().process(state, "git status --wat")

    assert result.processed is False
    assert result.exit_code == 129
    assert "error: unknown option" in result.output
    assert "usage: git status" in result.output


def test_pygit2_command_engine_uses_local_remote_for_clone_without_network():
    state = {
        "repository_initialized": False,
        "commits": [],
        "branches": {"main": None},
        "head": {"type": "none", "name": None},
        "working_tree": {},
        "staging": {},
        "conflicts": [],
        "remote_branches": {"origin/main": "r0"},
    }

    result = Pygit2GitCommandEngine(timeout_seconds=5).process(
        state,
        "git clone https://example.test/app.git app",
    )

    assert result.processed is True
    assert result.exit_code == 0
    assert "Cloning into 'app'" in result.output
    assert "example.test" not in result.output
