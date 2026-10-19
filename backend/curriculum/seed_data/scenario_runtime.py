"""Join the current scenario contract to deterministic simulator fixtures.

The level scaffold supplies repository setup for each exercise. Authored IDs,
commands, file edits, budgets, and learner content come from the scenario bank.
Exercises with a different repository shape receive a focused runtime override.
"""

from __future__ import annotations

import copy
import shlex
from typing import Any

from curriculum.seed_data.scenario_bank import scenario_bank

DISPLACED_REVISED_CASE_IDS = {
    "bh8": "rebase-hard-continue",
    "bm8": "rebase-medium-abort",
    "cherry-hard-abort": "cherry-hard-abort-conflict",
    "cherry-hard-export-null": "cherry-hard-export-conflict",
    "cherry-hard-queue-finalize": "cherry-hard-trace-source",
    "cherry-hard-rate-limit": "cherry-hard-two-releases",
    "init-medium-quiet-research-log": "init-medium-existing-files",
    "manual-hard-medium-carryover": "manual-hard-abort-redo",
    "mergetool-easy-auth-copy": "mergetool-easy-cache-ttl",
    "mergetool-easy-billing-copy": "mergetool-easy-upload-limit",
    "mergetool-easy-config-copy": "mergetool-easy-app-locale",
    "mergetool-easy-navbar-copy": "mergetool-easy-labels",
    "mergetool-easy-profile-copy": "mergetool-easy-mail-footer",
    "mergetool-hard-medium-carryover": "mergetool-hard-no-leftovers",
    "mergetool-hard-migration": "mergetool-hard-take-theirs",
    "mergetool-hard-pricing": "mergetool-hard-choose-tool",
    "mergetool-hard-schema": "mergetool-hard-one-of-two",
    "mergetool-medium-easy-carryover": "mergetool-medium-docs-sync",
    "mergetool-medium-gateway": "mergetool-medium-db-names",
    "mergetool-medium-policy": "mergetool-medium-api-limits",
    "mergetool-medium-router": "mergetool-medium-checkout-copy",
}


def _state(
    commits: list[dict[str, Any]],
    branches: dict[str, str | None],
    head: str,
    **extra: Any,
) -> dict[str, Any]:
    return {
        "repository_initialized": True,
        "commits": commits,
        "branches": branches,
        "head": {"type": "branch", "name": head},
        "staging": {},
        "working_tree": {},
        "conflicts": [],
        **extra,
    }


def _commit(commit_id: str, message: str, parents: list[str], tree: dict[str, str]) -> dict:
    return {"id": commit_id, "message": message, "parents": parents, "tree": tree}


def _clean_requirements(head: str, *rules: dict[str, Any]) -> dict[str, Any]:
    return {
        "head_branch": head,
        "conflict_free": True,
        "staging_empty": True,
        "working_tree_clean": True,
        "rules": list(rules),
    }


def _init_existing_files() -> dict[str, Any]:
    return {
        "initial_state": {
            "repository_initialized": False,
            "commits": [],
            "branches": {},
            "head": {"type": "branch", "name": "main"},
            "staging": {},
            "working_tree": {
                "field-notes/notes.txt": {
                    "status": "untracked",
                    "content": "Field observations\n",
                },
                "field-notes/data.csv": {
                    "status": "untracked",
                    "content": "date,value\n2026-10-17,1\n",
                },
            },
            "conflicts": [],
        },
        "state_requirements": {
            "repository_initialized": True,
            "head_branch": "main",
            "staging_empty": True,
            "rules": [
                {"type": "commit_count_equals", "count": 0},
                {
                    "type": "operation_metadata_path_matches",
                    "key": "last_init_directory",
                    "value": "field-notes",
                },
                {
                    "type": "working_tree_matches_exact_paths",
                    "paths": ["field-notes/notes.txt", "field-notes/data.csv"],
                },
                {
                    "type": "working_tree_contains_tokens",
                    "tokens": ["Field observations", "date,value", "2026-10-17,1"],
                },
            ],
        },
    }


