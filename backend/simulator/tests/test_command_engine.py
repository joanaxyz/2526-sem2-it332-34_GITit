from simulator.command_engine import SimulatedGitCommandEngine


def test_simulated_command_engine_returns_git_like_status_text_without_system_git():
    state = {
        "commits": [],
        "branches": {"main": None},
        "head": {"type": "branch", "name": "main"},
        "working_tree": {"README.md": "untracked"},
        "staging": {},
        "conflicts": [],
    }

    result = SimulatedGitCommandEngine().process(state, "git status")

    assert result.processed is True
    assert result.exit_code == 0
    assert "On branch main" in result.output
    assert "Untracked files:" in result.output
    assert "README.md" in result.output
    assert "Only simulated" not in result.output


def test_simulated_command_engine_returns_git_like_errors_for_invalid_options():
    state = {
        "commits": [],
        "branches": {"main": None},
        "head": {"type": "branch", "name": "main"},
        "working_tree": {},
        "staging": {},
        "conflicts": [],
    }

    result = SimulatedGitCommandEngine().process(state, "git status --wat")

    assert result.processed is False
    assert result.exit_code == 129
    assert "error: unknown option" in result.output


def test_simulated_command_engine_clones_without_system_git_or_network():
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

    result = SimulatedGitCommandEngine(timeout_seconds=5).process(
        state,
        "git clone https://example.test/app.git app",
    )

    assert result.processed is True
    assert result.exit_code == 0
    assert "Cloning into 'app'" in result.output
    assert "example.test" not in result.output


def test_mutate_in_place_reuses_state_object_for_successful_command():
    state = {
        "repository_initialized": True,
        "commits": [{"id": "c0", "message": "Base", "parents": []}],
        "branches": {"main": "c0"},
        "head": {"type": "branch", "name": "main"},
        "working_tree": {"README.md": "untracked"},
        "staging": {},
        "conflicts": [],
    }
    state_id = id(state)

    result = SimulatedGitCommandEngine().process(state, "git status", mutate_in_place=True)

    assert result.processed is True
    assert id(result.state) == state_id
