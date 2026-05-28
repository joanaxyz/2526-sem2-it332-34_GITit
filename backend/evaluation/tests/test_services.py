from types import SimpleNamespace

import pytest

from common.constants import RESULT_TARGET_MATCHED, RESULT_TARGET_NOT_YET_MATCHED
from evaluation.completion import CompletionEvaluationContext, StateRuleCompletionEvaluator
from evaluation.services import StateBasedEvaluator
from simulator.services import RepositoryStateSimulator
from simulator.workspace_files import WorkspaceFileStateService


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


def test_completion_evaluator_uses_variant_owned_target_rule():
    context = CompletionEvaluationContext(
        session=SimpleNamespace(
            variant=SimpleNamespace(
                target_rule={"repository_initialized": True},
                initial_state={"repository_initialized": False},
            )
        ),
        previous_state={"repository_initialized": False},
        next_state={"repository_initialized": True},
        executed_commands=[],
    )

    result = StateRuleCompletionEvaluator().evaluate(context)

    assert result.result_category == RESULT_TARGET_MATCHED


def test_completion_evaluator_requires_variant_target_rule():
    context = CompletionEvaluationContext(
        session=SimpleNamespace(
            variant=SimpleNamespace(
                target_rule={},
                initial_state={"repository_initialized": False},
            )
        ),
        previous_state={"repository_initialized": False},
        next_state={"repository_initialized": True},
        executed_commands=[],
    )

    with pytest.raises(ValueError, match="missing target_rule"):
        StateRuleCompletionEvaluator().evaluate(context)


def test_module4_completion_uses_state_match_without_required_command_history():
    target_state = {
        "repository_initialized": True,
        "commits": [{"id": "c0", "message": "Base", "parents": []}],
        "branches": {"main": "c0"},
        "head": {"type": "branch", "name": "main"},
        "working_tree": {},
        "staging": {},
        "conflicts": [],
    }
    context = CompletionEvaluationContext(
        session=SimpleNamespace(
            learning_unit=SimpleNamespace(number=4),
            variant=SimpleNamespace(
                target_rule={"required_commands": ["git show"]},
                target_state=target_state,
                initial_state={"repository_initialized": False},
            ),
        ),
        previous_state={"repository_initialized": False},
        next_state=target_state,
        executed_commands=["git switch -c recovery c0"],
    )

    result = StateRuleCompletionEvaluator().evaluate(context)

    assert result.result_category == RESULT_TARGET_MATCHED


def test_non_module4_completion_still_enforces_required_commands():
    state = {
        "repository_initialized": True,
        "commits": [{"id": "r0", "message": "Remote commit r0", "parents": []}],
        "branches": {"main": "r0"},
        "head": {"type": "branch", "name": "main"},
        "working_tree": {},
        "staging": {},
        "conflicts": [],
    }
    context = CompletionEvaluationContext(
        session=SimpleNamespace(
            learning_unit=SimpleNamespace(number=1),
            variant=SimpleNamespace(
                target_rule={"repository_initialized": True, "required_commands": ["git clone"]},
                target_state=state,
                initial_state={"repository_initialized": False},
            ),
        ),
        previous_state={"repository_initialized": False},
        next_state=state,
        executed_commands=["git init"],
    )

    result = StateRuleCompletionEvaluator().evaluate(context)

    assert result.result_category == RESULT_TARGET_NOT_YET_MATCHED


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
        "repository_state_unchanged_except": [
            "remotes",
            "remote_branches",
            "upstream_tracking",
            "reflog",
        ],
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


