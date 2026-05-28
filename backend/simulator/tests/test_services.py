from simulator.services import RepositoryStateSimulator
from simulator.workspace_files import WorkspaceFileStateService


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
    assert current["operation_metadata"]["last_init_directory"] is None
    assert current["operation_metadata"]["last_init_current_directory"] is True
    assert current["operation_metadata"]["last_init_quiet"] is False
    assert current["operation_metadata"]["last_init_reinitialized"] is False


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


def test_init_quiet_directory_branch_combo_and_safe_reinitialization():
    simulator = RepositoryStateSimulator()
    state = simulator.normalize_state(
        {
            "repository_initialized": False,
            "commits": [],
            "branches": {},
            "head": {"type": "none"},
            "working_tree": {"README.md": "untracked"},
            "staging": {},
        }
    )

    quiet = simulator.process(state, "git init --quiet --initial-branch=trunk docs-site")

    assert quiet.output == ""
    assert quiet.state["head"]["name"] == "trunk"
    assert quiet.state["operation_metadata"]["last_init_directory"] == "docs-site"
    assert quiet.state["operation_metadata"]["last_init_quiet"] is True
    assert quiet.state["operation_metadata"]["last_init_reinitialized"] is False

    reinitialized = simulator.process(quiet.state, "git init")

    assert reinitialized.state["branches"] == {"trunk": None}
    assert reinitialized.state["working_tree"] == {"README.md": "untracked"}
    assert reinitialized.state["operation_metadata"]["last_init_reinitialized"] is True


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
    assert result.state["operation_metadata"]["last_clone_branch"] == "main"
    assert result.state["operation_metadata"]["last_clone_depth"] is None
    assert result.state["operation_metadata"]["last_clone_remote_name"] == "origin"
    assert result.state["operation_metadata"]["last_clone_default_branch"] == "main"
    assert result.state["operation_metadata"]["last_clone_shallow"] is False
    assert result.state["branches"]["main"] == "r10"
    assert result.state["remote_branches"]["origin/main"] == "r10"
    assert result.state["upstream_tracking"]["main"] == "origin/main"
    assert result.state["commits"][0]["message"] == "Create docs portal starter"
    assert result.state["commits"][0]["tree"]["docs/intro.md"] == "docs-intro-v1"


def test_clone_specific_branch_checks_out_requested_remote_branch():
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
                "branches": {"origin/main": "r40", "origin/starter": "r41"},
                "default_branch": "origin/main",
                "commits": [
                    {
                        "id": "r40",
                        "message": "Create lab base",
                        "parents": [],
                        "tree": {"README.md": "base-readme"},
                    },
                    {
                        "id": "r41",
                        "message": "Prepare starter branch",
                        "parents": ["r40"],
                        "tree": {"README.md": "starter-readme", "starter.md": "starter-v1"},
                    },
                ],
            },
        }
    )

    result = simulator.process(
        state, "git clone -b starter https://example.test/training/lab.git lab"
    )

    assert result.processed is True
    assert result.state["head"]["name"] == "starter"
    assert result.state["branches"] == {"starter": "r41"}
    assert result.state["remote_branches"]["origin/starter"] == "r41"
    assert result.state["upstream_tracking"] == {"starter": "origin/starter"}
    assert result.state["operation_metadata"]["last_clone_branch"] == "starter"
    assert result.state["operation_metadata"]["last_clone_default_branch"] == "main"
    assert result.state["commits"][-1]["tree"]["starter.md"] == "starter-v1"


def test_clone_depth_records_shallow_metadata_and_limits_history():
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
                "branches": {"origin/main": "r52"},
                "default_branch": "origin/main",
                "commits": [
                    {
                        "id": "r50",
                        "message": "Create project",
                        "parents": [],
                        "tree": {"README.md": "v1"},
                    },
                    {
                        "id": "r51",
                        "message": "Add source",
                        "parents": ["r50"],
                        "tree": {"README.md": "v1", "src/app.py": "v1"},
                    },
                    {
                        "id": "r52",
                        "message": "Polish source",
                        "parents": ["r51"],
                        "tree": {"README.md": "v2", "src/app.py": "v2"},
                    },
                ],
            },
        }
    )

    result = simulator.process(state, "git clone --depth 1 https://example.test/app.git")

    assert result.processed is True
    assert result.state["operation_metadata"]["last_clone_depth"] == 1
    assert result.state["operation_metadata"]["last_clone_shallow"] is True
    assert result.state["branches"]["main"] == "r52"
    assert [commit["id"] for commit in result.state["commits"]] == ["r52"]
    assert result.state["commits"][0]["parents"] == []