def _manual_abort_redo() -> dict[str, Any]:
    path = "src/routes.ts"
    base = {path: "route('/help')"}
    main = {path: "route('/support')"}
    legacy = {path: "route('/legacy-help')"}
    help_center = {path: "route('/help-center')"}
    commits = [
        _commit("c0", "Base routes", [], base),
        _commit("c1", "Main support route", ["c0"], main),
        _commit("c2", "Legacy help route", ["c0"], legacy),
        _commit("c3", "Help center route", ["c0"], help_center),
    ]
    branches = {"main": "c1", "feature/legacy-help": "c2", "feature/help-center": "c3"}
    clean = _state(commits, branches, "main")
    conflicted = copy.deepcopy(clean)
    conflicted.update(
        {
            "merge_parent": "c2",
            "merge_abort_state": clean,
            "conflicts": [path],
            "conflict_details": {
                path: {
                    "base": base[path],
                    "ours": main[path],
                    "theirs": legacy[path],
                    "merge_branch": "feature/legacy-help",
                }
            },
            "working_tree": {
                path: {
                    "status": "conflicted",
                    "content": (
                        "<<<<<<< HEAD\nroute('/support')\n=======\n"
                        "route('/legacy-help')\n>>>>>>> feature/legacy-help\n"
                    ),
                }
            },
            "operation_metadata": {
                "last_merge_branch": "feature/legacy-help",
                "last_merge_target": "c2",
                "last_merge_conflicted": True,
            },
        }
    )
    required = "route('/support')\nroute('/help-center')"
    return {
        "initial_state": conflicted,
        "state_requirements": _clean_requirements(
            "main",
            {"type": "commit_is_merge", "branch": "main"},
            {"type": "commit_has_parent", "branch": "main", "parent": "c3"},
            {"type": "branch_history_excludes", "branch": "main", "commits": ["c2"]},
            {"type": "commit_tree_contains", "branch": "main", "tree": {path: required}},
        ),
    }


def _mergetool_case(
    *,
    branch: str,
    required_files: list[dict[str, str]],
    incoming_is_required: bool = False,
    extra_incoming: dict[str, str] | None = None,
) -> dict[str, Any]:
    paths = [item["path"] for item in required_files]
    base = {path: f"base value for {path}" for path in paths}
    ours = {path: f"main value for {path}" for path in paths}
    theirs = {
        item["path"]: item["content"]
        if incoming_is_required
        else f"feature value for {item['path']}"
        for item in required_files
    }
    if extra_incoming:
        base.update({path: "old" for path in extra_incoming})
        ours.update({path: "old" for path in extra_incoming})
        theirs.update(extra_incoming)
    commits = [
        _commit("c0", "Common base", [], base),
        _commit("c1", "Main updates", ["c0"], ours),
        _commit("c2", f"Updates on {branch}", ["c0"], theirs),
    ]
    required_tree = {
        **{item["path"]: item["content"] for item in required_files},
        **(extra_incoming or {}),
    }
    rules: list[dict[str, Any]] = [
        {"type": "commit_is_merge", "branch": "main"},
        {"type": "commit_has_parent", "branch": "main", "parent": "c2"},
        {"type": "commit_tree_contains", "branch": "main", "tree": required_tree},
        {
            "type": "operation_metadata_equals",
            "key": "last_mergetool_opened",
            "value": True,
        },
    ]
    if branch == "feature/i18n-refresh":
        rules = [
            rule
            for rule in rules
            if not (
                rule.get("type") == "operation_metadata_equals"
                and rule.get("key") == "last_mergetool_opened"
            )
        ]
    return {
        "initial_state": _state(
            commits,
            {"main": "c1", branch: "c2"},
            "main",
            conflict_on_merge=True,
            conflict_files=paths,
        ),
        "state_requirements": _clean_requirements("main", *rules),
    }


def _cherry_conflict() -> dict[str, Any]:
    path = "src/export.py"
    base = {path: "def export(rows):\n    return rows"}
    source = {path: "def export(rows):\n    return [r for r in rows if r is not None]"}
    release = {path: "def export(rows):\n    return list(rows)"}
    required = source[path]
    commits = [
        _commit("c0", "Export baseline", [], base),
        _commit("c1", "Skip null export rows", ["c0"], source),
        _commit("c2", "Main continues", ["c1"], {**source, "README.md": "main"}),
        _commit("c3", "Release export adjustment", ["c0"], release),
    ]
    return {
        "initial_state": _state(
            commits,
            {"main": "c2", "release-2.0": "c3"},
            "release-2.0",
            cherry_pick_conflict_files=[path],
        ),
        "state_requirements": _clean_requirements(
            "release-2.0",
            {"type": "cherry_pick_created_new_commit"},
            {"type": "cherry_pick_copied_changes_from", "commit": "c1"},
            {"type": "commit_tree_contains", "branch": "release-2.0", "tree": {path: required}},
        ),
    }


