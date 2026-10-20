import pytest

from common.exceptions import BadRequest
from common.git.command_transition_verifier import ClientTransitionVerifier


def _state(**overrides):
    state = {
        "repository_initialized": True,
        "commits": [],
        "branches": {},
        "head": {"type": "branch", "name": "main"},
        "staging": {},
        "working_tree": {},
        "conflicts": [],
    }
    state.update(overrides)
    return state


def _diverged(**overrides):
    return _state(
        commits=[
            {"id": "c1", "message": "base", "parents": [], "tree": {"app.py": "base", "docs.md": "d1"}},
            {
                "id": "c2",
                "message": "ours",
                "parents": ["c1"],
                "tree": {"app.py": "base", "docs.md": "d1", "local.py": "l"},
            },
            {
                "id": "c3",
                "message": "theirs",
                "parents": ["c1"],
                "tree": {"app.py": "base", "docs.md": "d2", "remote.py": "r"},
            },
        ],
        branches={"main": "c2", "feature": "c3"},
        **overrides,
    )


def test_divergent_merge_keeps_files_only_this_branch_changed():
    verifier = ClientTransitionVerifier()
    expected = verifier._expected_merge_state(command="git merge feature", previous_state=_diverged())

    merge_commit = expected["commits"][-1]
    assert merge_commit["parents"] == ["c2", "c3"]
    assert merge_commit["tree"] == {
        "app.py": "base",
        "docs.md": "d2",
        "local.py": "l",
        "remote.py": "r",
    }


def test_conflicted_merge_stages_only_incoming_changes():
    previous = _diverged()
    previous["commits"][1]["tree"]["app.py"] = "ours"
    previous["commits"][2]["tree"]["app.py"] = "theirs"
    verifier = ClientTransitionVerifier()

    expected = verifier._expected_merge_state(command="git merge feature", previous_state=previous)

    assert expected["conflicts"] == ["app.py"]
    assert sorted(expected["staging"]) == ["docs.md", "remote.py"]


def test_merge_refuses_to_overwrite_uncommitted_changes_on_a_path_it_touches():
    previous = _diverged(working_tree={"docs.md": {"status": "modified", "content": "wip"}})
    verifier = ClientTransitionVerifier()

    with pytest.raises(BadRequest):
        verifier._expected_merge_state(command="git merge feature", previous_state=previous)


def test_unrelated_uncommitted_changes_do_not_block_a_merge():
    previous = _diverged(working_tree={"notes.txt": {"status": "untracked", "content": "x"}})
    verifier = ClientTransitionVerifier()

    expected = verifier._expected_merge_state(command="git merge feature", previous_state=previous)

    assert expected["commits"][-1]["parents"] == ["c2", "c3"]
