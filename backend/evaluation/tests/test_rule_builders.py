"""Pins the state_requirements -> rules expansion of StateBasedEvaluator.

Every seed-spec key must keep producing the same rule dicts in the same order;
this is the contract the rule-builder decomposition must preserve.
"""

from evaluation.services import StateBasedEvaluator


def rules_for(spec):
    return StateBasedEvaluator()._rules_from_state_requirements(spec)


def test_empty_spec_yields_no_rules():
    assert rules_for({}) == []


def test_raw_rules_pass_through_copied():
    raw = {"type": "custom", "x": 1}
    rules = rules_for({"rules": [raw]})
    assert rules == [raw]
    assert rules[0] is not raw  # defensive copy


def test_full_spec_expansion_order_and_shapes():
    spec = {
        "rules": [{"type": "custom"}],
        "required_commands": ["git add ."],
        "forbidden_commands": ["git push --force"],
        "repository_initialized": True,
        "branch_exists": ["main"],
        "branch_absent": ["scratch"],
        "branch_points_to": {"main": "c3"},
        "remote_branch_points_to": {"origin/main": "c3"},
        "head_branch": "main",
        "remote_exists": ["origin"],
        "remote_branch_exists": ["origin/main"],
        "remote_branch_absent": ["origin/scratch"],
        "upstream_tracking_set": ["main"],
        "remote_url_matches": {"origin": "https://example.test/repo.git"},
        "upstream_tracking": {"main": "origin/main"},
        "remote_tracking_updated": True,
        "remote_branch_matches_local": {"origin/main": "main"},
        "working_tree_clean": True,
        "staging_empty": True,
        "conflict_free": True,
        "stash_stack_empty": True,
        "min_commits_on_branch": {"main": 2},
        "branches_equal": [["main", "feature"]],
        "working_tree_contains": ["notes.txt"],
        "working_tree_absent": ["secret.txt"],
        "staging_contains": ["staged.txt"],
        "latest_commit": {
            "branch": "main",
            "contains_paths": ["notes.txt"],
            "excludes_paths": ["secret.txt"],
            "message_contains": ["docs"],
        },
        "reflog_contains": ["checkout"],
        "repository_state_unchanged": True,
        "repository_state_unchanged_except": ["head"],
    }
    assert rules_for(spec) == [
        {"type": "custom"},
        {"type": "required_command", "command": "git add ."},
        {"type": "forbidden_command", "command": "git push --force"},
        {"type": "repository_initialized", "value": True},
        {"type": "branch_exists", "branch": "main"},
        {"type": "branch_absent", "branch": "scratch"},
        {"type": "branch_points_to", "branch": "main", "commit": "c3"},
        {"type": "remote_branch_points_to", "remote_branch": "origin/main", "commit": "c3"},
        {"type": "head_branch_equals", "branch": "main"},
        {"type": "remote_exists", "remote": "origin"},
        {"type": "remote_branch_exists", "remote_branch": "origin/main"},
        {"type": "remote_branch_absent", "remote_branch": "origin/scratch"},
        {"type": "upstream_tracking_set", "branch": "main"},
        {"type": "remote_url_matches", "remote": "origin", "url": "https://example.test/repo.git"},
        {"type": "upstream_tracking_equals", "branch": "main", "upstream": "origin/main"},
        {"type": "remote_tracking_updated", "value": True},
        {"type": "remote_branch_matches_local", "remote_branch": "origin/main", "branch": "main"},
        {"type": "working_tree_clean"},
        {"type": "index_empty"},
        {"type": "conflict_free"},
        {"type": "stash_stack_empty"},
        {"type": "min_commits_on_branch", "branch": "main", "minimum": 2},
        {"type": "branches_equal", "left": "main", "right": "feature"},
        {"type": "working_tree_contains", "path": "notes.txt"},
        {"type": "working_tree_absent", "path": "secret.txt"},
        {"type": "staging_contains", "path": "staged.txt"},
        {
            "type": "branch_tip_commit",
            "branch": "main",
            "changes_include": ["notes.txt"],
            "changes_exclude": ["secret.txt"],
            "message_contains": ["docs"],
        },
        {"type": "reflog_contains", "expected": "checkout"},
        {"type": "repository_state_unchanged"},
        {"type": "repository_state_unchanged_except", "except": ["head"]},
    ]


def test_repository_initialized_false_still_emits_rule():
    assert rules_for({"repository_initialized": False}) == [
        {"type": "repository_initialized", "value": False}
    ]


def test_falsy_flags_emit_nothing():
    spec = {
        "working_tree_clean": False,
        "staging_empty": False,
        "conflict_free": False,
        "stash_stack_empty": False,
        "head_branch": "",
        "repository_state_unchanged": False,
        "latest_commit": {},
    }
    assert rules_for(spec) == []


def test_stash_rule_emitted_once_for_either_or_both_keys():
    assert rules_for({"stash_stack_empty": True}) == [{"type": "stash_stack_empty"}]
    assert rules_for({"stash_stack_empty_after_pop": True}) == [{"type": "stash_stack_empty"}]
    assert rules_for(
        {"stash_stack_empty": True, "stash_stack_empty_after_pop": True}
    ) == [{"type": "stash_stack_empty"}]
