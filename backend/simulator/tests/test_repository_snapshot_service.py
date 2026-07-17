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


def test_repository_snapshot_preserves_authored_conflict_details_without_enrichment():
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
        "conflict_details": {
            "src/auth.js": {
                "base": "timeout=3000",
                "ours": "timeout=5000",
                "theirs": "timeout=2500",
            }
        },
        "operation_metadata": {"last_merge_branch": "feature/auth-timeout"},
    }

    snapshot = RepositorySnapshotService().snapshot(state)

    assert snapshot["conflict_details"]["src/auth.js"] == {
        "base": "timeout=3000",
        "ours": "timeout=5000",
        "theirs": "timeout=2500",
    }


def test_snapshot_round_trip_normalizes_identical_to_raw_state():
    # API responses carry snapshot_for_command output, and the browser submits
    # its mutation of THAT copy back as execution.next_state. If snapshotting
    # fills default-empty keys (config, merge_*, rebase_state, ...) that a
    # stored initial_state omits, normalization must erase the difference -
    # otherwise the transition verifier falsely rejects the first mutating
    # command of every fresh run ("cannot change config for this command").
    from simulator.services import RepositoryStateSimulator

    tools = RepositoryStateSimulator()
    snapshotter = RepositorySnapshotService()
    # Same minimal shape spec_helpers.repo() persists for seeded variants.
    raw = {
        "repository_initialized": True,
        "commits": [{"id": "c0", "message": "Initial", "parents": [], "tree": {"README.md": "notes"}}],
        "branches": {"main": "c0"},
        "head": {"type": "branch", "name": "main"},
        "working_tree": {"README.md": {"status": "modified", "content": "notes v2"}},
        "staging": {},
        "conflicts": [],
    }

    raw_hash = tools.state_hash(raw)
    assert tools.state_hash(snapshotter.snapshot(raw)) == raw_hash
    assert tools.state_hash(snapshotter.snapshot_for_command(raw)) == raw_hash


def test_snapshot_round_trip_preserves_conflict_and_legacy_metadata_exactly():
    from simulator.services import RepositoryStateSimulator

    tools = RepositoryStateSimulator()
    snapshotter = RepositorySnapshotService()
    raw = {
        "repository_initialized": True,
        "commits": [
            {
                "id": "c0",
                "message": "Base",
                "parents": [],
                "tree": {"src/relay.conf": "load=low"},
            }
        ],
        "branches": {"main": "c0"},
        "head": {"type": "branch", "name": "main"},
        "working_tree": {
            "src/relay.conf": {
                "status": "conflicted",
                "content": "<<<<<<< HEAD\nload=high\n=======\nload=low\n>>>>>>> team/strict",
            }
        },
        "staging": {},
        "conflicts": ["src/relay.conf"],
        "conflict_details": {
            "src/relay.conf": {
                "base": "load=medium",
                "ours": "load=high",
                "theirs": "load=low",
            }
        },
        "operation_metadata": {"last_merge_branch": "team/strict"},
        "last_merge_branch": "team/strict",
        "squash_merge_staged": True,
        "scenario_marker": {"preserve": ["arbitrary", "metadata"]},
        "project_tree": {"stale": "derived"},
        "visible_tree": {"stale": "derived"},
    }

    normalized = tools.normalize_state(raw)
    command_snapshot = snapshotter.snapshot_for_command(raw)
    display_snapshot = snapshotter.snapshot(raw)

    assert tools.state_hash(command_snapshot) == tools.state_hash_for_normalized(normalized)
    assert tools.state_hash(display_snapshot) == tools.state_hash_for_normalized(normalized)
    assert command_snapshot["conflict_details"] == normalized["conflict_details"]
    assert command_snapshot["last_merge_branch"] == "team/strict"
    assert command_snapshot["squash_merge_staged"] is True
    assert command_snapshot["scenario_marker"] == {"preserve": ["arbitrary", "metadata"]}
    assert "project_tree" not in command_snapshot
    assert "visible_tree" not in command_snapshot

    normalized_snapshot = snapshotter.snapshot_for_command(normalized, already_normalized=True)
    normalized_snapshot["scenario_marker"]["preserve"].append("isolated")
    assert normalized["scenario_marker"] == {"preserve": ["arbitrary", "metadata"]}

    command_snapshot["operation_metadata"]["last_merge_branch"] = "mutated"
    command_snapshot["scenario_marker"]["preserve"].append("mutated")
    assert raw["operation_metadata"]["last_merge_branch"] == "team/strict"
    assert raw["scenario_marker"] == {"preserve": ["arbitrary", "metadata"]}

    display_snapshot["visible_tree"]["src/relay.conf"]["content"] = "mutated"
    assert display_snapshot["project_tree"]["src/relay.conf"]["content"] != "mutated"
