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
    assert result.state["commits"][0]["tree"]["README.md"] == "untracked"
    assert result.state["commits"][0]["changes"]["README.md"]["change_type"] == "added"


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


def test_init_directory_records_operation_metadata():
    simulator = RepositoryStateSimulator()
    state = {
        "repository_initialized": False,
        "commits": [],
        "branches": {},
        "head": {"type": "none"},
        "working_tree": {},
        "staging": {},
    }

    named = simulator.process(state, "git init research-log").state
    current = simulator.process(state, "git init").state

    assert named["operation_metadata"]["last_init_directory"] == "research-log"
    assert named["operation_metadata"]["last_init_current_directory"] is False
    assert "last_init_directory" not in current["operation_metadata"]
    assert current["operation_metadata"]["last_init_current_directory"] is True


def test_clone_records_destination_and_materializes_remote_fixture_tree():
    simulator = RepositoryStateSimulator()
    state = simulator.normalize_state(
        {
            "repository_initialized": False,
            "commits": [],
            "branches": {},
            "head": {"type": "none"},
            "working_tree": {},
            "staging": {},
            "remote_fixtures": {
                "origin/main": "r10",
                "commits": [
                    {
                        "id": "r10",
                        "message": "Create docs portal starter",
                        "parents": [],
                        "tree": {
                            "README.md": "docs-readme-v1",
                            "docs/intro.md": "docs-intro-v1",
                        },
                    }
                ],
            },
        }
    )

    result = simulator.process(state, "git clone https://example.test/training/docs-portal.git docs-portal")

    assert result.processed is True
    assert result.state["operation_metadata"]["last_clone_url"] == "https://example.test/training/docs-portal.git"
    assert result.state["operation_metadata"]["last_clone_destination"] == "docs-portal"
    assert result.state["branches"]["main"] == "r10"
    assert result.state["remote_branches"]["origin/main"] == "r10"
    assert result.state["upstream_tracking"]["main"] == "origin/main"
    assert result.state["commits"][0]["message"] == "Create docs portal starter"
    assert result.state["commits"][0]["tree"]["docs/intro.md"] == "docs-intro-v1"


def test_rm_cached_preserves_local_ignored_file_and_stages_deletion():
    simulator = RepositoryStateSimulator()
    state = simulator.normalize_state(
        {
            "commits": [
                {
                    "id": "c0",
                    "message": "Track env",
                    "parents": [],
                    "tree": {".env": "SECRET=1", "app.py": "v1"},
                }
            ],
            "branches": {"main": "c0"},
            "head": {"type": "branch", "name": "main"},
            "working_tree": {},
            "staging": {},
        }
    )

    state = simulator.process(state, "git rm --cached .env").state
    result = simulator.process(state, 'git commit -m "Stop tracking env"')

    assert state["staging"][".env"] == "deleted"
    assert state["working_tree"][".env"]["status"] == "ignored"
    assert result.state["commits"][-1]["changes"][".env"]["change_type"] == "deleted"
    assert ".env" not in result.state["commits"][-1]["tree"]
    assert result.state["working_tree"][".env"]["status"] == "ignored"
    assert result.state["operation_metadata"]["last_rm_cached_paths"] == [".env"]


def test_add_patch_commits_target_hunks_and_leaves_leftover_hunks():
    simulator = RepositoryStateSimulator()
    state = simulator.normalize_state(
        {
            "commits": [
                {"id": "c0", "message": "Base", "parents": [], "tree": {"src/auth.py": "auth-v1"}}
            ],
            "branches": {"main": "c0"},
            "head": {"type": "branch", "name": "main"},
            "working_tree": {
                "src/auth.py": {
                    "status": "modified",
                    "hunks": ["auth-validation-hunk", "auth-refactor-hunk"],
                }
            },
            "partial_hunks": {
                "src/auth.py": {
                    "target_hunks": ["auth-validation-hunk"],
                    "leftover_hunks": ["auth-refactor-hunk"],
                }
            },
            "staging": {},
        }
    )

    state = simulator.process(state, "git add -p src/auth.py").state
    assert state["staging"]["src/auth.py"]["hunks"] == ["auth-validation-hunk"]
    assert state["working_tree"]["src/auth.py"]["hunks"] == ["auth-refactor-hunk"]

    state = simulator.process(state, 'git commit -m "Validate auth input"').state

    latest = state["commits"][-1]
    assert "auth-validation-hunk" in str(latest["changes"]["src/auth.py"])
    assert "auth-refactor-hunk" not in str(latest["changes"]["src/auth.py"])
    assert state["staging"] == {}
    assert state["working_tree"]["src/auth.py"]["hunks"] == ["auth-refactor-hunk"]


def test_commit_amend_replaces_branch_tip_without_child_commit():
    simulator = RepositoryStateSimulator()
    state = simulator.normalize_state(
        {
            "commits": [
                {"id": "c0", "message": "Base", "parents": [], "tree": {"README.md": "v1"}},
                {"id": "c1", "message": "WIP", "parents": ["c0"], "tree": {"README.md": "v2"}},
            ],
            "branches": {"main": "c1"},
            "head": {"type": "branch", "name": "main"},
            "working_tree": {"app.py": "v1"},
            "staging": {},
        }
    )

    state = simulator.process(state, "git add app.py").state
    state = simulator.process(state, 'git commit --amend -m "Create starter app"').state

    assert state["branches"]["main"] == "c2"
    assert state["commits"][-1]["parents"] == ["c0"]
    assert state["commits"][-1]["message"] == "Create starter app"
    assert state["commits"][-1]["tree"]["app.py"] == "v1"
    assert state["operation_metadata"]["last_amend_replaced_commit"] == "c1"
    assert state["operation_metadata"]["last_amend_created_commit"] == "c2"


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
    assert "auth.py" in state["commits"][-1]["files"]

    state = simulator.process(state, "git revert c1").state
    assert state["branches"]["feature/auth"] == "c3"
    assert simulator.process(state, "git reflog").processed is True
