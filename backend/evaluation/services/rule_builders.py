
from simulator.services import normalize_command


def _canonical_form(command: str) -> str:
    """Return the canonical normalized form of a command for comparison.

    git checkout -b <branch> [<start>] is semantically identical to
    git switch -c <branch> [<start>]; normalize both to the switch form so
    command_matches() accepts either spelling.
    """
    normalized = normalize_command(command).lower()
    # "git checkout -b <branch>" is equivalent to "git switch -c <branch>".
    parts = normalized.split()
    if len(parts) >= 3 and parts[1] == "checkout" and parts[2] == "-b":
        parts[1] = "switch"
        parts[2] = "-c"
        return " ".join(parts)
    return normalized

def command_matches(executed: str, required: str) -> bool:
    executed = _canonical_form(executed)
    required = _canonical_form(required)
    return executed == required or executed.startswith(f"{required} ")

def _each(spec: dict, key: str, rule_type: str, field: str) -> list[dict]:
    """One rule per item of a list-valued spec key."""
    return [{"type": rule_type, field: item} for item in spec.get(key, [])]

def _pairs(spec: dict, key: str, rule_type: str, left: str, right: str) -> list[dict]:
    """One rule per entry of a mapping-valued spec key."""
    return [{"type": rule_type, left: k, right: v} for k, v in spec.get(key, {}).items()]

def _flag(spec: dict, key: str, rule_type: str) -> list[dict]:
    """A bare rule when a boolean spec key is truthy."""
    return [{"type": rule_type}] if spec.get(key) else []

def _presence_bool(spec: dict, key: str, rule_type: str) -> list[dict]:
    """A valued rule whenever the key is present - False is a real requirement."""
    return [{"type": rule_type, "value": bool(spec[key])}] if key in spec else []

def _command_rules(spec: dict) -> list[dict]:
    return [
        *_each(spec, "required_commands", "required_command", "command"),
        *_each(spec, "forbidden_commands", "forbidden_command", "command"),
    ]

def _branch_rules(spec: dict) -> list[dict]:
    return [
        *_presence_bool(spec, "repository_initialized", "repository_initialized"),
        *_each(spec, "branch_exists", "branch_exists", "branch"),
        *_each(spec, "branch_absent", "branch_absent", "branch"),
        *_pairs(spec, "branch_points_to", "branch_points_to", "branch", "commit"),
        *_pairs(
            spec, "remote_branch_points_to", "remote_branch_points_to", "remote_branch", "commit"
        ),
        *(
            [{"type": "head_branch_equals", "branch": spec["head_branch"]}]
            if spec.get("head_branch")
            else []
        ),
        # Variant-safe branch/HEAD predicates: levels whose variants differ only
        # by branch name can still assert the *shape* of the change (a branch was
        # created/deleted, HEAD detached or moved off its starting branch)
        # without naming the variant-specific branch.
        *_flag(spec, "head_detached", "head_detached"),
        *_flag(spec, "head_branch_changed", "head_branch_changed"),
        *(
            [{"type": "local_branches_min", "minimum": spec["local_branches_min"]}]
            if "local_branches_min" in spec
            else []
        ),
        *(
            [{"type": "local_branches_at_most", "maximum": spec["local_branches_at_most"]}]
            if "local_branches_at_most" in spec
            else []
        ),
    ]

def _remote_rules(spec: dict) -> list[dict]:
    return [
        *_each(spec, "remote_exists", "remote_exists", "remote"),
        *_each(spec, "remote_branch_exists", "remote_branch_exists", "remote_branch"),
        *_each(spec, "remote_branch_absent", "remote_branch_absent", "remote_branch"),
        *_each(spec, "upstream_tracking_set", "upstream_tracking_set", "branch"),
        *_pairs(spec, "remote_url_matches", "remote_url_matches", "remote", "url"),
        *_pairs(spec, "upstream_tracking", "upstream_tracking_equals", "branch", "upstream"),
        *_presence_bool(spec, "remote_tracking_updated", "remote_tracking_updated"),
        *_pairs(
            spec,
            "remote_branch_matches_local",
            "remote_branch_matches_local",
            "remote_branch",
            "branch",
        ),
    ]

def _cleanliness_rules(spec: dict) -> list[dict]:
    stash_required = spec.get("stash_stack_empty") or spec.get("stash_stack_empty_after_pop")
    return [
        *_flag(spec, "working_tree_clean", "working_tree_clean"),
        *_flag(spec, "staging_empty", "index_empty"),
        *_flag(spec, "conflict_free", "conflict_free"),
        # Inverse cleanliness flags: needed for variant-safe objective checks on
        # levels whose variants differ only by the path acted on (e.g. stage one
        # hunk, stage a removal) - "something is staged"/"work is left unstaged"
        # captures the goal without naming the variant-specific path.
        *_flag(spec, "staging_not_empty", "staging_not_empty"),
        *_flag(spec, "working_tree_dirty", "working_tree_dirty"),
        *([{"type": "stash_stack_empty"}] if stash_required else []),
    ]

def _commit_graph_rules(spec: dict) -> list[dict]:
    return [
        *_pairs(spec, "min_commits_on_branch", "min_commits_on_branch", "branch", "minimum"),
        *(
            {"type": "branches_equal", "left": left, "right": right}
            for left, right in spec.get("branches_equal", [])
        ),
    ]

def _path_rules(spec: dict) -> list[dict]:
    return [
        *_each(spec, "working_tree_contains", "working_tree_contains", "path"),
        *_each(spec, "working_tree_absent", "working_tree_absent", "path"),
        *_each(spec, "staging_contains", "staging_contains", "path"),
    ]

def _history_rules(spec: dict) -> list[dict]:
    latest_commit = spec.get("latest_commit", {})
    return [
        *(
            [
                {
                    "type": "branch_tip_commit",
                    "branch": latest_commit.get("branch"),
                    "changes_include": latest_commit.get("contains_paths", []),
                    "changes_exclude": latest_commit.get("excludes_paths", []),
                    "message_contains": latest_commit.get("message_contains", []),
                }
            ]
            if latest_commit
            else []
        ),
        *_each(spec, "reflog_contains", "reflog_contains", "expected"),
    ]

def _invariance_rules(spec: dict) -> list[dict]:
    return [
        *_flag(spec, "repository_state_unchanged", "repository_state_unchanged"),
        *(
            [
                {
                    "type": "repository_state_unchanged_except",
                    "except": spec["repository_state_unchanged_except"],
                }
            ]
            if spec.get("repository_state_unchanged_except")
            else []
        ),
    ]

def rules_from_state_requirements(state_requirements: dict | None) -> list[dict]:
    """Expand a seed-authored state_requirements spec into flat rule dicts.

    Module-level so non-evaluation callers (e.g. the battle layer deriving
    monster HP from "distance to target") can count rules without instantiating
    an evaluator. Group order is part of the contract (pinned by
    test_rule_builders): the failed-rules list surfaces to learners in spec order.
    """
    spec = state_requirements or {}
    return [
        *(dict(rule) for rule in spec.get("rules", [])),
        *_command_rules(spec),
        *_branch_rules(spec),
        *_remote_rules(spec),
        *_cleanliness_rules(spec),
        *_commit_graph_rules(spec),
        *_path_rules(spec),
        *_history_rules(spec),
        *_invariance_rules(spec),
    ]
