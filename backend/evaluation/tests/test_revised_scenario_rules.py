from evaluation.services.state_based import StateBasedEvaluator

BASE_STATE = {
    "repository_initialized": True,
    "commits": [],
    "branches": {"main": None},
    "head": {"type": "branch", "name": "main"},
    "staging": {},
    "working_tree": {},
    "conflicts": [],
}


def test_operation_metadata_path_matches_relative_and_absolute_directory_forms():
    evaluator = StateBasedEvaluator()
    requirements = {
        "rules": [
            {
                "type": "operation_metadata_path_matches",
                "key": "last_init_directory",
                "value": "field-notes",
            }
        ]
    }

    for directory in ("field-notes", "./field-notes/", "C:/work/field-notes"):
        state = {**BASE_STATE, "operation_metadata": {"last_init_directory": directory}}
        assert evaluator.evaluate(state, requirements).target_matched

    wrong = {**BASE_STATE, "operation_metadata": {"last_init_directory": "work"}}
    assert not evaluator.evaluate(wrong, requirements).target_matched


def test_cherry_pick_not_in_progress_tracks_the_operation_state():
    evaluator = StateBasedEvaluator()
    requirements = {"rules": [{"type": "cherry_pick_not_in_progress"}]}

    assert evaluator.evaluate(BASE_STATE, requirements).target_matched
    assert not evaluator.evaluate(
        {**BASE_STATE, "cherry_pick_in_progress": True}, requirements
    ).target_matched


def test_branch_rules_resolve_first_parent_ancestors():
    evaluator = StateBasedEvaluator()
    state = {
        **BASE_STATE,
        "commits": [
            {"id": "c1", "message": "Base", "parents": [], "tree": {}},
            {"id": "c0", "message": "Fix token expiry check", "parents": ["c1"], "tree": {}},
            {"id": "c2", "message": "Tidy API logging", "parents": ["c0"], "tree": {}},
        ],
        "branches": {"main": "c2"},
    }

    def tip_message(branch: str, message: str) -> bool:
        requirements = {
            "rules": [{"type": "branch_tip_commit", "branch": branch, "message_equals": message}]
        }
        return evaluator.evaluate(state, requirements).target_matched

    assert tip_message("main", "Tidy API logging")
    assert tip_message("main~1", "Fix token expiry check")
    assert tip_message("main~2", "Base")
    assert not tip_message("main~1", "Tidy API logging")
    assert not tip_message("main~3", "Base")
