from simulator.services import RepositoryStateSimulator


def test_simulator_rejects_non_git_input_without_execution():
    state = {"commits": [], "branches": {"main": None}, "head": {"type": "branch", "name": "main"}}

    result = RepositoryStateSimulator().process(state, "powershell Remove-Item important.txt")

    assert result.processed is False
    assert result.state == state
    assert "Only simulated git commands" in result.output


def test_init_allows_pre_repository_first_commit_flow():
    simulator = RepositoryStateSimulator()
    state = {
        "repository_initialized": False,
        "commits": [],
        "branches": {"main": None},
        "head": {"type": "none", "name": None},
        "working_tree": {"README.md": "untracked"},
        "staging": {},
        "conflicts": [],
    }

    state = simulator.process(state, "git init").state
    state = simulator.process(state, "git add .").state
    result = simulator.process(state, 'git commit -m "starter snapshot"')

    assert result.processed is True
    assert result.state["repository_initialized"] is True
    assert result.state["branches"]["main"] == "c0"
    assert result.state["working_tree"] == {}


def test_pre_repository_git_syntax_errors_are_reported_before_not_a_repo():
    simulator = RepositoryStateSimulator()
    state = {
        "repository_initialized": False,
        "commits": [],
        "branches": {"main": None},
        "head": {"type": "none", "name": None},
        "working_tree": {"README.md": "untracked"},
        "staging": {},
        "conflicts": [],
    }

    result = simulator.process(state, "git status --wat")

    assert result.processed is False
    assert result.state == state
    assert "unknown option" in result.output


def test_clone_cannot_replace_an_initialized_repository():
    simulator = RepositoryStateSimulator()
    state = {
        "repository_initialized": False,
        "commits": [],
        "branches": {"main": None},
        "head": {"type": "none", "name": None},
        "working_tree": {"README.md": "untracked"},
        "staging": {},
        "conflicts": [],
    }

    initialized = simulator.process(state, "git init").state
    result = simulator.process(initialized, "git clone https://example.test/app.git app")

    assert result.processed is False
    assert result.state == initialized
    assert "only available before initialization" in result.output


def test_init_does_not_keep_pre_repository_remote_metadata():
    simulator = RepositoryStateSimulator()
    state = simulator.normalize_state(
        {
            "repository_initialized": False,
            "commits": [],
            "branches": {"main": None},
            "head": {"type": "none", "name": None},
            "working_tree": {},
            "staging": {},
            "conflicts": [],
            "remotes": {"origin": "https://example.test/app.git"},
            "remote_branches": {"origin/main": "r0"},
            "upstream_tracking": {"main": "origin/main"},
        }
    )

    result = simulator.process(state, "git init")

    assert result.processed is True
    assert result.state["remotes"] == {}
    assert result.state["remote_branches"] == {}
    assert result.state["upstream_tracking"] == {}


def test_remote_fetch_pull_and_push_update_remote_state():
    simulator = RepositoryStateSimulator()
    state = simulator.normalize_state(
        {
            "commits": [{"id": "c0", "message": "Base", "parents": []}],
            "branches": {"main": "c0"},
            "head": {"type": "branch", "name": "main"},
            "working_tree": {},
            "staging": {},
            "conflicts": [],
            "remotes": {"origin": "https://example.test/app.git"},
            "remote_branches": {"origin/main": "c1"},
            "upstream_tracking": {"main": "origin/main"},
        }
    )

    fetched = simulator.process(state, "git fetch origin").state
    pulled = simulator.process(fetched, "git pull").state
    pushed = simulator.process(pulled, "git push").state

    assert fetched["remote_tracking_updated"] is True
    assert pulled["branches"]["main"] == "c1"
    assert pushed["remote_branches"]["origin/main"] == pushed["branches"]["main"]


def test_restore_stash_revert_amend_and_reflog_are_simulated():
    simulator = RepositoryStateSimulator()
    state = simulator.normalize_state(
        {
            "commits": [
                {"id": "c0", "message": "Base", "parents": []},
                {"id": "c1", "message": "Bad auth change", "parents": ["c0"]},
            ],
            "branches": {"main": "c1", "feature/auth": "c1"},
            "head": {"type": "branch", "name": "main"},
            "working_tree": {"scratch.md": "modified", "auth.py": "modified"},
            "staging": {},
            "conflicts": [],
        }
    )

    state = simulator.process(state, "git restore scratch.md").state
    assert "scratch.md" not in state["working_tree"]

    state = simulator.process(state, "git stash").state
    assert state["working_tree"] == {}
    assert len(state["stash_stack"]) == 1

    state = simulator.process(state, "git switch feature/auth").state
    state = simulator.process(state, "git stash pop").state
    assert state["head"]["name"] == "feature/auth"
    assert "auth.py" in state["working_tree"]
    assert state["stash_stack"] == []

    state = simulator.process(state, "git add auth.py").state
    state = simulator.process(state, "git commit --amend").state
    assert "auth.py" in state["commits"][1]["files"]

    state = simulator.process(state, "git revert c1").state
    assert state["branches"]["feature/auth"] == "c2"
    assert simulator.process(state, "git reflog").processed is True
