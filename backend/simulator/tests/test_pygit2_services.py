from simulator.pygit2_services import (
    Pygit2RepositoryMaterializer,
    Pygit2RepositorySnapshotter,
)


def test_pygit2_materializer_builds_repository_from_teaching_state(tmp_path):
    state = {
        "commits": [
            {"id": "c0", "message": "Base", "parents": []},
            {"id": "c1", "message": "Feature", "parents": ["c0"]},
        ],
        "branches": {"main": "c0", "feature/auth": "c1"},
        "head": {"type": "branch", "name": "feature/auth"},
        "working_tree": {},
        "staging": {},
    }

    materialized = Pygit2RepositoryMaterializer().materialize(
        state=state,
        path=tmp_path,
    )
    snapshot = Pygit2RepositorySnapshotter().snapshot(repo=materialized.repo)

    assert set(materialized.aliases_to_oids) == {"c0", "c1"}
    assert snapshot["head"]["type"] == "branch"
    assert snapshot["head"]["name"] == "feature/auth"
    assert len(snapshot["commits"]) == 2
    assert snapshot["branches"]["main"]
    assert snapshot["branches"]["feature/auth"]


def test_pygit2_materializer_preserves_index_and_worktree_state(tmp_path):
    state = {
        "commits": [{"id": "c0", "message": "Base", "parents": [], "files": {"tracked.md": "added"}}],
        "branches": {"main": "c0"},
        "head": {"type": "branch", "name": "main"},
        "working_tree": {"draft.md": "untracked", "tracked.md": "modified"},
        "staging": {"ready.md": "added"},
    }

    materialized = Pygit2RepositoryMaterializer().materialize(state=state, path=tmp_path)
    snapshot = Pygit2RepositorySnapshotter().snapshot(
        repo=materialized.repo,
        aliases_to_oids=materialized.aliases_to_oids,
        previous_state=state,
    )

    assert snapshot["branches"]["main"] == "c0"
    assert snapshot["staging"] == {"ready.md": "added"}
    assert snapshot["working_tree"]["draft.md"] == "untracked"
    assert snapshot["working_tree"]["tracked.md"] == "modified"
