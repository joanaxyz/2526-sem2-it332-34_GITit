from __future__ import annotations

import copy
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from common.constants import (
    COMPLETION_STATE_BASED,
    DIFFICULTY_EASY,
    DIFFICULTY_HARD,
    DIFFICULTY_MAX_COUNTED_COMMANDS,
    DIFFICULTY_MEDIUM,
)
from learning.management.commands.seed_module1_scenarios import commit, repo_with_head
from learning.models import LearningUnit, Lesson, OrientationProgress
from scenarios.builders import ScenarioVariantBuildError, StaticCaseMaterializer
from scenarios.command_content import (
    command_content_key_for_command,
    command_preview_section_ids_for_command,
    command_preview_syntax_for_command,
    seed_git_command_content_library,
)
from scenarios.models import (
    CommandCountPolicy,
    CompletionRecord,
    DifficultyInstance,
    ScenarioSession,
    ScenarioSkillFocus,
    ScenarioVariant,
)
from simulator.services import RepositoryStateSimulator, is_diagnostic_command

DIAG_PATTERNS = [
    "git status",
    "git status -s",
    "git status --short",
    "git status --porcelain",
    "git status -sb",
    "git diff",
    "git diff <path>",
    "git diff --staged",
    "git diff --cached",
    "git diff --name-only",
    "git diff main..feature",
    "git diff --ours <path>",
    "git diff --theirs <path>",
    "git diff --base <path>",
    "git diff --check",
    "git diff --check <path>",
    "git log --oneline --graph --all",
    "git show <commit>",
    "git ls-files",
    "git ls-files -u",
]

MODULE_THREE_LESSONS = [
    (
        1,
        "diagnosing-conflict-state",
        "Diagnosing Conflict State",
        "Use read-only commands to inspect branches, unmerged paths, conflict sides, and marker risk.",
    ),
    (
        2,
        "what-causes-merge-conflicts",
        "What Causes Merge Conflicts",
        "Initiate and inspect merge conflict states.",
    ),
    (
        3,
        "reading-conflict-markers",
        "Reading Conflict Markers",
        "Read HEAD, separator, and incoming sections before resolving.",
    ),
    (
        4,
        "resolving-conflicts-manually",
        "Resolving Conflicts Manually",
        "Resolve conflict content, stage it, and complete the merge.",
    ),
    (
        5,
        "using-a-merge-tool",
        "Using a Merge Tool",
        "Configure and run a merge tool to resolve conflicts.",
    ),
    (
        6,
        "conflict-prevention-strategies",
        "Conflict Prevention Strategies",
        "Fetch and compare before merging long-lived work.",
    ),
    (
        7,
        "cherry-picking-commits",
        "Cherry-Picking Commits",
        "Apply selected commits without merging an entire branch.",
    ),
    (
        8,
        "conflict-resolution-review",
        "Conflict Resolution Review",
        "Combine diagnostics, merge resolution, merge tools, prevention checks, and selective commits.",
    ),
]


def student_context_template(kind: str) -> dict[str, Any]:
    common = {
        "constraints": [
            "Do not leave conflict marker lines in the final committed file.",
        ],
    }
    if kind == "conflict-diagnostics":
        return {
            "story": "{{project}} is paused in a conflicted merge. Gather evidence before choosing a resolution.",
            "required_details": [
                {"label": "Current branch", "value": "main"},
                {"label": "Conflict file", "value": "{{conflict_path}}"},
                {"label": "Source branch", "value": "{{source_branch}}"},
            ],
            "constraints": [
                "Use read-only diagnostics only; keep the repository state unchanged.",
            ],
        }
    if kind == "conflict-identification":
        return {
            "story": "{{project}} has parallel branch work. Start the merge that reveals the exact conflict file.",
            "required_details": [
                {"label": "Current branch", "value": "main"},
                {"label": "Source branch", "value": "{{source_branch}}"},
                {"label": "Expected conflict file", "value": "{{conflict_path}}"},
            ],
        }
    if kind == "manual-resolution":
        return {
            "story": "{{project}} is already stopped in a conflicted merge. Combine both changes manually.",
            "required_details": [
                {"label": "Current branch", "value": "main"},
                {"label": "Conflict file", "value": "{{conflict_path}}"},
                {"label": "Manual resolution detail", "value": "{{resolution_token}}"},
                {"label": "Commit message text", "value": "{{commit_message}}"},
                {"label": "Markers to remove", "value": "<<<<<<<, =======, >>>>>>>"},
            ],
            **common,
        }
    if kind == "accept-ours":
        return {
            "story": "{{project}} is already stopped in a conflicted merge. Keep the current branch version of the conflicted file.",
            "required_details": [
                {"label": "Current branch", "value": "main"},
                {"label": "Conflict file", "value": "{{conflict_path}}"},
                {"label": "Resolution strategy", "value": "Keep ours / HEAD / current branch"},
                {"label": "Commit message text", "value": "{{commit_message}}"},
                {"label": "Markers to remove", "value": "<<<<<<<, =======, >>>>>>>"},
            ],
            **common,
        }
    if kind == "accept-theirs":
        return {
            "story": "{{project}} is already stopped in a conflicted merge. Accept the incoming branch version of the conflicted file.",
            "required_details": [
                {"label": "Current branch", "value": "main"},
                {"label": "Incoming branch", "value": "{{source_branch}}"},
                {"label": "Conflict file", "value": "{{conflict_path}}"},
                {"label": "Resolution strategy", "value": "Accept theirs / incoming branch"},
                {"label": "Commit message text", "value": "{{commit_message}}"},
                {"label": "Markers to remove", "value": "<<<<<<<, =======, >>>>>>>"},
            ],
            **common,
        }
    if kind == "merge-abort":
        return {
            "story": "{{project}} is in a conflicted merge. Cancel the merge and return to the pre-merge state.",
            "required_details": [
                {"label": "Current branch", "value": "main"},
                {"label": "Conflict file", "value": "{{conflict_path}}"},
                {"label": "Pre-merge tip", "value": "{{pre_merge_tip}}"},
            ],
        }
    if kind == "mergetool":
        return {
            "story": "{{project}} needs the configured merge tool to inspect and resolve the conflict.",
            "required_details": [
                {"label": "Current branch", "value": "main"},
                {"label": "Source branch", "value": "{{source_branch}}"},
                {"label": "Merge tool", "value": "{{merge_tool}}"},
                {"label": "Conflict file", "value": "{{conflict_path}}"},
                {"label": "Resolution detail", "value": "{{resolution_token}}"},
                {"label": "Markers to remove", "value": "<<<<<<<, =======, >>>>>>>"},
            ],
            **common,
        }
    if kind == "prevention":
        return {
            "story": "{{project}} needs a prevention check before anyone merges stale branch work.",
            "required_details": [
                {"label": "Current branch", "value": "{{target_branch}}"},
                {"label": "Remote", "value": "{{remote}}"},
                {"label": "Remote branch", "value": "{{remote_branch}}"},
                {"label": "Local tip before fetch", "value": "{{local_tip}}"},
                {"label": "Remote tip after fetch", "value": "{{remote_tip}}"},
            ],
            "constraints": [
                "Update remote-tracking information without moving the current local branch.",
            ],
        }
    if kind == "cherry-pick":
        return {
            "story": "{{project}} needs one selected commit applied to the current branch.",
            "required_details": [
                {"label": "Current branch", "value": "{{target_branch}}"},
                {"label": "Source commit", "value": "{{source_commit}}"},
                {"label": "Expected file", "value": "{{target_path}}"},
                {"label": "Expected token", "value": "{{expected_token}}"},
            ],
        }
    if kind == "cherry-pick-abort":
        return {
            "story": "{{project}} has a cherry-pick in progress that should be canceled.",
            "required_details": [
                {"label": "Current branch", "value": "{{target_branch}}"},
                {"label": "Original branch tip", "value": "{{original_tip}}"},
            ],
        }
    if kind == "capstone":
        return {
            "story": "{{project}} has a remote branch conflict and a separate hotfix that both need to land cleanly.",
            "required_details": [
                {"label": "Current branch", "value": "main"},
                {"label": "Remote", "value": "{{remote}}"},
                {"label": "Source branch", "value": "{{source_branch}}"},
                {"label": "Merge tool", "value": "{{merge_tool}}"},
                {"label": "Conflict file", "value": "{{conflict_path}}"},
                {"label": "Resolution token", "value": "{{resolution_token}}"},
                {"label": "Hotfix commit", "value": "{{source_commit}}"},
                {"label": "Hotfix token", "value": "{{hotfix_token}}"},
                {"label": "Markers to remove", "value": "<<<<<<<, =======, >>>>>>>"},
            ],
            **common,
        }
    return {}


