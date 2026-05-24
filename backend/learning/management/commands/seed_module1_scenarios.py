from __future__ import annotations

import json
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from common.constants import (
    COMPLETION_EXPANDED_STATE_BASED,
    COMPLETION_INSPECTION,
    COMPLETION_STATE_BASED,
    DIFFICULTY_EASY,
    DIFFICULTY_HARD,
    DIFFICULTY_MEDIUM,
)
from learning.models import LearningUnit, Lesson, OrientationProgress
from scenarios.builders import RuntimeScenarioBuilder, ScenarioVariantBuildError, TemplateRenderer
from scenarios.models import (
    CommandCountPolicy,
    CompletionRecord,
    DifficultyInstance,
    ScenarioGenerationBlueprint,
    ScenarioSession,
    ScenarioSkillFocus,
    ScenarioVariant,
    TargetStateRule,
)

DIAG_PATTERNS = [
    "git status",
    "git log",
    "git log --oneline",
    "git log --oneline --graph --all",
    "git diff",
    "git diff --staged",
    "git diff --cached",
    "git diff HEAD",
    "git show",
    "git remote -v",
    "git branch",
    "git branch -v",
    "git reflog",
]

SESSION_COUNTS = {
    DIFFICULTY_EASY: 3,
    DIFFICULTY_MEDIUM: 2,
    DIFFICULTY_HARD: 2,
}


MODULE_ONE_LESSONS = [
    (
        1,
        "inspecting-repository-state",
        "Inspecting Repository State",
        "Read repository status, history, diffs, branches, remotes, and objects before acting.",
        "scenario",
    ),
    (
        2,
        "initializing-a-local-repository",
        "Initializing a Local Repository",
        "Create Git metadata in an existing or named project folder.",
        "scenario",
    ),
    (
        3,
        "cloning-a-remote-repository",
        "Cloning a Remote Repository",
        "Create a local working copy and verify the origin relationship.",
        "scenario",
    ),
    (
        4,
        "staging-and-committing-basic-workflow",
        "Staging and Committing: The Basic Workflow",
        "Prepare intentional changes and save them with a clear message.",
        "scenario",
    ),
    (
        5,
        "ignoring-files-with-gitignore",
        "Ignoring Files with .gitignore",
        "Keep generated files, dependency folders, logs, and secrets out of history.",
        "scenario",
    ),
    (
        6,
        "partial-staging-and-git-add-p",
        "Partial Staging and git add -p",
        "Stage selected hunks so each commit has one clear purpose.",
        "scenario",
    ),
    (
        7,
        "amending-commits",
        "Amending Commits",
        "Repair the latest commit message or contents before sharing it.",
        "scenario",
    ),
    (
        8,
        "unstaging-and-discarding-changes",
        "Unstaging and Discarding Changes",
        "Move changes out of the index and safely discard unwanted work.",
        "scenario",
    ),
    (
        9,
        "module-1-review-and-practice",
        "Module 1 Review and Practice",
        "Combine the local workflow skills in larger repository situations.",
        "scenario",
    ),
]


def commit(
    commit_id: str, message: str, tree: dict[str, Any], parents: list[str] | None = None
) -> dict[str, Any]:
    """Author a commit with a full tree. The normalizer will infer changes."""
    return {
        "id": commit_id,
        "message": message,
        "parents": parents or [],
        "tree": tree,
    }