def test_evaluator_supports_module1_exact_state_rules():
    simulator = RepositoryStateSimulator()
    state = simulator.normalize_state(
        {
            "commits": [
                {"id": "c0", "message": "Base", "parents": [], "tree": {"src/auth.py": "auth-v1"}},
                {
                    "id": "c1",
                    "message": "WIP auth",
                    "parents": ["c0"],
                    "tree": {"src/auth.py": "auth-v2"},
                },
            ],
            "branches": {"main": "c1"},
            "head": {"type": "branch", "name": "main"},
            "working_tree": {
                "src/auth.py": {
                    "status": "modified",
                    "hunks": ["auth-validation-hunk", "auth-refactor-hunk"],
                },
                "debug.log": {"status": "ignored", "content": "debug-noise"},
            },
            "partial_hunks": {
                "src/auth.py": {
                    "target_hunks": ["auth-validation-hunk"],
                    "leftover_hunks": ["auth-refactor-hunk"],
                }
            },
            "staging": {},
        }
    )
    state = simulator.process(state, "git add -p src/auth.py").state
    state = simulator.process(state, 'git commit --amend -m "Validate auth input"').state

    rule = {
        "rules": [
            {"type": "commit_count_equals", "count": 3},
            {"type": "commit_count_on_branch_equals", "branch": "main", "count": 2},
            {
                "type": "operation_metadata_equals",
                "key": "last_amend_replaced_commit",
                "value": "c1",
            },
            {
                "type": "operation_metadata_not_equals",
                "key": "last_amend_created_commit",
                "value": "c1",
            },
            {
                "type": "operation_metadata_contains",
                "key": "last_amend_created_commit",
                "value": "c2",
            },
            {"type": "partial_hunks_committed", "paths": {"src/auth.py": ["auth-validation-hunk"]}},
            {
                "type": "partial_hunks_left_in_working_tree",
                "paths": {"src/auth.py": ["auth-refactor-hunk"]},
            },
            {"type": "commit_changes_exclude_tokens", "tokens": ["auth-refactor-hunk"]},
            {"type": "commit_tree_contains_tokens", "tokens": ["auth-validation-hunk"]},
            {"type": "working_tree_excludes_tokens", "tokens": ["auth-validation-hunk"]},
            {"type": "ignored_paths_present", "paths": ["debug.log"], "statuses": ["ignored"]},
            {"type": "commit_replaced_by_amend", "old": "c1", "new": "c2"},
            {"type": "branch_tip_replaces_commit", "branch": "main", "commit": "c1"},
            {"type": "commit_not_followed_by_extra_commit", "branch": "main", "commit": "c2"},
        ]
    }

    result = StateBasedEvaluator().evaluate(state, rule)

    assert result.result_category == RESULT_TARGET_MATCHED
    assert result.failed_rules == ()


def test_evaluator_checks_init_clone_and_tracked_generated_file_rules():
    simulator = RepositoryStateSimulator()
    init_state = simulator.process({"repository_initialized": False}, "git init research-log").state
    init_result = StateBasedEvaluator().evaluate(
        init_state,
        {
            "repository_initialized": True,
            "rules": [
                {"type": "commit_count_equals", "count": 0},
                {
                    "type": "operation_metadata_equals",
                    "key": "last_init_directory",
                    "value": "research-log",
                },
            ],
        },
    )

    clone_state = simulator.normalize_state(
        {
            "repository_initialized": False,
            "remote_fixtures": {
                "origin/main": "r10",
                "commits": [
                    {
                        "id": "r10",
                        "message": "Create docs portal starter",
                        "parents": [],
                        "tree": {"README.md": "docs-readme-v1"},
                    }
                ],
            },
        }
    )
    clone_state = simulator.process(
        clone_state,
        "git clone https://example.test/training/docs-portal.git docs-portal",
    ).state
    clone_result = StateBasedEvaluator().evaluate(
        clone_state,
        {
            "repository_initialized": True,
            "head_branch": "main",
            "remote_url_matches": {"origin": "https://example.test/training/docs-portal.git"},
            "branch_points_to": {"main": "r10"},
            "remote_branch_points_to": {"origin/main": "r10"},
            "upstream_tracking": {"main": "origin/main"},
            "working_tree_clean": True,
            "staging_empty": True,
            "rules": [
                {
                    "type": "operation_metadata_equals",
                    "key": "last_clone_destination",
                    "value": "docs-portal",
                },
                {
                    "type": "commit_tree_contains",
                    "commit": "r10",
                    "tree": {"README.md": "docs-readme-v1"},
                },
            ],
        },
    )

    rm_state = simulator.normalize_state(
        {
            "commits": [
                {
                    "id": "c0",
                    "message": "Base",
                    "parents": [],
                    "tree": {".env": "secret", ".gitignore": "*.env"},
                }
            ],
            "branches": {"main": "c0"},
            "head": {"type": "branch", "name": "main"},
            "working_tree": {},
            "staging": {},
        }
    )
    rm_state = simulator.process(rm_state, "git rm --cached .env").state
    rm_state = simulator.process(rm_state, 'git commit -m "Stop tracking env"').state
    rm_result = StateBasedEvaluator().evaluate(
        rm_state,
        {
            "rules": [
                {"type": "tracked_path_removed_from_commit_tree", "path": ".env"},
                {"type": "ignored_paths_present", "path": ".env"},
            ]
        },
    )

    assert init_result.result_category == RESULT_TARGET_MATCHED
    assert clone_result.result_category == RESULT_TARGET_MATCHED
    assert rm_result.result_category == RESULT_TARGET_MATCHED