def _cherry_invoice_rounding() -> dict[str, Any]:
    base = {"src/invoice.py": "invoice-base"}
    fixed = {"src/invoice.py": "rounding-fix-v1"}
    commits = [
        _commit("c0", "Baseline", [], base),
        _commit("c1", "Fix rounding", ["c0"], fixed),
        _commit("c2", "Main continues", ["c1"], {**fixed, "src/other.py": "other-v1"}),
        _commit("c3", "Release branch base", ["c0"], base),
    ]
    return {
        "initial_state": _state(
            commits,
            {"main": "c2", "release-1.1": "c3", "feature/invoice-rounding": "c1"},
            "release-1.1",
        ),
        "state_requirements": _clean_requirements(
            "release-1.1",
            {"type": "cherry_pick_created_new_commit"},
            {"type": "cherry_pick_copied_changes_from", "commit": "c1"},
            {"type": "commit_tree_contains", "branch": "release-1.1", "tree": fixed},
        ),
    }


def _reflog_recovery(branch: str) -> dict[str, Any]:
    commits = [
        _commit("c0", "Reset position", [], {"src/search.py": "baseline"}),
        _commit("c1", "Search groundwork", ["c0"], {"src/search.py": "groundwork"}),
        _commit("c2", "Continue search work", ["c1"], {"src/search.py": "continued"}),
        _commit("c3", "Fix borrower search", ["c2"], {"src/search.py": "borrower search fix"}),
        _commit(
            "c4",
            "Abandoned search experiment",
            ["c2"],
            {"src/search.py": "abandoned search experiment"},
        ),
    ]
    return {
        "initial_state": _state(
            commits,
            {"main": "c0"},
            "main",
            reflog=[
                {"ref": "main", "commit": "c4", "action": "checkout"},
                {"ref": "main", "commit": "c3", "action": "commit"},
                {"ref": "main", "commit": "c0", "action": "reset: moving to HEAD~3"},
            ],
        ),
        "state_requirements": _clean_requirements(
            branch,
            {"type": "branch_points_to", "branch": branch, "commit": "c3"},
            {"type": "branch_points_to", "branch": "main", "commit": "c0"},
            {
                "type": "required_command_sequence",
                "commands": ["git show c4", "git show c3"],
            },
        ),
    }


def _cherry_abort() -> dict[str, Any]:
    path = "src/search.py"
    base = {path: "query = 'base'"}
    source = {path: "query = 'fixed'"}
    release = {path: "query = 'release'"}
    commits = [
        _commit("c0", "Search baseline", [], base),
        _commit("c1", "Fix search query", ["c0"], source),
        _commit("c2", "Main continues", ["c1"], {**source, "README.md": "main"}),
        _commit("c3", "Release search", ["c0"], release),
    ]
    return {
        "initial_state": _state(
            commits,
            {"main": "c2", "release-abort": "c3"},
            "release-abort",
            cherry_pick_in_progress=True,
            cherry_pick_original_head="c3",
            cherry_pick_source="c1",
            staging={"README.md": {"status": "added", "content": "partial patch"}},
            conflicts=[path],
            conflict_details={
                path: {"base": base[path], "ours": release[path], "theirs": source[path]}
            },
            working_tree={
                path: {
                    "status": "conflicted",
                    "content": "<<<<<<< HEAD\nquery = 'release'\n=======\nquery = 'fixed'\n>>>>>>> c1\n",
                }
            },
        ),
        "state_requirements": _clean_requirements(
            "release-abort",
            {"type": "branch_points_to", "branch": "release-abort", "commit": "c3"},
            {"type": "cherry_pick_not_in_progress"},
        ),
    }