def test_clone_unknown_branch_returns_beginner_friendly_error():
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
                "branches": {"origin/main": "r60"},
                "commits": [{"id": "r60", "message": "Base", "parents": [], "tree": {}}],
            },
        }
    )

    result = simulator.process(
        state, "git clone --branch starter https://example.test/app.git lab"
    )

    assert result.processed is False
    assert result.exit_code == 128
    assert "Remote branch 'starter' was not found" in result.output


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


def test_diff_head_and_name_only_include_staged_and_unstaged_changes():
    simulator = RepositoryStateSimulator()
    state = simulator.normalize_state(
        {
            "commits": [
                {
                    "id": "c0",
                    "message": "Base",
                    "parents": [],
                    "tree": {"README.md": "v1", "app.py": "v1"},
                }
            ],
            "branches": {"main": "c0"},
            "head": {"type": "branch", "name": "main"},
            "staging": {"README.md": "v2"},
            "working_tree": {"app.py": "v2", "notes.md": "untracked"},
        }
    )

    diff_head = simulator.process(state, "git diff HEAD")
    unstaged_names = simulator.process(state, "git diff --name-only")
    staged_names = simulator.process(state, "git diff --staged --name-only")

    assert "diff --git a/README.md b/README.md" in diff_head.output
    assert "diff --git a/app.py b/app.py" in diff_head.output
    assert "notes.md" not in diff_head.output
    assert unstaged_names.output == "app.py"
    assert staged_names.output == "README.md"


def test_gitignore_diagnostics_status_check_ignore_and_ls_files():
    simulator = RepositoryStateSimulator()
    state = simulator.normalize_state(
        {
            "commits": [
                {
                    "id": "c0",
                    "message": "Base",
                    "parents": [],
                    "tree": {".env": "SECRET=1", "app.py": "v1"},
                }
            ],
            "branches": {"main": "c0"},
            "head": {"type": "branch", "name": "main"},
            "staging": {},
            "working_tree": {
                ".gitignore": ".env\nlogs/",
                ".env": {"status": "ignored", "content": "SECRET=2"},
                "logs/app.log": {"status": "ignored", "content": "log"},
            },
        }
    )

    status = simulator.process(state, "git status --ignored")
    check_ignore = simulator.process(state, "git check-ignore -v .env")
    ls_files_before = simulator.process(state, "git ls-files")
    removed = simulator.process(state, "git rm --cached .env").state
    ls_files_after = simulator.process(removed, "git ls-files")

    assert "Ignored files:" in status.output
    assert ".env" in status.output
    assert check_ignore.output == ".gitignore:1:.env\t.env"
    assert ls_files_before.output == ".env\napp.py"
    assert ls_files_after.output == "app.py"


def test_rm_recursive_cached_untracks_directory_without_deleting_local_files():
    simulator = RepositoryStateSimulator()
    state = simulator.normalize_state(
        {
            "commits": [
                {
                    "id": "c0",
                    "message": "Track build",
                    "parents": [],
                    "tree": {"dist/app.js": "old", "dist/app.css": "old", "src/app.js": "v1"},
                }
            ],
            "branches": {"main": "c0"},
            "head": {"type": "branch", "name": "main"},
            "working_tree": {},
            "staging": {},
        }
    )

    result = simulator.process(state, "git rm -r --cached dist")

    assert sorted(result.state["staging"]) == ["dist/app.css", "dist/app.js"]
    assert result.state["working_tree"]["dist/app.js"]["status"] == "ignored"
    assert result.state["operation_metadata"]["last_rm_cached_paths"] == [
        "dist/app.css",
        "dist/app.js",
    ]


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


