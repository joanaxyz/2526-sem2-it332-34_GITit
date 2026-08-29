from evaluation.checklist import ObjectiveChecklistEvaluator

BASE_STATE = {
    "repository_initialized": True,
    "commits": [],
    "branches": {"main": None},
    "head": {"type": "branch", "name": "main"},
    "working_tree": {},
    "staging": {"app.py": "print('x')\n"},
    "conflicts": [],
}


def test_objective_checklist_marks_each_check_against_state():
    checks = [
        {"label": "Repo is initialized.", "requirement": {"repository_initialized": True}},
        {"label": "app.py is staged.", "requirement": {"staging_contains": ["app.py"]}},
        {"label": "other.py is staged.", "requirement": {"staging_contains": ["other.py"]}},
    ]

    results = ObjectiveChecklistEvaluator().evaluate(checks, state=BASE_STATE)

    by_label = {result["label"]: result["satisfied"] for result in results}
    assert by_label["Repo is initialized."] is True
    assert by_label["app.py is staged."] is True
    assert by_label["other.py is staged."] is False


def test_objective_checklist_supports_inverse_cleanliness_rules():
    # Variant-safe checks for path-only-varying levels: "something is staged" /
    # "work is left in the tree" capture the goal without naming a path.
    checks = [
        {"label": "Something is staged.", "requirement": {"staging_not_empty": True}},
        {"label": "Work is left in the tree.", "requirement": {"working_tree_dirty": True}},
    ]

    dirty = {**BASE_STATE, "working_tree": {"draft.md": "wip"}}
    by_label = {
        row["label"]: row["satisfied"]
        for row in ObjectiveChecklistEvaluator().evaluate(checks, state=dirty)
    }
    assert by_label["Something is staged."] is True
    assert by_label["Work is left in the tree."] is True

    clean = {**BASE_STATE, "staging": {}, "working_tree": {}}
    by_label = {
        row["label"]: row["satisfied"]
        for row in ObjectiveChecklistEvaluator().evaluate(checks, state=clean)
    }
    assert by_label["Something is staged."] is False
    assert by_label["Work is left in the tree."] is False


def test_objective_checklist_check_without_requirement_is_unsatisfied():
    # An empty requirement would match vacuously in the evaluator, so the
    # checklist must report it unsatisfied rather than always-green.
    results = ObjectiveChecklistEvaluator().evaluate(
        [{"label": "Has no predicate.", "requirement": {}}],
        state=BASE_STATE,
    )

    assert results == [{"label": "Has no predicate.", "satisfied": False}]


def test_objective_checklist_skips_unlabeled_and_non_dict_entries():
    results = ObjectiveChecklistEvaluator().evaluate(
        [
            "not a dict",
            {"label": "", "requirement": {"repository_initialized": True}},
            {"label": "Kept.", "requirement": {"repository_initialized": True}},
        ],
        state=BASE_STATE,
    )

    assert results == [{"label": "Kept.", "satisfied": True}]