def test_evaluator_checks_created_gitignore_patterns_and_ignored_paths():
    simulator = RepositoryStateSimulator()
    state = simulator.normalize_state(
        {
            "commits": [
                {
                    "id": "c0",
                    "message": "Base",
                    "parents": [],
                    "tree": {"README.md": "readme-v1"},
                }
            ],
            "branches": {"main": "c0"},
            "head": {"type": "branch", "name": "main"},
            "working_tree": {
                ".env": {"status": "untracked", "content": "SECRET=local"},
                "dist/app.js": {"status": "untracked", "content": "bundle"},
            },
            "staging": {},
        }
    )
    state = WorkspaceFileStateService().create_file(
        state,
        path=".gitignore",
        content=".env*\ndist/\n",
    )
    for command in ["git add .gitignore", 'git commit -m "Add ignore rules"']:
        state = simulator.process(state, command).state

    result = StateBasedEvaluator().evaluate(
        state,
        {
            "head_branch": "main",
            "staging_empty": True,
            "working_tree_clean": True,
            "latest_commit": {
                "branch": "main",
                "contains_paths": [".gitignore"],
                "excludes_paths": [".env", "dist/app.js"],
                "message_contains": ["Add ignore rules"],
            },
            "rules": [
                {
                    "type": "ignored_paths_present",
                    "paths": [".env", "dist/app.js"],
                    "statuses": ["ignored"],
                },
                {"type": "gitignore_matches_paths", "paths": [".env", "dist/app.js"]},
                {
                    "type": "commit_tree_contains",
                    "branch": "main",
                    "tree": {".gitignore": ".env*\ndist/\n"},
                },
            ],
        },
    )

    assert result.result_category == RESULT_TARGET_MATCHED
    assert result.failed_rules == ()


def test_rule_evaluator_checks_commit_message_changes_scope_and_clean_state():
    initial = {
        "commits": [
            {
                "id": "c1",
                "message": "Base",
                "parents": [],
                "tree": {"README.md": "readme-v1", "src/form.js": "form-validation-v1"},
            }
        ],
        "branches": {"main": "c1"},
        "head": {"type": "branch", "name": "main"},
        "working_tree": {"src/form.js": "form-validation-v2", "debug.log": "debug-v1"},
        "staging": {},
        "conflicts": [],
    }
    state = {
        **initial,
        "commits": [
            initial["commits"][0],
            {
                "id": "c2",
                "message": "Update form validation",
                "parents": ["c1"],
                "tree": {"README.md": "readme-v1", "src/form.js": "form-validation-v2"},
                "changes": {
                    "src/form.js": {
                        "change_type": "modified",
                        "before": "form-validation-v1",
                        "after": "form-validation-v2",
                    }
                },
            },
        ],
        "branches": {"main": "c2"},
        "head": {"type": "branch", "name": "main"},
        "working_tree": {},
        "staging": {},
    }
    rule = {
        "rules": [
            {"type": "head_branch_equals", "branch": "main"},
            {
                "type": "branch_tip_commit",
                "branch": "main",
                "message_contains": "form validation",
                "changes_include": ["src/form.js"],
                "changes_exclude": ["debug.log"],
                "parent_equals": "$initial.head_commit",
            },
            {"type": "index_empty"},
            {"type": "working_tree_clean"},
        ]
    }

    result = StateBasedEvaluator().evaluate(state, rule, initial_state=initial)

    assert result.result_category == RESULT_TARGET_MATCHED
    assert result.failed_rules == ()


