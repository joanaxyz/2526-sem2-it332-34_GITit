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


def test_init_initial_branch_variants_create_requested_branch():
    simulator = RepositoryStateSimulator()
    state = {
        "repository_initialized": False,
        "commits": [],
        "branches": {},
        "head": {"type": "none"},
    }

    short = simulator.process(state, "git init -b trunk").state
    long = simulator.process(state, "git init --initial-branch=main").state

    assert short["head"]["name"] == "trunk"
    assert short["branches"] == {"trunk": None}
    assert long["head"]["name"] == "main"
    assert long["operation_metadata"]["last_init_initial_branch"] == "main"


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

    result = simulator.process(
        state, "git clone https://example.test/training/docs-portal.git docs-portal"
    )

    assert result.processed is True
    assert (
        result.state["operation_metadata"]["last_clone_url"]
        == "https://example.test/training/docs-portal.git"
    )
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


def test_add_all_and_update_respect_tracked_vs_untracked_files():
    simulator = RepositoryStateSimulator()
    state = simulator.normalize_state(
        {
            "commits": [
                {
                    "id": "c0",
                    "message": "Base",
                    "parents": [],
                    "tree": {"tracked.txt": "v1", "gone.txt": "v1"},
                }
            ],
            "branches": {"main": "c0"},
            "head": {"type": "branch", "name": "main"},
            "working_tree": {"tracked.txt": "v2", "new.txt": "untracked", "gone.txt": "deleted"},
            "staging": {},
        }
    )

    update = simulator.process(state, "git add -u").state
    all_changes = simulator.process(state, "git add --all").state

    assert sorted(update["staging"]) == ["gone.txt", "tracked.txt"]
    assert update["working_tree"] == {"new.txt": "untracked"}
    assert sorted(all_changes["staging"]) == ["gone.txt", "new.txt", "tracked.txt"]
    assert all_changes["working_tree"] == {}


def test_commit_am_stages_tracked_changes_only():
    simulator = RepositoryStateSimulator()
    state = simulator.normalize_state(
        {
            "commits": [
                {"id": "c0", "message": "Base", "parents": [], "tree": {"tracked.txt": "v1"}}
            ],
            "branches": {"main": "c0"},
            "head": {"type": "branch", "name": "main"},
            "working_tree": {"tracked.txt": "v2", "new.txt": "untracked"},
            "staging": {},
        }
    )

    result = simulator.process(state, 'git commit -am "Update tracked"')

    assert result.processed is True
    assert result.state["commits"][-1]["changes"].keys() == {"tracked.txt"}
    assert result.state["working_tree"] == {"new.txt": "untracked"}


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


def test_branch_switch_checkout_remote_reset_restore_variants():
    simulator = RepositoryStateSimulator()
    state = simulator.normalize_state(
        {
            "commits": [
                {"id": "c0", "message": "Base", "parents": [], "tree": {"README.md": "v1"}},
                {
                    "id": "c1",
                    "message": "Update readme",
                    "parents": ["c0"],
                    "tree": {"README.md": "v2"},
                },
            ],
            "branches": {"main": "c1"},
            "head": {"type": "branch", "name": "main"},
            "working_tree": {"README.md": "v3"},
            "staging": {"notes.md": "draft"},
        }
    )

    state = simulator.process(state, "git branch feature/readme").state
    state = simulator.process(state, "git switch feature/readme").state
    state = simulator.process(state, "git checkout -b scratch").state
    state = simulator.process(state, "git restore --staged notes.md").state
    state = simulator.process(state, "git reset --soft HEAD~1").state
    state = simulator.process(state, "git remote add origin https://example.test/repo.git").state
    state = simulator.process(state, "git remote rename origin upstream").state
    state = simulator.process(state, "git remote remove upstream").state

    assert state["head"]["name"] == "scratch"
    assert state["branches"]["scratch"] == "c0"
    assert "README.md" in state["staging"]
    assert state["remotes"] == {}


def test_diagnostic_commands_record_metadata_without_state_mutation():
    simulator = RepositoryStateSimulator()
    state = simulator.normalize_state(
        {
            "commits": [
                {"id": "c0", "message": "Base", "parents": [], "tree": {"README.md": "v1"}}
            ],
            "branches": {"main": "c0"},
            "head": {"type": "branch", "name": "main"},
            "working_tree": {"README.md": "v2"},
            "staging": {},
            "remotes": {"origin": "https://example.test/repo.git"},
        }
    )

    status = simulator.process(state, "git status -s")
    diff = simulator.process(state, "git diff")
    remote = simulator.process(state, "git remote -v")

    assert status.diagnostic_metadata == ("inspected_short_status",)
    assert diff.diagnostic_metadata == ("inspected_diff",)
    assert remote.diagnostic_metadata == ("inspected_remote_list",)
    assert status.state == state
    assert diff.state == state
    assert remote.state == state


def test_snapshot_visible_tree_includes_clean_committed_and_changed_files():
    from simulator.services import RepositorySnapshotService

    simulator = RepositoryStateSimulator()
    state = simulator.normalize_state(
        {
            "commits": [
                {
                    "id": "c0",
                    "message": "Base",
                    "parents": [],
                    "tree": {"README.md": "v1", "src/app.py": "v1"},
                }
            ],
            "branches": {"main": "c0"},
            "head": {"type": "branch", "name": "main"},
            "staging": {"src/app.py": "v2"},
            "working_tree": {"notes.md": "untracked"},
        }
    )

    snapshot = RepositorySnapshotService().snapshot(state)

    assert snapshot["project_tree"]["README.md"]["status"] == "clean"
    assert snapshot["project_tree"]["src/app.py"]["source"] == "staging"
    assert snapshot["project_tree"]["notes.md"]["status"] == "untracked"


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
