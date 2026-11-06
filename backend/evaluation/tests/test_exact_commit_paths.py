import pytest

from evaluation.services.state_based import StateBasedEvaluator


@pytest.mark.parametrize("nested", [False, True])
@pytest.mark.parametrize(
    "paths,accepted",
    [
        (["src/api.py", "tests/test_api.py"], True),
        (["tests/test_api.py", "src/api.py"], True),
        (["src/api.py"], False),
        (["src/api.py", "tests/test_api.py", "notes/unapproved.txt"], False),
        (["src/api.py", "tests/test_api.py", "README.md"], False),
        ([], False),
    ],
)
def test_exact_commit_paths_reject_missing_extra_and_deleted_paths(nested, paths, accepted):
    state = {
        "repository_initialized": True,
        "commits": [
            {
                "id": "c1",
                "message": "Fix",
                "parents": [],
                "tree": {},
                "changes": {
                    path: {"change_type": "deleted" if path == "README.md" else "modified"}
                    for path in paths
                },
            }
        ],
        "branches": {"main": "c1"},
        "head": {"type": "branch", "name": "main"},
    }
    approved = ["src/api.py", "tests/test_api.py"]
    rule = (
        {"type": "branch_tip_commit", "branch": "main", "changes_match_exact_paths": approved}
        if nested
        else {"type": "commit_changes_match_exact_paths", "branch": "main", "paths": approved}
    )
    assert StateBasedEvaluator().evaluate(state, {"rules": [rule]}).target_matched is accepted


def test_empty_exact_path_requirement_is_not_treated_as_an_absent_constraint():
    state = {
        "repository_initialized": True,
        "commits": [
            {
                "id": "c1",
                "message": "Fix",
                "parents": [],
                "tree": {},
                "changes": {"extra.txt": "added"},
            }
        ],
        "branches": {"main": "c1"},
        "head": {"type": "branch", "name": "main"},
    }
    evaluator = StateBasedEvaluator()
    rule = {"type": "branch_tip_commit", "branch": "main", "message_equals": "Fix"}
    assert evaluator.evaluate(state, {"rules": [rule]}).target_matched
    assert not evaluator.evaluate(
        state, {"rules": [{**rule, "changes_match_exact_paths": []}]}
    ).target_matched