def test_rule_evaluator_reports_failed_rule_diagnostics():
    state = {
        "commits": [
            {"id": "c0", "message": "Base", "parents": [], "files": {"README.md": "added"}}
        ],
        "branches": {"main": "c0"},
        "head": {"type": "branch", "name": "main"},
        "working_tree": {},
        "staging": {},
        "conflicts": [],
    }
    rule = {
        "rules": [{"type": "branch_tip_commit", "branch": "main", "changes_include": ["app.py"]}]
    }

    result = StateBasedEvaluator().evaluate(state, rule)

    assert result.result_category == RESULT_TARGET_NOT_YET_MATCHED
    assert result.failed_rules[0]["type"] == "branch_tip_commit"
    assert "missing" in result.failed_rules[0]["reason"].lower()


def test_rule_evaluator_supports_selective_staging_expectations():
    state = {
        "commits": [
            {
                "id": "c0",
                "message": "Base",
                "parents": [],
                "tree": {"app.py": "v1", "notes.md": "v1"},
            },
            {
                "id": "c1",
                "message": "Update app only",
                "parents": ["c0"],
                "tree": {"app.py": "v2", "notes.md": "v1"},
                "changes": {"app.py": {"change_type": "modified", "before": "v1", "after": "v2"}},
            },
        ],
        "branches": {"main": "c1"},
        "head": {"type": "branch", "name": "main"},
        "working_tree": {"notes.md": "draft-v2"},
        "staging": {},
        "conflicts": [],
    }
    rule = {
        "rules": [
            {
                "type": "branch_tip_commit",
                "branch": "main",
                "changes_include": ["app.py"],
                "changes_exclude": ["notes.md"],
            },
            {"type": "working_tree_contains", "path": "notes.md"},
            {"type": "index_empty"},
        ]
    }

    result = StateBasedEvaluator().evaluate(state, rule)

    assert result.result_category == RESULT_TARGET_MATCHED


def test_rule_evaluator_checks_branch_creation_from_initial_head():
    initial = {
        "commits": [{"id": "c0", "message": "Base", "parents": []}],
        "branches": {"main": "c0"},
        "head": {"type": "branch", "name": "main"},
        "working_tree": {},
        "staging": {},
        "conflicts": [],
    }
    state = {
        **initial,
        "branches": {"main": "c0", "feature/form": "c0"},
        "head": {"type": "branch", "name": "feature/form"},
    }
    rule = {
        "rules": [
            {"type": "branch_exists", "branch": "feature/form"},
            {"type": "head_branch_equals", "branch": "feature/form"},
            {
                "type": "branch_points_to",
                "branch": "feature/form",
                "commit": "$initial.head_commit",
            },
        ]
    }

    result = StateBasedEvaluator().evaluate(state, rule, initial_state=initial)

    assert result.result_category == RESULT_TARGET_MATCHED


