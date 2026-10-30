"""Target generation refuses an authored route the backend would reject."""

from curriculum.services.solution_replay import verify_backend_transitions

READY = {
    "repository_initialized": True,
    "commits": [{"id": "c1", "message": "Base", "parents": [], "tree": {"a.txt": "a"}}],
    "branches": {"main": "c1"},
    "head": {"type": "branch", "name": "main"},
    "staging": {},
    "working_tree": {},
    "conflicts": [],
}


def _replay(after: dict, *, exit_code: int) -> dict:
    return {
        "steps": [
            {
                "command": "git branch feature",
                "normalized_command": "git branch feature",
                "command_family": "branch",
                "exit_code": exit_code,
                "diagnostic": False,
                "ready": READY,
            }
        ],
        "final": after,
    }


def test_a_route_the_verifier_reproduces_passes():
    created = {**READY, "branches": {"main": "c1", "feature": "c1"}}
    assert verify_backend_transitions({"ok": _replay(created, exit_code=0)}) == []


def test_a_failed_command_that_changes_state_is_reported():
    created = {**READY, "branches": {"main": "c1", "feature": "c1"}}
    rejected = verify_backend_transitions({"bad": _replay(created, exit_code=1)})
    assert len(rejected) == 1
    assert rejected[0].startswith("bad step 1 (git branch feature):")
