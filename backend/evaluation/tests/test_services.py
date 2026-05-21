from common.constants import RESULT_TARGET_MATCHED, RESULT_TARGET_NOT_YET_MATCHED
from evaluation.services import InspectionEvaluator, StateBasedEvaluator


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


def test_evaluator_supports_remote_stash_reflog_and_unchanged_rules():
    initial = {
        "repository_initialized": True,
        "commits": [{"id": "c0", "message": "Base", "parents": []}],
        "branches": {"main": "c0"},
        "head": {"type": "branch", "name": "main"},
        "working_tree": {},
        "staging": {},
        "conflicts": [],
        "remotes": {},
        "remote_branches": {},
        "upstream_tracking": {},
        "stash_stack": [],
        "reflog": [],
    }
    state = {
        **initial,
        "remotes": {"origin": "https://example.test/app.git"},
        "remote_branches": {"origin/main": "c0"},
        "upstream_tracking": {"main": "origin/main"},
        "reflog": [{"ref": "HEAD@{1}", "target": "c0", "message": "reset"}],
    }
    rule = {
        "repository_initialized": True,
        "remote_exists": ["origin"],
        "remote_branch_exists": ["origin/main"],
        "remote_url_matches": {"origin": "https://example.test/app.git"},
        "upstream_tracking": {"main": "origin/main"},
        "remote_branch_matches_local": {"origin/main": "main"},
        "stash_stack_empty": True,
        "reflog_contains": ["reset"],
        "repository_state_unchanged_except": ["remotes", "remote_branches", "upstream_tracking", "reflog"],
    }

    result = StateBasedEvaluator().evaluate(state, rule, initial_state=initial)

    assert result.result_category == RESULT_TARGET_MATCHED


def test_state_based_evaluator_can_require_command_history():
    state = {
        "repository_initialized": True,
        "commits": [{"id": "r0", "message": "Remote commit r0", "parents": []}],
        "branches": {"main": "r0"},
        "head": {"type": "branch", "name": "main"},
        "working_tree": {},
        "staging": {},
        "conflicts": [],
        "remotes": {"origin": "https://example.test/app.git"},
        "remote_branches": {"origin/main": "r0"},
        "upstream_tracking": {"main": "origin/main"},
    }
    rule = {
        "repository_initialized": True,
        "remote_exists": ["origin"],
        "head_branch": "main",
        "working_tree_clean": True,
        "required_commands": ["git clone"],
    }

    matched = StateBasedEvaluator().evaluate(
        state,
        rule,
        executed_commands=["git clone https://example.test/app.git app"],
    )
    missing_required_command = StateBasedEvaluator().evaluate(
        state,
        rule,
        executed_commands=["git init", "git remote add origin https://example.test/app.git"],
    )

    assert matched.result_category == RESULT_TARGET_MATCHED
    assert missing_required_command.result_category == RESULT_TARGET_NOT_YET_MATCHED


def test_inspection_evaluator_requires_commands_and_unchanged_state():
    state = {
        "commits": [{"id": "c0", "message": "Base", "parents": []}],
        "branches": {"main": "c0"},
        "head": {"type": "branch", "name": "main"},
        "working_tree": {"README.md": "modified"},
        "staging": {},
        "conflicts": [],
    }
    expected = {
        "required_commands": ["git status"],
        "repository_state_unchanged": True,
        "checks": {"head_branch": "main", "unstaged_changes": ["README.md"], "staging_empty": True},
    }

    matched = InspectionEvaluator().evaluate(
        initial_state=state,
        current_state=state,
        expected_observations=expected,
        executed_commands=["git status"],
    )
    missing_command = InspectionEvaluator().evaluate(
        initial_state=state,
        current_state=state,
        expected_observations=expected,
        executed_commands=["git diff"],
    )

    assert matched.result_category == RESULT_TARGET_MATCHED
    assert missing_command.result_category == RESULT_TARGET_NOT_YET_MATCHED