def test_rule_evaluator_checks_merge_commit_and_conflict_state():
    simulator = RepositoryStateSimulator()
    state = simulator.normalize_state(
        {
            "commits": [
                {"id": "c0", "message": "Base", "parents": [], "tree": {"app.py": "base"}},
                {"id": "c1", "message": "Main", "parents": ["c0"], "tree": {"app.py": "main"}},
                {
                    "id": "c2",
                    "message": "Feature",
                    "parents": ["c0"],
                    "tree": {"app.py": "feature"},
                },
            ],
            "branches": {"main": "c1", "feature/app": "c2"},
            "head": {"type": "branch", "name": "main"},
            "working_tree": {},
            "staging": {},
            "conflicts": [],
        }
    )

    merged = simulator.normalize_state(
        {
            **state,
            "commits": [
                *state["commits"],
                {
                    "id": "c3",
                    "message": "Merge feature/app",
                    "parents": ["c1", "c2"],
                    "tree": {"app.py": "feature"},
                },
            ],
            "branches": {"main": "c3", "feature/app": "c2"},
        }
    )
    merge_result = StateBasedEvaluator().evaluate(
        merged,
        {
            "rules": [
                {
                    "type": "branch_tip_commit",
                    "branch": "main",
                    "parent_count_equals": 2,
                    "is_merge": True,
                },
                {"type": "conflict_free"},
            ]
        },
    )

    conflict_state = simulator.normalize_state(
        {**state, "conflict_on_merge": True, "conflict_files": ["app.py"]}
    )
    conflicted = simulator.normalize_state({**conflict_state, "conflicts": ["app.py"]})
    conflict_result = StateBasedEvaluator().evaluate(
        conflicted,
        {"rules": [{"type": "conflicts_contain_paths", "paths": ["app.py"]}]},
    )

    assert merge_result.result_category == RESULT_TARGET_MATCHED
    assert conflict_result.result_category == RESULT_TARGET_MATCHED


def test_rule_evaluator_distinguishes_reset_modes():
    simulator = RepositoryStateSimulator()
    state = simulator.normalize_state(
        {
            "commits": [
                {"id": "c0", "message": "Base", "parents": [], "tree": {"app.py": "v1"}},
                {"id": "c1", "message": "Update app", "parents": ["c0"], "tree": {"app.py": "v2"}},
            ],
            "branches": {"main": "c1"},
            "head": {"type": "branch", "name": "main"},
            "working_tree": {},
            "staging": {},
            "conflicts": [],
        }
    )

    soft = simulator.normalize_state(
        {**state, "branches": {"main": "c0"}, "staging": {"app.py": "v2"}}
    )
    mixed = simulator.normalize_state(
        {**state, "branches": {"main": "c0"}, "working_tree": {"app.py": "v2"}}
    )
    hard = simulator.normalize_state({**state, "branches": {"main": "c0"}})

    evaluator = StateBasedEvaluator()
    assert evaluator.evaluate(
        soft, {"rules": [{"type": "staging_contains", "path": "app.py"}]}
    ).target_matched
    assert evaluator.evaluate(
        mixed,
        {"rules": [{"type": "working_tree_contains", "path": "app.py"}, {"type": "index_empty"}]},
    ).target_matched
    assert evaluator.evaluate(
        hard, {"rules": [{"type": "working_tree_clean"}, {"type": "index_empty"}]}
    ).target_matched


def test_rule_evaluator_checks_restore_index_and_working_tree_effects():
    simulator = RepositoryStateSimulator()
    state = simulator.normalize_state(
        {
            "commits": [{"id": "c0", "message": "Base", "parents": [], "tree": {"app.py": "v1"}}],
            "branches": {"main": "c0"},
            "head": {"type": "branch", "name": "main"},
            "working_tree": {"app.py": "v2", "notes.md": "draft"},
            "staging": {"app.py": "v2"},
            "conflicts": [],
        }
    )

    unstaged = simulator.process(state, "git restore --staged app.py").state
    restored = simulator.process(unstaged, "git restore app.py").state
    evaluator = StateBasedEvaluator()

    assert evaluator.evaluate(
        unstaged,
        {
            "rules": [
                {"type": "staging_excludes", "path": "app.py"},
                {"type": "working_tree_contains", "path": "app.py"},
            ]
        },
    ).target_matched
    assert evaluator.evaluate(
        restored,
        {
            "rules": [
                {"type": "working_tree_absent", "path": "app.py"},
                {"type": "working_tree_contains", "path": "notes.md"},
            ]
        },
    ).target_matched