def _cherry_trace_source() -> dict[str, Any]:
    commits = [
        _commit("c0", "Queue baseline", [], {"src/queue.ts": "base"}),
        _commit("c1", "Fix queue delivery", ["c0"], {"src/queue.ts": "fixed"}),
        _commit("c2", "Main continues", ["c1"], {"src/queue.ts": "fixed", "README.md": "main"}),
        _commit("c3", "Release baseline", ["c0"], {"src/queue.ts": "base"}),
    ]
    return {
        "initial_state": _state(
            commits,
            {"main": "c2", "release-finalize": "c3"},
            "release-finalize",
        ),
        "state_requirements": _clean_requirements(
            "release-finalize",
            {"type": "cherry_pick_created_new_commit"},
            {"type": "cherry_pick_copied_changes_from", "commit": "c1"},
            {"type": "latest_commit_message_contains", "text": "cherry picked from commit c1"},
        ),
    }


def _cherry_two_releases() -> dict[str, Any]:
    base = {"src/ratelimit.py": "limit = 100"}
    fixed = {"src/ratelimit.py": "limit = 60"}
    commits = [
        _commit("c0", "Rate limit baseline", [], base),
        _commit("c1", "Fix rate limit", ["c0"], fixed),
        _commit("c2", "Main continues", ["c1"], {**fixed, "README.md": "main"}),
        _commit("c3", "Release 1.2 baseline", ["c0"], {**base, "release.txt": "1.2"}),
        _commit("c4", "Release 1.1 baseline", ["c0"], {**base, "release.txt": "1.1"}),
    ]
    return {
        "initial_state": _state(
            commits,
            {"main": "c2", "release-1.2": "c3", "release-1.1": "c4"},
            "main",
        ),
        "state_requirements": _clean_requirements(
            "release-1.1",
            {"type": "commit_count_on_branch_equals", "branch": "release-1.2", "count": 3},
            {"type": "commit_count_on_branch_equals", "branch": "release-1.1", "count": 3},
            {"type": "commit_tree_contains", "branch": "release-1.2", "tree": fixed},
            {"type": "commit_tree_contains", "branch": "release-1.1", "tree": fixed},
            {"type": "branch_points_to", "branch": "main", "commit": "c2"},
        ),
    }


def _rebase_abort() -> dict[str, Any]:
    commits = [
        _commit("c0", "Export baseline", [], {"src/export.py": "export = 'base'"}),
        _commit("c1", "Main export update", ["c0"], {"src/export.py": "export = 'main'"}),
        _commit("c2", "Add PDF export", ["c0"], {"src/export.py": "export = 'pdf'"}),
        _commit(
            "c3",
            "Document PDF export",
            ["c2"],
            {"src/export.py": "export = 'pdf'", "docs/pdf.md": "PDF"},
        ),
        _commit(
            "c4", "Partially replay PDF export", ["c1"], {"src/export.py": "export = 'partial'"}
        ),
    ]
    original = _state(
        commits[:4],
        {"main": "c1", "feature/export-pdf": "c3"},
        "feature/export-pdf",
    )
    stopped = _state(
        commits,
        {"main": "c1", "feature/export-pdf": "c4"},
        "feature/export-pdf",
        conflicts=["src/export.py"],
        working_tree={
            "src/export.py": {
                "status": "conflicted",
                "content": "<<<<<<< HEAD\nexport = 'main'\n=======\nexport = 'pdf'\n>>>>>>> c2\n",
            }
        },
        rebase_state={
            "abort_state": original,
            "current_source": "c2",
            "remaining": ["c3"],
            "applied": [],
            "branch": "feature/export-pdf",
        },
    )
    return {
        "initial_state": stopped,
        "state_requirements": _clean_requirements(
            "feature/export-pdf",
            {"type": "rebase_not_in_progress"},
            {"type": "branch_points_to", "branch": "feature/export-pdf", "commit": "c3"},
        ),
    }