def template(
    *,
    slug: str,
    kind: str,
    signature: str,
    cases: list[dict[str, Any]],
    initial_state: dict[str, Any],
    target_rule: dict[str, Any],
    solution: list[str],
    label: str,
    workspace_files: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    payload = {
        "slug": slug,
        "slug_template": f"{slug}-{{{{case_id}}}}",
        "label_template": label,
        "template_key": signature,
        "structure_key": signature,
        "cases": cases,
        "initial_state_template": initial_state,
        "target_rule_template": target_rule,
        "solution_commands_template": solution,
        "student_context_template": student_context_template(kind),
    }
    if workspace_files:
        payload["solution_workspace_files_template"] = workspace_files
    return payload


def diff(
    policy: tuple[int, int],
    narrative: str,
    task: str,
    templates: list[dict[str, Any]],
    *,
    required_attempts: int,
) -> dict[str, Any]:
    return {
        "policy": policy,
        "narrative": narrative,
        "task": task,
        "templates": templates,
        "completion_type": COMPLETION_STATE_BASED,
        "required_successful_attempts": required_attempts,
    }


def scenario_dict(
    *,
    lesson: tuple,
    slug: str,
    title: str,
    focus: str,
    summary: str,
    explanation: str,
    primary: list[str],
    supporting: list[str],
    concepts: list[str],
    difficulties: dict[str, Any],
    kind=ScenarioSkillFocus.SkillFocusType.WORKFLOW_SPECIFIC,
) -> dict[str, Any]:
    return {
        "lesson": lesson,
        "slug": slug,
        "title": title,
        "focus": focus,
        "summary": summary,
        "explanation": explanation,
        "primary": primary,
        "supporting": supporting,
        "concepts": concepts,
        "kind": kind,
        "difficulties": difficulties,
    }


def conflict_repo_case(
    case_id: str,
    *,
    project: str,
    conflict_path: str,
    base_content: str,
    main_content: str,
    feature_content: str,
    resolution_content: str,
    resolution_token: str,
    source_branch: str,
    answer_anchor: str,
) -> dict[str, Any]:
    state = repo_with_head(
        commits=[
            commit("c0", "Create shared baseline", {conflict_path: base_content}),
            commit("c1", "Update main copy", {conflict_path: main_content}, ["c0"]),
            commit(
                "c2",
                f"Update {source_branch}",
                {conflict_path: feature_content},
                ["c0"],
            ),
        ],
        head="c1",
        branch="main",
        extra={
            "conflict_on_merge": True,
            "conflict_files": [conflict_path],
            "merge_resolutions": {conflict_path: resolution_content},
        },
    )
    state["branches"][source_branch] = "c2"
    return {
        "case_id": case_id,
        "project": project,
        "conflict_path": conflict_path,
        "source_branch": source_branch,
        "base_content": base_content,
        "main_content": main_content,
        "feature_content": feature_content,
        "resolution_content": resolution_content,
        "resolution_token": resolution_token,
        "initial_state": state,
        "answer_anchor": answer_anchor,
    }


def conflicted_case(base_case: dict[str, Any], *, commit_message: str) -> dict[str, Any]:
    simulator = RepositoryStateSimulator()
    conflicted = simulator.process(
        base_case["initial_state"],
        f"git merge {base_case['source_branch']}",
    ).state
    return {
        **base_case,
        "initial_state": conflicted,
        "commit_message": commit_message,
        "solution_commands": [
            f"git add {base_case['conflict_path']}",
            f'git commit -m "{commit_message}"',
        ],
        "solution_workspace_files": [
            {
                "mode": "write",
                "path": base_case["conflict_path"],
                "content": base_case["resolution_content"],
            }
        ],
    }


def conflict_side_case(
    base_case: dict[str, Any],
    *,
    side: str,
    commit_message: str,
) -> dict[str, Any]:
    simulator = RepositoryStateSimulator()
    conflicted = simulator.process(
        base_case["initial_state"],
        f"git merge {base_case['source_branch']}",
    ).state
    side_option = "--ours" if side == "ours" else "--theirs"
    side_content = base_case["main_content"] if side == "ours" else base_case["feature_content"]
    return {
        **base_case,
        "initial_state": conflicted,
        "side": side,
        "side_label": "current branch" if side == "ours" else "incoming branch",
        "side_content": side_content,
        "commit_message": commit_message,
        "solution_commands": [
            f"git checkout {side_option} {base_case['conflict_path']}",
            f"git add {base_case['conflict_path']}",
            f'git commit -m "{commit_message}"',
        ],
    }


def merge_abort_case(base_case: dict[str, Any]) -> dict[str, Any]:
    simulator = RepositoryStateSimulator()
    conflicted = simulator.process(
        base_case["initial_state"],
        f"git merge {base_case['source_branch']}",
    ).state
    return {
        **base_case,
        "initial_state": conflicted,
        "pre_merge_tip": "c1",
        "solution_commands": ["git merge --abort"],
    }


def cherry_pick_case(
    case_id: str,
    *,
    project: str,
    target_branch: str,
    source_commit: str,
    target_path: str,
    expected_token: str,
    answer_anchor: str,
) -> dict[str, Any]:
    state = repo_with_head(
        commits=[
            commit("c0", "Release baseline", {"README.md": "release-base"}),
            commit(
                "c1",
                "Patch login timeout",
                {"README.md": "release-base", target_path: expected_token},
                ["c0"],
            ),
            commit(
                "c2",
                "Continue main work",
                {"README.md": "release-base", target_path: expected_token, "main.txt": "main"},
                ["c1"],
            ),
            commit("c3", "Prepare release branch", {"README.md": "release-notes"}, ["c0"]),
        ],
        head="c3",
        branch=target_branch,
    )
    state["branches"]["main"] = "c2"
    return {
        "case_id": case_id,
        "project": project,
        "target_branch": target_branch,
        "source_commit": source_commit,
        "target_path": target_path,
        "expected_token": expected_token,
        "initial_state": state,
        "answer_anchor": answer_anchor,
    }


def prevention_case(
    case_id: str,
    *,
    project: str,
    target_branch: str,
    remote: str,
    remote_branch: str,
    local_tip: str,
    remote_tip: str,
    watched_path: str,
    remote_content: str,
    answer_anchor: str,
) -> dict[str, Any]:
    state = repo_with_head(
        commits=[
            commit("c0", "Shared baseline", {"README.md": "baseline", watched_path: "v1"}),
            commit(local_tip, "Local integration point", {"README.md": "baseline", watched_path: "local"}, ["c0"]),
            commit(remote_tip, "Remote branch update", {"README.md": "baseline", watched_path: remote_content}, [local_tip]),
        ],
        head=local_tip,
        branch=target_branch,
        remotes={remote: f"https://example.test/{project}.git"},
        remote_branches={remote_branch: local_tip},
        upstream_tracking={target_branch: remote_branch},
        extra={"remote_updates": {remote_branch: remote_tip}},
    )
    return {
        "case_id": case_id,
        "project": project,
        "target_branch": target_branch,
        "remote": remote,
        "remote_branch": remote_branch,
        "local_tip": local_tip,
        "remote_tip": remote_tip,
        "watched_path": watched_path,
        "remote_content": remote_content,
        "initial_state": state,
        "answer_anchor": answer_anchor,
    }


def capstone_case(
    case_id: str,
    *,
    project: str,
    conflict_path: str,
    hotfix_path: str,
    base_content: str,
    main_content: str,
    feature_content: str,
    resolution_content: str,
    resolution_token: str,
    hotfix_token: str,
    source_branch: str,
    merge_tool: str,
    answer_anchor: str,
) -> dict[str, Any]:
    state = repo_with_head(
        commits=[
            commit(
                "c0",
                "Release baseline",
                {conflict_path: base_content, hotfix_path: "hotfix-base"},
            ),
            commit(
                "c1",
                "Main branch update",
                {conflict_path: main_content, hotfix_path: "hotfix-base"},
                ["c0"],
            ),
            commit(
                "c2",
                "Remote feature update",
                {conflict_path: feature_content, hotfix_path: "hotfix-base"},
                ["c0"],
            ),
            commit(
                "c3",
                "Patch production hotfix",
                {conflict_path: base_content, hotfix_path: hotfix_token},
                ["c0"],
            ),
        ],
        head="c1",
        branch="main",
        remotes={"origin": f"https://example.test/{project}.git"},
        remote_branches={"origin/main": "c1"},
        upstream_tracking={"main": "origin/main"},
        extra={
            "remote_updates": {source_branch: "c2"},
            "conflict_on_merge": True,
            "conflict_files": [conflict_path],
            "merge_resolutions": {conflict_path: resolution_content},
        },
    )
    return {
        "case_id": case_id,
        "project": project,
        "remote": "origin",
        "source_branch": source_branch,
        "merge_tool": merge_tool,
        "conflict_path": conflict_path,
        "resolution_content": resolution_content,
        "resolution_token": resolution_token,
        "source_commit": "c3",
        "hotfix_path": hotfix_path,
        "hotfix_token": hotfix_token,
        "initial_state": state,
        "answer_anchor": answer_anchor,
    }


def module_three_scenarios() -> list[dict[str, Any]]:
    easy_conflicts = [
        conflict_repo_case(
            "conflict-easy-auth-copy",
            project="auth-service",
            conflict_path="src/auth.js",
            base_content="timeout=3000",
            main_content="timeout=5000",
            feature_content="timeout=2500",
            resolution_content="timeout=5000\nretry=enabled",
            resolution_token="retry=enabled",
            source_branch="feature/auth-timeout",
            answer_anchor="merge feature/auth-timeout produces conflict in src/auth.js",
        ),
        conflict_repo_case(
            "conflict-easy-profile-copy",
            project="profile-ui",
            conflict_path="src/profile.tsx",
            base_content="title=Profile",
            main_content="title=Account profile",
            feature_content="title=Member profile",
            resolution_content="title=Account profile\nsubtitle=Member profile",
            resolution_token="subtitle=Member profile",
            source_branch="feature/profile-copy",
            answer_anchor="merge feature/profile-copy produces conflict in src/profile.tsx",
        ),
        conflict_repo_case(
            "conflict-easy-billing-copy",
            project="billing-api",
            conflict_path="src/billing.py",
            base_content="currency='USD'",
            main_content="currency='PHP'",
            feature_content="currency='EUR'",
            resolution_content="currency='PHP'\nsupported=['PHP','EUR']",
            resolution_token="supported=['PHP','EUR']",
            source_branch="feature/regional-currency",
            answer_anchor="merge feature/regional-currency produces conflict in src/billing.py",
        ),
    ]
    medium_conflicts = [
        conflict_repo_case(
            "conflict-medium-router",
            project="support-portal",
            conflict_path="src/routes.ts",
            base_content="route('/help')",
            main_content="route('/support')",
            feature_content="route('/help-center')",
            resolution_content="route('/support')\nroute('/help-center')",
            resolution_token="route('/help-center')",
            source_branch="feature/help-center",
            answer_anchor="merge feature/help-center conflicts in src/routes.ts",
        ),
        conflict_repo_case(
            "conflict-medium-policy",
            project="policy-engine",
            conflict_path="src/policy.yml",
            base_content="review: basic",
            main_content="review: strict",
            feature_content="review: assisted",
            resolution_content="review: strict\nassist: enabled",
            resolution_token="assist: enabled",
            source_branch="feature/assisted-review",
            answer_anchor="merge feature/assisted-review conflicts in src/policy.yml",
        ),
    ]
    hard_conflicts = [
        conflict_repo_case(
            "conflict-hard-pricing",
            project="pricing-service",
            conflict_path="src/pricing.rb",
            base_content="discount = 0",
            main_content="discount = regional_rate",
            feature_content="discount = loyalty_rate",
            resolution_content="discount = [regional_rate, loyalty_rate].max",
            resolution_token="loyalty_rate].max",
            source_branch="feature/loyalty-discounts",
            answer_anchor="merge feature/loyalty-discounts conflicts in src/pricing.rb",
        ),
        conflict_repo_case(
            "conflict-hard-schema",
            project="warehouse-sync",
            conflict_path="schema/orders.sql",
            base_content="status text",
            main_content="status varchar(24)",
            feature_content="status text not null",
            resolution_content="status varchar(24) not null",
            resolution_token="not null",
            source_branch="feature/order-status-required",
            answer_anchor="merge feature/order-status-required conflicts in schema/orders.sql",
        ),
    ]

    manual_easy = [
        conflicted_case(case, commit_message="Resolve conflict cleanly")
        for case in easy_conflicts
    ]
    manual_medium = [
        conflicted_case(case, commit_message="Resolve integration conflict")
        for case in [*medium_conflicts, easy_conflicts[0]]
    ]
    manual_hard = [
        conflicted_case(case, commit_message="Resolve release conflict")
        for case in hard_conflicts
    ]
    accept_ours_easy = [
        conflict_side_case(case, side="ours", commit_message="Keep current branch version")
        for case in easy_conflicts[:2]
    ]
    accept_theirs_medium = [
        conflict_side_case(case, side="theirs", commit_message="Accept incoming branch version")
        for case in medium_conflicts
    ]
    accept_side_hard = [
        conflict_side_case(hard_conflicts[0], side="ours", commit_message="Keep release branch version"),
        conflict_side_case(hard_conflicts[1], side="theirs", commit_message="Accept incoming schema version"),
    ]
    merge_abort_easy = [merge_abort_case(case) for case in easy_conflicts[:2]]
    merge_abort_medium = [merge_abort_case(case) for case in medium_conflicts]
    merge_abort_hard = [merge_abort_case(case) for case in hard_conflicts]

    diagnostic_case_fields = {"solution_workspace_files", "solution_commands", "commit_message"}
    diagnostic_easy = [
        {key: value for key, value in case.items() if key not in diagnostic_case_fields}
        for case in manual_easy
    ]
    diagnostic_medium = [
        {key: value for key, value in case.items() if key not in diagnostic_case_fields}
        for case in manual_medium[:2]
    ]
    diagnostic_hard = [
        {key: value for key, value in case.items() if key not in diagnostic_case_fields}
        for case in manual_hard
    ]

    cherry_easy = [
        cherry_pick_case(
            "cherry-easy-login-timeout",
            project="release-1.0",
            target_branch="release/1.0",
            source_commit="c1",
            target_path="src/login.js",
            expected_token="timeout-fix-v1",
            answer_anchor="release branch receives login timeout patch as a new commit",
        ),
        cherry_pick_case(
            "cherry-easy-invoice-rounding",
            project="release-1.1",
            target_branch="release/1.1",
            source_commit="c1",
            target_path="src/invoice.py",
            expected_token="rounding-fix-v1",
            answer_anchor="release branch receives invoice rounding patch as a new commit",
        ),
        cherry_pick_case(
            "cherry-easy-export-null",
            project="release-2.0",
            target_branch="release/2.0",
            source_commit="c1",
            target_path="src/export.ts",
            expected_token="null-export-fix",
            answer_anchor="release branch receives export null patch as a new commit",
        ),
    ]
    cherry_medium = [
        *cherry_easy[:2],
        {
            **cherry_pick_case(
                "cherry-medium-no-commit",
                project="release-review",
                target_branch="release/review",
                source_commit="c1",
                target_path="src/report.ts",
                expected_token="report-hotfix",
                answer_anchor="no-commit cherry-pick stages report hotfix for review",
            ),
            "solution_commands": ["git cherry-pick --no-commit c1"],
        },
    ]
    cherry_hard_abort = cherry_pick_case(
        "cherry-hard-abort",
        project="release-abort",
        target_branch="release/abort",
        source_commit="c1",
        target_path="src/search.ts",
        expected_token="search-hotfix",
        answer_anchor="abort in-progress cherry-pick and return to c3",
    )
    cherry_hard_abort["initial_state"] = {
        **copy.deepcopy(cherry_hard_abort["initial_state"]),
        "cherry_pick_in_progress": True,
        "cherry_pick_original_head": "c3",
        "staging": {"src/search.ts": {"status": "modified", "content": "search-hotfix"}},
    }
    cherry_hard_abort["original_tip"] = "c3"
    cherry_hard_abort["solution_commands"] = ["git cherry-pick --abort"]
    cherry_hard = [cherry_easy[2], cherry_hard_abort]

    prevention_easy = [
        prevention_case(
            "prevent-easy-docs-refresh",
            project="docs-portal",
            target_branch="main",
            remote="origin",
            remote_branch="origin/main",
            local_tip="c1",
            remote_tip="c2",
            watched_path="docs/index.md",
            remote_content="docs-v2",
            answer_anchor="fetch updates origin/main while main stays at c1",
        ),
        prevention_case(
            "prevent-easy-api-contract",
            project="api-contracts",
            target_branch="main",
            remote="origin",
            remote_branch="origin/main",
            local_tip="c1",
            remote_tip="c2",
            watched_path="openapi.yml",
            remote_content="contract-v2",
            answer_anchor="fetch updates origin/main without moving local main",
        ),
    ]
    prevention_medium = [
        prevention_case(
            "prevent-medium-release-notes",
            project="release-notes",
            target_branch="main",
            remote="origin",
            remote_branch="origin/release-notes",
            local_tip="c1",
            remote_tip="c2",
            watched_path="CHANGELOG.md",
            remote_content="release-notes-v2",
            answer_anchor="fetch updates origin/release-notes before merge planning",
        ),
        prevention_case(
            "prevent-medium-design-tokens",
            project="design-system",
            target_branch="main",
            remote="origin",
            remote_branch="origin/design-tokens",
            local_tip="c1",
            remote_tip="c2",
            watched_path="tokens/colors.json",
            remote_content="tokens-v2",
            answer_anchor="fetch updates origin/design-tokens before integration",
        ),
    ]
    prevention_hard = [
        prevention_case(
            "prevent-hard-payments",
            project="payments",
            target_branch="main",
            remote="origin",
            remote_branch="origin/payments-reconcile",
            local_tip="c1",
            remote_tip="c2",
            watched_path="src/reconcile.py",
            remote_content="remote-reconcile-v2",
            answer_anchor="fetch only updates remote tracking for payment branch",
        ),
        prevention_case(
            "prevent-hard-search",
            project="search",
            target_branch="main",
            remote="origin",
            remote_branch="origin/search-ranking",
            local_tip="c1",
            remote_tip="c2",
            watched_path="src/ranking.ts",
            remote_content="remote-ranking-v2",
            answer_anchor="fetch only updates remote tracking for search branch",
        ),
    ]

    capstone_easy = [
        capstone_case(
            "capstone-easy-auth-hotfix",
            project="auth-service",
            conflict_path="src/auth.js",
            hotfix_path="src/session.js",
            base_content="timeout=3000",
            main_content="timeout=5000",
            feature_content="timeout=2500",
            resolution_content="timeout=5000\nretry=enabled",
            resolution_token="retry=enabled",
            hotfix_token="session-hotfix-v1",
            source_branch="origin/feature/auth-timeout",
            merge_tool="vscode",
            answer_anchor="fetch, resolve remote conflict, then cherry-pick session hotfix",
        ),
        capstone_case(
            "capstone-easy-profile-hotfix",
            project="profile-ui",
            conflict_path="src/profile.tsx",
            hotfix_path="src/avatar.tsx",
            base_content="title=Profile",
            main_content="title=Account profile",
            feature_content="title=Member profile",
            resolution_content="title=Account profile\nsubtitle=Member profile",
            resolution_token="subtitle=Member profile",
            hotfix_token="avatar-hotfix-v1",
            source_branch="origin/feature/profile-copy",
            merge_tool="vimdiff",
            answer_anchor="fetch, resolve profile conflict, then cherry-pick avatar hotfix",
        ),
    ]
    capstone_medium = [
        capstone_case(
            "capstone-medium-support-hotfix",
            project="support-portal",
            conflict_path="src/routes.ts",
            hotfix_path="src/ticket.ts",
            base_content="route('/help')",
            main_content="route('/support')",
            feature_content="route('/help-center')",
            resolution_content="route('/support')\nroute('/help-center')",
            resolution_token="route('/help-center')",
            hotfix_token="ticket-hotfix-v1",
            source_branch="origin/feature/help-center",
            merge_tool="vscode",
            answer_anchor="fetch, resolve support route conflict, then cherry-pick ticket hotfix",
        ),
        capstone_case(
            "capstone-medium-policy-hotfix",
            project="policy-engine",
            conflict_path="src/policy.yml",
            hotfix_path="src/audit.yml",
            base_content="review: basic",
            main_content="review: strict",
            feature_content="review: assisted",
            resolution_content="review: strict\nassist: enabled",
            resolution_token="assist: enabled",
            hotfix_token="audit-hotfix-v1",
            source_branch="origin/feature/assisted-review",
            merge_tool="vimdiff",
            answer_anchor="fetch, resolve policy conflict, then cherry-pick audit hotfix",
        ),
    ]
    capstone_hard = [
        capstone_case(
            "capstone-hard-pricing-hotfix",
            project="pricing-service",
            conflict_path="src/pricing.rb",
            hotfix_path="src/tax.rb",
            base_content="discount = 0",
            main_content="discount = regional_rate",
            feature_content="discount = loyalty_rate",
            resolution_content="discount = [regional_rate, loyalty_rate].max",
            resolution_token="loyalty_rate].max",
            hotfix_token="tax-hotfix-v1",
            source_branch="origin/feature/loyalty-discounts",
            merge_tool="vscode",
            answer_anchor="fetch, resolve pricing conflict, then cherry-pick tax hotfix",
        ),
        capstone_case(
            "capstone-hard-schema-hotfix",
            project="warehouse-sync",
            conflict_path="schema/orders.sql",
            hotfix_path="schema/shipments.sql",
            base_content="status text",
            main_content="status varchar(24)",
            feature_content="status text not null",
            resolution_content="status varchar(24) not null",
            resolution_token="not null",
            hotfix_token="shipment-hotfix-v1",
            source_branch="origin/feature/order-status-required",
            merge_tool="vimdiff",
            answer_anchor="fetch, resolve schema conflict, then cherry-pick shipment hotfix",
        ),
    ]

    conflict_target = {
        "head_branch": "main",
        "rules": [
            {"type": "conflicts_contain_paths", "paths": ["{{conflict_path}}"]},
            {
                "type": "operation_metadata_equals",
                "key": "last_merge_branch",
                "value": "{{source_branch}}",
            },
        ],
    }
    resolved_target = {
        "head_branch": "main",
        "staging_empty": True,
        "working_tree_clean": True,
        "conflict_free": True,
        "rules": [
            {
                "type": "branch_tip_commit",
                "branch": "main",
                "changes_include": ["{{conflict_path}}"],
                "parent_count_equals": 2,
                "is_merge": True,
            },
            {
                "type": "commit_tree_contains_tokens",
                "branch": "main",
                "tokens": ["{{resolution_token}}"],
            },
            {
                "type": "commit_tree_excludes_tokens",
                "branch": "main",
                "tokens": ["<<<<<<<", "=======", ">>>>>>>"],
            },
        ],
    }
    accept_side_target = {
        "head_branch": "main",
        "staging_empty": True,
        "working_tree_clean": True,
        "conflict_free": True,
        "rules": [
            {
                "type": "branch_tip_commit",
                "branch": "main",
                "changes_include": ["{{conflict_path}}"],
                "parent_count_equals": 2,
                "is_merge": True,
            },
            {
                "type": "commit_tree_contains",
                "branch": "main",
                "tree": {"{{conflict_path}}": "{{side_content}}"},
            },
            {
                "type": "commit_tree_excludes_tokens",
                "branch": "main",
                "tokens": ["<<<<<<<", "=======", ">>>>>>>"],
            },
        ],
    }
    abort_merge_target = {
        "head_branch": "main",
        "staging_empty": True,
        "working_tree_clean": True,
        "conflict_free": True,
        "branch_points_to": {"main": "{{pre_merge_tip}}"},
        "rules": [
            {
                "type": "operation_metadata_equals",
                "key": "last_merge_aborted",
                "value": True,
            },
        ],
    }
    mergetool_target = {
        **resolved_target,
        "rules": [
            *resolved_target["rules"],
            {
                "type": "operation_metadata_equals",
                "key": "configured_merge_tool",
                "value": "{{merge_tool}}",
            },
            {
                "type": "operation_metadata_contains",
                "key": "last_mergetool_paths",
                "value": "{{conflict_path}}",
            },
        ],
    }
    cherry_target = {
        "staging_empty": True,
        "working_tree_clean": True,
        "conflict_free": True,
        "head_branch": "{{target_branch}}",
        "rules": [
            {
                "type": "cherry_pick_created_new_commit",
                "source": "{{source_commit}}",
                "branch": "{{target_branch}}",
            },
            {
                "type": "cherry_pick_copied_changes_from",
                "source": "{{source_commit}}",
                "branch": "{{target_branch}}",
            },
            {
                "type": "commit_tree_contains_tokens",
                "branch": "{{target_branch}}",
                "tokens": ["{{expected_token}}"],
            },
        ],
    }
    cherry_no_commit_target = {
        "head_branch": "{{target_branch}}",
        "staging_contains": ["{{target_path}}"],
        "rules": [
            {
                "type": "staging_contains_tokens",
                "paths": {"{{target_path}}": ["{{expected_token}}"]},
            },
            {
                "type": "operation_metadata_equals",
                "key": "last_cherry_pick_source",
                "value": "{{source_commit}}",
            },
        ],
    }
    cherry_abort_target = {
        "head_branch": "{{target_branch}}",
        "staging_empty": True,
        "working_tree_clean": True,
        "conflict_free": True,
        "branch_points_to": {"{{target_branch}}": "{{original_tip}}"},
        "rules": [
            {
                "type": "operation_metadata_equals",
                "key": "last_cherry_pick_aborted",
                "value": True,
            }
        ],
    }
    diagnostic_target = {
        "repository_state_unchanged": True,
        "rules": [
            {"type": "conflicts_contain_paths", "paths": ["{{conflict_path}}"]},
        ],
    }
    prevention_target = {
        "head_branch": "{{target_branch}}",
        "required_commands": ["git fetch", "git diff"],
        "branch_points_to": {"{{target_branch}}": "{{local_tip}}"},
        "remote_branch_points_to": {"{{remote_branch}}": "{{remote_tip}}"},
        "staging_empty": True,
        "working_tree_clean": True,
        "conflict_free": True,
        "rules": [
            {
                "type": "fetch_updated_remote_tracking_without_moving_local",
                "branch": "{{target_branch}}",
            },
            {
                "type": "operation_metadata_equals",
                "key": "last_fetch_remote",
                "value": "{{remote}}",
            },
        ],
    }
    capstone_target = {
        "head_branch": "main",
        "staging_empty": True,
        "working_tree_clean": True,
        "conflict_free": True,
        "required_commands": ["git fetch", "git diff", "git merge", "git mergetool", "git cherry-pick"],
        "remote_branch_exists": ["{{source_branch}}"],
        "rules": [
            {
                "type": "operation_metadata_equals",
                "key": "last_fetch_remote",
                "value": "{{remote}}",
            },
            {
                "type": "operation_metadata_equals",
                "key": "last_merge_branch",
                "value": "{{source_branch}}",
            },
            {
                "type": "operation_metadata_contains",
                "key": "last_mergetool_paths",
                "value": "{{conflict_path}}",
            },
            {
                "type": "operation_metadata_equals",
                "key": "last_cherry_pick_source",
                "value": "{{source_commit}}",
            },
            {
                "type": "cherry_pick_created_new_commit",
                "source": "{{source_commit}}",
                "branch": "main",
            },
            {
                "type": "cherry_pick_copied_changes_from",
                "source": "{{source_commit}}",
                "branch": "main",
            },
            {
                "type": "commit_tree_contains_tokens",
                "branch": "main",
                "tokens": ["{{resolution_token}}", "{{hotfix_token}}"],
            },
            {
                "type": "commit_tree_excludes_tokens",
                "branch": "main",
                "tokens": ["<<<<<<<", "=======", ">>>>>>>"],
            },
        ],
    }

    return [
        scenario_dict(
            lesson=MODULE_THREE_LESSONS[0],
            slug="diagnose-conflict-state",
            title="Diagnose conflict state before resolving",
            focus="conflict diagnostics",
            summary="Use read-only commands to inspect unmerged paths and both sides of a conflict.",
            explanation="Conflict diagnostics help students slow down: status identifies the state, diff side options compare ours/theirs/base, --check catches marker lines, and ls-files -u exposes unmerged index stages.",
            primary=["git status", "git diff", "git ls-files"],
            supporting=["git diff --check", "git log --oneline --graph --all"],
            concepts=["diagnostic commands", "unmerged index", "ours/theirs/base", "conflict markers"],
            kind=ScenarioSkillFocus.SkillFocusType.CONCEPT_SPECIFIC,
            difficulties={
                DIFFICULTY_EASY: diff(
                    (0, 1),
                    "Inspect a conflicted file without changing repository state.",
                    "Run the diagnostic checklist for the conflicted file.",
                    [
                        template(
                            slug="diagnose-conflict",
                            kind="conflict-diagnostics",
                            signature="module3.diagnostics.easy",
                            cases=diagnostic_easy,
                            initial_state="{{initial_state}}",
                            target_rule=diagnostic_target,
                            solution=[
                                "git status",
                                "git diff --ours {{conflict_path}}",
                                "git diff --theirs {{conflict_path}}",
                                "git ls-files -u",
                            ],
                            label="Diagnose {{conflict_path}}",
                        )
                    ],
                    required_attempts=3,
                ),
                DIFFICULTY_MEDIUM: diff(
                    (0, 1),
                    "Inspect conflict sides and marker risk before resolving.",
                    "Use conflict diagnostics while leaving the conflict unchanged.",
                    [
                        template(
                            slug="diagnose-conflict",
                            kind="conflict-diagnostics",
                            signature="module3.diagnostics.medium",
                            cases=diagnostic_medium,
                            initial_state="{{initial_state}}",
                            target_rule=diagnostic_target,
                            solution=[
                                "git status -sb",
                                "git ls-files -u",
                                "git diff --base {{conflict_path}}",
                                "git diff --check {{conflict_path}}",
                            ],
                            label="Inspect {{conflict_path}}",
                        )
                    ],
                    required_attempts=2,
                ),
                DIFFICULTY_HARD: diff(
                    (0, 1),
                    "Use the full conflict diagnostic pass without mutating state.",
                    "Identify the unmerged file, both sides, common base, and marker risk.",
                    [
                        template(
                            slug="diagnose-conflict",
                            kind="conflict-diagnostics",
                            signature="module3.diagnostics.hard",
                            cases=diagnostic_hard,
                            initial_state="{{initial_state}}",
                            target_rule=diagnostic_target,
                            solution=[
                                "git status --porcelain",
                                "git ls-files -u",
                                "git diff --ours {{conflict_path}}",
                                "git diff --theirs {{conflict_path}}",
                                "git diff --base {{conflict_path}}",
                                "git diff --check {{conflict_path}}",
                            ],
                            label="Audit {{conflict_path}}",
                        )
                    ],
                    required_attempts=2,
                ),
            },
        ),
        scenario_dict(
            lesson=MODULE_THREE_LESSONS[1],
            slug="identify-merge-conflict-state",
            title="Identify a merge conflict state",
            focus="git merge",
            summary="Start a merge and recognize the resulting conflict state.",
            explanation="A merge conflict is represented by branch state plus conflicted working-tree paths. The evaluator checks the resulting state, not a text transcript.",
            primary=["git merge"],
            supporting=["git status", "git diff", "git ls-files -u", "git log --oneline --graph --all"],
            concepts=["merge conflicts", "conflict state", "branch divergence"],
            difficulties={
                DIFFICULTY_EASY: diff(
                    (1, 1),
                    "Start the named merge and inspect the conflict it creates.",
                    "Reach the conflict state for the named source branch.",
                    [
                        template(
                            slug="identify-conflict",
                            kind="conflict-identification",
                            signature="module3.conflict.identify.easy",
                            cases=easy_conflicts,
                            initial_state="{{initial_state}}",
                            target_rule=conflict_target,
                            solution=["git merge {{source_branch}}"],
                            label="Identify conflict in {{conflict_path}}",
                        )
                    ],
                    required_attempts=3,
                ),
                DIFFICULTY_MEDIUM: diff(
                    (1, 1),
                    "Start a merge from a less obvious branch name and reach the conflict state.",
                    "Reach the conflict state without changing the wrong branch.",
                    [
                        template(
                            slug="identify-conflict",
                            kind="conflict-identification",
                            signature="module3.conflict.identify.medium",
                            cases=medium_conflicts,
                            initial_state="{{initial_state}}",
                            target_rule=conflict_target,
                            solution=["git merge {{source_branch}}"],
                            label="Identify conflict in {{conflict_path}}",
                        )
                    ],
                    required_attempts=2,
                ),
                DIFFICULTY_HARD: diff(
                    (1, 1),
                    "Read the branch setup and start the merge that exposes the conflict.",
                    "Reach the authored conflict state.",
                    [
                        template(
                            slug="identify-conflict",
                            kind="conflict-identification",
                            signature="module3.conflict.identify.hard",
                            cases=hard_conflicts,
                            initial_state="{{initial_state}}",
                            target_rule=conflict_target,
                            solution=["git merge {{source_branch}}"],
                            label="Identify conflict in {{conflict_path}}",
                        )
                    ],
                    required_attempts=2,
                ),
            },
        ),
        scenario_dict(
            lesson=MODULE_THREE_LESSONS[2],
            slug="accept-conflict-side",
            title="Accept one side of a conflict",
            focus="git checkout conflict side",
            summary="Resolve a conflict by intentionally choosing ours or theirs.",
            explanation="Some conflicts should not be combined. These variants teach the supported subset: inspect the conflict, choose the requested side into the working tree, stage it, and complete the merge.",
            primary=["git checkout", "git add", "git commit"],
            supporting=["git status", "git diff --ours <path>", "git diff --theirs <path>", "git ls-files -u"],
            concepts=["ours", "theirs", "HEAD", "incoming branch", "unmerged index"],
            difficulties={
                DIFFICULTY_EASY: diff(
                    (3, 5),
                    "Keep the current branch version of the conflicted file.",
                    "Resolve by keeping ours, then stage and finish the merge.",
                    [
                        template(
                            slug="accept-ours",
                            kind="accept-ours",
                            signature="module3.accept-side.easy.ours",
                            cases=accept_ours_easy,
                            initial_state="{{initial_state}}",
                            target_rule=accept_side_target,
                            solution="{{solution_commands}}",
                            label="Keep ours for {{conflict_path}}",
                        )
                    ],
                    required_attempts=2,
                ),
                DIFFICULTY_MEDIUM: diff(
                    (3, 5),
                    "Accept the incoming branch version of the conflicted file.",
                    "Resolve by accepting theirs, then stage and finish the merge.",
                    [
                        template(
                            slug="accept-theirs",
                            kind="accept-theirs",
                            signature="module3.accept-side.medium.theirs",
                            cases=accept_theirs_medium,
                            initial_state="{{initial_state}}",
                            target_rule=accept_side_target,
                            solution="{{solution_commands}}",
                            label="Accept theirs for {{conflict_path}}",
                        )
                    ],
                    required_attempts=2,
                ),
                DIFFICULTY_HARD: diff(
                    (3, 5),
                    "Choose the requested conflict side without combining both changes.",
                    "Use the side named by the scenario, then stage and finish the merge.",
                    [
                        template(
                            slug="accept-ours",
                            kind="accept-ours",
                            signature="module3.accept-side.hard.ours",
                            cases=[accept_side_hard[0]],
                            initial_state="{{initial_state}}",
                            target_rule=accept_side_target,
                            solution="{{solution_commands}}",
                            label="Choose {{side_label}} for {{conflict_path}}",
                        ),
                        template(
                            slug="accept-theirs",
                            kind="accept-theirs",
                            signature="module3.accept-side.hard.theirs",
                            cases=[accept_side_hard[1]],
                            initial_state="{{initial_state}}",
                            target_rule=accept_side_target,
                            solution="{{solution_commands}}",
                            label="Choose {{side_label}} for {{conflict_path}}",
                        )
                    ],
                    required_attempts=2,
                ),
            },
        ),
        scenario_dict(
            lesson=MODULE_THREE_LESSONS[3],
            slug="resolve-conflicts-manually",
            title="Resolve conflicts manually",
            focus="manual conflict resolution",
            summary="Stage a clean manual resolution and complete the merge commit.",
            explanation="Manual resolution is evaluated by the final repository state: the merge commit must contain the resolved content and no marker tokens. Students can inspect and edit the conflicted file from the project file tree before staging it.",
            primary=["git add", "git commit"],
            supporting=["git status", "git diff", "git diff --check", "git diff --ours <path>", "git diff --theirs <path>"],
            concepts=["conflict markers", "merge commit", "merge abort"],
            difficulties={
                DIFFICULTY_EASY: diff(
                    (2, 3),
                    "Complete a single-file manual conflict resolution.",
                    "Stage the resolved file and complete the merge commit.",
                    [
                        template(
                            slug="manual-resolution",
                            kind="manual-resolution",
                            signature="module3.manual.easy",
                            cases=manual_easy,
                            initial_state="{{initial_state}}",
                            target_rule=resolved_target,
                            solution="{{solution_commands}}",
                            workspace_files="{{solution_workspace_files}}",
                            label="Resolve {{conflict_path}}",
                        )
                    ],
                    required_attempts=3,
                ),
                DIFFICULTY_MEDIUM: diff(
                    (2, 3),
                    "Resolve conflict content in a slightly larger branch context.",
                    "Commit the clean resolved content with the requested message.",
                    [
                        template(
                            slug="manual-resolution",
                            kind="manual-resolution",
                            signature="module3.manual.medium",
                            cases=manual_medium,
                            initial_state="{{initial_state}}",
                            target_rule=resolved_target,
                            solution="{{solution_commands}}",
                            workspace_files="{{solution_workspace_files}}",
                            label="Resolve {{conflict_path}}",
                        )
                    ],
                    required_attempts=3,
                ),
                DIFFICULTY_HARD: diff(
                    (2, 3),
                    "Resolve conflict situations based on the requested outcome.",
                    "Produce the clean target state for the conflicted merge.",
                    [
                        template(
                            slug="manual-resolution",
                            kind="manual-resolution",
                            signature="module3.manual.hard.resolve",
                            cases=manual_hard,
                            initial_state="{{initial_state}}",
                            target_rule=resolved_target,
                            solution="{{solution_commands}}",
                            workspace_files="{{solution_workspace_files}}",
                            label="Resolve {{conflict_path}}",
                        ),
                    ],
                    required_attempts=2,
                ),
            },
        ),
        scenario_dict(
            lesson=MODULE_THREE_LESSONS[3],
            slug="abort-conflicted-merge",
            title="Abort a conflicted merge",
            focus="git merge --abort",
            summary="Cancel a merge conflict and restore the pre-merge branch state.",
            explanation="Not every conflict should be resolved. These variants ask students to recognize that the correct outcome is to cancel the merge and leave no unmerged files behind.",
            primary=["git merge"],
            supporting=["git status", "git diff", "git ls-files -u"],
            concepts=["merge abort", "pre-merge tip", "conflict cleanup"],
            difficulties={
                DIFFICULTY_EASY: diff(
                    (1, 1),
                    "Cancel the conflicted merge and return to the pre-merge state.",
                    "Abort the merge without committing the incoming branch.",
                    [
                        template(
                            slug="abort-merge",
                            kind="merge-abort",
                            signature="module3.merge-abort.easy",
                            cases=merge_abort_easy,
                            initial_state="{{initial_state}}",
                            target_rule=abort_merge_target,
                            solution="{{solution_commands}}",
                            label="Abort merge for {{conflict_path}}",
                        )
                    ],
                    required_attempts=2,
                ),
                DIFFICULTY_MEDIUM: diff(
                    (1, 1),
                    "Cancel the merge after confirming the conflict should not land.",
                    "Return main to the pre-merge tip with no conflict state.",
                    [
                        template(
                            slug="abort-merge",
                            kind="merge-abort",
                            signature="module3.merge-abort.medium",
                            cases=merge_abort_medium,
                            initial_state="{{initial_state}}",
                            target_rule=abort_merge_target,
                            solution="{{solution_commands}}",
                            label="Cancel merge for {{conflict_path}}",
                        )
                    ],
                    required_attempts=2,
                ),
                DIFFICULTY_HARD: diff(
                    (1, 1),
                    "Recognize a conflict that should be canceled instead of resolved.",
                    "Restore the original branch tip and clear all merge state.",
                    [
                        template(
                            slug="abort-merge",
                            kind="merge-abort",
                            signature="module3.merge-abort.hard",
                            cases=merge_abort_hard,
                            initial_state="{{initial_state}}",
                            target_rule=abort_merge_target,
                            solution="{{solution_commands}}",
                            label="Restore pre-merge {{conflict_path}}",
                        )
                    ],
                    required_attempts=2,
                ),
            },
        ),
        scenario_dict(
            lesson=MODULE_THREE_LESSONS[4],
            slug="use-merge-tool-workflow",
            title="Use a merge tool workflow",
            focus="git mergetool",
            summary="Configure a merge tool, use it to resolve conflicts, and complete the merge.",
            explanation="The simulator records the merge tool launch and opens the workspace conflict editor. Students still choose and save the resolution, stage the file, and complete the merge.",
            primary=["git config", "git merge", "git mergetool", "git add", "git commit"],
            supporting=["git status", "git diff --check", "git ls-files -u"],
            concepts=["merge tool", "LOCAL", "REMOTE", "BASE", "MERGED"],
            difficulties={
                DIFFICULTY_EASY: diff(
                    (4, 5),
                    "Configure the requested merge tool and use it to finish the merge.",
                    "Use the merge tool workflow for the named source branch.",
                    [
                        template(
                            slug="mergetool-resolution",
                            kind="mergetool",
                            signature="module3.mergetool.easy",
                            cases=[
                                {**easy_conflicts[0], "merge_tool": "vscode"},
                                {**easy_conflicts[1], "merge_tool": "vimdiff"},
                            ],
                            initial_state="{{initial_state}}",
                            target_rule=mergetool_target,
                            solution=[
                                "git config --global merge.tool {{merge_tool}}",
                                "git merge {{source_branch}}",
                                "git mergetool",
                                "git add {{conflict_path}}",
                                "git commit",
                            ],
                            workspace_files=[
                                {
                                    "mode": "write",
                                    "path": "{{conflict_path}}",
                                    "content": "{{resolution_content}}",
                                    "after_command": "git mergetool",
                                }
                            ],
                            label="Resolve {{conflict_path}} with {{merge_tool}}",
                        )
                    ],
                    required_attempts=2,
                ),
                DIFFICULTY_MEDIUM: diff(
                    (4, 5),
                    "Use mergetool on branch conflicts with different file types.",
                    "Configure the tool, launch it, and complete the merge.",
                    [
                        template(
                            slug="mergetool-resolution",
                            kind="mergetool",
                            signature="module3.mergetool.medium",
                            cases=[
                                {**medium_conflicts[0], "merge_tool": "vscode"},
                                {**medium_conflicts[1], "merge_tool": "vimdiff"},
                            ],
                            initial_state="{{initial_state}}",
                            target_rule=mergetool_target,
                            solution=[
                                "git config --global merge.tool {{merge_tool}}",
                                "git merge {{source_branch}}",
                                "git mergetool",
                                "git add {{conflict_path}}",
                                "git commit",
                            ],
                            workspace_files=[
                                {
                                    "mode": "write",
                                    "path": "{{conflict_path}}",
                                    "content": "{{resolution_content}}",
                                    "after_command": "git mergetool",
                                }
                            ],
                            label="Resolve {{conflict_path}} with {{merge_tool}}",
                        )
                    ],
                    required_attempts=2,
                ),
                DIFFICULTY_HARD: diff(
                    (4, 5),
                    "Use the merge tool workflow without extra scaffolding.",
                    "Finish the merge through the configured tool.",
                    [
                        template(
                            slug="mergetool-resolution",
                            kind="mergetool",
                            signature="module3.mergetool.hard",
                            cases=[
                                {**hard_conflicts[0], "merge_tool": "vscode"},
                                {**hard_conflicts[1], "merge_tool": "vimdiff"},
                            ],
                            initial_state="{{initial_state}}",
                            target_rule=mergetool_target,
                            solution=[
                                "git config --global merge.tool {{merge_tool}}",
                                "git merge {{source_branch}}",
                                "git mergetool",
                                "git add {{conflict_path}}",
                                "git commit",
                            ],
                            workspace_files=[
                                {
                                    "mode": "write",
                                    "path": "{{conflict_path}}",
                                    "content": "{{resolution_content}}",
                                    "after_command": "git mergetool",
                                }
                            ],
                            label="Resolve {{conflict_path}} with {{merge_tool}}",
                        )
                    ],
                    required_attempts=2,
                ),
            },
        ),
        scenario_dict(
            lesson=MODULE_THREE_LESSONS[5],
            slug="prevent-stale-conflict-merge",
            title="Prevent stale conflict merges",
            focus="git fetch",
            summary="Fetch and compare remote-tracking branch work before merging.",
            explanation="Prevention checks teach students to update remote-tracking refs and inspect differences before they merge a branch that may have drifted.",
            primary=["git fetch"],
            supporting=["git status -sb", "git diff main..origin/main", "git log --oneline --graph --all"],
            concepts=["remote-tracking branch", "fetch before merge", "branch comparison"],
            difficulties={
                DIFFICULTY_EASY: diff(
                    (1, 2),
                    "Fetch origin and compare the updated remote-tracking branch.",
                    "Update the remote-tracking branch without moving local main, then inspect the diff.",
                    [
                        template(
                            slug="prevent-stale-merge",
                            kind="prevention",
                            signature="module3.prevention.easy",
                            cases=prevention_easy,
                            initial_state="{{initial_state}}",
                            target_rule=prevention_target,
                            solution=[
                                "git fetch {{remote}}",
                                "git diff {{target_branch}}..{{remote_branch}}",
                            ],
                            label="Check {{remote_branch}}",
                        )
                    ],
                    required_attempts=2,
                ),
                DIFFICULTY_MEDIUM: diff(
                    (1, 2),
                    "Refresh and compare a named remote branch before integration.",
                    "Fetch the remote branch state and inspect what would come in.",
                    [
                        template(
                            slug="prevent-stale-merge",
                            kind="prevention",
                            signature="module3.prevention.medium",
                            cases=prevention_medium,
                            initial_state="{{initial_state}}",
                            target_rule=prevention_target,
                            solution=[
                                "git fetch {{remote}}",
                                "git status -sb",
                                "git diff {{target_branch}}..{{remote_branch}}",
                            ],
                            label="Compare {{remote_branch}}",
                        )
                    ],
                    required_attempts=2,
                ),
                DIFFICULTY_HARD: diff(
                    (1, 2),
                    "Use prevention diagnostics for a long-lived remote branch.",
                    "Update remote tracking and compare branch history/content before merging.",
                    [
                        template(
                            slug="prevent-stale-merge",
                            kind="prevention",
                            signature="module3.prevention.hard",
                            cases=prevention_hard,
                            initial_state="{{initial_state}}",
                            target_rule=prevention_target,
                            solution=[
                                "git fetch {{remote}}",
                                "git log --oneline --graph --all",
                                "git diff {{target_branch}}..{{remote_branch}}",
                            ],
                            label="Review {{remote_branch}}",
                        )
                    ],
                    required_attempts=2,
                ),
            },
        ),
        scenario_dict(
            lesson=MODULE_THREE_LESSONS[6],
            slug="cherry-pick-selected-commit",
            title="Cherry-pick a selected commit",
            focus="git cherry-pick",
            summary="Apply a specific commit to the current branch without merging all source history.",
            explanation="Cherry-pick creates a new commit on the target branch with copied changes. In no-commit mode, those copied changes remain staged for review.",
            primary=["git cherry-pick"],
            supporting=["git log --oneline --graph --all", "git show <commit>", "git status"],
            concepts=["selective commit application", "backport", "new commit id"],
            difficulties={
                DIFFICULTY_EASY: diff(
                    (1, 1),
                    "Cherry-pick one named fix onto the current release branch.",
                    "Apply the selected commit as a new commit on the current branch.",
                    [
                        template(
                            slug="cherry-pick",
                            kind="cherry-pick",
                            signature="module3.cherry.easy",
                            cases=[
                                {**case, "solution_commands": ["git cherry-pick c1"]}
                                for case in cherry_easy
                            ],
                            initial_state="{{initial_state}}",
                            target_rule=cherry_target,
                            solution="{{solution_commands}}",
                            label="Cherry-pick {{source_commit}}",
                        )
                    ],
                    required_attempts=3,
                ),
                DIFFICULTY_MEDIUM: diff(
                    (1, 2),
                    "Cherry-pick either directly or into the index for review.",
                    "Reach the requested cherry-pick state.",
                    [
                        template(
                            slug="cherry-pick",
                            kind="cherry-pick",
                            signature="module3.cherry.medium.commit",
                            cases=[
                                {**case, "solution_commands": ["git cherry-pick c1"]}
                                for case in cherry_medium[:2]
                            ],
                            initial_state="{{initial_state}}",
                            target_rule=cherry_target,
                            solution="{{solution_commands}}",
                            label="Cherry-pick {{source_commit}}",
                        ),
                        template(
                            slug="cherry-no-commit",
                            kind="cherry-pick",
                            signature="module3.cherry.medium.no-commit",
                            cases=[cherry_medium[2]],
                            initial_state="{{initial_state}}",
                            target_rule=cherry_no_commit_target,
                            solution="{{solution_commands}}",
                            label="Stage cherry-pick {{source_commit}}",
                        ),
                    ],
                    required_attempts=3,
                ),
                DIFFICULTY_HARD: diff(
                    (1, 2),
                    "Choose between completing and aborting cherry-pick states.",
                    "Reach the requested selective-application outcome.",
                    [
                        template(
                            slug="cherry-pick",
                            kind="cherry-pick",
                            signature="module3.cherry.hard.commit",
                            cases=[
                                {**cherry_hard[0], "solution_commands": ["git cherry-pick c1"]}
                            ],
                            initial_state="{{initial_state}}",
                            target_rule=cherry_target,
                            solution="{{solution_commands}}",
                            label="Cherry-pick {{source_commit}}",
                        ),
                        template(
                            slug="cherry-abort",
                            kind="cherry-pick-abort",
                            signature="module3.cherry.hard.abort",
                            cases=[cherry_hard[1]],
                            initial_state="{{initial_state}}",
                            target_rule=cherry_abort_target,
                            solution="{{solution_commands}}",
                            label="Abort cherry-pick",
                        ),
                    ],
                    required_attempts=2,
                ),
            },
        ),
        scenario_dict(
            lesson=MODULE_THREE_LESSONS[7],
            slug="module3-integrated-conflict-workflow",
            title="Complete an integrated conflict workflow",
            focus="conflict resolution workflow",
            summary="Combine fetch, diagnostics, merge conflict resolution, mergetool, merge continuation, and cherry-pick.",
            explanation="This final scenario combines the Module 3 skills in one repository: refresh remote knowledge, inspect the incoming branch, resolve the merge conflict, finish the merge, then apply a selected hotfix commit.",
            primary=["git fetch", "git merge", "git mergetool", "git cherry-pick"],
            supporting=["git status", "git diff", "git diff --check", "git ls-files -u", "git log --oneline --graph --all"],
            concepts=["integrated workflow", "conflict diagnostics", "merge tool", "selective commit", "clean final state"],
            difficulties={
                DIFFICULTY_EASY: diff(
                    (5, 7),
                    "Refresh remote state, resolve a merge conflict with a tool, and apply a hotfix.",
                    "Reach a clean branch containing both the resolved merge content and the hotfix.",
                    [
                        template(
                            slug="integrated-conflict-workflow",
                            kind="capstone",
                            signature="module3.capstone.easy",
                            cases=capstone_easy,
                            initial_state="{{initial_state}}",
                            target_rule=capstone_target,
                            solution=[
                                "git fetch {{remote}}",
                                "git diff main..{{source_branch}}",
                                "git merge {{source_branch}}",
                                "git mergetool --tool {{merge_tool}} {{conflict_path}}",
                                "git add {{conflict_path}}",
                                "git merge --continue",
                                "git cherry-pick {{source_commit}}",
                            ],
                            workspace_files=[
                                {
                                    "mode": "write",
                                    "path": "{{conflict_path}}",
                                    "content": "{{resolution_content}}",
                                    "after_command": "git mergetool --tool {{merge_tool}} {{conflict_path}}",
                                }
                            ],
                            label="Complete {{project}} integration",
                        )
                    ],
                    required_attempts=2,
                ),
                DIFFICULTY_MEDIUM: diff(
                    (5, 7),
                    "Use diagnostics plus mergetool to land remote work and a selected hotfix.",
                    "Finish the integrated conflict workflow cleanly.",
                    [
                        template(
                            slug="integrated-conflict-workflow",
                            kind="capstone",
                            signature="module3.capstone.medium",
                            cases=capstone_medium,
                            initial_state="{{initial_state}}",
                            target_rule=capstone_target,
                            solution=[
                                "git fetch {{remote}}",
                                "git status -sb",
                                "git diff main..{{source_branch}}",
                                "git merge {{source_branch}}",
                                "git ls-files -u",
                                "git mergetool --tool {{merge_tool}} {{conflict_path}}",
                                "git add {{conflict_path}}",
                                "git merge --continue",
                                "git cherry-pick {{source_commit}}",
                            ],
                            workspace_files=[
                                {
                                    "mode": "write",
                                    "path": "{{conflict_path}}",
                                    "content": "{{resolution_content}}",
                                    "after_command": "git mergetool --tool {{merge_tool}} {{conflict_path}}",
                                }
                            ],
                            label="Integrate {{project}}",
                        )
                    ],
                    required_attempts=2,
                ),
                DIFFICULTY_HARD: diff(
                    (5, 8),
                    "Complete the full conflict-resolution workflow with minimal scaffolding.",
                    "Combine prevention, conflict diagnostics, mergetool, merge continuation, and cherry-pick.",
                    [
                        template(
                            slug="integrated-conflict-workflow",
                            kind="capstone",
                            signature="module3.capstone.hard",
                            cases=capstone_hard,
                            initial_state="{{initial_state}}",
                            target_rule=capstone_target,
                            solution=[
                                "git fetch {{remote}}",
                                "git log --oneline --graph --all",
                                "git diff main..{{source_branch}}",
                                "git merge {{source_branch}}",
                                "git diff --check {{conflict_path}}",
                                "git mergetool --tool {{merge_tool}} {{conflict_path}}",
                                "git add {{conflict_path}}",
                                "git merge --continue",
                                "git cherry-pick {{source_commit}}",
                            ],
                            workspace_files=[
                                {
                                    "mode": "write",
                                    "path": "{{conflict_path}}",
                                    "content": "{{resolution_content}}",
                                    "after_command": "git mergetool --tool {{merge_tool}} {{conflict_path}}",
                                }
                            ],
                            label="Review {{project}} integration",
                        )
                    ],
                    required_attempts=2,
                ),
            },
        ),
    ]


class Command(BaseCommand):
    help = "Seed Module 3 conflict-resolution scenario skill focuses and authored variants."

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true")
        parser.add_argument("--confirm", action="store_true")
        parser.add_argument("--validate-build", action="store_true")

    @transaction.atomic
    def handle(self, *args, **options):
        if options["reset"]:
            self._reset_module_three(confirm=options["confirm"])

        seed_git_command_content_library()
        unit, _ = LearningUnit.objects.update_or_create(
            slug="conflict-resolution",
            defaults={
                "number": 3,
                "title": "Conflict Resolution",
                "description": "Practice conflict diagnostics, manual resolution, mergetool workflows, prevention checks, cherry-picking, and integrated recovery.",
                "is_orientation": False,
                "is_published": True,
                "sort_order": 3,
            },
        )
        lesson_by_order = {}
        for order, slug, title, subtitle in MODULE_THREE_LESSONS:
            lesson, _ = Lesson.objects.update_or_create(
                unit=unit,
                slug=slug,
                defaults={
                    "title": title,
                    "subtitle": subtitle,
                    "content_html": self._anchor_html(title, subtitle),
                    "scoped_css": "",
                    "interaction_steps": [],
                    "is_published": True,
                    "sort_order": order,
                },
            )
            lesson_by_order[order] = lesson

        specs = module_three_scenarios()
        ScenarioSkillFocus.objects.filter(learning_unit=unit).exclude(
            slug__in=[spec["slug"] for spec in specs]
        ).update(is_published=False)

        for spec in specs:
            lesson_order, _, _, _ = spec["lesson"]
            scenario, _ = ScenarioSkillFocus.objects.update_or_create(
                learning_unit=unit,
                slug=spec["slug"],
                defaults={
                    "lesson": lesson_by_order[lesson_order],
                    "title": spec["title"],
                    "focus": spec["focus"],
                    "summary": spec["summary"],
                    "short_explanation": spec["explanation"],
                    "skill_focus_type": spec["kind"],
                    "primary_focus_commands": spec["primary"],
                    "supporting_diagnostic_commands": spec["supporting"],
                    "safe_demo_commands": self._demo_commands(spec),
                    "demo_repository_state": self._demo_state(spec),
                    "demo_dag_config": {},
                    "demo_explanation_steps": [],
                    "command_preview_config": self._command_preview_config(spec),
                    "related_git_concepts": spec["concepts"],
                    "narrative": spec["summary"],
                    "task_prompt": "Start an authored practice variant and reach the requested repository outcome.",
                    "is_published": True,
                    "sort_order": lesson_order,
                },
            )
            for difficulty, dspec in spec["difficulties"].items():
                difficulty_instance, _ = DifficultyInstance.objects.update_or_create(
                    scenario=scenario,
                    difficulty=difficulty,
                    defaults={
                        "completion_type": dspec["completion_type"],
                        "required_successful_attempts": dspec["required_successful_attempts"],
                        "narrative": dspec["narrative"],
                        "task_prompt": dspec["task"],
                        "is_published": True,
                    },
                )
                min_count, _authored_max = dspec["policy"]
                max_count = DIFFICULTY_MAX_COUNTED_COMMANDS[difficulty]
                CommandCountPolicy.objects.update_or_create(
                    difficulty_instance=difficulty_instance,
                    defaults={
                        "min_counted_commands": min_count,
                        "max_counted_commands": max_count,
                        "non_counted_patterns": DIAG_PATTERNS,
                    },
                )
                variants = self._render_variants(
                    scenario=scenario,
                    difficulty_instance=difficulty_instance,
                    dspec=dspec,
                )
                active_semantic_keys = []
                for variant in variants:
                    active_semantic_keys.append(variant.semantic_key)
                    ScenarioVariant.objects.update_or_create(
                        difficulty_instance=difficulty_instance,
                        semantic_key=variant.semantic_key,
                        defaults={
                            "scenario": scenario,
                            "slug": variant.slug,
                            "label": variant.label,
                            "structure_signature": variant.structure_signature,
                            "initial_state": variant.initial_state,
                            "target_rule": variant.target_rule,
                            "target_state": variant.target_state,
                            "expected_state_diagram": variant.expected_state_diagram,
                            "solution_commands": variant.solution_commands,
                            "case_id": variant.case_id,
                            "parameter_context": variant.parameter_context,
                            "student_context": variant.student_context,
                            "is_published": True,
                        },
                    )
                ScenarioVariant.objects.filter(difficulty_instance=difficulty_instance).exclude(
                    semantic_key__in=active_semantic_keys
                ).update(is_published=False)

        self.stdout.write(self.style.SUCCESS("Seeded Module 3 authored scenario variants."))
        if options["validate_build"]:
            self.stdout.write(self.style.SUCCESS("All Module 3 authored variants are valid."))

    def _render_variants(
        self,
        *,
        scenario: ScenarioSkillFocus,
        difficulty_instance: DifficultyInstance,
        dspec: dict[str, Any],
    ) -> list[ScenarioVariant]:
        materializer = StaticCaseMaterializer()
        variants = []
        for authored_template in dspec["templates"]:
            for index, case in enumerate(authored_template["cases"], start=1):
                try:
                    variants.append(
                        materializer.materialize_variant(
                            difficulty_instance=difficulty_instance,
                            template=authored_template,
                            case=case,
                            index=index,
                        )
                    )
                except (KeyError, ScenarioVariantBuildError) as exc:
                    raise CommandError(
                        f"{scenario.slug}/{difficulty_instance.difficulty}/"
                        f"{authored_template['slug']}/{case.get('case_id')}: {exc}"
                    ) from exc
        if not variants:
            raise CommandError(f"{scenario.slug}/{difficulty_instance.difficulty}: no variants")
        return variants

    def _reset_module_three(self, *, confirm: bool):
        if not settings.DEBUG:
            raise CommandError("--reset is only available when DEBUG=True.")
        if not confirm:
            raise CommandError("Pass --confirm with --reset to clear Module 3 seeded data.")
        unit = LearningUnit.objects.filter(slug="conflict-resolution").first()
        if not unit:
            return
        CompletionRecord.objects.filter(scenario__learning_unit=unit).delete()
        ScenarioSession.objects.filter(learning_unit=unit).delete()
        ScenarioVariant.objects.filter(scenario__learning_unit=unit).delete()
        DifficultyInstance.objects.filter(scenario__learning_unit=unit).delete()
        ScenarioSkillFocus.objects.filter(learning_unit=unit).delete()
        OrientationProgress.objects.filter(lesson__unit=unit).delete()
        unit.lessons.all().delete()
        unit.delete()

    def _anchor_html(self, title: str, subtitle: str) -> str:
        return f"""
<section class=\"internal-scenario-anchor\">
  <h1>{title}</h1>
  <p>{subtitle}</p>
  <p>Internal scenario anchor for Module 3 conflict-resolution practice.</p>
</section>
""".strip()

    def _demo_state(self, spec: dict[str, Any]) -> dict[str, Any]:
        first_case = next(
            case
            for dspec in spec["difficulties"].values()
            for authored_template in dspec["templates"]
            for case in authored_template["cases"]
        )
        return first_case["initial_state"]

    def _demo_commands(self, spec: dict[str, Any]) -> list[str]:
        focus = spec["focus"]
        commands = {
            "conflict diagnostics": [
                "git status",
                "git ls-files -u",
                "git diff --ours src/auth.js",
                "git diff --theirs src/auth.js",
                "git diff --base src/auth.js",
                "git diff --check src/auth.js",
            ],
            "git merge": [
                "git log --oneline --graph --all",
                "git merge feature/auth-timeout",
                "git status",
                "git ls-files -u",
            ],
            "manual conflict resolution": ["git status", "git diff", "git add src/auth.js", "git commit"],
            "git checkout conflict side": [
                "git status",
                "git diff --ours src/auth.js",
                "git diff --theirs src/auth.js",
                "git checkout --ours src/auth.js",
                "git add src/auth.js",
                "git commit",
            ],
            "git merge --abort": [
                "git status",
                "git ls-files -u",
                "git merge --abort",
            ],
            "git mergetool": [
                "git config --global merge.tool vscode",
                "git merge feature/auth-timeout",
                "git ls-files -u",
                "git mergetool",
                "git add src/auth.js",
                "git commit",
                "git status",
            ],
            "git fetch": [
                "git fetch origin",
                "git status -sb",
                "git diff main..origin/main",
            ],
            "git cherry-pick": [
                "git log --oneline --graph --all",
                "git show c1",
                "git cherry-pick c1",
                "git cherry-pick --no-commit c1",
                "git cherry-pick --abort",
            ],
            "conflict resolution workflow": [
                "git fetch origin",
                "git diff main..origin/feature/auth-timeout",
                "git merge origin/feature/auth-timeout",
                "git mergetool --tool vscode src/auth.js",
                "git add src/auth.js",
                "git merge --continue",
                "git cherry-pick c3",
            ],
        }.get(focus, [])
        return commands

    def _command_preview_config(self, spec: dict[str, Any]) -> dict[str, Any]:
        commands = self._demo_commands(spec)
        diagnostic = bool(commands) and all(is_diagnostic_command(command) for command in commands)
        return {
            "schema_version": 2,
            "title": f"{spec['focus']} command preview",
            "intro": spec["explanation"],
            "purpose": "Understand the Module 3 repository-state transition before starting an authored practice variant.",
            "focus_label": spec["focus"],
            "command_title": spec["title"],
            "command_refs": self._preview_command_refs(commands),
            "supported_demo_commands": commands,
            "demo_repository_state": self._demo_state(spec),
            "demo_dag_config": {},
            "diagnostic": diagnostic,
            "counted": not diagnostic,
        }

    def _preview_command_refs(self, commands: list[str]) -> list[dict[str, Any]]:
        refs = []
        seen = set()
        for command in commands:
            if not command.startswith("git "):
                continue
            syntax = command_preview_syntax_for_command(command)
            key = command_content_key_for_command(syntax or command)
            identity = (key, syntax)
            if identity in seen:
                continue
            seen.add(identity)
            refs.append(
                {
                    "id": f"{key}-{len(refs) + 1}",
                    "key": key,
                    "command": syntax or command,
                    "include_section_ids": command_preview_section_ids_for_command(
                        syntax or command
                    ),
                }
            )
        return refs
