import copy

import pytest

from common.exceptions import BadRequest
from common.git.command_transition_verifier import ClientTransitionVerifier
from simulator.services import RepositoryStateSimulator


def test_staged_only_patch_is_a_noop_and_cannot_forge_index_selection():
    previous = RepositoryStateSimulator().normalize_state(
        {
            "repository_initialized": True,
            "commits": [
                {"id": "c1", "message": "Baseline", "parents": [], "tree": {"src/api.py": "base"}}
            ],
            "branches": {"main": "c1"},
            "head": {"type": "branch", "name": "main"},
            "staging": {"src/api.py": {"status": "modified", "hunks": ["fix", "experiment"]}},
            "working_tree": {},
            "partial_hunks": {
                "src/api.py": {"target_hunks": ["fix"], "leftover_hunks": ["experiment"]}
            },
        }
    )
    verifier = ClientTransitionVerifier()
    verifier.verify(
        command="git add -p src/api.py",
        previous_state=previous,
        next_state=copy.deepcopy(previous),
        command_family="add",
        exit_code=0,
    )
    forged = copy.deepcopy(previous)
    forged["staging"]["src/api.py"] = {"status": "partial", "hunks": ["fix"]}
    forged["working_tree"]["src/api.py"] = {"status": "modified", "hunks": ["experiment"]}
    with pytest.raises(BadRequest):
        verifier.verify(
            command="git add -p src/api.py",
            previous_state=previous,
            next_state=forged,
            command_family="add",
            exit_code=0,
        )