def _rebase_continue() -> dict[str, Any]:
    path = "src/limiter.py"
    base = {path: "LIMIT_NAME = 'legacy'"}
    main = {path: "LIMIT_NAME = 'api'"}
    feature = {path: "LIMIT_NAME = 'legacy'\nRETRY_COUNT = 3"}
    commits = [
        _commit("c0", "Limiter baseline", [], base),
        _commit("c1", "Name the API limit", ["c0"], main),
        _commit("c2", "Add retry count", ["c0"], feature),
        _commit("c3", "Document rate limits", ["c2"], {**feature, "docs/limits.md": "limits"}),
    ]
    original = _state(
        commits,
        {"main": "c1", "feature/rate-limits": "c3"},
        "feature/rate-limits",
    )
    stopped = _state(
        commits,
        {"main": "c1", "feature/rate-limits": "c1"},
        "feature/rate-limits",
        conflicts=[path],
        conflict_details={
            path: {
                "base": base[path],
                "ours": main[path],
                "theirs": feature[path],
            }
        },
        working_tree={
            path: {
                "status": "conflicted",
                "content": (
                    "<<<<<<< HEAD\nLIMIT_NAME = 'api'\n=======\n"
                    "LIMIT_NAME = 'legacy'\nRETRY_COUNT = 3\n>>>>>>> c2\n"
                ),
            }
        },
        rebase_state={
            "abort_state": original,
            "current_source": "c2",
            "remaining": ["c3"],
            "applied": [],
            "branch": "feature/rate-limits",
            "target": "c1",
        },
    )
    required = "LIMIT_NAME = 'api'\nRETRY_COUNT = 3"
    return {
        "initial_state": stopped,
        "state_requirements": _clean_requirements(
            "feature/rate-limits",
            {"type": "rebase_not_in_progress"},
            {
                "type": "branch_history_contains",
                "branch": "feature/rate-limits",
                "commits": ["c1"],
            },
            {
                "type": "commit_tree_contains",
                "branch": "feature/rate-limits",
                "tree": {path: required, "docs/limits.md": "limits"},
            },
            {
                "type": "commit_count_on_branch_equals",
                "branch": "feature/rate-limits",
                "count": 4,
            },
        ),
    }


def _runtime_overrides() -> dict[str, dict[str, Any]]:
    content = scenario_bank()
    mergetool_specs = {
        "mergetool-easy-cache-ttl": ("feature/cache-ttl", False, None),
        "mergetool-easy-mail-footer": ("feature/mail-footer", False, None),
        "mergetool-easy-upload-limit": ("feature/upload-limit", False, None),
        "mergetool-easy-app-locale": ("feature/app-locale", False, None),
        "mergetool-easy-labels": ("feature/labels-fil", False, None),
        "mergetool-medium-checkout-copy": ("feature/checkout-copy", False, None),
        "mergetool-medium-api-limits": ("feature/api-limits", False, None),
        "mergetool-medium-db-names": ("feature/db-rename", False, None),
        "mergetool-medium-docs-sync": ("feature/docs-sync", False, None),
        "mergetool-hard-choose-tool": ("feature/pricing-v2", False, None),
        "mergetool-hard-one-of-two": (
            "feature/release-notes",
            False,
            {"docs/release.md": "Release 2.1 notes"},
        ),
        "mergetool-hard-take-theirs": ("feature/i18n-refresh", True, None),
        "mergetool-hard-no-leftovers": ("feature/auth-timeout", False, None),
    }
    overrides: dict[str, dict[str, Any]] = {
        "init-medium-existing-files": _init_existing_files(),
        "manual-hard-abort-redo": _manual_abort_redo(),
        "cherry-medium-invoice-rounding": _cherry_invoice_rounding(),
        "cherry-hard-export-conflict": _cherry_conflict(),
        "cherry-hard-abort-conflict": _cherry_abort(),
        "cherry-hard-trace-source": _cherry_trace_source(),
        "cherry-hard-two-releases": _cherry_two_releases(),
        "rebase-medium-abort": _rebase_abort(),
        "rebase-hard-continue": _rebase_continue(),
    }
    for suffix in range(1, 6):
        case_id = f"h{suffix}"
        overrides[case_id] = _reflog_recovery(f"recovery/{case_id}")
    for case_id, (branch, incoming_is_required, extra_incoming) in mergetool_specs.items():
        overrides[case_id] = _mergetool_case(
            branch=branch,
            required_files=content[case_id]["required_files"],
            incoming_is_required=incoming_is_required,
            extra_incoming=extra_incoming,
        )
    return overrides


RUNTIME_OVERRIDES = _runtime_overrides()


def _commit_message(commands: list[str]) -> str | None:
    for command in reversed(commands):
        parts = shlex.split(command)
        if len(parts) < 3 or parts[:2] != ["git", "commit"] or "-m" not in parts:
            continue
        index = parts.index("-m")
        if index + 1 < len(parts):
            return parts[index + 1]
    return None


