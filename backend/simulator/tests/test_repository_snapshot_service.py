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
