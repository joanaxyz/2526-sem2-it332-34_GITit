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
        "resolving-conflicts-manually",
        "Resolving Merge Conflicts Manually",
        "Resolve conflict content, stage it, and complete the merge.",
    ),
    (
        2,
        "using-a-merge-tool",
        "Resolving Conflicts Using a Merge Tool",
        "Configure and run a merge tool to resolve conflicts.",
    ),
    (
        3,
        "cherry-picking-commits",
        "Cherry-Picking Commits",
        "Apply selected commits without merging an entire branch.",
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
            "story": "{{context}}",
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
            "story": "{{context}}",
            "required_details": [
                {"label": "Current branch", "value": "main"},
                {"label": "Source branch", "value": "{{source_branch}}"},
                {"label": "Expected conflict file", "value": "{{conflict_path}}"},
            ],
        }
    if kind == "manual-resolution":
        return {
            "story": "{{context}}",
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
            "story": "{{context}}",
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
            "story": "{{context}}",
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
            "story": "{{context}}",
            "required_details": [
                {"label": "Current branch", "value": "main"},
                {"label": "Conflict file", "value": "{{conflict_path}}"},
                {"label": "Pre-merge tip", "value": "{{pre_merge_tip}}"},
            ],
        }
    if kind == "mergetool":
        return {
            "story": "{{context}}",
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
            "story": "{{context}}",
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
            "story": "{{context}}",
            "required_details": [
                {"label": "Current branch", "value": "{{target_branch}}"},
                {"label": "Source commit", "value": "{{source_commit}}"},
                {"label": "Expected file", "value": "{{target_path}}"},
                {"label": "Expected token", "value": "{{expected_token}}"},
            ],
        }
    if kind == "cherry-pick-abort":
        return {
            "story": "{{context}}",
            "required_details": [
                {"label": "Current branch", "value": "{{target_branch}}"},
                {"label": "Original branch tip", "value": "{{original_tip}}"},
            ],
        }
    if kind == "capstone":
        return {
            "story": "{{context}}",
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
    context: str,
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
        "context": context,
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
    context: str,
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
        "context": context,
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
    context: str,
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
        "context": context,
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
    context: str,
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
        "context": context,
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
            context="You're integrating a teammate's auth timeout changes into main. Both branches modified src/auth.js — yours increased the timeout, theirs lowered it. Git cannot auto-merge the conflicting values.",
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
            context="A profile page rebrand landed on two separate branches. Both changed src/profile.tsx — main updated the title to 'Account profile', the feature branch to 'Member profile'. Neither can auto-merge.",
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
            context="Two billing teams updated currency handling simultaneously. src/billing.py was changed on main to PHP and on the feature branch to EUR. The merge cannot proceed without a resolution.",
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
        conflict_repo_case(
            "conflict-easy-config-copy",
            context="You're integrating a teammate's debug configuration changes into main. Both branches modified src/config.py — yours added a log level, theirs re-enabled debug mode. Git cannot auto-merge them.",
            project="config-service",
            conflict_path="src/config.py",
            base_content="debug=False",
            main_content="debug=False\nlog_level=INFO",
            feature_content="debug=True\nlog_level=DEBUG",
            resolution_content="debug=False\nlog_level=INFO\nverbose_errors=True",
            resolution_token="verbose_errors=True",
            source_branch="feature/debug-config",
            answer_anchor="merge feature/debug-config produces conflict in src/config.py",
        ),
        conflict_repo_case(
            "conflict-easy-navbar-copy",
            context="A navbar rebrand landed on two branches simultaneously. Both changed src/components/Navbar.tsx — main updated the brand to 'MyApp', the feature branch to 'BetaApp'. The merge cannot proceed without a manual resolution.",
            project="frontend-app",
            conflict_path="src/components/Navbar.tsx",
            base_content="brand=AppName",
            main_content="brand=MyApp",
            feature_content="brand=BetaApp",
            resolution_content="brand=MyApp\ntagline=Beta",
            resolution_token="tagline=Beta",
            source_branch="feature/navbar-rebrand",
            answer_anchor="merge feature/navbar-rebrand produces conflict in src/components/Navbar.tsx",
        ),
    ]
    medium_conflicts = [
        conflict_repo_case(
            "conflict-medium-router",
            context="Two teams updated the support portal's route configuration. main renamed '/help' to '/support' while the feature branch renamed it to '/help-center'. The routes.ts file now conflicts.",
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
            context="Policy review modes diverged. main enforces strict review while the feature branch introduces assisted review. src/policy.yml has a merge conflict that needs manual resolution.",
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
        conflict_repo_case(
            "conflict-medium-gateway",
            context="Two teams updated the API gateway timeout configuration. main increased the timeout to 60s, the feature branch decreased it to 15s for resilience testing. config/gateway.yml now has a conflict.",
            project="api-gateway",
            conflict_path="config/gateway.yml",
            base_content="timeout: 30",
            main_content="timeout: 60",
            feature_content="timeout: 15",
            resolution_content="timeout: 60\nretry_on_timeout: true",
            resolution_token="retry_on_timeout: true",
            source_branch="feature/gateway-resilience",
            answer_anchor="merge feature/gateway-resilience conflicts in config/gateway.yml",
        ),
    ]
    hard_conflicts = [
        conflict_repo_case(
            "conflict-hard-pricing",
            context="Regional and loyalty discount logic landed on separate branches. Both modified the discount formula in src/pricing.rb — one uses regional_rate, the other loyalty_rate. The merge fails.",
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
            context="Two database migrations modified the orders status column definition. main added varchar(24) while the feature added 'not null'. schema/orders.sql has a conflict that needs a combined resolution.",
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
        conflict_repo_case(
            "conflict-hard-migration",
            context="Two database engineers modified the users email column definition simultaneously. main added 'unique', the feature branch changed the type to varchar(320). db/migrations/001_users.sql conflicts and needs a combined resolution.",
            project="user-service",
            conflict_path="db/migrations/001_users.sql",
            base_content="email text",
            main_content="email text unique",
            feature_content="email varchar(320)",
            resolution_content="email varchar(320) unique",
            resolution_token="varchar(320) unique",
            source_branch="feature/email-constraint",
            answer_anchor="merge feature/email-constraint conflicts in db/migrations/001_users.sql",
        ),
    ]

    manual_easy = [
        conflicted_case(case, commit_message="Resolve conflict cleanly")
        for case in easy_conflicts
    ]
    manual_medium = [
        conflicted_case(case, commit_message="Resolve integration conflict")
        for case in medium_conflicts
    ]
    manual_hard = [
        conflicted_case(case, commit_message="Resolve release conflict")
        for case in [*hard_conflicts, medium_conflicts[0]]
    ]
    accept_ours_easy = [
        conflict_side_case(case, side="ours", commit_message="Keep current branch version")
        for case in easy_conflicts
    ]
    accept_theirs_medium = [
        conflict_side_case(case, side="theirs", commit_message="Accept incoming branch version")
        for case in [*medium_conflicts, easy_conflicts[0]]
    ]
    accept_side_hard = [
        conflict_side_case(hard_conflicts[0], side="ours", commit_message="Keep release branch version"),
        conflict_side_case(hard_conflicts[1], side="theirs", commit_message="Accept incoming schema version"),
        conflict_side_case(hard_conflicts[2], side="ours", commit_message="Keep email constraint version"),
        conflict_side_case(medium_conflicts[0], side="theirs", commit_message="Accept incoming route version"),
    ]
    merge_abort_easy = [merge_abort_case(case) for case in easy_conflicts]
    merge_abort_medium = [merge_abort_case(case) for case in [*medium_conflicts, easy_conflicts[0]]]
    merge_abort_hard = [merge_abort_case(case) for case in [*hard_conflicts, medium_conflicts[0]]]

    diagnostic_case_fields = {"solution_workspace_files", "solution_commands", "commit_message"}
    diagnostic_easy = [
        {key: value for key, value in case.items() if key not in diagnostic_case_fields}
        for case in manual_easy
    ]
    diagnostic_medium = [
        {key: value for key, value in case.items() if key not in diagnostic_case_fields}
        for case in manual_medium
    ]
    diagnostic_hard = [
        {key: value for key, value in case.items() if key not in diagnostic_case_fields}
        for case in manual_hard
    ]

    cherry_easy = [
        cherry_pick_case(
            "cherry-easy-login-timeout",
            context="The release/1.0 branch needs a critical login timeout fix that was already merged to main. You need to bring just that one patch to the release branch without pulling in any other main changes.",
            project="release-1.0",
            target_branch="release/1.0",
            source_commit="c1",
            target_path="src/login.js",
            expected_token="timeout-fix-v1",
            answer_anchor="release branch receives login timeout patch as a new commit",
        ),
        cherry_pick_case(
            "cherry-easy-invoice-rounding",
            context="A rounding bug in the invoice service was patched on main. Your release/1.1 branch ships tomorrow and needs only that fix — not the other work that landed after it.",
            project="release-1.1",
            target_branch="release/1.1",
            source_commit="c1",
            target_path="src/invoice.py",
            expected_token="rounding-fix-v1",
            answer_anchor="release branch receives invoice rounding patch as a new commit",
        ),
        cherry_pick_case(
            "cherry-easy-export-null",
            context="A null-export crash fix was committed to main as part of a larger feature. You're on release/2.0 and need to backport just the crash fix — not the surrounding feature changes.",
            project="release-2.0",
            target_branch="release/2.0",
            source_commit="c1",
            target_path="src/export.ts",
            expected_token="null-export-fix",
            answer_anchor="release branch receives export null patch as a new commit",
        ),
        cherry_pick_case(
            "cherry-easy-rate-limit",
            context="A rate-limiter fix was merged into main after the release branch was cut. Cherry-pick just that commit onto release/1.2 to patch the rate limiting bug without pulling in unrelated main work.",
            project="release-1.2",
            target_branch="release/1.2",
            source_commit="c1",
            target_path="src/ratelimit.py",
            expected_token="rate-limit-fix-v1",
            answer_anchor="release branch receives rate limit patch as a new commit",
        ),
        cherry_pick_case(
            "cherry-easy-null-check",
            context="A null check fix for the parser was committed to main. The release/2.1 branch needs it immediately. Cherry-pick the specific commit rather than merging all of main into the release branch.",
            project="release-2.1",
            target_branch="release/2.1",
            source_commit="c1",
            target_path="src/parser.ts",
            expected_token="null-check-fix-v1",
            answer_anchor="release branch receives null check patch as a new commit",
        ),
    ]
    cherry_medium = [
        *cherry_easy[:2],
        {
            **cherry_pick_case(
                "cherry-medium-no-commit",
                context="Your team wants to review the report hotfix content before it commits to release/review. Stage the cherry-picked changes for inspection without creating a commit.",
                project="release-review",
                target_branch="release/review",
                source_commit="c1",
                target_path="src/report.ts",
                expected_token="report-hotfix",
                answer_anchor="no-commit cherry-pick stages report hotfix for review",
            ),
            "solution_commands": ["git cherry-pick --no-commit c1"],
        },
        {
            **cherry_pick_case(
                "cherry-medium-staged-review",
                context="A cache hotfix needs to be staged on the release branch for review before committing. Use cherry-pick --no-commit to apply the changes from main so a teammate can inspect the diff first.",
                project="release-staged",
                target_branch="release/staged",
                source_commit="c1",
                target_path="src/cache.py",
                expected_token="cache-hotfix",
                answer_anchor="no-commit cherry-pick stages cache hotfix for review",
            ),
            "solution_commands": ["git cherry-pick --no-commit c1"],
        },
    ]
    cherry_hard_commit = cherry_pick_case(
        "cherry-hard-no-commit-finalize",
        context="A queue management hotfix must land on the release/finalize branch without staged review — cherry-pick it and finalize immediately with a clean commit.",
        project="release-finalize",
        target_branch="release/finalize",
        source_commit="c1",
        target_path="src/queue.ts",
        expected_token="queue-hotfix",
        answer_anchor="cherry-pick applied and committed to release/finalize",
    )
    cherry_hard_abort = cherry_pick_case(
        "cherry-hard-abort",
        context="A cherry-pick of the search hotfix is already in progress on release/abort but the changes conflict with local work. The cherry-pick must be canceled and the branch returned to its original state.",
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
    cherry_hard = [
        {**cherry_easy[2], "solution_commands": ["git cherry-pick c1"]},
        cherry_hard_abort,
        {**cherry_hard_commit, "solution_commands": ["git cherry-pick c1"]},
        {**cherry_easy[3], "solution_commands": ["git cherry-pick c1"]},
    ]

    prevention_easy = [
        prevention_case(
            "prevent-easy-docs-refresh",
            context="Your team has been pushing doc updates to origin. Before you merge anything into main, you want to see what the remote has that you don't — without moving your local branch.",
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
            context="The API contracts repo has received updates from another team. You want to inspect what changed in openapi.yml on the remote before deciding whether to merge.",
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
        prevention_case(
            "prevent-easy-config-sync",
            context="Your config-sync main branch may be behind origin. Fetch origin to update remote-tracking refs, then compare local vs origin/main before merging to catch stale configuration.",
            project="config-sync",
            target_branch="main",
            remote="origin",
            remote_branch="origin/main",
            local_tip="c1",
            remote_tip="c2",
            watched_path="config/app.yml",
            remote_content="config-v2",
            answer_anchor="fetch reveals origin/main is ahead; diff confirms config/app.yml changed",
        ),
        prevention_case(
            "prevent-easy-auth-tokens",
            context="The auth-tokens repo has upstream token rotation changes. Fetch origin and compare local vs origin/main to verify what changed in src/tokens.py before merging.",
            project="auth-tokens",
            target_branch="main",
            remote="origin",
            remote_branch="origin/main",
            local_tip="c1",
            remote_tip="c2",
            watched_path="src/tokens.py",
            remote_content="tokens-v2",
            answer_anchor="fetch reveals origin/main is ahead; diff confirms src/tokens.py changed",
        ),
    ]
    prevention_medium = [
        prevention_case(
            "prevent-medium-release-notes",
            context="A release manager has been pushing changelog updates to origin/release-notes. You're planning a merge but want to review what's on that branch without integrating it yet.",
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
            context="The design team has been evolving the color token values on origin/design-tokens. You need to see what changed in tokens/colors.json before you integrate those tokens into main.",
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
        prevention_case(
            "prevent-medium-db-schema",
            context="The db-schema repo has incoming schema changes from origin. Fetch and compare local main vs origin/db-schema to verify what changed in schema/users.sql before merging.",
            project="db-schema",
            target_branch="main",
            remote="origin",
            remote_branch="origin/db-schema",
            local_tip="c1",
            remote_tip="c2",
            watched_path="schema/users.sql",
            remote_content="schema-v2",
            answer_anchor="fetch reveals origin/db-schema is ahead; diff confirms schema/users.sql changed",
        ),
        prevention_case(
            "prevent-medium-notifications",
            context="The notifications repo has upstream notify changes. Fetch and inspect origin/notifications-v2 vs local main to see what changed in src/notify.py before you merge.",
            project="notifications",
            target_branch="main",
            remote="origin",
            remote_branch="origin/notifications-v2",
            local_tip="c1",
            remote_tip="c2",
            watched_path="src/notify.py",
            remote_content="notify-v2",
            answer_anchor="fetch reveals origin/notifications-v2 is ahead; diff confirms src/notify.py changed",
        ),
    ]
    prevention_hard = [
        prevention_case(
            "prevent-hard-payments",
            context="The payments reconciliation branch on origin has drifted significantly from your local main. Finance depends on the accuracy of src/reconcile.py — you need to know what changed remotely before any merge.",
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
            context="A search ranking algorithm update was pushed to origin/search-ranking. Before merging it into main, you need to review the delta in src/ranking.ts without pulling any changes locally.",
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
        prevention_case(
            "prevent-hard-billing-reconcile",
            context="The billing-reconcile service has critical upstream changes. Fetch origin and carefully compare local main vs origin/billing-reconcile before merging — a stale merge here could break reconciliation.",
            project="billing-reconcile",
            target_branch="main",
            remote="origin",
            remote_branch="origin/billing-reconcile",
            local_tip="c1",
            remote_tip="c2",
            watched_path="src/billing.py",
            remote_content="billing-v2",
            answer_anchor="fetch reveals origin/billing-reconcile is ahead; diff confirms src/billing.py changed",
        ),
        prevention_case(
            "prevent-hard-infra-pipelines",
            context="The infra-pipelines repo has CI/CD pipeline changes on origin. Fetch and compare before merging — changes to .github/workflows/deploy.yml affect production deployments.",
            project="infra-pipelines",
            target_branch="main",
            remote="origin",
            remote_branch="origin/infra-pipelines",
            local_tip="c1",
            remote_tip="c2",
            watched_path=".github/workflows/deploy.yml",
            remote_content="pipeline-v2",
            answer_anchor="fetch reveals origin/infra-pipelines is ahead; diff confirms deploy.yml changed",
        ),
    ]

    capstone_easy = [
        capstone_case(
            "capstone-easy-auth-hotfix",
            context="The auth-service remote has new feature work that conflicts with your local timeout changes. A separate session hotfix was also committed on main. You need to land both: resolve the remote conflict with a merge tool, then cherry-pick the session fix.",
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
            context="A profile rebrand feature on the remote conflicts with your local copy changes. An avatar bug fix also needs to land. Your goal: resolve the remote conflict through the merge tool, then bring in only the avatar fix.",
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
        capstone_case(
            "capstone-easy-config-hotfix",
            context="config-service has a remote conflict and a separate hotfix that both need to land. Fetch the remote feature branch, configure vscode as the merge tool, resolve the conflict in src/config.py, then cherry-pick the hotfix.",
            project="config-service",
            conflict_path="src/config.py",
            hotfix_path="src/feature_flags.py",
            base_content="debug=False",
            main_content="debug=False\nlog_level=INFO",
            feature_content="debug=True\nlog_level=DEBUG",
            resolution_content="debug=False\nlog_level=INFO\nverbose_errors=True",
            resolution_token="verbose_errors=True",
            hotfix_token="flags-hotfix-v1",
            source_branch="origin/feature/debug-config",
            merge_tool="vscode",
            answer_anchor="config-service conflict resolved with vscode and hotfix cherry-picked",
        ),
        capstone_case(
            "capstone-easy-navbar-hotfix",
            context="frontend-app has a remote navbar conflict and a footer hotfix waiting. Fetch the rebrand branch, configure vimdiff, resolve the Navbar.tsx conflict, then cherry-pick the footer hotfix.",
            project="frontend-app",
            conflict_path="src/components/Navbar.tsx",
            hotfix_path="src/components/Footer.tsx",
            base_content="brand=AppName",
            main_content="brand=MyApp",
            feature_content="brand=BetaApp",
            resolution_content="brand=MyApp\ntagline=Beta",
            resolution_token="tagline=Beta",
            hotfix_token="footer-hotfix-v1",
            source_branch="origin/feature/navbar-rebrand",
            merge_tool="vimdiff",
            answer_anchor="frontend-app conflict resolved with vimdiff and footer hotfix cherry-picked",
        ),
    ]
    capstone_medium = [
        capstone_case(
            "capstone-medium-support-hotfix",
            context="Two teams renamed the help route differently — the conflict in src/routes.ts needs manual mergetool resolution. A ticket system hotfix also needs to land via cherry-pick after the merge is complete.",
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
            context="Policy configuration diverged between main and the remote feature branch. The src/policy.yml conflict needs mergetool resolution, and an audit system fix needs to be cherry-picked onto main afterward.",
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
        capstone_case(
            "capstone-medium-gateway-hotfix",
            context="api-gateway needs the resilience conflict resolved using vimdiff and an auth hotfix applied. Fetch, configure vimdiff, resolve the timeout conflict, commit, then cherry-pick the auth fix.",
            project="api-gateway",
            conflict_path="config/gateway.yml",
            hotfix_path="config/auth.yml",
            base_content="timeout: 30",
            main_content="timeout: 60",
            feature_content="timeout: 15",
            resolution_content="timeout: 60\nretry_on_timeout: true",
            resolution_token="retry_on_timeout: true",
            hotfix_token="auth-hotfix-v1",
            source_branch="origin/feature/gateway-resilience",
            merge_tool="vimdiff",
            answer_anchor="api-gateway conflict resolved with vimdiff and auth hotfix cherry-picked",
        ),
        capstone_case(
            "capstone-medium-migration-hotfix",
            context="user-service has an email column conflict and a database index hotfix. Fetch origin, configure vscode, resolve the migration conflict, commit, then cherry-pick the index hotfix.",
            project="user-service",
            conflict_path="db/migrations/001_users.sql",
            hotfix_path="db/migrations/002_indexes.sql",
            base_content="email text",
            main_content="email text unique",
            feature_content="email varchar(320)",
            resolution_content="email varchar(320) unique",
            resolution_token="varchar(320) unique",
            hotfix_token="index-hotfix-v1",
            source_branch="origin/feature/email-constraint",
            merge_tool="vscode",
            answer_anchor="user-service migration conflict resolved with vscode and index hotfix cherry-picked",
        ),
    ]
    capstone_hard = [
        capstone_case(
            "capstone-hard-pricing-hotfix",
            context="Regional and loyalty discount logic collided on separate branches. The src/pricing.rb conflict requires a combined resolution via mergetool. A tax calculation hotfix also needs to be selectively applied after the merge.",
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
            context="Two database migrations modified the orders status column in incompatible ways. The schema/orders.sql conflict needs careful combined resolution. A shipment schema hotfix from main must also be cherry-picked once the merge is complete.",
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
        capstone_case(
            "capstone-hard-gateway-vimdiff",
            context="api-gateway has a critical timeout conflict and a production auth fix. Fetch, configure vimdiff carefully, resolve the gateway.yml conflict preserving resilience settings, then cherry-pick the auth hotfix.",
            project="api-gateway",
            conflict_path="config/gateway.yml",
            hotfix_path="config/auth.yml",
            base_content="timeout: 30",
            main_content="timeout: 60",
            feature_content="timeout: 15",
            resolution_content="timeout: 60\nretry_on_timeout: true",
            resolution_token="retry_on_timeout: true",
            hotfix_token="auth-hotfix-v1",
            source_branch="origin/feature/gateway-resilience",
            merge_tool="vimdiff",
            answer_anchor="api-gateway hard conflict resolved with vimdiff and auth hotfix cherry-picked",
        ),
        capstone_case(
            "capstone-hard-migration-vimdiff",
            context="user-service has a critical email column constraint conflict and an index hotfix. Fetch, configure vimdiff, resolve the migration carefully to preserve both constraints, then cherry-pick the index fix.",
            project="user-service",
            conflict_path="db/migrations/001_users.sql",
            hotfix_path="db/migrations/002_indexes.sql",
            base_content="email text",
            main_content="email text unique",
            feature_content="email varchar(320)",
            resolution_content="email varchar(320) unique",
            resolution_token="varchar(320) unique",
            hotfix_token="index-hotfix-v1",
            source_branch="origin/feature/email-constraint",
            merge_tool="vimdiff",
            answer_anchor="user-service migration hard conflict resolved with vimdiff and index hotfix cherry-picked",
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
            slug="resolve-conflicts-manually",
            title="Resolving Merge Conflicts Manually",
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
            lesson=MODULE_THREE_LESSONS[1],
            slug="use-merge-tool-workflow",
            title="Resolving Conflicts Using a Merge Tool",
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
                                {**easy_conflicts[2], "merge_tool": "vscode"},
                                {**easy_conflicts[3], "merge_tool": "vimdiff"},
                                {**easy_conflicts[4], "merge_tool": "vscode"},
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
                                {**medium_conflicts[2], "merge_tool": "vscode"},
                                {**easy_conflicts[0], "merge_tool": "vimdiff"},
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
                                {**hard_conflicts[2], "merge_tool": "vscode"},
                                {**medium_conflicts[0], "merge_tool": "vimdiff"},
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
            lesson=MODULE_THREE_LESSONS[2],
            slug="cherry-pick-selected-commit",
            title="Cherry-Picking Commits",
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
                            cases=[cherry_medium[2], cherry_medium[3]],
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
                            cases=[cherry_hard[0], cherry_hard[2], cherry_hard[3]],
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