def _canonicalize_requirements(case: dict[str, Any]) -> None:
    """Remove assertions tied to the archived answer instead of the revised one."""

    case_id = case["case_id"]
    requirements = copy.deepcopy(case.get("state_requirements") or {})
    rules = list(requirements.get("rules") or [])

    if case_id.startswith("init-") and not any(
        token in command.split()
        for command in case["solution_commands"]
        for token in ("-q", "--quiet")
    ):
        rules = [
            rule
            for rule in rules
            if not (
                rule.get("type") == "operation_metadata_equals"
                and rule.get("key") == "last_init_quiet"
            )
        ]

    if case_id.startswith("partial-"):
        message = _commit_message(case["solution_commands"])
        if message and isinstance(requirements.get("latest_commit"), dict):
            requirements["latest_commit"]["message_contains"] = [message]

    expanded_rules: list[dict[str, Any]] = []
    resolved_files = {
        item["path"]: item["content"]
        for item in case.get("solution_workspace_files") or []
        if item.get("mode") == "write" and item.get("path")
    }
    for rule in rules:
        if rule.get("type") != "merge_commit_contains_tree":
            expanded_rules.append(rule)
            continue
        branch = requirements.get("head_branch") or case["initial_state"]["head"]["name"]
        expanded_rules.extend(
            [
                {"type": "commit_is_merge", "branch": branch},
                {
                    "type": "commit_tree_contains",
                    "branch": branch,
                    "tree": copy.deepcopy(resolved_files or rule.get("tree") or {}),
                },
            ]
        )
    requirements["rules"] = expanded_rules

    if case_id == "v21h-from-develop":
        requirements = {
            "head_branch": "feature/workspace",
            "branch_points_to": {"feature/workspace": "c2"},
            "staging_empty": True,
            "working_tree_clean": True,
        }
    elif case_id == "cherry-medium-login-timeout":
        requirements = _clean_requirements(
            "release-1.0",
            {"type": "commit_count_on_branch_equals", "branch": "release-1.0", "count": 4},
            {
                "type": "commit_tree_contains",
                "branch": "release-1.0",
                "tree": {"src/login.js": "timeout-fix-v1", "src/other.js": "other-v1"},
            },
        )
    elif case_id in {f"e{index}" for index in range(1, 6)} | {f"m{index}" for index in range(1, 6)}:
        branch = f"recovery/{case_id}"
        main_tip = case["initial_state"]["branches"]["main"]
        requirements = _clean_requirements(
            branch,
            {"type": "branch_points_to", "branch": branch, "commit": "c3"},
            {"type": "branch_points_to", "branch": "main", "commit": main_tip},
            {
                "type": "required_command_sequence",
                "commands": ["git reflog", "git show c3"],
            },
        )

    case["state_requirements"] = requirements


def apply_scenario_bank(levels: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Mutate the archived level objects into the canonical revised bank.

    Pairing is by authored scenario number/order, never by an old alias ID.
    This preserves unchanged deterministic fixtures while replacing every
    document-owned field and all genuinely revised runtime exercises.
    """

    canonical = list(scenario_bank().items())
    slots = [
        (difficulty, tier, index, case)
        for level in levels
        for difficulty, tier in level.get("tiers", {}).items()
        for index, case in enumerate(tier.get("cases", []))
    ]
    if len(slots) != len(canonical) or len(canonical) != 265:
        raise RuntimeError(
            f"Scenario bank/seed slot mismatch: {len(canonical)} canonical, {len(slots)} slots"
        )

    for (difficulty, tier, index, archived), (case_id, authored) in zip(
        slots, canonical, strict=True
    ):
        if difficulty != authored["difficulty"]:
            raise RuntimeError(
                f"Difficulty mismatch at {authored['scenario_number']}: {difficulty} != "
                f"{authored['difficulty']}"
            )
        case = copy.deepcopy(archived)
        case.update(
            {
                "case_id": case_id,
                "label": authored["label"],
                "context": authored["story"],
                "solution_commands": list(authored["solution_commands"]),
                "solution_workspace_files": copy.deepcopy(authored["solution_workspace_files"]),
            }
        )
        case.update(copy.deepcopy(RUNTIME_OVERRIDES.get(case_id, {})))
        _canonicalize_requirements(case)
        tier["cases"][index] = case

    return levels
