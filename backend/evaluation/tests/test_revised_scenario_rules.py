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