def repo_with_head(
    *,
    commits: list[dict[str, Any]] | None = None,
    head: str | None = "c1",
    branch: str = "main",
    working_tree: dict[str, Any] | str | None = None,
    staging: dict[str, Any] | str | None = None,
    partial_hunks: dict[str, Any] | str | None = None,
    remotes: dict[str, str] | None = None,
    remote_branches: dict[str, str] | None = None,
    upstream_tracking: dict[str, str] | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    state = {
        "repository_initialized": True,
        "commits": commits
        or [commit("c1", "Initial project snapshot", {"README.md": "readme-v1"})],
        "branches": {branch: head},
        "head": {"type": "branch", "name": branch},
        "staging": staging or {},
        "working_tree": working_tree or {},
        "conflicts": [],
        "remotes": remotes or {},
        "remote_branches": remote_branches or {},
        "upstream_tracking": upstream_tracking or {},
        "stash_stack": [],
        "reflog": [],
        "partial_hunks": partial_hunks or {},
        "operation_metadata": {},
    }
    if extra:
        state.update(extra)
    return state


def uninitialized_state(**extra: Any) -> dict[str, Any]:
    state = {
        "repository_initialized": False,
        "commits": [],
        "branches": {},
        "head": {"type": "branch", "name": "main"},
        "staging": {},
        "working_tree": {},
        "conflicts": [],
        "remotes": {},
        "remote_branches": {},
        "upstream_tracking": {},
        "stash_stack": [],
        "reflog": [],
        "partial_hunks": {},
        "operation_metadata": {},
    }
    state.update(extra)
    return state


def student_context_template(kind: str) -> dict[str, Any]:
    common = {
        # Keep the active-attempt context focused on the brief and required values.
        # The UI intentionally hides task/checklist/helpful-inspection scaffolds
        # because those sections can leak evaluator rules or imply exact commands.
    }
    templates = {
        "init": {
            "story": "You are preparing {{project}} for version control.",
            "provided_values": [
                {"label": "Project", "value": "{{project}}"},
                {"label": "Target directory", "value": "{{target_directory}}"},
                {"label": "Expected untracked paths", "value": "{{expected_untracked_paths}}"},
            ],
            "requirements": [],
            "success_checklist": [],
            **common,
        },
        "diagnostic": {
            "story": "Before changing {{project}}, inspect the repository and report what you observe.",
            "provided_values": [
                {"label": "Question", "value": "{{question}}"},
                {"label": "Observation fields", "value": "{{must_identify}}"},
            ],
            "warnings": [
                "Use read-only commands only; the repository state should not change.",
            ],
            "requirements": [],
            "success_checklist": [],
            **common,
        },
        "clone": {
            "story": "You need a local working copy of {{project}} from its remote repository.",
            "provided_values": [
                {"label": "Remote URL", "value": "{{remote_url}}"},
                {"label": "Destination folder", "value": "{{destination_folder}}"},
                {"label": "Remote tip", "value": "{{remote_head}}"},
            ],
            "requirements": [],
            "success_checklist": [],
            **common,
        },
        "commit": {
            "story": "You are preparing a focused project snapshot for {{project}}.",
            "provided_values": [
                {"label": "Target files", "value": "{{target_files}}"},
                {"label": "Files to leave out", "value": "{{excluded_files}}"},
                {"label": "Required commit message text", "value": "{{required_commit_message}}"},
            ],
            "requirements": [],
            "success_checklist": [],
            **common,
        },
        "gitignore": {
            "story": "{{project}} has local/generated files that should not be saved in project history.",
            "provided_values": [
                {"label": "Ignore file", "value": ".gitignore"},
                {"label": "Ignore marker", "value": "{{gitignore_token}}"},
                {"label": "Ignored/generated paths", "value": "{{ignored_paths}}"},
                {
                    "label": "Tracked generated path to remove from history",
                    "value": "{{tracked_generated_path}}",
                },
                {"label": "Required commit message text", "value": "{{required_commit_message}}"},
            ],
            "requirements": [],
            "success_checklist": [],
            **common,
        },
        "partial": {
            "story": "{{project}} has multiple changes, but only one logical hunk belongs in the next snapshot.",
            "provided_values": [
                {"label": "Target files", "value": "{{target_files}}"},
                {"label": "Hunks to commit", "value": "{{target_hunks}}"},
                {"label": "Hunks to leave in working tree", "value": "{{leftover_hunks}}"},
                {"label": "Other files to leave out", "value": "{{unrelated_files}}"},
                {"label": "Required commit message text", "value": "{{required_commit_message}}"},
            ],
            "requirements": [],
            "success_checklist": [],
            **common,
        },
        "amend": {
            "story": "The latest local snapshot in {{project}} needs to be repaired before it is considered final.",
            "provided_values": [
                {"label": "Commit to repair", "value": "{{commit_to_repair}}"},
                {"label": "Corrected message", "value": "{{required_commit_message}}"},
                {"label": "Files in repaired commit", "value": "{{target_files}}"},
            ],
            "requirements": [],
            "success_checklist": [],
            **common,
        },
        "restore": {
            "story": "{{project}} has mixed changes. Some should be kept for later, and some should be discarded.",
            "provided_values": [
                {"label": "Keep but unstage", "value": "{{keep_paths}}"},
                {"label": "Discard from working tree", "value": "{{discard_paths}}"},
            ],
            "requirements": [],
            "success_checklist": [],
            **common,
        },
        "review": {
            "story": "{{project}} combines several Module 1 local workflow skills in one task.",
            "provided_values": [
                {"label": "Target files", "value": "{{target_files}}"},
                {"label": "Files/hunks to leave out", "value": "{{excluded_files}}"},
                {"label": "Required commit message text", "value": "{{required_commit_message}}"},
                {"label": "Hunks to commit", "value": "{{target_hunks}}"},
                {"label": "Hunks to leave", "value": "{{leftover_hunks}}"},
                {"label": "Commit to repair", "value": "{{commit_to_repair}}"},
            ],
            "requirements": [],
            "success_checklist": [],
            **common,
        },
    }
    return templates[kind]


def base_scenarios() -> list[dict[str, Any]]:
    base_tree = {"README.md": "readme-v1", "src/app.py": "app-v1", "styles/site.css": "style-v1"}
    return [
        diagnostic_scenario(),
        init_scenario(),
        clone_scenario(),
        commit_scenario(base_tree),
        gitignore_scenario(),
        partial_staging_scenario(),
        amend_scenario(),
        restore_scenario(),
        review_scenario(),
    ]


def diagnostic_scenario() -> dict[str, Any]:
    base = repo_with_head(
        commits=[
            commit(
                "c1", "Create starter files", {"README.md": "readme-v1", "src/app.py": "app-v1"}
            ),
            commit(
                "c2",
                "Add dashboard shell",
                {
                    "README.md": "readme-v1",
                    "src/app.py": "app-v1",
                    "src/dashboard.py": "dashboard-v1",
                },
                ["c1"],
            ),
        ],
        head="c2",
        working_tree={"src/app.py": "app-v2", "notes/todo.md": "untracked"},
        staging={"src/dashboard.py": "dashboard-v2"},
        remotes={"origin": "https://example.test/training/dashboard.git"},
        remote_branches={"origin/main": "c2"},
        upstream_tracking={"main": "origin/main"},
    )
    easy_cases = [
        diagnostic_case(
            "diagnostic-easy-status",
            "dashboard-lab",
            "Identify the current branch, staged paths, unstaged paths, and untracked files.",
            ["git status"],
            ["head_branch", "staged_paths", "unstaged_paths", "untracked_paths"],
            {
                "head_branch": "main",
                "staged_paths": ["src/dashboard.py"],
                "unstaged_paths": ["src/app.py"],
                "untracked_paths": ["notes/todo.md"],
            },
            "status identifies main, staged dashboard, unstaged app, and untracked notes",
            base,
        ),
        diagnostic_case(
            "diagnostic-easy-diff",
            "dashboard-lab",
            "Use diff views to separate unstaged and staged changes.",
            ["git diff", "git diff --staged"],
            ["unstaged_diff_paths", "staged_diff_paths"],
            {
                "unstaged_diff_paths": ["src/app.py"],
                "staged_diff_paths": ["src/dashboard.py"],
            },
            "diff separates app working change from staged dashboard change",
            base,
        ),
    ]
    medium_state = repo_with_head(
        commits=[
            commit("c1", "Create starter files", {"README.md": "readme-v1"}),
            commit(
                "c2",
                "Add profile page",
                {"README.md": "readme-v1", "src/profile.py": "profile-v1"},
                ["c1"],
            ),
            commit(
                "c3",
                "Add profile tests",
                {
                    "README.md": "readme-v1",
                    "src/profile.py": "profile-v1",
                    "tests/test_profile.py": "profile-test-v1",
                },
                ["c2"],
            ),
        ],
        head="c3",
        working_tree={"src/profile.py": "profile-v2"},
        staging={},
        remotes={"origin": "https://example.test/training/profile.git"},
        remote_branches={"origin/main": "c3"},
        upstream_tracking={"main": "origin/main"},
    )
    medium_cases = [
        diagnostic_case(
            "diagnostic-medium-history",
            "profile-lab",
            "Read the compact history and identify the latest commit and message.",
            ["git log --oneline", "git show"],
            ["latest_commit", "commit_message", "changed_paths"],
            {
                "latest_commit": "c3",
                "commit_message": "Add profile tests",
                "changed_paths": ["tests/test_profile.py"],
            },
            "history points to c3 with profile test change",
            medium_state,
        ),
        diagnostic_case(
            "diagnostic-medium-branches",
            "profile-lab",
            "Inspect local branches before choosing any action.",
            ["git branch", "git branch -v"],
            ["head_branch", "available_branches", "branch_tips"],
            {
                "head_branch": "main",
                "available_branches": ["main"],
                "branch_tips": {"main": "c3"},
            },
            "branch output identifies main at c3",
            medium_state,
        ),
    ]
    hard_state = repo_with_head(
        commits=[
            commit("c1", "Create starter files", {"README.md": "readme-v1"}),
            commit(
                "c2", "Add API client", {"README.md": "readme-v1", "src/api.py": "api-v1"}, ["c1"]
            ),
            commit(
                "c3",
                "Add export command",
                {"README.md": "readme-v1", "src/api.py": "api-v1", "src/export.py": "export-v1"},
                ["c2"],
            ),
        ],
        head="c3",
        working_tree={"src/export.py": "export-v2", "debug.log": "untracked"},
        staging={"src/api.py": "api-v2"},
        remotes={"origin": "https://example.test/training/export.git"},
        remote_branches={"origin/main": "c3", "origin/release": "c2"},
        upstream_tracking={"main": "origin/main"},
        extra={"branches": {"main": "c3", "release-check": "c2"}},
    )
    hard_cases = [
        diagnostic_case(
            "diagnostic-hard-combined-read",
            "export-lab",
            "Combine status, staged diff, history, branch, remote, and show output before acting.",
            [
                "git status",
                "git diff --staged",
                "git log --oneline --graph --all",
                "git show",
                "git branch -v",
                "git remote -v",
            ],
            [
                "head_branch",
                "staged_paths",
                "unstaged_paths",
                "commit_history",
                "available_branches",
                "latest_commit",
            ],
            {
                "head_branch": "main",
                "staged_paths": ["src/api.py"],
                "unstaged_paths": ["src/export.py"],
                "commit_history": ["c1", "c2", "c3"],
                "available_branches": ["main", "release-check"],
                "latest_commit": "c3",
            },
            "combined diagnostics identify branch, index, worktree, history, and remote context",
            hard_state,
        ),
        diagnostic_case(
            "diagnostic-hard-reflog-recovery",
            "export-lab",
            "Use reflog plus status/history views to confirm where HEAD is before making changes.",
            ["git reflog", "git status", "git log --oneline"],
            ["head_branch", "latest_commit", "unstaged_paths", "staged_paths"],
            {
                "head_branch": "main",
                "latest_commit": "c3",
                "unstaged_paths": ["src/export.py"],
                "staged_paths": ["src/api.py"],
            },
            "reflog/status/history confirm main at c3 with split changes",
            {
                **hard_state,
                "reflog": [
                    {"ref": "HEAD@{0}", "target": "c3", "message": "commit: Add export command"}
                ],
            },
        ),
    ]
    return scenario_dict(
        lesson=(
            1,
            "inspecting-repository-state",
            "Inspecting Repository State",
            "Read repository status, history, diffs, branches, remotes, and objects before acting.",
        ),
        slug="inspect-repository-state",
        title="Inspect repository state before acting",
        focus="diagnostic commands",
        summary="Practice read-only Git commands before making repository changes.",
        explanation="Diagnostic commands help you understand the branch, history, index, working tree, remotes, and commit details before choosing an action.",
        primary=[
            "git status",
            "git log --oneline",
            "git diff",
            "git diff --staged",
            "git show",
            "git branch",
            "git remote -v",
        ],
        supporting=["git log --oneline --graph --all", "git branch -v", "git reflog"],
        concepts=["status", "history", "diffs", "branches", "remotes", "read-only inspection"],
        kind=ScenarioSkillFocus.SkillFocusType.CONCEPT_SPECIFIC,
        difficulties={
            DIFFICULTY_EASY: diff(
                (0, 0),
                "Read the repository before acting.",
                "Use the requested diagnostic command and submit the observations.",
                [
                    diagnostic_bp(
                        "diagnostic-status-and-diff",
                        easy_cases,
                        "module1.diagnostic.status-diff",
                        "status-diff",
                    )
                ],
                completion_type=COMPLETION_INSPECTION,
            ),
            DIFFICULTY_MEDIUM: diff(
                (0, 0),
                "Read history and branch context.",
                "Use diagnostic history or branch commands and submit the observations.",
                [
                    diagnostic_bp(
                        "diagnostic-history-branches",
                        medium_cases,
                        "module1.diagnostic.history-branches",
                        "history-branches",
                    )
                ],
                completion_type=COMPLETION_INSPECTION,
            ),
            DIFFICULTY_HARD: diff(
                (0, 0),
                "Combine multiple diagnostic views.",
                "Use only read-only commands to inspect the repository and submit the observations.",
                [
                    diagnostic_bp(
                        "diagnostic-combined",
                        hard_cases,
                        "module1.diagnostic.combined",
                        "combined-diagnostics",
                    )
                ],
                completion_type=COMPLETION_INSPECTION,
            ),
        },
    )


def diagnostic_case(
    case_id: str,
    project: str,
    question: str,
    required_commands: list[str],
    must_identify: list[str],
    expected_answer: dict[str, Any],
    answer_anchor: str,
    state: dict[str, Any],
) -> dict[str, Any]:
    return {
        "case_id": case_id,
        "project": project,
        "question": question,
        "required_commands": required_commands,
        "must_identify": must_identify,
        "expected_answer": expected_answer,
        "answer_anchor": answer_anchor,
        "initial_state": state,
    }


def diagnostic_bp(
    slug: str, cases: list[dict[str, Any]], signature: str, subtemplate: str
) -> dict[str, Any]:
    return bp(
        slug=slug,
        kind="diagnostic",
        signature=signature,
        subtemplate=subtemplate,
        cases=cases,
        initial_state="{{initial_state}}",
        target_rule={
            "completion_type": COMPLETION_INSPECTION,
            "required_commands": "{{required_commands}}",
            "repository_state_unchanged": True,
            "must_identify": "{{must_identify}}",
            "rules": [
                {"type": "inspection_answer_matches", "expected": "{{expected_answer}}"},
            ],
        },
        solution="{{required_commands}}",
        label="Inspect {{project}}",
        slug_template="diagnostic-{{case_id}}",
    )


def init_scenario() -> dict[str, Any]:
    """Module 1.1: intentionally avoids fake variety.

    Easy is a single current-directory warm-up because the honest answer is always
    `git init`. Medium and hard use the simulator-supported `git init <dir>` form so
    each generated variant has a different target directory and final-state check.
    """
    return {
        "lesson": (
            2,
            "initializing-a-local-repository",
            "Initializing a Local Repository",
            "Create Git metadata in an existing or named project folder.",
        ),
        "slug": "initialize-local-repository",
        "title": "Initialize a local repository",
        "focus": "git init",
        "summary": "Create repository metadata without staging or committing files.",
        "explanation": "Initialization creates Git metadata for a folder. It does not save a snapshot, stage files, or change file contents.",
        "primary": ["git init"],
        "supporting": ["git status"],
        "concepts": [
            "repository metadata",
            ".git directory",
            "HEAD",
            "working tree",
            "untracked files",
        ],
        "kind": ScenarioSkillFocus.SkillFocusType.COMMAND_SPECIFIC,
        "difficulties": {
            DIFFICULTY_EASY: diff(
                (1, 1),
                "Initialize the current empty folder.",
                "Make the current folder a Git repository, but do not create a commit.",
                [
                    bp(
                        slug="init-current-empty",
                        kind="init",
                        signature="module1.init.current-empty",
                        subtemplate="current-directory-empty",
                        cases=[
                            {
                                "case_id": "init-easy-current-empty",
                                "project": "empty-lab",
                                "target_directory": "current folder",
                                "expected_untracked_paths": [],
                                "answer_anchor": "initialized the current folder only; zero commits",
                            },
                        ],
                        initial_state=uninitialized_state(),
                        target_rule={
                            "repository_initialized": True,
                            "head_branch": "main",
                            "staging_empty": True,
                            "rules": [
                                {"type": "commit_count_equals", "count": 0},
                                {"type": "working_tree_matches_exact_paths", "paths": []},
                                {"type": "operation_metadata_absent", "key": "last_init_directory"},
                                {
                                    "type": "operation_metadata_equals",
                                    "key": "last_init_current_directory",
                                    "value": True,
                                },
                            ],
                        },
                        solution=["git init -b main"],
                        label="Initialize the current folder",
                        slug_template="init-{{case_id}}",
                    )
                ],
                required_attempts=1,
            ),
            DIFFICULTY_MEDIUM: diff(
                (1, 1),
                "Initialize a named project folder from the current workspace.",
                "Initialize the exact target directory named in the brief; do not initialize the parent/current folder.",
                [
                    bp(
                        slug="init-named-directory",
                        kind="init",
                        signature="module1.init.named-directory",
                        subtemplate="named-directory",
                        cases=[
                            {
                                "case_id": "init-medium-docs-site",
                                "project": "workspace",
                                "target_directory": "docs-site",
                                "expected_untracked_paths": [],
                                "answer_anchor": "initialized docs-site only; zero commits",
                            },
                            {
                                "case_id": "init-medium-api-playground",
                                "project": "workspace",
                                "target_directory": "api-playground",
                                "expected_untracked_paths": [],
                                "answer_anchor": "initialized api-playground only; zero commits",
                            },
                            {
                                "case_id": "init-medium-design-kit",
                                "project": "workspace",
                                "target_directory": "design-kit",
                                "expected_untracked_paths": [],
                                "answer_anchor": "initialized design-kit only; zero commits",
                            },
                        ],
                        initial_state=uninitialized_state(),
                        target_rule={
                            "repository_initialized": True,
                            "head_branch": "main",
                            "staging_empty": True,
                            "rules": [
                                {"type": "commit_count_equals", "count": 0},
                                {
                                    "type": "operation_metadata_equals",
                                    "key": "last_init_directory",
                                    "value": "{{target_directory}}",
                                },
                                {
                                    "type": "operation_metadata_equals",
                                    "key": "last_init_current_directory",
                                    "value": False,
                                },
                            ],
                        },
                        solution=["git init --initial-branch=main {{target_directory}}"],
                        label="Initialize {{target_directory}}",
                        slug_template="init-{{case_id}}",
                    )
                ],
            ),
            DIFFICULTY_HARD: diff(
                (1, 1),
                "Choose the correct child folder from a parent workspace with sibling traps.",
                "Initialize only the requested child directory; the parent/current workspace must not be the initialized target.",
                [
                    bp(
                        slug="init-correct-child-directory",
                        kind="init",
                        signature="module1.init.child-directory-trap",
                        subtemplate="named-directory-from-parent",
                        cases=[
                            {
                                "case_id": "init-hard-research-log",
                                "project": "parent-workspace",
                                "target_directory": "research-log",
                                "expected_untracked_paths": ["research-log/README.md"],
                                "sibling_directories": ["notes", "archive"],
                                "answer_anchor": "initialized research-log only; parent and siblings not targeted",
                                "initial_working_tree": {
                                    "research-log/README.md": "untracked",
                                    "notes/ideas.md": "untracked",
                                    "archive/old.md": "untracked",
                                },
                            },
                            {
                                "case_id": "init-hard-ui-kit",
                                "project": "design-parent",
                                "target_directory": "ui-kit",
                                "expected_untracked_paths": ["ui-kit/tokens.css"],
                                "sibling_directories": ["brand-assets", "experiments"],
                                "answer_anchor": "initialized ui-kit only; sibling folders untouched",
                                "initial_working_tree": {
                                    "ui-kit/tokens.css": "untracked",
                                    "brand-assets/logo.svg": "untracked",
                                    "experiments/mockup.html": "untracked",
                                },
                            },
                            {
                                "case_id": "init-hard-deploy-checklist",
                                "project": "ops-parent",
                                "target_directory": "deploy-checklist",
                                "expected_untracked_paths": ["deploy-checklist/steps.md"],
                                "sibling_directories": ["docs", "scripts"],
                                "answer_anchor": "initialized deploy-checklist only; parent/current workspace not initialized",
                                "initial_working_tree": {
                                    "deploy-checklist/steps.md": "untracked",
                                    "docs/runbook.md": "untracked",
                                    "scripts/deploy.sh": "untracked",
                                },
                            },
                        ],
                        initial_state=uninitialized_state(working_tree="{{initial_working_tree}}"),
                        target_rule={
                            "repository_initialized": True,
                            "head_branch": "main",
                            "staging_empty": True,
                            "rules": [
                                {"type": "commit_count_equals", "count": 0},
                                {
                                    "type": "operation_metadata_equals",
                                    "key": "last_init_directory",
                                    "value": "{{target_directory}}",
                                },
                                {
                                    "type": "operation_metadata_equals",
                                    "key": "last_init_current_directory",
                                    "value": False,
                                },
                                {
                                    "type": "operation_metadata_not_equals",
                                    "key": "last_init_directory",
                                    "value": ".",
                                },
                            ],
                        },
                        solution=["git init --initial-branch=main {{target_directory}}"],
                        label="Initialize {{target_directory}} only",
                        slug_template="init-{{case_id}}",
                    )
                ],
            ),
        },
    }


def bp(
    *,
    slug: str,
    kind: str,
    signature: str,
    subtemplate: str,
    cases: list[dict[str, Any]],
    initial_state: dict[str, Any],
    target_rule: dict[str, Any],
    solution: list[str],
    label: str,
    slug_template: str,
    expected_observations: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if expected_observations is None and all("answer_anchor" in case for case in cases):
        expected_observations = {"answer_anchor": "{{answer_anchor}}"}
    return {
        "slug": slug,
        "slug_template": slug_template,
        "label_template": label,
        "blueprint_signature": signature,
        "subtemplate_signature": subtemplate,
        "parameter_pools": {"cases": cases},
        "generation_count": len(cases),
        "max_combinations": len(cases),
        "initial_state_template": initial_state,
        "target_rule_template": target_rule,
        "solution_commands_template": solution,
        "expected_observations_template": expected_observations or {},
        "student_context_template": student_context_template(kind),
    }


def clone_scenario() -> dict[str, Any]:
    easy_cases = [
        remote_case(
            "clone-easy-docs-portal",
            "docs-portal",
            "https://example.test/training/docs-portal.git",
            "docs-portal",
            "r10",
            {"README.md": "docs-readme-v1", "docs/intro.md": "docs-intro-v1"},
            [
                {
                    "id": "r10",
                    "message": "Create docs portal starter",
                    "parents": [],
                    "tree": {"README.md": "docs-readme-v1", "docs/intro.md": "docs-intro-v1"},
                }
            ],
            "origin URL docs-portal; main/origin-main -> r10; docs tree checked out",
        ),
        remote_case(
            "clone-easy-api-lab",
            "api-lab",
            "https://example.test/training/api-lab.git",
            "api-lab",
            "r11",
            {"README.md": "api-readme-v1", "api/routes.py": "api-routes-v1"},
            [
                {
                    "id": "r11",
                    "message": "Create API lab starter",
                    "parents": [],
                    "tree": {"README.md": "api-readme-v1", "api/routes.py": "api-routes-v1"},
                }
            ],
            "origin URL api-lab; main/origin-main -> r11; API tree checked out",
        ),
        remote_case(
            "clone-easy-profile-site",
            "profile-site",
            "https://example.test/training/profile-site.git",
            "profile-site",
            "r12",
            {"index.html": "profile-index-v1", "styles/site.css": "profile-css-v1"},
            [
                {
                    "id": "r12",
                    "message": "Create profile site starter",
                    "parents": [],
                    "tree": {"index.html": "profile-index-v1", "styles/site.css": "profile-css-v1"},
                }
            ],
            "origin URL profile-site; main/origin-main -> r12; site tree checked out",
        ),
    ]
    medium_cases = [
        remote_case(
            "clone-medium-cli-tool",
            "cli-tool",
            "https://example.test/tools/cli-tool.git",
            "cli-practice",
            "r20",
            {"README.md": "cli-readme-v2", "src/parser.py": "cli-parser-v2"},
            [
                {
                    "id": "r19",
                    "message": "Create CLI skeleton",
                    "parents": [],
                    "tree": {"README.md": "cli-readme-v1"},
                },
                {
                    "id": "r20",
                    "message": "Add parser command",
                    "parents": ["r19"],
                    "tree": {"README.md": "cli-readme-v2", "src/parser.py": "cli-parser-v2"},
                },
            ],
            "custom folder cli-practice; r20 tree/history",
        ),
        remote_case(
            "clone-medium-css-kit",
            "css-kit",
            "https://example.test/frontend/css-kit.git",
            "style-lab",
            "r21",
            {"README.md": "css-readme-v1", "styles/tokens.css": "tokens-v1"},
            [
                {
                    "id": "r21",
                    "message": "Create style token kit",
                    "parents": [],
                    "tree": {"README.md": "css-readme-v1", "styles/tokens.css": "tokens-v1"},
                }
            ],
            "custom folder style-lab; CSS token tree",
        ),
        remote_case(
            "clone-medium-recipe-book",
            "recipe-book",
            "https://example.test/docs/recipe-book.git",
            "kitchen-docs",
            "r22",
            {"README.md": "recipe-readme-v1", "recipes/adobo.md": "adobo-v1"},
            [
                {
                    "id": "r22",
                    "message": "Create recipe book starter",
                    "parents": [],
                    "tree": {"README.md": "recipe-readme-v1", "recipes/adobo.md": "adobo-v1"},
                }
            ],
            "custom folder kitchen-docs; recipe tree",
        ),
    ]
    hard_cases = [
        remote_case(
            "clone-hard-analytics",
            "analytics-lab",
            "git@example.test:training/analytics-lab.git",
            "analytics-worktree",
            "r30",
            {
                "README.md": "analytics-readme-v3",
                "metrics/report.md": "metrics-report-v2",
                "src/summary.py": "summary-v1",
            },
            [
                {
                    "id": "r28",
                    "message": "Create analytics starter",
                    "parents": [],
                    "tree": {"README.md": "analytics-readme-v1"},
                },
                {
                    "id": "r29",
                    "message": "Add metrics report",
                    "parents": ["r28"],
                    "tree": {
                        "README.md": "analytics-readme-v2",
                        "metrics/report.md": "metrics-report-v1",
                    },
                },
                {
                    "id": "r30",
                    "message": "Add summary script",
                    "parents": ["r29"],
                    "tree": {
                        "README.md": "analytics-readme-v3",
                        "metrics/report.md": "metrics-report-v2",
                        "src/summary.py": "summary-v1",
                    },
                },
            ],
            "SSH URL; custom folder analytics-worktree; three-commit history ending r30",
        ),
        remote_case(
            "clone-hard-mobile-ui",
            "mobile-ui",
            "git@example.test:frontend/mobile-ui.git",
            "mobile-ui-lab",
            "r31",
            {
                "README.md": "mobile-readme-v2",
                "screens/home.tsx": "home-v1",
                "styles/mobile.css": "mobile-css-v1",
            },
            [
                {
                    "id": "r23",
                    "message": "Create mobile UI shell",
                    "parents": [],
                    "tree": {"README.md": "mobile-readme-v1"},
                },
                {
                    "id": "r31",
                    "message": "Add mobile home screen",
                    "parents": ["r23"],
                    "tree": {
                        "README.md": "mobile-readme-v2",
                        "screens/home.tsx": "home-v1",
                        "styles/mobile.css": "mobile-css-v1",
                    },
                },
            ],
            "SSH URL; custom folder mobile-ui-lab; UI tree ending r31",
        ),
        remote_case(
            "clone-hard-lab-notebook",
            "lab-notebook",
            "git@example.test:docs/lab-notebook.git",
            "notebook-review",
            "r32",
            {
                "README.md": "notebook-readme-v2",
                "entries/day-1.md": "day1-v1",
                "entries/day-2.md": "day2-v1",
            },
            [
                {
                    "id": "r24",
                    "message": "Create lab notebook",
                    "parents": [],
                    "tree": {"README.md": "notebook-readme-v1", "entries/day-1.md": "day1-v1"},
                },
                {
                    "id": "r32",
                    "message": "Add second lab entry",
                    "parents": ["r24"],
                    "tree": {
                        "README.md": "notebook-readme-v2",
                        "entries/day-1.md": "day1-v1",
                        "entries/day-2.md": "day2-v1",
                    },
                },
            ],
            "SSH URL; custom folder notebook-review; notebook tree ending r32",
        ),
    ]
    return scenario_dict(
        lesson=(
            3,
            "cloning-a-remote-repository",
            "Cloning a Remote Repository",
            "Create a local working copy and verify the origin relationship.",
        ),
        slug="clone-remote-repository",
        title="Clone a remote repository",
        focus="git clone",
        summary="Create a local repository from a remote and verify origin/main.",
        explanation="Cloning creates a local repository, configures origin, checks out main, and records remote-tracking information.",
        primary=["git clone"],
        supporting=["git remote -v", "git log --oneline", "git status"],
        concepts=["origin", "remote-tracking branch", "upstream", "working tree checkout"],
        difficulties={
            DIFFICULTY_EASY: diff(
                (1, 1),
                "Clone with the default folder name.",
                "Use the provided remote URL and let the destination use the default repository name.",
                [
                    clone_bp(
                        "clone-default-folder",
                        easy_cases,
                        False,
                        "module1.clone.https-default-folder",
                        "clone-https-default",
                    )
                ],
            ),
            DIFFICULTY_MEDIUM: diff(
                (1, 1),
                "Clone into a required custom folder.",
                "Use the provided remote URL and the exact destination folder.",
                [
                    clone_bp(
                        "clone-custom-folder",
                        medium_cases,
                        True,
                        "module1.clone.https-custom-folder",
                        "clone-https-custom-destination",
                    )
                ],
            ),
            DIFFICULTY_HARD: diff(
                (1, 1),
                "Clone an SSH remote into a required custom folder with deeper history.",
                "Use the exact SSH-style remote and destination folder, then end with clean tracking refs.",
                [
                    clone_bp(
                        "clone-ssh-custom-folder",
                        hard_cases,
                        True,
                        "module1.clone.ssh-custom-folder-history",
                        "clone-ssh-custom-history",
                    )
                ],
            ),
        },
    )


def remote_case(
    case_id: str,
    project: str,
    url: str,
    folder: str,
    head: str,
    tree: dict[str, Any],
    commits: list[dict[str, Any]],
    answer_anchor: str,
) -> dict[str, Any]:
    return {
        "case_id": case_id,
        "project": project,
        "remote_url": url,
        "destination_folder": folder,
        "remote_head": head,
        "remote_tree": tree,
        "remote_commits": commits,
        "answer_anchor": answer_anchor,
    }


def clone_bp(
    slug: str, cases: list[dict[str, Any]], custom_folder: bool, signature: str, subtemplate: str
) -> dict[str, Any]:
    command = (
        "git clone {{remote_url}} {{destination_folder}}"
        if custom_folder
        else "git clone {{remote_url}}"
    )
    return bp(
        slug=slug,
        kind="clone",
        signature=signature,
        subtemplate=subtemplate,
        cases=cases,
        initial_state=uninitialized_state(
            remote_fixtures={
                "branches": {"origin/main": "{{remote_head}}"},
                "commits": "{{remote_commits}}",
            }
        ),
        target_rule={
            "repository_initialized": True,
            "head_branch": "main",
            "remote_exists": ["origin"],
            "remote_url_matches": {"origin": "{{remote_url}}"},
            "remote_branch_exists": ["origin/main"],
            "remote_branch_points_to": {"origin/main": "{{remote_head}}"},
            "branch_points_to": {"main": "{{remote_head}}"},
            "upstream_tracking": {"main": "origin/main"},
            "staging_empty": True,
            "working_tree_clean": True,
            "rules": [
                {
                    "type": "operation_metadata_equals",
                    "key": "last_clone_destination",
                    "value": "{{destination_folder}}",
                },
                {
                    "type": "operation_metadata_equals",
                    "key": "last_clone_url",
                    "value": "{{remote_url}}",
                },
                {"type": "commit_exists", "commit": "{{remote_head}}"},
                {
                    "type": "commit_tree_contains",
                    "commit": "{{remote_head}}",
                    "tree": "{{remote_tree}}",
                },
            ],
        },
        solution=[command],
        label="Clone {{project}}",
        slug_template="clone-{{case_id}}",
    )


def commit_scenario(base_tree: dict[str, str]) -> dict[str, Any]:
    cases_easy = [
        commit_case(
            "commit-easy-form-validation",
            "form-flow",
            {"src/form.js": "form-validation-v2"},
            ["src/form.js"],
            [],
            [],
            {"src/form.js": "form-validation-v2"},
            "Update form validation",
            "commit message and changed path src/form.js",
        ),
        commit_case(
            "commit-easy-readme-setup",
            "setup-notes",
            {"README.md": "readme-setup-v2"},
            ["README.md"],
            [],
            [],
            {"README.md": "readme-setup-v2"},
            "Clarify setup steps",
            "commit message and changed path README.md",
            commit_command='git commit --message "Clarify setup steps"',
        ),
        commit_case(
            "commit-easy-navbar-spacing",
            "style-polish",
            {"styles/navbar.css": "navbar-spacing-v2"},
            ["styles/navbar.css"],
            [],
            [],
            {"styles/navbar.css": "navbar-spacing-v2"},
            "Adjust navbar spacing",
            "commit message and changed path styles/navbar.css",
            stage_command="git add -A",
        ),
    ]
    cases_medium = [
        commit_case(
            "commit-medium-profile-card",
            "profile-card",
            {"src/profile-card.js": "profile-js-v2", "styles/profile-card.css": "profile-css-v2"},
            ["src/profile-card.js", "styles/profile-card.css"],
            [],
            [],
            {"src/profile-card.js": "profile-js-v2", "styles/profile-card.css": "profile-css-v2"},
            "Update profile card layout",
            "commit has two profile-card paths",
            stage_command="git add --all",
        ),
        commit_case(
            "commit-medium-search-results",
            "search-view",
            {"src/search.js": "search-js-v2", "templates/search.html": "search-template-v2"},
            ["src/search.js", "templates/search.html"],
            [],
            [],
            {"src/search.js": "search-js-v2", "templates/search.html": "search-template-v2"},
            "Refine search results view",
            "commit has JS and template paths",
            commit_command='git commit --message "Refine search results view"',
        ),
        commit_case(
            "commit-medium-export-flow",
            "export-flow",
            {"src/export.py": "export-code-v2", "docs/export.md": "export-docs-v2"},
            ["src/export.py", "docs/export.md"],
            [],
            [],
            {"src/export.py": "export-code-v2", "docs/export.md": "export-docs-v2"},
            "Document export flow update",
            "commit has code and docs paths",
        ),
    ]
    cases_hard = [
        commit_case(
            "commit-hard-profile-distractor",
            "profile-card",
            {
                "src/profile-card.js": "profile-js-v3",
                "notes/profile-ideas.md": "profile-notes-draft",
            },
            ["src/profile-card.js"],
            ["notes/profile-ideas.md"],
            ["notes/profile-ideas.md"],
            {"src/profile-card.js": "profile-js-v3"},
            "Update profile card behavior",
            "commit includes profile-card.js; notes remain uncommitted",
        ),
        commit_case(
            "commit-hard-export-distractor",
            "export-flow",
            {
                "src/export.py": "export-code-v3",
                "scratch/export-test-output.txt": "export-output-draft",
            },
            ["src/export.py"],
            ["scratch/export-test-output.txt"],
            ["scratch/export-test-output.txt"],
            {"src/export.py": "export-code-v3"},
            "Fix export validation",
            "commit includes export.py; scratch output remains uncommitted",
        ),
        commit_case(
            "commit-hard-search-two-targets-one-distractor",
            "search-view",
            {
                "src/search.js": "search-js-v3",
                "templates/search.html": "search-template-v3",
                "notes/search-ranking.md": "search-notes-draft",
            },
            ["src/search.js", "templates/search.html"],
            ["notes/search-ranking.md"],
            ["notes/search-ranking.md"],
            {"src/search.js": "search-js-v3", "templates/search.html": "search-template-v3"},
            "Refine search ranking display",
            "commit includes two target paths; notes remain uncommitted",
        ),
    ]
    return scenario_dict(
        lesson=(
            4,
            "staging-and-committing-basic-workflow",
            "Staging and Committing: The Basic Workflow",
            "Prepare intentional changes and save them with a clear message.",
        ),
        slug="stage-and-commit-basic-workflow",
        title="Stage and commit the intended change",
        focus="git commit",
        summary="Stage intended changes and create a focused commit.",
        explanation="A commit saves the staged snapshot and moves the current branch to the new commit.",
        primary=["git add", "git commit"],
        supporting=["git status", "git diff", "git diff --staged"],
        concepts=["working tree", "staging area", "commit", "branch tip"],
        difficulties={
            DIFFICULTY_EASY: diff(
                (2, 3),
                "Commit one clear file change.",
                "Stage and save the single intended file with the required message.",
                [
                    commit_bp(
                        "commit-single-file",
                        cases_easy,
                        base_tree,
                        True,
                        "module1.commit.single-file",
                        "one-target-file",
                    )
                ],
            ),
            DIFFICULTY_MEDIUM: diff(
                (2, 4),
                "Commit multiple related files.",
                "Stage and save all intended files as one focused snapshot.",
                [
                    commit_bp(
                        "commit-multiple-files",
                        cases_medium,
                        base_tree,
                        True,
                        "module1.commit.multi-file",
                        "multi-target-files",
                    )
                ],
            ),
            DIFFICULTY_HARD: diff(
                (2, 5),
                "Commit intended work while leaving unrelated work out.",
                "Stage and save only the target files; leave unrelated work uncommitted.",
                [
                    commit_bp(
                        "commit-selective-files",
                        cases_hard,
                        base_tree,
                        False,
                        "module1.commit.selective-with-distractor",
                        "target-plus-distractor",
                    )
                ],
            ),
        },
    )


def commit_case(
    case_id: str,
    project: str,
    working_tree: dict[str, Any],
    target_files: list[str],
    excluded_files: list[str],
    allowed_working_tree_paths: list[str],
    target_tree_requirements: dict[str, Any],
    message: str,
    answer_anchor: str,
    *,
    stage_command: str | None = None,
    commit_command: str | None = None,
) -> dict[str, Any]:
    return {
        "case_id": case_id,
        "project": project,
        "base_commit": "c1",
        "working_tree": working_tree,
        "target_files": target_files,
        "excluded_files": excluded_files,
        "allowed_working_tree_paths": allowed_working_tree_paths,
        "target_tree_requirements": target_tree_requirements,
        "stage_args": " ".join(target_files),
        "required_commit_message": message,
        "stage_command": stage_command or f"git add {' '.join(target_files)}",
        "commit_command": commit_command or f'git commit -m "{message}"',
        "answer_anchor": answer_anchor,
    }


def commit_bp(
    slug: str,
    cases: list[dict[str, Any]],
    base_tree: dict[str, str],
    clean: bool,
    signature: str,
    subtemplate: str,
) -> dict[str, Any]:
    rules = [
        {"type": "commit_parent_equals", "branch": "main", "parent": "{{base_commit}}"},
        {"type": "commit_tree_contains", "branch": "main", "tree": "{{target_tree_requirements}}"},
    ]
    rules.append({"type": "working_tree_clean_except", "paths": "{{allowed_working_tree_paths}}"})
    target_rule = {
        "head_branch": "main",
        "latest_commit": {
            "branch": "main",
            "message_contains": ["{{required_commit_message}}"],
            "contains_paths": "{{target_files}}",
            "excludes_paths": "{{excluded_files}}",
        },
        "staging_empty": True,
        "rules": rules,
    }
    if clean:
        target_rule["working_tree_clean"] = True
    return bp(
        slug=slug,
        kind="commit",
        signature=signature,
        subtemplate=subtemplate,
        cases=cases,
        initial_state=repo_with_head(
            commits=[commit("c1", "Initial project snapshot", base_tree)],
            working_tree="{{working_tree}}",
        ),
        target_rule=target_rule,
        solution=["{{stage_command}}", "{{commit_command}}"],
        label="Commit {{project}}",
        slug_template="commit-{{case_id}}",
    )


def gitignore_scenario() -> dict[str, Any]:
    base = {"README.md": "readme-v1", "src/app.py": "app-v1"}
    easy_cases = [
        ignore_case(
            "ignore-easy-node-env",
            "node-app",
            "node-ignore-v1",
            ["node_modules/pkg/index.js", ".env"],
            "Add Node ignore rules",
            "commit contains .gitignore token node-ignore-v1; excludes node_modules and .env",
        ),
        ignore_case(
            "ignore-easy-python-cache",
            "python-api",
            "python-ignore-v1",
            ["__pycache__/app.cpython.pyc", ".env"],
            "Add Python ignore rules",
            "commit contains .gitignore token python-ignore-v1; excludes pycache and .env",
        ),
        ignore_case(
            "ignore-easy-web-build",
            "static-site",
            "web-ignore-v1",
            ["dist/site.js", "dist/site.css"],
            "Add web build ignore rules",
            "commit contains .gitignore token web-ignore-v1; excludes dist outputs",
        ),
    ]
    medium_cases = [
        ignore_case(
            "ignore-medium-node-logs-build",
            "node-dashboard",
            "node-ignore-v2",
            ["node_modules/lib.js", "dist/app.js", "logs/debug.log", ".env.local"],
            "Ignore Node dependencies and build output",
            "excludes four ignored artifact paths",
        ),
        ignore_case(
            "ignore-medium-python-venv-cache",
            "data-tools",
            "python-ignore-v2",
            [".venv/pyvenv.cfg", "__pycache__/clean.cpython.pyc", "output/report.csv"],
            "Ignore Python environment artifacts",
            "excludes venv, cache, and output paths",
        ),
        ignore_case(
            "ignore-medium-java-target",
            "java-service",
            "java-ignore-v1",
            ["target/classes/App.class", "target/app.jar", "logs/server.log"],
            "Ignore Java build artifacts",
            "excludes target and log paths",
        ),
    ]
    hard_cases = [
        ignore_case(
            "ignore-hard-untrack-env",
            "backend-service",
            "service-ignore-v3",
            [".env", "logs/server.log"],
            "Stop tracking local environment files",
            ".env removed from committed tree but remains local/ignored; .gitignore committed",
            tracked_generated_path=".env",
            base_tree={**base, ".env": "secret-v1"},
        ),
        ignore_case(
            "ignore-hard-untrack-dist",
            "frontend-bundle",
            "frontend-ignore-v3",
            ["dist/app.js", "dist/app.css"],
            "Stop tracking build outputs",
            "dist/app.js removed from commit tree; build outputs remain local/ignored",
            tracked_generated_path="dist/app.js",
            base_tree={**base, "dist/app.js": "dist-old"},
        ),
        ignore_case(
            "ignore-hard-untrack-pycache",
            "script-runner",
            "pycache-ignore-v3",
            ["__pycache__/runner.cpython.pyc", ".pytest_cache/v/cache"],
            "Stop tracking Python cache files",
            "tracked pycache removed from future tree; .gitignore committed",
            tracked_generated_path="__pycache__/runner.cpython.pyc",
            base_tree={**base, "__pycache__/runner.cpython.pyc": "pycache-old"},
        ),
    ]
    return scenario_dict(
        lesson=(
            5,
            "ignoring-files-with-gitignore",
            "Ignoring Files with .gitignore",
            "Keep generated files, dependency folders, logs, and secrets out of history.",
        ),
        slug="configure-gitignore-rules",
        title="Configure ignore rules",
        focus=".gitignore",
        summary="Commit ignore rules while keeping generated files out of history.",
        explanation=".gitignore controls which untracked local files Git should ignore. Already tracked files require an explicit untrack step.",
        primary=["git add", "git commit"],
        supporting=["git status", "git diff", "git diff --staged"],
        concepts=["ignored files", "untracked files", "tracked files", "index"],
        difficulties={
            DIFFICULTY_EASY: diff(
                (2, 4),
                "Commit simple ignore rules.",
                "Commit .gitignore while ignored generated files remain local.",
                [
                    ignore_bp(
                        "ignore-basic",
                        easy_cases,
                        base,
                        False,
                        "module1.ignore.basic",
                        "ignore-untracked-generated",
                    )
                ],
                completion_type=COMPLETION_EXPANDED_STATE_BASED,
            ),
            DIFFICULTY_MEDIUM: diff(
                (2, 5),
                "Commit ecosystem-specific ignore rules.",
                "Commit .gitignore with several patterns and keep all generated paths out.",
                [
                    ignore_bp(
                        "ignore-ecosystem",
                        medium_cases,
                        base,
                        False,
                        "module1.ignore.ecosystem",
                        "multiple-ignore-patterns",
                    )
                ],
                completion_type=COMPLETION_EXPANDED_STATE_BASED,
            ),
            DIFFICULTY_HARD: diff(
                (3, 6),
                "Stop tracking a generated file and keep it local.",
                "Commit ignore rules and remove one already tracked generated path from tracking.",
                [
                    ignore_bp(
                        "ignore-tracked-generated",
                        hard_cases,
                        "{{base_tree}}",
                        True,
                        "module1.ignore.tracked-generated",
                        "tracked-generated-removal",
                    )
                ],
                completion_type=COMPLETION_EXPANDED_STATE_BASED,
            ),
        },
    )


def ignore_case(
    case_id: str,
    project: str,
    token: str,
    ignored_paths: list[str],
    message: str,
    answer_anchor: str,
    *,
    tracked_generated_path: str = "none",
    base_tree: dict[str, Any] | None = None,
) -> dict[str, Any]:
    working_tree: dict[str, Any] = {".gitignore": token}
    for path in ignored_paths:
        if path == tracked_generated_path:
            continue
        working_tree[path] = {"status": "ignored", "content": f"{path}-local"}
    return {
        "case_id": case_id,
        "project": project,
        "base_tree": base_tree or {},
        "gitignore_token": token,
        "working_tree": working_tree,
        "ignored_paths": ignored_paths,
        "target_files": [".gitignore"],
        "excluded_files": ignored_paths,
        "tracked_generated_path": tracked_generated_path,
        "required_commit_message": message,
        "answer_anchor": answer_anchor,
    }


def ignore_bp(
    slug: str,
    cases: list[dict[str, Any]],
    base_tree: dict[str, str] | str,
    hard: bool,
    signature: str,
    subtemplate: str,
) -> dict[str, Any]:
    latest_excludes: list[str] | str = "{{excluded_files}}"
    if hard:
        latest_excludes = []
    rules = [
        {"type": "ignored_paths_present", "paths": "{{ignored_paths}}"},
        {
            "type": "commit_tree_contains",
            "branch": "main",
            "tree": {".gitignore": "{{gitignore_token}}"},
        },
        {"type": "commit_tree_excludes", "branch": "main", "paths": "{{excluded_files}}"},
    ]
    solution = ["git add .gitignore", 'git commit -m "{{required_commit_message}}"']
    if hard:
        solution = [
            "git rm --cached {{tracked_generated_path}}",
            "git add .gitignore",
            'git commit -m "{{required_commit_message}}"',
        ]
        rules.append(
            {
                "type": "tracked_path_removed_from_commit_tree",
                "paths": ["{{tracked_generated_path}}"],
            }
        )
        rules.append(
            {
                "type": "operation_metadata_contains",
                "key": "last_rm_cached_paths",
                "value": "{{tracked_generated_path}}",
            }
        )
    else:
        rules.append({"type": "ignored_paths_excluded_from_commit", "paths": "{{ignored_paths}}"})
    return bp(
        slug=slug,
        kind="gitignore",
        signature=signature,
        subtemplate=subtemplate,
        cases=cases,
        initial_state=repo_with_head(
            commits=[commit("c1", "Initial project snapshot", base_tree)],
            working_tree="{{working_tree}}",
        ),
        target_rule={
            "head_branch": "main",
            "latest_commit": {
                "branch": "main",
                "message_contains": ["{{required_commit_message}}"],
                "contains_paths": "{{target_files}}",
                "excludes_paths": latest_excludes,
            },
            "staging_empty": True,
            "working_tree_clean": True,
            "rules": rules,
        },
        solution=solution,
        label="Ignore rules for {{project}}",
        slug_template="ignore-{{case_id}}",
    )


def partial_staging_scenario() -> dict[str, Any]:
    cases_easy = [
        partial_case(
            "partial-easy-auth-validation",
            "auth-module",
            ["src/auth.py"],
            ["auth-validation-hunk"],
            ["auth-refactor-hunk"],
            [],
            "Isolate auth validation",
            "commit contains auth-validation-hunk; working tree keeps auth-refactor-hunk",
        ),
        partial_case(
            "partial-easy-search-ranking",
            "search-module",
            ["src/search.py"],
            ["search-ranking-hunk"],
            ["search-cleanup-hunk"],
            [],
            "Isolate search ranking",
            "commit contains search-ranking-hunk; working tree keeps search-cleanup-hunk",
        ),
        partial_case(
            "partial-easy-export-format",
            "export-module",
            ["src/export.py"],
            ["export-format-hunk"],
            ["export-logging-hunk"],
            [],
            "Isolate export formatting",
            "commit contains export-format-hunk; working tree keeps export-logging-hunk",
        ),
    ]
    cases_medium = [
        partial_case(
            "partial-medium-profile-validation",
            "profile-editor",
            ["src/profile.py"],
            ["profile-validation-hunk"],
            ["profile-copy-hunk", "profile-cleanup-hunk"],
            ["notes/profile-todo.md"],
            "Commit profile validation only",
            "validation hunk committed; two hunks and notes remain uncommitted",
        ),
        partial_case(
            "partial-medium-payment-rounding",
            "payment-flow",
            ["src/payment.py"],
            ["payment-rounding-hunk"],
            ["payment-logging-hunk", "payment-comment-hunk"],
            ["tmp/payment-scratch.txt"],
            "Commit payment rounding fix",
            "rounding hunk committed; logging/comment hunks remain",
        ),
        partial_case(
            "partial-medium-dashboard-filter",
            "dashboard",
            ["src/dashboard.js"],
            ["dashboard-filter-hunk"],
            ["dashboard-theme-hunk", "dashboard-console-hunk"],
            ["notes/dashboard-ideas.md"],
            "Commit dashboard filter change",
            "filter hunk committed; theme/console hunks remain",
        ),
    ]
    cases_hard = [
        partial_case(
            "partial-hard-auth-cross-file",
            "auth-module",
            ["src/auth.py", "tests/test_auth.py"],
            ["auth-validation-hunk", "auth-validation-test-hunk"],
            ["auth-refactor-hunk", "auth-test-cleanup-hunk"],
            ["notes/auth-debug.md"],
            "Commit auth validation path",
            "two validation hunks committed across files; refactor/test cleanup and notes remain",
        ),
        partial_case(
            "partial-hard-search-cross-file",
            "search-module",
            ["src/search.py", "tests/test_search.py"],
            ["search-ranking-hunk", "search-ranking-test-hunk"],
            ["search-cleanup-hunk", "search-test-fixture-hunk"],
            ["tmp/search-output.txt"],
            "Commit search ranking path",
            "ranking hunks committed across code/test; cleanup/fixture and tmp remain",
        ),
        partial_case(
            "partial-hard-export-cross-file",
            "export-module",
            ["src/export.py", "tests/test_export.py"],
            ["export-format-hunk", "export-format-test-hunk"],
            ["export-logging-hunk", "export-test-cleanup-hunk"],
            ["notes/export-followup.md"],
            "Commit export formatting path",
            "export formatting hunks committed; logging/test cleanup and notes remain",
        ),
    ]
    return scenario_dict(
        lesson=(
            6,
            "partial-staging-and-git-add-p",
            "Partial Staging and git add -p",
            "Stage selected hunks so each commit has one clear purpose.",
        ),
        slug="partial-staging-add-p",
        title="Stage selected hunks",
        focus="git add -p",
        summary="Commit selected hunks while leaving other changes uncommitted.",
        explanation="Partial staging lets one file contribute only the selected logical change to the next commit.",
        primary=["git add -p", "git commit"],
        supporting=["git status", "git diff", "git diff --staged"],
        concepts=["hunks", "partial staging", "index", "working tree leftovers"],
        difficulties={
            DIFFICULTY_EASY: diff(
                (2, 4),
                "Commit one selected hunk from one file.",
                "Commit only the named hunk and leave the other hunk in the working tree.",
                [
                    partial_bp(
                        "partial-one-file",
                        cases_easy,
                        "module1.partial.one-file",
                        "two-hunks-one-file",
                    )
                ],
                completion_type=COMPLETION_EXPANDED_STATE_BASED,
            ),
            DIFFICULTY_MEDIUM: diff(
                (2, 5),
                "Commit one hunk while another file remains unrelated.",
                "Commit only the target hunk and leave the unrelated file out.",
                [
                    partial_bp(
                        "partial-with-unrelated",
                        cases_medium,
                        "module1.partial.with-unrelated",
                        "hunk-plus-unrelated-file",
                    )
                ],
                completion_type=COMPLETION_EXPANDED_STATE_BASED,
            ),
            DIFFICULTY_HARD: diff(
                (2, 6),
                "Commit selected hunks across files in a noisy workspace.",
                "Use the hunk-level target and leave all unrelated work out of the final snapshot.",
                [
                    partial_bp(
                        "partial-noisy",
                        cases_hard,
                        "module1.partial.noisy",
                        "cross-file-hunk-selection",
                    )
                ],
                completion_type=COMPLETION_EXPANDED_STATE_BASED,
            ),
        },
    )


def partial_case(
    case_id: str,
    project: str,
    target_files: list[str],
    target_hunks: list[str],
    leftover_hunks: list[str],
    unrelated_files: list[str],
    message: str,
    answer_anchor: str,
) -> dict[str, Any]:
    working: dict[str, Any] = {}
    partial_hunks: dict[str, Any] = {}
    target_hunk_map: dict[str, list[str]] = {}
    leftover_hunk_map: dict[str, list[str]] = {}
    for index, target_file in enumerate(target_files):
        target = [target_hunks[index]]
        leftover = [leftover_hunks[index]]
        working[target_file] = {"status": "modified", "hunks": [*target, *leftover]}
        partial_hunks[target_file] = {"target_hunks": target, "leftover_hunks": leftover}
        target_hunk_map[target_file] = target
        leftover_hunk_map[target_file] = leftover
    for path in unrelated_files:
        working[path] = "modified"
    return {
        "case_id": case_id,
        "project": project,
        "target_files": target_files,
        "target_hunks": target_hunks,
        "leftover_hunks": leftover_hunks,
        "target_hunk_map": target_hunk_map,
        "leftover_hunk_map": leftover_hunk_map,
        "unrelated_files": unrelated_files,
        "excluded_files": unrelated_files,
        "allowed_working_tree_paths": [*target_files, *unrelated_files],
        "working_tree": working,
        "partial_hunks": partial_hunks,
        "required_commit_message": message,
        "solution_commands": [
            *(f"git add -p {path}" for path in target_files),
            f'git commit -m "{message}"',
        ],
        "answer_anchor": answer_anchor,
        "target_file": ", ".join(target_files),
        "target_hunk": ", ".join(target_hunks),
        "leftover_hunk": ", ".join(leftover_hunks),
        "other_file": ", ".join(unrelated_files) if unrelated_files else "none",
        "commit_to_repair": "none",
    }


def partial_bp(
    slug: str, cases: list[dict[str, Any]], signature: str, subtemplate: str
) -> dict[str, Any]:
    return bp(
        slug=slug,
        kind="partial",
        signature=signature,
        subtemplate=subtemplate,
        cases=cases,
        initial_state=repo_with_head(
            commits=[commit("c1", "Initial project snapshot", {"README.md": "readme-v1"})],
            working_tree="{{working_tree}}",
            partial_hunks="{{partial_hunks}}",
        ),
        target_rule={
            "head_branch": "main",
            "latest_commit": {
                "branch": "main",
                "message_contains": ["{{required_commit_message}}"],
                "contains_paths": "{{target_files}}",
                "excludes_paths": "{{excluded_files}}",
            },
            "working_tree_contains": "{{target_files}}",
            "staging_empty": True,
            "rules": [
                {"type": "partial_hunks_committed", "paths": "{{target_hunk_map}}"},
                {"type": "partial_hunks_left_in_working_tree", "paths": "{{leftover_hunk_map}}"},
                {"type": "commit_changes_exclude_tokens", "tokens": "{{leftover_hunks}}"},
                {"type": "working_tree_clean_except", "paths": "{{allowed_working_tree_paths}}"},
            ],
        },
        solution="{{solution_commands}}",
        label="Partial stage {{project}}",
        slug_template="partial-{{case_id}}",
    )


def amend_scenario() -> dict[str, Any]:
    easy = [
        amend_case(
            "amend-easy-login-copy-message",
            "login-copy",
            ["src/login.js"],
            "Update text",
            "Clarify login copy",
            {},
            "branch tip is amended commit with message Clarify login copy; no extra commit",
        ),
        amend_case(
            "amend-easy-readme-message",
            "setup-docs",
            ["README.md"],
            "Update README",
            "Clarify setup requirements",
            {},
            "amended tip message Clarify setup requirements; same tree",
        ),
        amend_case(
            "amend-easy-navbar-message",
            "style-polish",
            ["styles/navbar.css"],
            "CSS updates",
            "Adjust navbar spacing",
            {},
            "amended tip message Adjust navbar spacing; same tree",
        ),
    ]
    medium = [
        amend_case(
            "amend-medium-profile-missing-css",
            "profile-card",
            ["src/profile-card.js", "styles/profile-card.css"],
            "Update profile card layout",
            "Update profile card layout",
            {"styles/profile-card.css": "profile-css-v2"},
            "amended tip includes missing CSS without creating new commit",
        ),
        amend_case(
            "amend-medium-export-doc",
            "export-flow",
            ["src/export.py", "docs/export.md"],
            "Document export flow update",
            "Document export flow update",
            {"docs/export.md": "export-docs-v2"},
            "amended tip includes export docs",
        ),
        amend_case(
            "amend-medium-search-template",
            "search-view",
            ["src/search.js", "templates/search.html"],
            "Refine search results view",
            "Refine search results view",
            {"templates/search.html": "search-template-v2"},
            "amended tip includes search template",
        ),
    ]
    hard = [
        amend_case(
            "amend-hard-profile-message-and-css",
            "profile-card",
            ["src/profile-card.js", "styles/profile-card.css"],
            "Update profile stuff",
            "Update profile card layout",
            {"styles/profile-card.css": "profile-css-v3"},
            "amended tip has corrected message and missing CSS; old tip replaced",
        ),
        amend_case(
            "amend-hard-auth-message-and-test",
            "auth-module",
            ["src/auth.py", "tests/test_auth.py"],
            "Auth changes",
            "Add auth validation coverage",
            {"tests/test_auth.py": "auth-test-v2"},
            "amended tip has corrected message and test path; no extra child commit",
        ),
        amend_case(
            "amend-hard-export-message-and-doc",
            "export-flow",
            ["src/export.py", "docs/export.md"],
            "Export update",
            "Document export validation behavior",
            {"docs/export.md": "export-docs-v3"},
            "amended tip has corrected message and docs; old tip replaced",
        ),
    ]
    return scenario_dict(
        lesson=(
            7,
            "amending-commits",
            "Amending Commits",
            "Repair the latest commit message or contents before sharing it.",
        ),
        slug="amend-latest-commit",
        title="Amend the latest commit",
        focus="git commit --amend",
        summary="Repair the latest local commit instead of creating a follow-up commit.",
        explanation="Amend replaces the branch tip with a corrected commit that keeps the intended parent relationship.",
        primary=["git commit --amend"],
        supporting=["git status", "git log --oneline", "git diff", "git diff --staged"],
        concepts=["latest commit", "amend", "branch tip replacement", "commit message"],
        difficulties={
            DIFFICULTY_EASY: diff(
                (1, 2),
                "Fix only the latest commit message.",
                "Repair the latest commit message without creating a separate commit.",
                [
                    amend_bp(
                        "amend-message-only", easy, "module1.amend.message-only", "message-only"
                    )
                ],
                completion_type=COMPLETION_EXPANDED_STATE_BASED,
            ),
            DIFFICULTY_MEDIUM: diff(
                (2, 4),
                "Add missing content to the latest commit.",
                "Stage the missing file and repair the latest commit while keeping its message.",
                [amend_bp("amend-content-only", medium, "module1.amend.content", "content-only")],
                completion_type=COMPLETION_EXPANDED_STATE_BASED,
            ),
            DIFFICULTY_HARD: diff(
                (2, 5),
                "Fix latest commit message and content together.",
                "Repair both the message and missing content in the latest commit.",
                [
                    amend_bp(
                        "amend-message-and-content",
                        hard,
                        "module1.amend.message-content",
                        "message-and-content",
                    )
                ],
                completion_type=COMPLETION_EXPANDED_STATE_BASED,
            ),
        },
    )


def amend_case(
    case_id: str,
    project: str,
    target_files: list[str],
    old_message: str,
    new_message: str,
    working_tree: dict[str, Any],
    answer_anchor: str,
) -> dict[str, Any]:
    tree_c1 = {"README.md": "readme-v1"}
    committed_files = [path for path in target_files if path not in working_tree]
    tree_c2 = {**tree_c1, **{path: f"{path}-committed-v1" for path in committed_files}}
    return {
        "case_id": case_id,
        "project": project,
        "target_file": ", ".join(target_files),
        "target_files": target_files,
        "excluded_files": [],
        "target_hunk": "none",
        "target_hunks": [],
        "leftover_hunk": "none",
        "leftover_hunks": [],
        "commit_to_repair": "c2",
        "old_message": old_message,
        "required_commit_message": new_message,
        "working_tree": working_tree,
        "commits": [
            commit("c1", "Initial project snapshot", tree_c1),
            commit("c2", old_message, tree_c2, ["c1"]),
        ],
        "solution_commands": [
            *(f"git add {path}" for path in working_tree),
            f'git commit --amend -m "{new_message}"',
        ],
        "answer_anchor": answer_anchor,
    }


def amend_bp(
    slug: str, cases: list[dict[str, Any]], signature: str, subtemplate: str
) -> dict[str, Any]:
    return bp(
        slug=slug,
        kind="amend",
        signature=signature,
        subtemplate=subtemplate,
        cases=cases,
        initial_state=repo_with_head(
            commits="{{commits}}", head="c2", working_tree="{{working_tree}}"
        ),
        target_rule={
            "head_branch": "main",
            "latest_commit": {
                "branch": "main",
                "message_contains": ["{{required_commit_message}}"],
                "contains_paths": "{{target_files}}",
            },
            "staging_empty": True,
            "working_tree_clean": True,
            "rules": [
                {
                    "type": "operation_metadata_equals",
                    "key": "last_amend_replaced_commit",
                    "value": "{{commit_to_repair}}",
                },
                {"type": "branch_tip_replaces_commit", "old": "{{commit_to_repair}}"},
                {"type": "commit_replaced_by_amend", "old": "{{commit_to_repair}}"},
            ],
        },
        solution="{{solution_commands}}",
        label="Amend {{project}}",
        slug_template="amend-{{case_id}}",
    )


def restore_scenario() -> dict[str, Any]:
    easy = [
        restore_case(
            "restore-easy-unstage-app",
            "cleanup-lab",
            {"src/app.py": "app-change-v2"},
            {},
            ["src/app.py"],
            [],
            "src/app.py moves from staging to working_tree; no commit created",
        ),
        restore_case(
            "restore-easy-unstage-guide",
            "docs-lab",
            {"docs/guide.md": "guide-change-v2"},
            {},
            ["docs/guide.md"],
            [],
            "docs/guide.md unstaged and preserved",
        ),
        restore_case(
            "restore-easy-unstage-css",
            "style-lab",
            {"styles/site.css": "css-change-v2"},
            {},
            ["styles/site.css"],
            [],
            "styles/site.css unstaged and preserved",
        ),
    ]
    medium = [
        restore_case(
            "restore-medium-app-debug",
            "cleanup-lab",
            {"src/app.py": "app-change-v2"},
            {"debug.log": "debug-draft"},
            ["src/app.py"],
            ["debug.log"],
            "app.py preserved as working change; debug.log discarded",
        ),
        restore_case(
            "restore-medium-docs-scratch",
            "docs-lab",
            {"docs/guide.md": "guide-change-v2"},
            {"tmp/scratch.txt": "scratch-draft"},
            ["docs/guide.md"],
            ["tmp/scratch.txt"],
            "guide preserved; scratch discarded",
        ),
        restore_case(
            "restore-medium-css-build",
            "style-lab",
            {"styles/site.css": "css-change-v2"},
            {"dist/site.css": "dist-generated"},
            ["styles/site.css"],
            ["dist/site.css"],
            "source CSS preserved; generated dist discarded",
        ),
    ]
    hard = [
        restore_case(
            "restore-hard-mixed-profile",
            "profile-card",
            {"src/profile-card.js": "profile-js-v2", "notes/profile-ideas.md": "notes-draft"},
            {"debug/profile.log": "debug-draft"},
            ["src/profile-card.js"],
            ["debug/profile.log"],
            "all staging cleared; profile-card.js preserved; debug log discarded; no commit",
        ),
        restore_case(
            "restore-hard-mixed-export",
            "export-flow",
            {"src/export.py": "export-code-v2", "notes/export-plan.md": "notes-draft"},
            {"tmp/export-output.txt": "generated-output"},
            ["src/export.py"],
            ["tmp/export-output.txt"],
            "export.py preserved; notes unstaged; generated output discarded; no commit",
        ),
        restore_case(
            "restore-hard-mixed-search",
            "search-view",
            {"src/search.js": "search-js-v2", "notes/search.md": "notes-draft"},
            {"debug/search.log": "search-debug"},
            ["src/search.js"],
            ["debug/search.log"],
            "search.js preserved; notes unstaged; debug log discarded; no commit",
        ),
    ]
    return scenario_dict(
        lesson=(
            8,
            "unstaging-and-discarding-changes",
            "Unstaging and Discarding Changes",
            "Move changes out of the index and safely discard unwanted work.",
        ),
        slug="unstage-and-discard-changes",
        title="Unstage and discard safely",
        focus="git restore",
        summary="Keep selected changes as working-tree work and discard unwanted paths.",
        explanation="Restoring from the index and working tree are different state changes. One preserves work, the other removes it.",
        primary=["git restore"],
        supporting=["git status", "git diff", "git diff --staged"],
        concepts=["restore", "unstage", "discard", "index", "working tree"],
        difficulties={
            DIFFICULTY_EASY: diff(
                (1, 2),
                "Unstage one file while keeping its working-tree change.",
                "Move the staged file back to the working tree without discarding it.",
                [
                    restore_bp(
                        "restore-unstage-one",
                        easy,
                        "module1.restore.unstage-one",
                        "one-file-unstage",
                    )
                ],
            ),
            DIFFICULTY_MEDIUM: diff(
                (2, 4),
                "Unstage one file and discard another working-tree change.",
                "Keep the staged work as a working-tree change and remove the unwanted file.",
                [
                    restore_bp(
                        "restore-unstage-and-discard",
                        medium,
                        "module1.restore.unstage-discard",
                        "one-keep-one-discard",
                    )
                ],
            ),
            DIFFICULTY_HARD: diff(
                (2, 5),
                "Clean a noisy mixed state.",
                "Preserve the requested path and discard the unwanted path without making a commit.",
                [
                    restore_bp(
                        "restore-noisy",
                        hard,
                        "module1.restore.noisy",
                        "multiple-staged-one-discard",
                    )
                ],
            ),
        },
    )


def restore_case(
    case_id: str,
    project: str,
    initial_staging: dict[str, Any],
    initial_working_tree: dict[str, Any],
    keep_paths: list[str],
    discard_paths: list[str],
    answer_anchor: str,
) -> dict[str, Any]:
    commands = [f"git restore --staged {' '.join(initial_staging)}"]
    if discard_paths:
        commands.append(f"git restore {' '.join(discard_paths)}")
    return {
        "case_id": case_id,
        "project": project,
        "keep_paths": keep_paths,
        "discard_paths": discard_paths,
        "staging": initial_staging,
        "working_tree": initial_working_tree,
        "solution_commands": commands,
        "answer_anchor": answer_anchor,
    }


def restore_bp(
    slug: str, cases: list[dict[str, Any]], signature: str, subtemplate: str
) -> dict[str, Any]:
    return bp(
        slug=slug,
        kind="restore",
        signature=signature,
        subtemplate=subtemplate,
        cases=cases,
        initial_state=repo_with_head(
            commits=[
                commit(
                    "c1",
                    "Initial project snapshot",
                    {
                        "README.md": "readme-v1",
                        "src/app.py": "app-v1",
                        "styles/site.css": "style-v1",
                    },
                )
            ],
            staging="{{staging}}",
            working_tree="{{working_tree}}",
        ),
        target_rule={
            "head_branch": "main",
            "branch_points_to": {"main": "c1"},
            "staging_empty": True,
            "working_tree_contains": "{{keep_paths}}",
            "working_tree_absent": "{{discard_paths}}",
            "rules": [{"type": "commit_count_equals", "count": 1}],
        },
        solution="{{solution_commands}}",
        label="Restore {{project}}",
        slug_template="restore-{{case_id}}",
    )


def review_scenario() -> dict[str, Any]:
    clean_cases = [
        review_clean_case(
            "review-easy-docs-ignore",
            "docs-portal",
            ["docs/intro.md", ".gitignore"],
            ["dist/site.html"],
            "Prepare docs portal intro",
            "commit contains docs/intro.md + .gitignore; excludes dist/site.html",
        ),
        review_clean_case(
            "review-easy-profile-ignore",
            "profile-site",
            ["src/profile-card.js", ".gitignore"],
            ["dist/profile-card.js"],
            "Prepare profile card update",
            "commit contains profile-card.js + .gitignore; excludes dist artifact",
        ),
        review_clean_case(
            "review-easy-export-ignore",
            "export-flow",
            ["src/export.py", ".gitignore"],
            ["output/export.csv"],
            "Prepare export workflow update",
            "commit contains export.py + .gitignore; excludes output CSV",
        ),
    ]
    medium_cases = [
        review_clean_case(
            "review-medium-profile-with-note",
            "profile-card",
            ["src/profile-card.js", "styles/profile-card.css", ".gitignore"],
            ["notes/profile-ideas.md", "dist/profile-card.js"],
            "Finalize profile card update",
            "commit has two source files + .gitignore; note remains; dist ignored",
            allowed_working_tree_paths=["notes/profile-ideas.md"],
        ),
        review_clean_case(
            "review-medium-search-with-output",
            "search-view",
            ["src/search.js", "templates/search.html", ".gitignore"],
            ["notes/search-ranking.md", "output/search-results.json"],
            "Finalize search results update",
            "source/template committed; note remains; output ignored",
            allowed_working_tree_paths=["notes/search-ranking.md"],
        ),
        review_clean_case(
            "review-medium-export-with-note",
            "export-flow",
            ["src/export.py", "docs/export.md", ".gitignore"],
            ["notes/export-plan.md", "output/export.csv"],
            "Finalize export documentation update",
            "code/docs/.gitignore committed; note remains; output ignored",
            allowed_working_tree_paths=["notes/export-plan.md"],
        ),
    ]
    hard_partial_cases = [
        partial_case(
            "review-hard-auth-partial",
            "auth-module",
            ["src/auth.py", "tests/test_auth.py"],
            ["auth-validation-hunk", "auth-validation-test-hunk"],
            ["auth-refactor-hunk", "auth-test-cleanup-hunk"],
            ["notes/auth-debug.md"],
            "Finalize auth validation change",
            "only validation hunks committed; leftovers and notes remain",
        ),
        partial_case(
            "review-hard-search-partial",
            "search-view",
            ["src/search.js", "tests/test_search.js"],
            ["search-ranking-hunk", "search-ranking-test-hunk"],
            ["search-theme-hunk", "search-fixture-cleanup-hunk"],
            ["tmp/search-output.json"],
            "Finalize search ranking behavior",
            "ranking hunks committed; theme/fixture/tmp leftovers remain",
        ),
    ]
    hard_amend_cases = [
        amend_case(
            "review-hard-export-amend",
            "export-flow",
            ["src/export.py", "docs/export.md"],
            "Export update",
            "Finalize export validation behavior",
            {"docs/export.md": "export-docs-final"},
            "branch tip is amended commit with corrected message and docs; no extra commit",
        ),
    ]
    return scenario_dict(
        lesson=(
            9,
            "module-1-review-and-practice",
            "Module 1 Review and Practice",
            "Combine the local workflow skills in larger repository situations.",
        ),
        slug="module1-integrated-local-workflow",
        title="Complete a focused local workflow",
        focus="local repository workflow",
        summary="Combine Module 1 skills to reach a clean local repository outcome.",
        explanation="The review scenario combines inspection, staging, committing, ignore rules, partial staging, restore, or amend within one local workflow task.",
        primary=["git add", "git commit"],
        supporting=["git status", "git diff", "git diff --staged", "git log --oneline"],
        concepts=[
            "focused snapshot",
            "ignore rules",
            "partial staging",
            "amend",
            "clean final state",
        ],
        kind=ScenarioSkillFocus.SkillFocusType.WORKFLOW_SPECIFIC,
        difficulties={
            DIFFICULTY_EASY: diff(
                (3, 6),
                "Clean focused commit with one target file and one ignored artifact.",
                "Commit the required file and ignore rules while leaving generated output out.",
                [
                    review_clean_bp(
                        "review-clean-ignore",
                        clean_cases,
                        "module1.review.clean-ignore",
                        "clean-commit-with-ignore",
                    )
                ],
                completion_type=COMPLETION_EXPANDED_STATE_BASED,
            ),
            DIFFICULTY_MEDIUM: diff(
                (3, 7),
                "Focused commit with .gitignore plus excluded local note or output.",
                "Commit the focused source changes and ignore rules while preserving the excluded local note.",
                [
                    review_clean_bp(
                        "review-focused-leftover",
                        medium_cases,
                        "module1.review.focused-leftover",
                        "focused-commit-with-leftover",
                    )
                ],
                completion_type=COMPLETION_EXPANDED_STATE_BASED,
            ),
            DIFFICULTY_HARD: diff(
                (3, 8),
                "Focused snapshot using partial staging or amend repair.",
                "Use the appropriate Module 1 workflow to produce the exact focused final state.",
                [
                    review_partial_bp("review-partial", hard_partial_cases),
                    review_amend_bp("review-amend", hard_amend_cases),
                ],
                completion_type=COMPLETION_EXPANDED_STATE_BASED,
            ),
        },
    )


def review_clean_case(
    case_id: str,
    project: str,
    target_files: list[str],
    excluded_files: list[str],
    message: str,
    answer_anchor: str,
    *,
    allowed_working_tree_paths: list[str] | None = None,
) -> dict[str, Any]:
    working_tree: dict[str, Any] = {
        path: f"{path}-v2" for path in target_files if path != ".gitignore"
    }
    working_tree[".gitignore"] = "review-ignore-v1"
    visible_leftovers = set(allowed_working_tree_paths or [])
    ignored_paths = [path for path in excluded_files if path not in visible_leftovers]
    for path in excluded_files:
        working_tree[path] = (
            "local-draft"
            if path in visible_leftovers
            else {"status": "ignored", "content": f"{path}-generated"}
        )
    return {
        "case_id": case_id,
        "project": project,
        "target_files": target_files,
        "excluded_files": excluded_files,
        "ignored_paths": ignored_paths,
        "allowed_working_tree_paths": allowed_working_tree_paths or [],
        "stage_args": " ".join(target_files),
        "required_commit_message": message,
        "working_tree": working_tree,
        "target_hunks": [],
        "leftover_hunks": [],
        "commit_to_repair": "none",
        "answer_anchor": answer_anchor,
    }


def review_clean_bp(
    slug: str, cases: list[dict[str, Any]], signature: str, subtemplate: str
) -> dict[str, Any]:
    return bp(
        slug=slug,
        kind="review",
        signature=signature,
        subtemplate=subtemplate,
        cases=cases,
        initial_state=repo_with_head(working_tree="{{working_tree}}"),
        target_rule={
            "head_branch": "main",
            "latest_commit": {
                "branch": "main",
                "message_contains": ["{{required_commit_message}}"],
                "contains_paths": "{{target_files}}",
                "excludes_paths": "{{excluded_files}}",
            },
            "staging_empty": True,
            "rules": [
                {"type": "working_tree_clean_except", "paths": "{{allowed_working_tree_paths}}"},
                {"type": "ignored_paths_present", "paths": "{{ignored_paths}}"},
            ],
        },
        solution=["git add {{stage_args}}", 'git commit -m "{{required_commit_message}}"'],
        label="Review {{project}}",
        slug_template="review-{{case_id}}",
    )


def review_partial_bp(slug: str, cases: list[dict[str, Any]]) -> dict[str, Any]:
    return bp(
        slug=slug,
        kind="review",
        signature="module1.review.partial",
        subtemplate="partial-staging-review",
        cases=cases,
        initial_state=repo_with_head(
            commits=[commit("c1", "Initial project snapshot", {"README.md": "readme-v1"})],
            working_tree="{{working_tree}}",
            partial_hunks="{{partial_hunks}}",
        ),
        target_rule={
            "head_branch": "main",
            "latest_commit": {
                "branch": "main",
                "message_contains": ["{{required_commit_message}}"],
                "contains_paths": "{{target_files}}",
                "excludes_paths": "{{excluded_files}}",
            },
            "working_tree_contains": "{{target_files}}",
            "staging_empty": True,
            "rules": [
                {"type": "partial_hunks_committed", "paths": "{{target_hunk_map}}"},
                {"type": "partial_hunks_left_in_working_tree", "paths": "{{leftover_hunk_map}}"},
                {"type": "commit_changes_exclude_tokens", "tokens": "{{leftover_hunks}}"},
                {"type": "working_tree_clean_except", "paths": "{{allowed_working_tree_paths}}"},
            ],
        },
        solution="{{solution_commands}}",
        label="Review {{project}}",
        slug_template="review-{{case_id}}",
    )


def review_amend_bp(slug: str, cases: list[dict[str, Any]]) -> dict[str, Any]:
    return bp(
        slug=slug,
        kind="review",
        signature="module1.review.amend",
        subtemplate="amend-review",
        cases=cases,
        initial_state=repo_with_head(
            commits="{{commits}}", head="c2", working_tree="{{working_tree}}"
        ),
        target_rule={
            "head_branch": "main",
            "latest_commit": {
                "branch": "main",
                "message_contains": ["{{required_commit_message}}"],
                "contains_paths": "{{target_files}}",
            },
            "staging_empty": True,
            "working_tree_clean": True,
            "rules": [
                {
                    "type": "operation_metadata_equals",
                    "key": "last_amend_replaced_commit",
                    "value": "{{commit_to_repair}}",
                },
                {"type": "branch_tip_replaces_commit", "old": "{{commit_to_repair}}"},
            ],
        },
        solution="{{solution_commands}}",
        label="Review {{project}}",
        slug_template="review-{{case_id}}",
    )


def scenario_dict(
    *,
    lesson,
    slug,
    title,
    focus,
    summary,
    explanation,
    primary,
    supporting,
    concepts,
    difficulties,
    kind=ScenarioSkillFocus.SkillFocusType.COMMAND_SPECIFIC,
):
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


def diff(
    policy,
    narrative,
    task,
    blueprints,
    completion_type=COMPLETION_STATE_BASED,
    required_attempts=None,
):
    payload = {
        "policy": policy,
        "narrative": narrative,
        "task": task,
        "blueprints": blueprints,
        "completion_type": completion_type,
    }
    if required_attempts is not None:
        payload["required_successful_attempts"] = required_attempts
    return payload


class Command(BaseCommand):
    help = "Seed Module 1 scenario skill focuses, difficulties, policies, and runtime generation blueprints."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing Module 1 content and generated sessions before seeding.",
        )
        parser.add_argument(
            "--confirm",
            action="store_true",
            help="Required with --reset to confirm development data deletion.",
        )
        parser.add_argument(
            "--validate-build",
            action="store_true",
            help="Try generating one variant for every difficulty after seeding.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["reset"]:
            self._reset_module_one(confirm=options["confirm"])

        unit, _ = LearningUnit.objects.update_or_create(
            slug="local-repository-foundations",
            defaults={
                "number": 1,
                "title": "Local Repository Foundations",
                "description": "Initialize, clone, stage, commit, ignore, partially stage, amend, clean up, and inspect local Git repositories through scenario practice.",
                "is_orientation": False,
                "is_published": True,
                "sort_order": 1,
            },
        )

        lesson_by_order = {}
        for (
            lesson_order,
            lesson_slug,
            lesson_title,
            lesson_subtitle,
            lesson_kind,
        ) in MODULE_ONE_LESSONS:
            kind = (
                Lesson.LessonKind.SCENARIO
                if lesson_kind == "scenario"
                else Lesson.LessonKind.CONTENT
            )
            lesson, _ = Lesson.objects.update_or_create(
                unit=unit,
                slug=lesson_slug,
                defaults={
                    "title": lesson_title,
                    "subtitle": lesson_subtitle,
                    "kind": kind,
                    "content_html": self._lesson_html(lesson_title, lesson_subtitle),
                    "scoped_css": "",
                    "interaction_steps": [],
                    "is_published": True,
                    "sort_order": lesson_order,
                },
            )
            lesson_by_order[lesson_order] = lesson

        specs = base_scenarios()
        self._validate_seed_specs(specs)
        active_scenario_slugs = [spec["slug"] for spec in specs]
        ScenarioSkillFocus.objects.filter(learning_unit=unit).exclude(
            slug__in=active_scenario_slugs
        ).update(is_published=False)

        for spec in specs:
            lesson_order, lesson_slug, lesson_title, lesson_subtitle = spec["lesson"]
            lesson = lesson_by_order[lesson_order]
            scenario, _ = ScenarioSkillFocus.objects.update_or_create(
                learning_unit=unit,
                slug=spec["slug"],
                defaults={
                    "lesson": lesson,
                    "title": spec["title"],
                    "focus": spec["focus"],
                    "summary": spec["summary"],
                    "short_explanation": spec["explanation"],
                    "skill_focus_type": spec["kind"],
                    "primary_focus_commands": spec["primary"],
                    "supporting_inspection_commands": spec["supporting"],
                    "safe_demo_commands": self._demo_commands(spec),
                    "demo_repository_state": self._demo_state(spec),
                    "demo_dag_config": {},
                    "demo_explanation_steps": self._demo_steps(spec),
                    "command_preview_config": self._command_preview_config(spec),
                    "related_git_concepts": spec["concepts"],
                    "narrative": spec["summary"],
                    "task_prompt": "Start a generated variant and reach the requested repository outcome.",
                    "is_published": True,
                    "sort_order": lesson_order,
                },
            )

            for difficulty, dspec in spec["difficulties"].items():
                difficulty_instance, _ = DifficultyInstance.objects.update_or_create(
                    scenario=scenario,
                    difficulty=difficulty,
                    defaults={
                        "completion_type": dspec.get("completion_type", COMPLETION_STATE_BASED),
                        "required_successful_attempts": dspec.get(
                            "required_successful_attempts", SESSION_COUNTS[difficulty]
                        ),
                        "narrative": dspec["narrative"],
                        "task_prompt": dspec["task"],
                        "is_published": True,
                    },
                )
                min_count, max_count = dspec["policy"]
                CommandCountPolicy.objects.update_or_create(
                    difficulty_instance=difficulty_instance,
                    defaults={
                        "min_counted_commands": min_count,
                        "max_counted_commands": max_count,
                        "non_counted_patterns": DIAG_PATTERNS,
                    },
                )
                TargetStateRule.objects.update_or_create(
                    difficulty_instance=difficulty_instance,
                    defaults={
                        "rule": dspec["blueprints"][0]["target_rule_template"],
                        "target_state_hash": "",
                    },
                )

                existing_slugs = []
                for index, blueprint in enumerate(dspec["blueprints"], start=1):
                    existing_slugs.append(blueprint["slug"])
                    ScenarioGenerationBlueprint.objects.update_or_create(
                        difficulty_instance=difficulty_instance,
                        slug=blueprint["slug"],
                        defaults={
                            "slug_template": blueprint["slug_template"],
                            "label_template": blueprint["label_template"],
                            "blueprint_signature": blueprint["blueprint_signature"],
                            "subtemplate_signature": blueprint["subtemplate_signature"],
                            "parameter_pools": blueprint["parameter_pools"],
                            "initial_state_template": blueprint["initial_state_template"],
                            "target_rule_template": blueprint["target_rule_template"],
                            "solution_commands_template": blueprint["solution_commands_template"],
                            "expected_observations_template": blueprint[
                                "expected_observations_template"
                            ],
                            "student_context_template": blueprint["student_context_template"],
                            "generation_count": blueprint["generation_count"],
                            "max_combinations": blueprint["max_combinations"],
                            "is_published": True,
                            "sort_order": index,
                        },
                    )
                ScenarioGenerationBlueprint.objects.filter(
                    difficulty_instance=difficulty_instance
                ).exclude(slug__in=existing_slugs).delete()

        self.stdout.write(self.style.SUCCESS("Seeded Module 1 scenario blueprints."))

        if options["validate_build"]:
            self._validate_builds()

    def _validate_seed_specs(self, specs: list[dict[str, Any]]) -> None:
        renderer = TemplateRenderer()
        failures: list[str] = []
        for spec in specs:
            for difficulty, dspec in spec["difficulties"].items():
                rendered_solutions: dict[str, list[str]] = {}
                for blueprint in dspec["blueprints"]:
                    cases = blueprint.get("parameter_pools", {}).get("cases", [])
                    if not cases:
                        failures.append(
                            f"{spec['slug']}/{difficulty}/{blueprint['slug']}: blueprint has no cases"
                        )
                        continue
                    case_ids = [case.get("case_id") for case in cases]
                    if len(set(case_ids)) != len(case_ids):
                        failures.append(
                            f"{spec['slug']}/{difficulty}/{blueprint['slug']}: duplicate case_id"
                        )
                    anchors = [case.get("answer_anchor") for case in cases]
                    if len(set(json.dumps(anchor, sort_keys=True) for anchor in anchors)) != len(
                        anchors
                    ):
                        failures.append(
                            f"{spec['slug']}/{difficulty}/{blueprint['slug']}: duplicate answer_anchor"
                        )
                    for case in cases:
                        rendered = renderer.render(
                            blueprint.get("solution_commands_template", []),
                            {**case, "index": 1},
                        )
                        key = json.dumps(rendered, sort_keys=True)
                        rendered_solutions.setdefault(key, []).append(
                            case.get("case_id", "unknown")
                        )
                for sequence, case_ids_for_sequence in rendered_solutions.items():
                    if len(case_ids_for_sequence) <= 1:
                        continue
                    waived_cases = [
                        case
                        for blueprint in dspec["blueprints"]
                        for case in blueprint.get("parameter_pools", {}).get("cases", [])
                        if case.get("case_id") in case_ids_for_sequence
                        and case.get("duplicate_solution_waiver")
                    ]
                    if len(waived_cases) != len(case_ids_for_sequence):
                        failures.append(
                            f"{spec['slug']}/{difficulty}: duplicate solution sequence {sequence} in cases {case_ids_for_sequence}"
                        )
        if failures:
            raise CommandError("Module 1 seed validation failed:\n" + "\n".join(failures))

    def _reset_module_one(self, *, confirm: bool):
        if not settings.DEBUG:
            raise CommandError("--reset is only available when DEBUG=True.")
        if not confirm:
            raise CommandError("Pass --confirm with --reset to clear Module 1 seeded data.")
        unit = LearningUnit.objects.filter(slug="local-repository-foundations").first()
        if not unit:
            return
        CompletionRecord.objects.filter(scenario__learning_unit=unit).delete()
        ScenarioSession.objects.filter(learning_unit=unit).delete()
        ScenarioVariant.objects.filter(scenario__learning_unit=unit).delete()
        ScenarioGenerationBlueprint.objects.filter(
            difficulty_instance__scenario__learning_unit=unit
        ).delete()
        TargetStateRule.objects.filter(difficulty_instance__scenario__learning_unit=unit).delete()
        DifficultyInstance.objects.filter(scenario__learning_unit=unit).delete()
        ScenarioSkillFocus.objects.filter(learning_unit=unit).delete()
        OrientationProgress.objects.filter(lesson__unit=unit).delete()
        unit.lessons.all().delete()
        unit.delete()

    def _lesson_html(self, title: str, subtitle: str) -> str:
        return f"""
<section class=\"lesson-overview\">
  <h1>{title}</h1>
  <p>{subtitle}</p>
  <p>This lesson overview explains the Git concept before practice. Open the scenario preview to see a command warm-up, then start a generated variant from the scenario card.</p>
</section>
""".strip()

    def _demo_state(self, spec: dict[str, Any]) -> dict[str, Any]:
        if spec["slug"] == "initialize-local-repository":
            return uninitialized_state(working_tree={"demo.txt": "untracked"})
        if spec["slug"] == "clone-remote-repository":
            return uninitialized_state(
                remote_fixtures={
                    "branches": {"origin/main": "r0"},
                    "commits": [
                        commit(
                            "r0",
                            "Create demo repository",
                            {"README.md": "demo-readme-v1", "src/demo.py": "demo-v1"},
                        )
                    ],
                }
            )
        return repo_with_head(
            commits=[
                commit(
                    "c0",
                    "Create demo repository",
                    {"README.md": "readme-v1", "demo.txt": "demo-v1", ".env": "SECRET=old"},
                ),
                commit(
                    "c1",
                    "Add baseline feature",
                    {
                        "README.md": "readme-v1",
                        "demo.txt": "demo-v1",
                        "baseline.txt": "base-v1",
                        ".env": "SECRET=old",
                    },
                    ["c0"],
                ),
            ],
            head="c1",
            working_tree={
                "demo.txt": "demo-v2",
                "notes.txt": "untracked",
                ".gitignore": "demo-ignore-v1",
                ".env": {"status": "ignored", "content": "SECRET=demo"},
            },
            staging={"staged.txt": "staged-v1"},
            partial_hunks={
                "demo.txt": {
                    "target_hunks": ["demo-target-hunk"],
                    "leftover_hunks": ["demo-leftover-hunk"],
                }
            },
            remotes={"origin": "https://example.test/demo/repository.git"},
            remote_branches={"origin/main": "c1"},
            upstream_tracking={"main": "origin/main"},
            extra={
                "reflog": [
                    {"ref": "HEAD@{0}", "target": "c1", "message": "commit: Add baseline feature"}
                ]
            },
        )

    def _demo_steps(self, spec: dict[str, Any]) -> list[dict[str, Any]]:
        return [
            {
                "command": command,
                "title": self._demo_title(command),
                "explanation": self._demo_command_explanation(command, spec),
                "repository_state": self._demo_state(spec),
                "common_mistake": self._demo_common_mistake(command),
                "diagnostic": command.strip().lower() in {item.lower() for item in DIAG_PATTERNS},
                "counted": command.strip().lower() not in {item.lower() for item in DIAG_PATTERNS},
            }
            for command in self._demo_commands(spec)
        ]

    def _command_preview_config(self, spec: dict[str, Any]) -> dict[str, Any]:
        commands = self._demo_commands(spec)
        demo_state = self._demo_state(spec)
        sections = []
        for command in commands:
            section_steps = [
                {
                    "command": command,
                    "title": self._demo_title(command),
                    "explanation": self._demo_command_explanation(command, spec),
                    "repository_state": demo_state,
                    "common_mistake": self._demo_common_mistake(command),
                    "diagnostic": command.strip().lower() in {item.lower() for item in DIAG_PATTERNS},
                    "counted": command.strip().lower() not in {item.lower() for item in DIAG_PATTERNS},
                }
            ]
            sections.append(
                {
                    "id": self._preview_section_id(command),
                    "title": self._demo_title(command),
                    "command": command,
                    "explanation": self._demo_command_explanation(command, spec),
                    "syntax_examples": self._preview_syntax_examples(command),
                    "what_changes": self._preview_changes(command),
                    "what_does_not_change": self._preview_non_changes(command),
                    "common_mistakes": [self._demo_common_mistake(command)],
                    "readiness_notes": self._preview_readiness_notes(command),
                    "demo_steps": section_steps,
                }
            )

        normalized_commands = [command.strip().lower() for command in commands]
        diagnostic = bool(commands) and all(command in {item.lower() for item in DIAG_PATTERNS} for command in normalized_commands)
        return {
            "title": f"{spec['focus']} command preview",
            "intro": spec["explanation"],
            "purpose": "Understand what this skill changes, what it only reports, and what to inspect before entering a generated scenario.",
            "focus_label": spec["focus"],
            "command_title": spec["title"],
            "sections": sections,
            "supported_demo_commands": commands,
            "demo_repository_state": demo_state,
            "demo_dag_config": {},
            "syntax_examples": [
                example
                for command in commands
                for example in self._preview_syntax_examples(command)
            ],
            "what_changes": self._preview_changes(spec["focus"]),
            "what_does_not_change": self._preview_non_changes(spec["focus"]),
            "common_mistakes": list(dict.fromkeys(self._demo_common_mistake(command) for command in commands))[:4],
            "readiness_notes": [
                "Read the scenario values before choosing paths, messages, or folders.",
                "Use the demo area to see command behavior, then apply the idea to the generated variant.",
            ],
            "diagnostic": diagnostic,
            "counted": not diagnostic,
        }

    def _demo_commands(self, spec: dict[str, Any]) -> list[str]:
        normalized_focus = " ".join(str(spec.get("focus", "")).split()).lower()
        commands = {
            "diagnostic commands": [
                "git status",
                "git log --oneline",
                "git diff",
                "git diff --staged",
                "git show",
                "git branch",
                "git remote -v",
                "git log --oneline --graph --all",
                "git branch -v",
                "git reflog",
            ],
            "git init": ["git status", "git init", "git init demo-project"],
            "git clone": [
                "git clone https://example.test/demo/repository.git demo-repository",
                "git remote -v",
                "git log --oneline",
                "git status",
            ],
            "git commit": [
                "git status",
                "git diff",
                "git add demo.txt",
                "git diff --staged",
                'git commit -m "Demo snapshot"',
                "git log --oneline",
            ],
            ".gitignore": [
                "git status",
                "git add .gitignore",
                "git rm --cached .env",
                'git commit -m "Demo ignore rules"',
            ],
            "git add -p": [
                "git status",
                "git add -p demo.txt",
                "git diff --staged",
                'git commit -m "Demo selected hunk"',
            ],
            "git commit --amend": [
                "git log --oneline",
                "git status",
                "git add demo.txt",
                'git commit --amend -m "Demo amended snapshot"',
                "git show",
            ],
            "git restore": [
                "git status",
                "git restore --staged staged.txt",
                "git restore demo.txt",
                "git diff",
            ],
            "local repository workflow": [
                "git status",
                "git diff",
                "git add demo.txt",
                'git commit -m "Demo workflow snapshot"',
                "git log --oneline",
            ],
        }.get(normalized_focus, [])
        for command in [*spec.get("primary", []), *spec.get("supporting", [])]:
            if command in DIAG_PATTERNS and command not in commands:
                commands.append(command)
        return commands

    def _demo_command_explanation(self, command: str, spec: dict[str, Any]) -> str:
        notes = {
            "git init": "git init creates Git metadata for the selected folder. It does not create a commit, stage files, or modify file contents.",
            "git clone": "git clone creates a local repository from a remote URL, checks out the default branch, and configures origin tracking.",
            "git add": "git add copies selected working-tree changes into the staging area so the next commit can save them.",
            "git commit": "git commit saves the staged snapshot and moves the current branch tip to the new commit.",
            "git add -p": "git add -p lets you stage selected hunks instead of staging an entire file.",
            "git commit --amend": "git commit --amend replaces the latest local commit with a corrected commit instead of creating a separate follow-up commit.",
            "git restore": "git restore changes either the staging area or the working tree, depending on whether --staged is used.",
        }
        normalized = command.strip().lower()
        if normalized.startswith("git status"):
            return "git status summarizes the current branch, staged changes, unstaged changes, and untracked files without changing the repository."
        if normalized.startswith("git log"):
            return "git log reads commit history. The --oneline, --graph, and --all flags change how history is displayed, not repository state."
        if normalized.startswith("git diff --staged") or normalized.startswith("git diff --cached"):
            return "git diff --staged shows what is already in the index for the next commit."
        if normalized.startswith("git diff"):
            return "git diff shows unstaged working-tree changes."
        if normalized.startswith("git show"):
            return "git show displays details for the current or named object, usually the latest commit."
        if normalized.startswith("git branch"):
            return "git branch lists local branches. With -v it also shows the commit each branch points to."
        if normalized.startswith("git remote -v"):
            return "git remote -v lists configured remote URLs for fetch and push."
        if normalized.startswith("git reflog"):
            return "git reflog shows recent HEAD movements for recovery and orientation."
        return notes.get(
            normalized,
            spec.get(
                "explanation",
                "Use the preview to understand the command behavior before starting a variant.",
            ),
        )

    def _demo_title(self, command: str) -> str:
        parts = command.split()
        return (
            " ".join(parts[:3])
            if len(parts) > 2 and parts[2].startswith("-")
            else " ".join(parts[:2])
        )

    def _demo_common_mistake(self, command: str) -> str:
        normalized = command.strip().lower()
        if normalized.startswith("git diff --staged"):
            return "Looking only at unstaged diff output and missing what is already staged."
        if normalized.startswith("git diff"):
            return "Assuming diff shows staged changes; plain git diff reads the working tree."
        if normalized.startswith("git add"):
            return "Staging every file when only one path or hunk belongs in the next commit."
        if normalized.startswith("git commit --amend"):
            return "Creating a second commit instead of replacing the latest local commit."
        if normalized.startswith("git restore --staged"):
            return "Using restore without --staged and discarding work instead of unstaging it."
        if normalized.startswith("git restore"):
            return "Restoring the wrong path and losing working-tree edits you meant to keep."
        if normalized.startswith("git clone"):
            return "Forgetting the destination folder when the task names one."
        if normalized.startswith("git init"):
            return "Initializing the parent folder when the task names a child directory."
        return "Skipping inspection and acting before you know what Git sees."

    def _preview_section_id(self, command: str) -> str:
        return (
            command.strip()
            .lower()
            .replace('"', "")
            .replace(".", "dot")
            .replace(" ", "-")
            .replace("/", "-")
        )

    def _preview_syntax_examples(self, command: str) -> list[str]:
        normalized = " ".join(command.split()).lower()
        examples = {
            "git status": ["git status"],
            "git log --oneline": ["git log --oneline", "git log --oneline --graph --all"],
            "git diff --staged": ["git diff --staged", "git diff --cached"],
            "git diff": ["git diff", "git diff -- <path>"],
            "git show": ["git show", "git show <commit>"],
            "git branch -v": ["git branch -v"],
            "git branch": ["git branch", "git branch -v"],
            "git remote -v": ["git remote -v"],
            "git reflog": ["git reflog"],
            "git init": ["git init", "git init <directory>"],
            "git clone": ["git clone <url>", "git clone <url> <folder>"],
            "git add -p": ["git add -p <path>"],
            "git add": ["git add <path>", "git add -p <path>"],
            "git rm --cached": ["git rm --cached <path>"],
            "git commit --amend": ["git commit --amend", 'git commit --amend -m "message"'],
            "git commit": ['git commit -m "message"'],
            "git restore --staged": ["git restore --staged <path>"],
            "git restore": ["git restore <path>", "git restore --staged <path>"],
        }
        for prefix, syntax in examples.items():
            if normalized.startswith(prefix):
                return syntax
        return [command]

    def _preview_changes(self, command: str) -> list[str]:
        normalized = " ".join(command.split()).lower()
        if normalized.startswith(("git status", "git log", "git diff", "git show", "git branch", "git remote", "git reflog")):
            return ["Nothing in the repository changes; the command only reports information."]
        if normalized.startswith("git init"):
            return ["Creates Git metadata for the target folder so Git can track future snapshots."]
        if normalized.startswith("git clone"):
            return ["Creates a local working copy, default branch checkout, and origin remote relationship."]
        if normalized.startswith("git add -p"):
            return ["Moves selected hunks from the working tree into the staging area."]
        if normalized.startswith("git add"):
            return ["Moves selected path changes from the working tree into the staging area."]
        if normalized.startswith("git rm --cached"):
            return ["Removes the path from the index while leaving the local file in the working tree."]
        if normalized.startswith("git commit --amend"):
            return ["Replaces the latest local commit with a corrected commit."]
        if normalized.startswith("git commit"):
            return ["Creates a new commit from the staged snapshot and advances the current branch."]
        if normalized.startswith("git restore --staged"):
            return ["Moves selected changes out of the staging area."]
        if normalized.startswith("git restore"):
            return ["Restores selected working-tree paths from the index or HEAD."]
        return ["The command changes the repository state described by the scenario."]

    def _preview_non_changes(self, command: str) -> list[str]:
        normalized = " ".join(command.split()).lower()
        if normalized.startswith(("git status", "git log", "git diff", "git show", "git branch", "git remote", "git reflog")):
            return ["It does not stage, commit, discard, or rewrite files."]
        if normalized.startswith("git init"):
            return ["It does not stage files, create a commit, or rewrite file contents."]
        if normalized.startswith("git clone"):
            return ["It does not modify the remote repository."]
        if normalized.startswith("git add"):
            return ["It does not create a commit or remove the working-tree edits from your files."]
        if normalized.startswith("git rm --cached"):
            return ["It does not delete the local file unless you use a different removal command."]
        if normalized.startswith("git commit --amend"):
            return ["It should not be used to rewrite shared history in these local-only scenarios."]
        if normalized.startswith("git commit"):
            return ["It does not include unstaged changes or ignored files."]
        if normalized.startswith("git restore --staged"):
            return ["It does not discard the working-tree file content."]
        if normalized.startswith("git restore"):
            return ["It does not affect unrelated paths."]
        return ["It does not replace careful inspection of the scenario requirements."]

    def _preview_readiness_notes(self, command: str) -> list[str]:
        normalized = " ".join(command.split()).lower()
        if normalized.startswith(("git status", "git log", "git diff", "git show", "git branch", "git remote", "git reflog")):
            return ["Use the output to name what Git sees before you act."]
        if normalized.startswith("git commit"):
            return ["Confirm the exact staged paths and required message before committing."]
        if normalized.startswith("git add"):
            return ["Confirm the target path or hunk before staging."]
        if normalized.startswith("git restore"):
            return ["Separate unstaging from discarding before you run the command."]
        return ["Check the scenario's named values before running the command."]

    def _validate_builds(self):
        builder = RuntimeScenarioBuilder()
        failures = []
        created_variant_ids = []
        try:
            for difficulty in DifficultyInstance.objects.filter(
                scenario__learning_unit__slug="local-repository-foundations"
            ).order_by("scenario__sort_order", "difficulty"):
                fingerprints = set()
                anchors = set()
                candidates = []
                for blueprint in difficulty.generation_blueprints.filter(
                    is_published=True
                ).order_by("sort_order", "id"):
                    candidates.extend(builder._candidates([blueprint]))
                if not candidates:
                    failures.append(
                        f"{difficulty.scenario.slug}/{difficulty.difficulty}: no blueprint cases"
                    )
                    continue
                for index, candidate in enumerate(candidates, start=1):
                    try:
                        variant = builder._build_variant(
                            candidate,
                            user=None,
                            difficulty_instance=difficulty,
                            generation_seed=f"seedcheck{difficulty.id:04d}{index:04d}",
                        )
                        created_variant_ids.append(variant.id)
                        fingerprints.add(candidate.candidate_fingerprint)
                        anchor = (variant.expected_observations or {}).get("answer_anchor")
                        if anchor:
                            anchors.add(json.dumps(anchor, sort_keys=True))
                        self.stdout.write(
                            f"Built {difficulty.scenario.slug}/{difficulty.difficulty}: {variant.slug}"
                        )
                    except ScenarioVariantBuildError as exc:
                        failures.append(
                            f"{difficulty.scenario.slug}/{difficulty.difficulty}: {exc}"
                        )
                if len(candidates) > 1 and len(fingerprints) != len(candidates):
                    failures.append(
                        f"{difficulty.scenario.slug}/{difficulty.difficulty}: duplicate parameter fingerprints"
                    )
                if len(candidates) > 1 and len(anchors) != len(candidates):
                    failures.append(
                        f"{difficulty.scenario.slug}/{difficulty.difficulty}: duplicate or missing answer anchors"
                    )
        finally:
            ScenarioVariant.objects.filter(id__in=created_variant_ids).delete()
        if failures:
            raise CommandError("Variant validation failed:\n" + "\n".join(failures))
        self.stdout.write(
            self.style.SUCCESS(
                "All Module 1 blueprint cases generated valid variants. Validation variants were removed."
            )
        )