def test_rule_evaluator_checks_fetch_pull_and_push_state():
    simulator = RepositoryStateSimulator()
    state = simulator.normalize_state(
        {
            "commits": [{"id": "c0", "message": "Base", "parents": []}],
            "branches": {"main": "c0"},
            "head": {"type": "branch", "name": "main"},
            "working_tree": {},
            "staging": {},
            "conflicts": [],
            "remotes": {"origin": "https://example.test/app.git"},
            "remote_branches": {"origin/main": "c1"},
            "upstream_tracking": {"main": "origin/main"},
        }
    )
    evaluator = StateBasedEvaluator()

    fetched = simulator.normalize_state({**state, "remote_tracking_updated": True})
    pulled = simulator.normalize_state({**fetched, "branches": {"main": "c1"}})
    pushed = simulator.normalize_state(
        {**pulled, "remote_branches": {"origin/main": pulled["branches"]["main"]}}
    )

    assert evaluator.evaluate(
        fetched,
        {
            "rules": [
                {"type": "fetch_updated_remote_tracking_without_moving_local", "branch": "main"}
            ]
        },
        initial_state=state,
    ).target_matched
    assert evaluator.evaluate(
        pulled, {"rules": [{"type": "pull_moved_local_to_upstream", "branch": "main"}]}
    ).target_matched
    assert evaluator.evaluate(
        pushed, {"rules": [{"type": "push_moved_remote_to_local_tip", "branch": "main"}]}
    ).target_matched


def test_rule_evaluator_checks_stash_save_and_pop():
    simulator = RepositoryStateSimulator()
    state = simulator.normalize_state(
        {
            "commits": [{"id": "c0", "message": "Base", "parents": []}],
            "branches": {"main": "c0"},
            "head": {"type": "branch", "name": "main"},
            "working_tree": {"app.py": "v2"},
            "staging": {"README.md": "v2"},
            "conflicts": [],
        }
    )

    stashed = simulator.normalize_state(
        {
            **state,
            "working_tree": {},
            "staging": {},
            "stash_stack": [
                {
                    "working_tree": {"app.py": "v2"},
                    "staging": {"README.md": "v2"},
                    "conflicts": [],
                }
            ],
        }
    )
    popped = simulator.normalize_state(
        {
            **state,
            "stash_stack": [],
            "operation_metadata": {"last_stash_pop_restored_paths": ["app.py", "README.md"]},
        }
    )
    evaluator = StateBasedEvaluator()

    assert evaluator.evaluate(
        stashed,
        {
            "rules": [
                {"type": "stash_stack_contains_paths", "paths": ["app.py", "README.md"]},
                {"type": "working_tree_clean"},
                {"type": "index_empty"},
            ]
        },
    ).target_matched
    assert evaluator.evaluate(
        popped,
        {
            "rules": [
                {"type": "stash_stack_empty"},
                {"type": "stash_pop_restored_paths", "paths": ["app.py", "README.md"]},
            ]
        },
    ).target_matched


def test_rule_evaluator_normalizes_legacy_commit_files_for_changes_and_tree():
    state = {
        "commits": [
            {"id": "c0", "message": "Base", "parents": []},
            {
                "id": "c1",
                "message": "Legacy change",
                "parents": ["c0"],
                "files": {"legacy.txt": "legacy-v1"},
            },
        ],
        "branches": {"main": "c1"},
        "head": {"type": "branch", "name": "main"},
        "working_tree": {},
        "staging": {},
        "conflicts": [],
    }
    rule = {
        "rules": [
            {"type": "branch_tip_commit", "branch": "main", "changes_include": ["legacy.txt"]},
            {"type": "commit_tree_contains", "commit": "c1", "tree": {"legacy.txt": "legacy-v1"}},
        ]
    }

    result = StateBasedEvaluator().evaluate(state, rule)

    assert result.result_category == RESULT_TARGET_MATCHED