def test_restore_dot_and_multi_path_variants():
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
            "working_tree": {"README.md": "v3", "debug.log": "draft", ".env": {"status": "ignored"}},
            "staging": {"notes.md": "draft", "docs/guide.md": "guide-v2"},
        }
    )

    unstaged = simulator.process(state, "git restore --staged notes.md docs/guide.md").state
    restored = simulator.process(unstaged, "git restore .").state

    assert unstaged["staging"] == {}
    assert sorted(unstaged["working_tree"]) == [".env", "README.md", "debug.log", "docs/guide.md", "notes.md"]
    assert restored["working_tree"] == {".env": {"status": "ignored"}}


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


def test_module_three_commands_merge_mergetool_fetch_and_cherry_pick():
    simulator = RepositoryStateSimulator()
    state = simulator.normalize_state(
        {
            "commits": [
                {"id": "c0", "message": "Base", "parents": [], "tree": {"app.py": "base"}},
                {"id": "c1", "message": "Main", "parents": ["c0"], "tree": {"app.py": "main"}},
                {
                    "id": "c2",
                    "message": "Feature",
                    "parents": ["c0"],
                    "tree": {"app.py": "feature"},
                },
                {
                    "id": "c3",
                    "message": "Hotfix",
                    "parents": ["c1"],
                    "tree": {"app.py": "main", "fix.py": "hotfix-token"},
                },
            ],
            "branches": {"main": "c1", "feature": "c2", "hotfix": "c3"},
            "head": {"type": "branch", "name": "main"},
            "working_tree": {},
            "staging": {},
            "conflicts": [],
            "conflict_on_merge": True,
            "conflict_files": ["app.py"],
            "merge_resolutions": {"app.py": "resolved"},
            "remotes": {"origin": "https://example.test/app.git"},
            "remote_updates": {"origin/main": "c3"},
        }
    )

    fetched = simulator.process(state, "git fetch origin").state
    configured = simulator.process(fetched, "git config --global merge.tool vscode").state
    conflicted = simulator.process(configured, "git merge feature").state
    tool_opened = simulator.process(conflicted, "git mergetool").state
    edited = WorkspaceFileStateService().write_file(
        tool_opened,
        path="app.py",
        content="resolved",
    )
    staged = simulator.process(edited, "git add app.py").state
    merged = simulator.process(staged, "git commit").state
    picked = simulator.process(merged, "git cherry-pick c3").state

    assert fetched["operation_metadata"]["remote_tracking_updated"] is True
    assert configured["operation_metadata"]["configured_merge_tool"] == "vscode"
    assert conflicted["conflicts"] == ["app.py"]
    assert tool_opened["staging"] == {}
    assert tool_opened["operation_metadata"]["last_mergetool_paths"] == ["app.py"]
    assert merged["commits"][-1]["parents"] == ["c1", "c2"]
    assert picked["commits"][-1]["message"] == "Hotfix"
    assert picked["commits"][-1]["tree"]["fix.py"] == "hotfix-token"


def test_module_four_commands_are_supported_with_expected_state_effects():
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
            "remote_branches": {"origin/main": "c0"},
            "upstream_tracking": {"main": "origin/main"},
        }
    )

    supported_module_four_commands = [
        "git push origin main",
        "git revert c0",
        "git switch main",
        "git rebase origin/main",
    ]

    for command in supported_module_four_commands:
        result = simulator.process(state, command)
        assert result.processed is True, command

    for command in [
        "git remote add origin https://example.test/repo.git",
        "git checkout main",
    ]:
        result = simulator.process(state, command)
        assert result.processed is False, command
        assert result.state == state, command
        assert result.exit_code == 129, command


def test_amend_and_reflog_remain_module_one_supported():
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

    state = simulator.process(state, "git add auth.py").state
    state = simulator.process(state, "git commit --amend").state
    assert "auth.py" in state["commits"][-1]["files"]

    assert simulator.process(state, "git reflog").processed is True
