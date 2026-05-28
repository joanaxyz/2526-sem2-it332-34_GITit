from simulator.services import RepositorySnapshotService


def test_repository_snapshot_normalizes_branch_head_and_visible_tree():
    state = {
        "commits": [
            {"id": "c0", "message": "Base", "parents": [], "tree": {"README.md": "readme-v1"}},
            {
                "id": "c1",
                "message": "Feature",
                "parents": ["c0"],
                "tree": {"README.md": "readme-v1", "src/auth.py": "auth-v1"},
            },
        ],
        "branches": {"main": "c0", "feature/auth": "c1"},
        "head": {"type": "branch", "name": "feature/auth"},
        "working_tree": {},
        "staging": {},
    }

    snapshot = RepositorySnapshotService().snapshot(state)

    assert snapshot["head"]["type"] == "branch"
    assert snapshot["head"]["name"] == "feature/auth"
    assert snapshot["head"]["target"] == "c1"
    assert len(snapshot["commits"]) == 2
    assert snapshot["branches"]["main"] == "c0"
    assert snapshot["branches"]["feature/auth"] == "c1"
    assert snapshot["project_tree"]["README.md"]["status"] == "clean"
    assert snapshot["project_tree"]["src/auth.py"]["status"] == "clean"


def test_repository_snapshot_preserves_index_and_worktree_state():
    state = {
        "commits": [
            {"id": "c0", "message": "Base", "parents": [], "tree": {"tracked.md": "tracked-v1"}}
        ],
        "branches": {"main": "c0"},
        "head": {"type": "branch", "name": "main"},
        "working_tree": {"draft.md": "untracked", "tracked.md": "modified"},
        "staging": {"ready.md": "added"},
    }

    snapshot = RepositorySnapshotService().snapshot(state)

    assert snapshot["branches"]["main"] == "c0"
    assert snapshot["staging"] == {"ready.md": "added"}
    assert snapshot["working_tree"]["draft.md"] == "untracked"
    assert snapshot["working_tree"]["tracked.md"] == "modified"
    assert snapshot["project_tree"]["tracked.md"]["source"] == "working_tree"
    assert snapshot["project_tree"]["ready.md"]["source"] == "staging"
    assert snapshot["project_tree"]["draft.md"]["status"] == "untracked"


def test_snapshot_for_command_omits_project_tree():
    state = {
        "commits": [
            {"id": "c0", "message": "Base", "parents": [], "tree": {"README.md": "readme-v1"}},
        ],
        "branches": {"main": "c0"},
        "head": {"type": "branch", "name": "main"},
        "working_tree": {},
        "staging": {},
    }

    snapshot = RepositorySnapshotService().snapshot_for_command(state)

    assert snapshot["head"]["target"] == "c0"
    assert "project_tree" not in snapshot
    assert "visible_tree" not in snapshot


def test_repository_snapshot_includes_conflict_details():
    state = {
        "commits": [
            {"id": "c0", "message": "Base", "parents": [], "tree": {"src/auth.js": "timeout=3000"}},
            {"id": "c1", "message": "Main", "parents": ["c0"], "tree": {"src/auth.js": "timeout=5000"}},
        ],
        "branches": {"main": "c1"},
        "head": {"type": "branch", "name": "main"},
        "working_tree": {
            "src/auth.js": {
                "status": "conflicted",
                "content": "<<<<<<< HEAD\ntimeout=5000\n=======\ntimeout=2500\n>>>>>>> feature/auth-timeout\n",
                "base": "timeout=3000",
                "ours": "timeout=5000",
                "theirs": "timeout=2500",
                "resolution": "timeout=5000\nretry=enabled",
            }
        },
        "staging": {},
        "conflicts": ["src/auth.js"],
        "operation_metadata": {"last_merge_branch": "feature/auth-timeout"},
    }

    snapshot = RepositorySnapshotService().snapshot(state)

    assert snapshot["conflict_details"]["src/auth.js"] == {
        "base": "timeout=3000",
        "ours": "timeout=5000",
        "theirs": "timeout=2500",
        "resolution": "timeout=5000\nretry=enabled",
        "merged": "<<<<<<< HEAD\ntimeout=5000\n=======\ntimeout=2500\n>>>>>>> feature/auth-timeout\n",
        "merge_branch": "feature/auth-timeout",
    }
