from common.constants import RESULT_TARGET_MATCHED, RESULT_TARGET_NOT_YET_MATCHED
from evaluation.services import StateBasedEvaluator


def test_evaluator_checks_partial_staging_commit_scope_and_message():
    state = {
        "commits": [
            {"id": "c0", "message": "Base", "parents": []},
            {
                "id": "c1",
                "message": "config baseline",
                "parents": ["c0"],
                "files": {"config.yml": "modified"},
            },
        ],
        "branches": {"main": "c1"},
        "head": {"type": "branch", "name": "main"},
        "working_tree": {"draft.md": "modified"},
        "staging": {},
        "conflicts": [],
    }
    rule = {
        "head_branch": "main",
        "staging_empty": True,
        "conflict_free": True,
        "working_tree_contains": ["draft.md"],
        "latest_commit": {
            "branch": "main",
            "contains_paths": ["config.yml"],
            "excludes_paths": ["draft.md"],
            "message_contains": ["config"],
        },
    }

    result = StateBasedEvaluator().evaluate(state, rule)

    assert result.result_category == RESULT_TARGET_MATCHED


def test_evaluator_rejects_commit_that_sweeps_draft_work_into_history():
    state = {
        "commits": [
            {"id": "c0", "message": "Base", "parents": []},
            {
                "id": "c1",
                "message": "config baseline",
                "parents": ["c0"],
                "files": {"config.yml": "modified", "draft.md": "modified"},
            },
        ],
        "branches": {"main": "c1"},
        "head": {"type": "branch", "name": "main"},
        "working_tree": {},
        "staging": {},
        "conflicts": [],
    }
    rule = {
        "head_branch": "main",
        "staging_empty": True,
        "conflict_free": True,
        "working_tree_contains": ["draft.md"],
        "latest_commit": {
            "branch": "main",
            "contains_paths": ["config.yml"],
            "excludes_paths": ["draft.md"],
            "message_contains": ["config"],
        },
    }

    result = StateBasedEvaluator().evaluate(state, rule)

    assert result.result_category == RESULT_TARGET_NOT_YET_MATCHED
