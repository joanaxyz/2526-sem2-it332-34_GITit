from __future__ import annotations

import json
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from common.constants import (
    COMPLETION_EXPANDED_STATE_BASED,
    COMPLETION_STATE_BASED,
    DIFFICULTY_EASY,
    DIFFICULTY_HARD,
    DIFFICULTY_MAX_COUNTED_COMMANDS,
    DIFFICULTY_MEDIUM,
)
from learning.models import LearningUnit, Lesson, OrientationProgress
from scenarios.builders import (
    PLACEHOLDER_RE,
    AuthoredVariantValidator,
    ScenarioVariantBuildError,
    StaticCaseMaterializer,
    StaticTemplateMaterializer,
)
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

DIAG_PATTERNS = [
    "git status",
    "git status -s",
    "git status --short",
    "git status --porcelain",
    "git status -sb",
    "git status --ignored",
    "git log",
    "git log --oneline",
    "git log --oneline --graph --all",
    "git log -n <number>",
    "git log --max-count=<number>",
    "git diff",
    "git diff <path>",
    "git diff --staged",
    "git diff --cached",
    "git diff --staged <path>",
    "git diff --cached <path>",
    "git diff HEAD",
    "git diff --name-only",
    "git diff --staged --name-only",
    "git show",
    "git show <commit>",
    "git show HEAD",
    "git show --name-only",
    "git remote",
    "git remote -v",
    "git branch",
    "git branch -v",
    "git reflog",
    "git check-ignore -v <path>",
    "git ls-files",
]

SESSION_COUNTS = {
    DIFFICULTY_EASY: 3,
    DIFFICULTY_MEDIUM: 2,
    DIFFICULTY_HARD: 2,
}

VALIDATION_ONLY_CASE_FIELDS = {
    "answer_anchor",
    "case_id",
    "duplicate_solution_waiver",
}


def normalize_preview_identity(command: str) -> str:
    return " ".join(str(command).strip().lower().split())



MODULE_ONE_SCENARIO_ANCHORS = [
    (
        1,
        "inspecting-repository-state",
        "Inspecting Repository State",
        "Read repository status, history, diffs, branches, remotes, and objects before acting.",
    ),
    (
        2,
        "initializing-a-local-repository",
        "Initializing Repositories",
        "Create Git metadata in an existing or named project folder.",
    ),
    (
        3,
        "cloning-a-remote-repository",
        "Cloning Remote Repositories",
        "Create a local working copy and verify the origin relationship.",
    ),
    (
        4,
        "staging-and-committing-basic-workflow",
        "Staging and Committing",
        "Prepare intentional changes and save them with a clear message.",
    ),
    (
        5,
        "partial-staging-and-git-add-p",
        "Partial Staging",
        "Stage selected hunks so each commit has one clear purpose.",
    ),
    (
        6,
        "amending-commits",
        "Amending Commits",
        "Repair the latest commit message or contents before sharing it.",
    ),
    (
        7,
        "unstaging-and-discarding-changes",
        "Unstaging and Discarding Changes",
        "Move changes out of the index and safely discard unwanted work.",
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
        # The UI intentionally hides legacy prompt and diagnostic scaffolds
        # because those sections can leak evaluator rules or imply exact commands.
    }
    templates = {
        "init": {
            "story": "{{context}}",
            "required_details": [
                {"label": "Project", "value": "{{project}}"},
                {"label": "Target directory", "value": "{{target_directory}}"},
                {"label": "Initial branch", "value": "{{expected_initial_branch}}"},
                {"label": "Quiet option", "value": "{{quiet_requirement}}"},
                {"label": "Repository status", "value": "{{repository_status}}"},
                {"label": "Expected untracked paths", "value": "{{expected_untracked_paths}}"},
            ],
            **common,
        },
        "diagnostic": {
            "story": "Before changing {{project}}, inspect the repository and report what you observe.",
            "required_details": [
                {"label": "Question", "value": "{{question}}"},
                {"label": "Observation fields", "value": "{{must_identify}}"},
            ],
            "constraints": [
                "Use read-only commands only; the repository state should not change.",
            ],
            **common,
        },
        "clone": {
            "story": "{{context}}",
            "required_details": [
                {"label": "Remote URL", "value": "{{remote_url}}"},
                {"label": "Destination folder", "value": "{{destination_folder}}"},
                {"label": "Branch to check out", "value": "{{selected_branch}}"},
                {"label": "Default remote branch", "value": "{{default_branch}}"},
                {"label": "Clone depth", "value": "{{clone_depth_label}}"},
                {"label": "Remote tip", "value": "{{remote_head}}"},
            ],
            **common,
        },
        "commit": {
            "story": "{{context}}",
            "required_details": [
                {"label": "Target files", "value": "{{target_files}}"},
                {"label": "Files to leave out", "value": "{{excluded_files}}"},
                {"label": "Required commit message text", "value": "{{required_commit_message}}"},
            ],
            **common,
        },
        "gitignore": {
            "story": "{{project}} has local/generated files that should not be saved in project history.",
            "required_details": [
                {"label": "Ignore file", "value": ".gitignore"},
                {"label": "Ignore patterns", "value": "{{gitignore_patterns}}"},
                {"label": "Ignored/generated paths", "value": "{{ignored_paths}}"},
                {
                    "label": "Tracked generated path to remove from history",
                    "value": "{{tracked_generated_path}}",
                },
                {"label": "Required commit message text", "value": "{{required_commit_message}}"},
            ],
            **common,
        },
        "partial": {
            "story": "{{context}}",
            "required_details": [
                {"label": "Target files", "value": "{{target_files}}"},
                {"label": "Hunks to commit", "value": "{{target_hunks}}"},
                {"label": "Hunks to leave in working tree", "value": "{{leftover_hunks}}"},
                {"label": "Other files to leave out", "value": "{{unrelated_files}}"},
                {"label": "Required commit message text", "value": "{{required_commit_message}}"},
            ],
            **common,
        },
        "amend": {
            "story": "{{context}}",
            "required_details": [
                {"label": "Commit to repair", "value": "{{commit_to_repair}}"},
                {"label": "Corrected message", "value": "{{required_commit_message}}"},
                {"label": "Files in repaired commit", "value": "{{target_files}}"},
            ],
            **common,
        },
        "restore": {
            "story": "{{context}}",
            "required_details": [
                {"label": "Keep but unstage", "value": "{{keep_paths}}"},
                {"label": "Discard from working tree", "value": "{{discard_paths}}"},
            ],
            **common,
        },
        "review": {
            "story": "{{context}}",
            "required_details": [
                {"label": "Target files", "value": "{{target_files}}"},
                {"label": "Files/hunks to leave out", "value": "{{excluded_files}}"},
                {"label": "Required commit message text", "value": "{{required_commit_message}}"},
                {"label": "Hunks to commit", "value": "{{target_hunks}}"},
                {"label": "Hunks to leave", "value": "{{leftover_hunks}}"},
                {"label": "Commit to repair", "value": "{{commit_to_repair}}"},
            ],
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
        partial_staging_scenario(),
        amend_scenario(),
        restore_scenario(),
    ]


def diagnostic_scenario() -> dict[str, Any]:
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
        concepts=["status", "history", "diffs", "branches", "remotes", "diagnostic commands"],
        kind=ScenarioSkillFocus.SkillFocusType.CONCEPT_SPECIFIC,
        difficulties={},
    )


def init_scenario() -> dict[str, Any]:
    """Module 1.1: variants map to simulator-supported git init metadata."""
    reinit_state = repo_with_head(
        commits=[commit("c1", "Keep existing notes", {"README.md": "readme-v1"})],
        head="c1",
        working_tree={"notes/today.md": "untracked"},
    )
    init_rule = {
        "repository_initialized": True,
        "head_branch": "{{expected_initial_branch}}",
        "staging_empty": True,
        "rules": [
            {"type": "commit_count_equals", "count": "{{expected_commit_count}}"},
            {
                "type": "operation_metadata_equals",
                "key": "last_init_directory",
                "value": "{{expected_init_directory}}",
            },
            {
                "type": "operation_metadata_equals",
                "key": "last_init_current_directory",
                "value": "{{expected_current_directory}}",
            },
            {
                "type": "operation_metadata_equals",
                "key": "last_init_initial_branch",
                "value": "{{expected_initial_branch}}",
            },
            {
                "type": "operation_metadata_equals",
                "key": "last_init_quiet",
                "value": "{{expected_quiet}}",
            },
            {
                "type": "operation_metadata_equals",
                "key": "last_init_reinitialized",
                "value": "{{expected_reinitialized}}",
            },
        ],
    }
    return {
        "lesson": (
            2,
            "initializing-a-local-repository",
            "Initializing Repositories",
            "Create Git metadata in an existing or named project folder.",
        ),
        "slug": "initialize-local-repository",
        "title": "Initializing Repositories",
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
                "Initialize the current folder with the requested first-branch behavior.",
                "Make the current folder a Git repository, but do not stage files or create a commit.",
                [
                    bp(
                        slug="init-current-folder",
                        kind="init",
                        signature="module1.init.current-folder",
                        subtemplate="current-directory",
                        cases=[
                            {
                                "case_id": "init-easy-current-empty",
                                "context": "Your team just created a project folder but never initialized it as a Git repository. Initialize the current directory so the project can be version-controlled.",
                                "project": "empty-lab",
                                "target_directory": "current folder",
                                "expected_untracked_paths": [],
                                "initial_state": uninitialized_state(),
                                "solution_commands": ["git init"],
                                "expected_init_directory": None,
                                "expected_current_directory": True,
                                "expected_initial_branch": "main",
                                "expected_quiet": False,
                                "quiet_requirement": "No quiet option required.",
                                "expected_reinitialized": False,
                                "repository_status": "This is not an existing Git repository.",
                                "expected_commit_count": 0,
                                "answer_anchor": "initialized the current folder only; zero commits",
                            },
                            {
                                "case_id": "init-easy-trunk-branch",
                                "context": "Your team uses 'trunk' as the main branch name by convention. Initialize the current directory as a Git repository with 'trunk' as the initial branch.",
                                "project": "trunk-lab",
                                "target_directory": "current folder",
                                "expected_untracked_paths": [],
                                "initial_state": uninitialized_state(),
                                "solution_commands": ["git init --initial-branch=trunk"],
                                "expected_init_directory": None,
                                "expected_current_directory": True,
                                "expected_initial_branch": "trunk",
                                "expected_quiet": False,
                                "quiet_requirement": "No quiet option required.",
                                "expected_reinitialized": False,
                                "repository_status": "This is not an existing Git repository.",
                                "expected_commit_count": 0,
                                "answer_anchor": "initialized current folder with trunk as the first branch",
                            },
                            {
                                "case_id": "init-easy-invoice",
                                "context": "A client hired you to build a simple invoice tracker. You need to start the project from scratch with Git version control. Create and initialize a new Git repository named invoice-tracker.",
                                "project": "invoice-tracker",
                                "target_directory": "invoice-tracker",
                                "expected_untracked_paths": [],
                                "initial_state": uninitialized_state(),
                                "solution_commands": ["git init invoice-tracker"],
                                "expected_init_directory": "invoice-tracker",
                                "expected_current_directory": False,
                                "expected_initial_branch": "main",
                                "expected_quiet": False,
                                "quiet_requirement": "No quiet option required.",
                                "expected_reinitialized": False,
                                "repository_status": "This is not an existing Git repository.",
                                "expected_commit_count": 0,
                                "answer_anchor": "initialized invoice-tracker as a new named directory; zero commits",
                            },
                        ],
                        initial_state="{{initial_state}}",
                        target_rule=init_rule,
                        solution="{{solution_commands}}",
                        label="Initialize the current folder",
                        slug_template="init-{{case_id}}",
                    )
                ],
                required_attempts=1,
            ),
            DIFFICULTY_MEDIUM: diff(
                (1, 1),
                "Initialize a named project folder with branch and quiet options when requested.",
                "Initialize the exact target directory and branch mode named in the brief.",
                [
                    bp(
                        slug="init-directory-options",
                        kind="init",
                        signature="module1.init.directory-options",
                        subtemplate="named-directory-options",
                        cases=[
                            {
                                "case_id": "init-med-oss",
                                "context": "You want to start contributing to an open-source project. Your mentor told you to first create a local scaffold directory called oss-contrib where you'll mirror your fork setup. Create and initialize the repo.",
                                "project": "oss-scaffold",
                                "target_directory": "oss-contrib",
                                "expected_untracked_paths": [],
                                "initial_state": uninitialized_state(),
                                "solution_commands": ["git init oss-contrib"],
                                "expected_init_directory": "oss-contrib",
                                "expected_current_directory": False,
                                "expected_initial_branch": "main",
                                "expected_quiet": False,
                                "quiet_requirement": "No quiet option required.",
                                "expected_reinitialized": False,
                                "repository_status": "This is not an existing Git repository.",
                                "expected_commit_count": 0,
                                "answer_anchor": "initialized oss-contrib as a new named directory; zero commits",
                            },
                            {
                                "case_id": "init-medium-docs-site",
                                "context": "Your team needs a dedicated Git repository for the project documentation site. Initialize a new repo named docs-site in your current workspace.",
                                "project": "workspace",
                                "target_directory": "docs-site",
                                "expected_untracked_paths": [],
                                "initial_state": uninitialized_state(),
                                "solution_commands": ["git init docs-site"],
                                "expected_init_directory": "docs-site",
                                "expected_current_directory": False,
                                "expected_initial_branch": "main",
                                "expected_quiet": False,
                                "quiet_requirement": "No quiet option required.",
                                "expected_reinitialized": False,
                                "repository_status": "This is not an existing Git repository.",
                                "expected_commit_count": 0,
                                "answer_anchor": "initialized docs-site only; zero commits",
                            },
                            {
                                "case_id": "init-medium-trunk-api-playground",
                                "context": "You're setting up a sandbox repo for API experiments. The team uses 'trunk' as the default branch. Initialize a new named directory api-playground with trunk as the initial branch.",
                                "project": "workspace",
                                "target_directory": "api-playground",
                                "expected_untracked_paths": [],
                                "initial_state": uninitialized_state(),
                                "solution_commands": ["git init -b trunk api-playground"],
                                "expected_init_directory": "api-playground",
                                "expected_current_directory": False,
                                "expected_initial_branch": "trunk",
                                "expected_quiet": False,
                                "quiet_requirement": "No quiet option required.",
                                "expected_reinitialized": False,
                                "repository_status": "This is not an existing Git repository.",
                                "expected_commit_count": 0,
                                "answer_anchor": "initialized api-playground with trunk as the first branch",
                            },
                            {
                                "case_id": "init-medium-quiet-research-log",
                                "context": "You're initializing a research notes repository called research-log. The CI script expects quiet output so nothing is printed to the console. Initialize it with quiet mode enabled.",
                                "project": "workspace",
                                "target_directory": "research-log",
                                "expected_untracked_paths": [],
                                "initial_state": uninitialized_state(),
                                "solution_commands": [
                                    "git init --quiet --initial-branch=main research-log"
                                ],
                                "expected_init_directory": "research-log",
                                "expected_current_directory": False,
                                "expected_initial_branch": "main",
                                "expected_quiet": True,
                                "quiet_requirement": "Use quiet output.",
                                "expected_reinitialized": False,
                                "repository_status": "This is not an existing Git repository.",
                                "expected_commit_count": 0,
                                "answer_anchor": "initialized research-log quietly with main as the first branch",
                            },
                        ],
                        initial_state="{{initial_state}}",
                        target_rule=init_rule,
                        solution="{{solution_commands}}",
                        label="Initialize {{target_directory}}",
                        slug_template="init-{{case_id}}",
                    )
                ],
            ),
            DIFFICULTY_HARD: diff(
                (1, 1),
                "Combine child-folder targeting with branch, quiet, and reinitialization details.",
                "Initialize only the requested child directory or safely reinitialize the existing repository as directed.",
                [
                    bp(
                        slug="init-combined-options",
                        kind="init",
                        signature="module1.init.combined-options",
                        subtemplate="combined-init-options",
                        cases=[
                            {
                                "case_id": "init-hard-ci",
                                "context": "You've been asked to create a versioned pipeline configuration store. The ops team refers to it as ci-configs. No step-by-step instructions were given — figure out what needs to be done and do it.",
                                "project": "ci-configs",
                                "target_directory": "ci-configs",
                                "expected_untracked_paths": [],
                                "answer_anchor": "initialized ci-configs only; parent workspace untouched",
                                "initial_state": uninitialized_state(
                                    working_tree={
                                        "pipelines/build.yml": "untracked",
                                    }
                                ),
                                "solution_commands": [
                                    "git init ci-configs",
                                ],
                                "expected_init_directory": "ci-configs",
                                "expected_current_directory": False,
                                "expected_initial_branch": "main",
                                "expected_quiet": False,
                                "quiet_requirement": "No quiet option required.",
                                "expected_reinitialized": False,
                                "repository_status": "This is not an existing Git repository.",
                                "expected_commit_count": 0,
                            },
                            {
                                "case_id": "init-hard-research-log",
                                "context": "You're working in a parent workspace with multiple subdirectories. Only the research-log subfolder should become a Git repository — the parent and sibling folders must not be affected. Initialize only that subdirectory, quietly.",
                                "project": "parent-workspace",
                                "target_directory": "research-log",
                                "expected_untracked_paths": ["research-log/README.md"],
                                "answer_anchor": "initialized research-log only; parent and siblings not targeted",
                                "initial_state": uninitialized_state(
                                    working_tree={
                                        "research-log/README.md": "untracked",
                                        "notes/ideas.md": "untracked",
                                        "archive/old.md": "untracked",
                                    }
                                ),
                                "solution_commands": [
                                    "git init -q -b main research-log",
                                ],
                                "expected_init_directory": "research-log",
                                "expected_current_directory": False,
                                "expected_initial_branch": "main",
                                "expected_quiet": True,
                                "quiet_requirement": "Use quiet output.",
                                "expected_reinitialized": False,
                                "repository_status": "This is not an existing Git repository.",
                                "expected_commit_count": 0,
                            },
                            {
                                "case_id": "init-hard-ui-kit",
                                "context": "You're in a design parent workspace. Only the ui-kit subfolder should be version-controlled — sibling folders like brand-assets and experiments must be left alone. Initialize ui-kit quietly with 'trunk' as the branch name.",
                                "project": "design-parent",
                                "target_directory": "ui-kit",
                                "expected_untracked_paths": ["ui-kit/tokens.css"],
                                "answer_anchor": "initialized ui-kit only; sibling folders untouched",
                                "initial_state": uninitialized_state(
                                    working_tree={
                                        "ui-kit/tokens.css": "untracked",
                                        "brand-assets/logo.svg": "untracked",
                                        "experiments/mockup.html": "untracked",
                                    }
                                ),
                                "solution_commands": [
                                    "git init --quiet --initial-branch=trunk ui-kit",
                                ],
                                "expected_init_directory": "ui-kit",
                                "expected_current_directory": False,
                                "expected_initial_branch": "trunk",
                                "expected_quiet": True,
                                "quiet_requirement": "Use quiet output.",
                                "expected_reinitialized": False,
                                "repository_status": "This is not an existing Git repository.",
                                "expected_commit_count": 0,
                            },
                            {
                                "case_id": "init-hard-safe-rerun",
                                "context": "The release-notes directory is already a Git repository with one commit. A teammate ran a script that re-runs git init as a safety check. You need to safely reinitialize without losing the existing history. Run it quietly.",
                                "project": "release-notes",
                                "target_directory": "current folder",
                                "expected_untracked_paths": ["notes/today.md"],
                                "answer_anchor": "re-ran init safely without deleting existing repository state",
                                "initial_state": reinit_state,
                                "solution_commands": ["git init --quiet"],
                                "expected_init_directory": None,
                                "expected_current_directory": True,
                                "expected_initial_branch": "main",
                                "expected_quiet": True,
                                "quiet_requirement": "Use quiet output.",
                                "expected_reinitialized": True,
                                "repository_status": "This is already a Git repository; reinitialize it without losing existing history.",
                                "expected_commit_count": 1,
                            },
                        ],
                        initial_state="{{initial_state}}",
                        target_rule=init_rule,
                        solution="{{solution_commands}}",
                        label="Initialize {{target_directory}} with required options",
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
    solution_workspace_files: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    payload = {
        "slug": slug,
        "slug_template": slug_template,
        "label_template": label,
        "template_key": signature,
        "structure_key": subtemplate,
        "cases": cases,
        "initial_state_template": initial_state,
        "target_rule_template": target_rule,
        "solution_commands_template": solution,
        "student_context_template": student_context_template(kind),
    }
    if solution_workspace_files:
        payload["solution_workspace_files_template"] = solution_workspace_files
    return payload


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
            context="Your team's documentation portal is hosted remotely. Clone it so you can start contributing to the docs locally.",
            solution_command="git clone {{remote_url}}",
        ),
        remote_case(
            "clone-easy-api-lab",
            "api-lab",
            "https://example.test/training/api-lab.git",
            "api-workshop",
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
            "custom folder api-workshop; main/origin-main -> r11; API tree checked out",
            context="You're onboarding at a startup. The backend API is hosted remotely. Your team's convention is to store repos in a folder named api-workshop. Clone it into that folder.",
            solution_command="git clone {{remote_url}} {{destination_folder}}",
        ),
        remote_case(
            "clone-easy-profile-starter",
            "profile-site",
            "https://example.test/training/profile-site.git",
            "profile-site",
            "r13",
            {
                "index.html": "profile-index-v2",
                "styles/site.css": "profile-css-v1",
                "starter-notes.md": "starter-notes-v1",
            },
            [
                {
                    "id": "r12",
                    "message": "Create profile site starter",
                    "parents": [],
                    "tree": {"index.html": "profile-index-v1", "styles/site.css": "profile-css-v1"},
                },
                {
                    "id": "r13",
                    "message": "Prepare starter branch",
                    "parents": ["r12"],
                    "tree": {
                        "index.html": "profile-index-v2",
                        "styles/site.css": "profile-css-v1",
                        "starter-notes.md": "starter-notes-v1",
                    },
                }
            ],
            "specific starter branch; starter/origin-starter -> r13; starter notes checked out",
            context="The profile site repo has a starter branch with template files ready to use. Clone it and check out the starter branch directly instead of main.",
            selected_branch="starter",
            default_head="r12",
            solution_command="git clone -b {{selected_branch}} {{remote_url}}",
        ),
        remote_case(
            "clone-easy-oss-ssh",
            "oss-toolkit",
            "git@github.com:open-dev/oss-toolkit.git",
            "oss-toolkit",
            "r40",
            {"README.md": "oss-readme-v1", "src/toolkit.py": "toolkit-v1"},
            [
                {
                    "id": "r40",
                    "message": "Initial OSS toolkit commit",
                    "parents": [],
                    "tree": {"README.md": "oss-readme-v1", "src/toolkit.py": "toolkit-v1"},
                }
            ],
            "SSH URL; default folder oss-toolkit; main/origin-main -> r40",
            context="You've set up SSH keys and want to clone the OSS project you're contributing to. Clone it using the SSH URL.",
            solution_command="git clone {{remote_url}}",
        ),
        remote_case(
            "clone-easy-corp",
            "audit-logs",
            "https://git.corp.example/it/audit-logs.git",
            "audit-logs-local",
            "r41",
            {"README.md": "audit-readme-v1", "logs/q1.csv": "q1-v1"},
            [
                {
                    "id": "r41",
                    "message": "Create audit logs repo",
                    "parents": [],
                    "tree": {"README.md": "audit-readme-v1", "logs/q1.csv": "q1-v1"},
                }
            ],
            "corporate HTTPS URL; custom folder audit-logs-local; main/origin-main -> r41",
            context="Your company hosts Git internally. Clone the internal audit logs repository into a local folder named audit-logs-local.",
            solution_command="git clone {{remote_url}} {{destination_folder}}",
        ),
    ]
    medium_cases = [
        remote_case(
            "clone-med-feature",
            "backend-api",
            "https://github.com/acme-startup/backend-api.git",
            "backend-api",
            "r50",
            {"README.md": "api-readme-v1", "src/auth.py": "auth-v1"},
            [
                {
                    "id": "r49",
                    "message": "Initial API commit",
                    "parents": [],
                    "tree": {"README.md": "api-readme-v1"},
                },
                {
                    "id": "r50",
                    "message": "Add auth feature skeleton",
                    "parents": ["r49"],
                    "tree": {"README.md": "api-readme-v1", "src/auth.py": "auth-v1"},
                },
            ],
            "branch feature/auth selected at clone; feature/auth -> r50; main -> r49",
            context="The backend team is mid-sprint on a feature/auth branch. You need to clone the repo and start from that branch directly rather than switching after cloning.",
            selected_branch="feature/auth",
            default_head="r49",
            solution_command="git clone -b {{selected_branch}} {{remote_url}}",
        ),
        remote_case(
            "clone-medium-analytics-ssh",
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
            context="You've configured SSH access to the analytics lab repository. Clone it into a custom local folder named analytics-worktree using the SSH URL.",
            solution_command="git clone {{remote_url}} {{destination_folder}}",
        ),
        remote_case(
            "clone-medium-cli-starter-folder",
            "cli-tool",
            "https://example.test/tools/cli-tool.git",
            "cli-starter-lab",
            "r20",
            {
                "README.md": "cli-readme-v2",
                "src/parser.py": "cli-parser-v2",
                "starter.md": "cli-starter-v1",
            },
            [
                {
                    "id": "r19",
                    "message": "Create CLI skeleton",
                    "parents": [],
                    "tree": {"README.md": "cli-readme-v1"},
                },
                {
                    "id": "r20",
                    "message": "Prepare CLI starter branch",
                    "parents": ["r19"],
                    "tree": {
                        "README.md": "cli-readme-v2",
                        "src/parser.py": "cli-parser-v2",
                        "starter.md": "cli-starter-v1",
                    },
                },
            ],
            "specific starter branch in cli-starter-lab; starter/origin-starter -> r20",
            context="A CLI tool repo has a starter branch prepared for onboarding contributors. Clone it into a folder called cli-starter-lab, checking out the starter branch immediately.",
            selected_branch="starter",
            default_head="r19",
            solution_command=(
                "git clone --branch {{selected_branch}} {{remote_url}} {{destination_folder}}"
            ),
        ),
        remote_case(
            "clone-medium-css-kit-shallow",
            "css-kit",
            "https://example.test/frontend/css-kit.git",
            "css-kit",
            "r22",
            {"README.md": "css-readme-v2", "styles/tokens.css": "tokens-v2"},
            [
                {
                    "id": "r21",
                    "message": "Create CSS kit starter",
                    "parents": [],
                    "tree": {"README.md": "css-readme-v1"},
                },
                {
                    "id": "r22",
                    "message": "Add style token kit",
                    "parents": ["r21"],
                    "tree": {"README.md": "css-readme-v2", "styles/tokens.css": "tokens-v2"},
                },
            ],
            "shallow depth 1 clone; main/origin-main -> r22; only tip history visible",
            context="Your CI pipeline needs a lightweight clone of the CSS kit repository for a one-time build. Disk space is limited — use a shallow clone of depth 1 to keep it fast.",
            clone_depth=1,
            solution_command="git clone --depth {{clone_depth}} {{remote_url}}",
        ),
    ]
    hard_cases = [
        remote_case(
            "clone-hard-ssh-shallow",
            "oss-toolkit",
            "git@github.com:open-dev/oss-toolkit.git",
            "oss-review",
            "r60",
            {"README.md": "oss-readme-v2", "src/toolkit.py": "toolkit-v2"},
            [
                {
                    "id": "r59",
                    "message": "Initial OSS commit",
                    "parents": [],
                    "tree": {"README.md": "oss-readme-v1"},
                },
                {
                    "id": "r60",
                    "message": "Improve toolkit utilities",
                    "parents": ["r59"],
                    "tree": {"README.md": "oss-readme-v2", "src/toolkit.py": "toolkit-v2"},
                },
            ],
            "SSH URL; shallow depth 1; custom folder oss-review; main/origin-main -> r60",
            context="You want a minimal clone of the OSS toolkit repository with only the latest commit using SSH, stored in a folder named oss-review. Combine shallow cloning with a custom destination.",
            clone_depth=1,
            solution_command=(
                "git clone --depth {{clone_depth}} {{remote_url}} {{destination_folder}}"
            ),
        ),
        remote_case(
            "clone-hard-mobile-ui-shallow-branch",
            "mobile-ui",
            "https://example.test/frontend/mobile-ui.git",
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
                    "message": "Prepare mobile starter branch",
                    "parents": ["r23"],
                    "tree": {
                        "README.md": "mobile-readme-v2",
                        "screens/home.tsx": "home-v1",
                        "styles/mobile.css": "mobile-css-v1",
                    },
                },
            ],
            "shallow starter branch in mobile-ui-lab; starter/origin-starter -> r31",
            context="You need a lightweight copy of the mobile UI starter branch for a quick review. Clone only the tip of the starter branch into a folder named mobile-ui-lab — no full history needed.",
            selected_branch="starter",
            default_head="r23",
            clone_depth=1,
            solution_command=(
                "git clone --depth {{clone_depth}} -b {{selected_branch}} "
                "{{remote_url}} {{destination_folder}}"
            ),
        ),
        remote_case(
            "clone-hard-lab-notebook-depth-branch",
            "lab-notebook",
            "https://example.test/docs/lab-notebook.git",
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
                    "message": "Prepare review branch",
                    "parents": ["r24"],
                    "tree": {
                        "README.md": "notebook-readme-v2",
                        "entries/day-1.md": "day1-v1",
                        "entries/day-2.md": "day2-v1",
                    },
                },
            ],
            "shallow review branch in notebook-review using --branch; review/origin-review -> r32",
            context="You need to review specific lab notebook entries on the review branch, but don't need the full commit history. Clone only the tip of the review branch into a folder named notebook-review.",
            selected_branch="review",
            default_head="r24",
            clone_depth=1,
            solution_command=(
                "git clone --depth {{clone_depth}} --branch {{selected_branch}} "
                "{{remote_url}} {{destination_folder}}"
            ),
        ),
        remote_case(
            "clone-hard-research-log-ssh",
            "research-log",
            "git@example.test:docs/research-log.git",
            "research-log-lab",
            "r34",
            {
                "README.md": "research-readme-v2",
                "notes/week-1.md": "week1-v1",
                "notes/week-2.md": "week2-v1",
            },
            [
                {
                    "id": "r33",
                    "message": "Create research log",
                    "parents": [],
                    "tree": {"README.md": "research-readme-v1", "notes/week-1.md": "week1-v1"},
                },
                {
                    "id": "r34",
                    "message": "Add second research note",
                    "parents": ["r33"],
                    "tree": {
                        "README.md": "research-readme-v2",
                        "notes/week-1.md": "week1-v1",
                        "notes/week-2.md": "week2-v1",
                    },
                },
            ],
            "SSH URL; custom folder research-log-lab; research tree ending r34",
            context="You've configured SSH access and need a full clone of the research log repository. Clone it via SSH into a local folder named research-log-lab for offline analysis.",
            solution_command="git clone {{remote_url}} {{destination_folder}}",
        ),
    ]
    return scenario_dict(
        lesson=(
            3,
            "cloning-a-remote-repository",
            "Cloning Remote Repositories",
            "Create a local working copy and verify the origin relationship.",
        ),
        slug="clone-remote-repository",
        title="Cloning Remote Repositories",
        focus="git clone",
        summary="Create a local repository from a remote and verify the origin relationship.",
        explanation="Cloning creates a local repository, configures origin, checks out the selected branch, and records remote-tracking information.",
        primary=["git clone"],
        supporting=["git remote -v", "git log --oneline", "git status"],
        concepts=[
            "origin",
            "remote-tracking branch",
            "upstream",
            "branch checkout",
            "shallow clone",
        ],
        difficulties={
            DIFFICULTY_EASY: diff(
                (1, 1),
                "Clone with the requested destination and branch behavior.",
                "Use the provided remote URL and follow the destination or branch details exactly.",
                [
                    clone_bp(
                        "clone-basic-forms",
                        easy_cases,
                        "module1.clone.basic-forms",
                        "clone-basic-forms",
                    )
                ],
            ),
            DIFFICULTY_MEDIUM: diff(
                (1, 1),
                "Clone SSH, branch, and shallow variants.",
                "Use the requested URL syntax, branch, destination folder, and depth exactly.",
                [
                    clone_bp(
                        "clone-branch-and-shallow",
                        medium_cases,
                        "module1.clone.branch-and-shallow",
                        "clone-branch-and-shallow",
                    )
                ],
            ),
            DIFFICULTY_HARD: diff(
                (1, 1),
                "Combine shallow clone, selected branch, and custom destination requirements.",
                "Use the exact clone syntax requested, then end with clean tracking refs.",
                [
                    clone_bp(
                        "clone-combined-forms",
                        hard_cases,
                        "module1.clone.combined-forms",
                        "clone-combined-forms",
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
    *,
    context: str = "",
    selected_branch: str = "main",
    default_branch: str = "main",
    default_head: str | None = None,
    clone_depth: int | None = None,
    solution_command: str = "git clone {{remote_url}}",
) -> dict[str, Any]:
    default_remote_branch = f"origin/{default_branch}"
    selected_remote_branch = f"origin/{selected_branch}"
    branch_targets = {
        default_remote_branch: default_head or head,
        selected_remote_branch: head,
    }
    rendered_solution_command = (
        solution_command.replace("{{remote_url}}", url)
        .replace("{{destination_folder}}", folder)
        .replace("{{selected_branch}}", selected_branch)
        .replace("{{clone_depth}}", str(clone_depth or ""))
    )
    return {
        "case_id": case_id,
        "context": context,
        "project": project,
        "remote_url": url,
        "destination_folder": folder,
        "remote_head": head,
        "remote_tree": tree,
        "remote_commits": commits,
        "remote_branches": branch_targets,
        "selected_branch": selected_branch,
        "selected_remote_branch": selected_remote_branch,
        "default_branch": default_branch,
        "default_remote_branch": default_remote_branch,
        "clone_depth": clone_depth,
        "clone_depth_label": str(clone_depth) if clone_depth else "full history",
        "clone_shallow": clone_depth is not None,
        "solution_command": rendered_solution_command,
        "answer_anchor": answer_anchor,
    }


def clone_bp(slug: str, cases: list[dict[str, Any]], signature: str, subtemplate: str) -> dict[str, Any]:
    return bp(
        slug=slug,
        kind="clone",
        signature=signature,
        subtemplate=subtemplate,
        cases=cases,
        initial_state=uninitialized_state(
            remote_fixtures={
                "branches": "{{remote_branches}}",
                "default_branch": "{{default_remote_branch}}",
                "commits": "{{remote_commits}}",
            }
        ),
        target_rule={
            "repository_initialized": True,
            "head_branch": "{{selected_branch}}",
            "remote_exists": ["origin"],
            "remote_url_matches": {"origin": "{{remote_url}}"},
            "remote_branch_exists": ["{{selected_remote_branch}}"],
            "remote_branch_points_to": {"{{selected_remote_branch}}": "{{remote_head}}"},
            "branch_points_to": {"{{selected_branch}}": "{{remote_head}}"},
            "upstream_tracking": {"{{selected_branch}}": "{{selected_remote_branch}}"},
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
                {
                    "type": "operation_metadata_equals",
                    "key": "last_clone_branch",
                    "value": "{{selected_branch}}",
                },
                {
                    "type": "operation_metadata_equals",
                    "key": "last_clone_depth",
                    "value": "{{clone_depth}}",
                },
                {
                    "type": "operation_metadata_equals",
                    "key": "last_clone_remote_name",
                    "value": "origin",
                },
                {
                    "type": "operation_metadata_equals",
                    "key": "last_clone_default_branch",
                    "value": "{{default_branch}}",
                },
                {
                    "type": "operation_metadata_equals",
                    "key": "last_clone_shallow",
                    "value": "{{clone_shallow}}",
                },
                {"type": "commit_exists", "commit": "{{remote_head}}"},
                {
                    "type": "commit_tree_contains",
                    "commit": "{{remote_head}}",
                    "tree": "{{remote_tree}}",
                },
            ],
        },
        solution=["{{solution_command}}"],
        label="Clone {{project}}",
        slug_template="clone-{{case_id}}",
    )


def commit_scenario(base_tree: dict[str, str]) -> dict[str, Any]:
    cases_easy = [
        commit_case(
            "commit-easy-initial",
            "library-system",
            {
                "README.md": "readme-init-v1",
                "main.py": "main-init-v1",
                "requirements.txt": "reqs-init-v1",
            },
            ["README.md", "main.py", "requirements.txt"],
            [],
            [],
            {
                "README.md": "readme-init-v1",
                "main.py": "main-init-v1",
                "requirements.txt": "reqs-init-v1",
            },
            "Initial commit",
            "commit message Initial commit; three new files staged and committed",
            context="You've just initialized the library-system repo. You have three files ready: README.md, main.py, and requirements.txt. Your group lead says 'do the initial commit.'",
            stage_command="git add .",
        ),
        commit_case(
            "commit-easy-auth-dir",
            "auth-module",
            {
                "src/auth/login.py": "login-v1",
                "src/auth/logout.py": "logout-v1",
            },
            ["src/auth/login.py", "src/auth/logout.py"],
            [],
            [],
            {
                "src/auth/login.py": "login-v1",
                "src/auth/logout.py": "logout-v1",
            },
            "Add auth module",
            "commit message Add auth module; directory staged with two new files",
            context="You added a new src/auth/ directory containing login.py and logout.py. Both are new files. Stage the entire directory and commit it as one focused snapshot.",
            stage_command="git add src/auth/",
        ),
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
            context="You updated the form validation logic in src/form.js. It's the only file changed and it's ready to commit.",
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
            context="You revised the README.md to make the setup instructions clearer. Stage it and commit with the required message.",
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
            context="You tweaked the navbar spacing in styles/navbar.css to fix a visual alignment issue. Stage and commit just that one file.",
            stage_command="git add -A",
        ),
    ]
    cases_medium = [
        commit_case(
            "commit-med-docker",
            "devops-setup",
            {
                "Dockerfile": "dockerfile-v2",
                ".env.example": "env-example-v1",
            },
            ["Dockerfile", ".env.example"],
            [],
            [],
            {"Dockerfile": "dockerfile-v2", ".env.example": "env-example-v1"},
            "Add Docker configuration",
            "commit has Dockerfile and .env.example; working tree clean",
            context="You updated Dockerfile and .env.example as part of a container setup. Stage both files and commit them together as one focused snapshot.",
        ),
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
            context="You redesigned the profile card component. Both the JavaScript logic and the CSS stylesheet are updated and ready to commit together.",
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
            context="You refined the search results view — the JavaScript handler and the HTML template both changed. Commit both files together with the required message.",
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
            context="You updated the export module and rewrote the matching documentation to reflect the new behavior. Commit both the code and the docs as one snapshot.",
        ),
    ]
    cases_hard = [
        commit_case(
            "commit-hard-selective",
            "backend-api",
            {
                "api/handler.py": "handler-bugfix-v2",
                "api/experimental.py": "experimental-wip-v1",
            },
            ["api/handler.py"],
            ["api/experimental.py"],
            ["api/experimental.py"],
            {"api/handler.py": "handler-bugfix-v2"},
            "Fix request handler null check",
            "commit includes handler.py only; experimental.py remains uncommitted",
            context="You've been working on two things: a bug fix in api/handler.py and experimental work in api/experimental.py. Only the bug fix is ready. Stage handler.py and leave the experimental file out.",
        ),
        commit_case(
            "commit-hard-parser",
            "oss-toolkit",
            {
                "src/parser.py": "parser-v2",
                "tests/test_parser.py": "test-parser-v1",
                "debug.log": "debug-draft",
                "scratch.py": "scratch-draft",
            },
            ["src/parser.py", "tests/test_parser.py"],
            ["debug.log", "scratch.py"],
            ["debug.log", "scratch.py"],
            {"src/parser.py": "parser-v2", "tests/test_parser.py": "test-parser-v1"},
            "Add parser module with unit tests",
            "commit includes parser and test; debug.log and scratch.py remain uncommitted",
            context="You're preparing a PR for a new parser feature. The files ready to go are src/parser.py and tests/test_parser.py. A debug.log and scratch.py are also in the tree — keep them out of the commit.",
        ),
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
            context="You updated the profile card behavior in src/profile-card.js. You also have a notes/profile-ideas.md scratch file in the working tree — that's not ready and should stay out of the commit.",
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
            context="You fixed the export validation logic in src/export.py. A scratch/export-test-output.txt file from your testing is also present — leave it uncommitted.",
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
            context="You refined the search ranking display — both src/search.js and templates/search.html are updated and ready. A notes/search-ranking.md scratch file is present but must stay out of this commit.",
        ),
    ]
    return scenario_dict(
        lesson=(
            4,
            "staging-and-committing-basic-workflow",
            "Staging and Committing",
            "Prepare intentional changes and save them with a clear message.",
        ),
        slug="stage-and-commit-basic-workflow",
        title="Staging and Committing",
        focus="git commit",
        summary="Stage intended changes and create a focused commit.",
        explanation="A commit saves the staged snapshot and moves the current branch to the new commit.",
        primary=["git add", "git commit"],
        supporting=[
            "git status",
            "git status --ignored",
            "git diff",
            "git diff --staged",
            "git check-ignore -v <path>",
            "git ls-files",
        ],
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
    context: str = "",
    stage_command: str | None = None,
    commit_command: str | None = None,
) -> dict[str, Any]:
    return {
        "case_id": case_id,
        "context": context,
        "project": project,
        "base_commit": "c1",
        "working_tree": working_tree,
        "target_files": target_files,
        "excluded_files": excluded_files,
        "allowed_working_tree_paths": allowed_working_tree_paths,
        "target_tree_requirements": target_tree_requirements,
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
            ["node_modules/pkg/index.js", ".env"],
            "Add Node ignore rules",
            "commit contains .gitignore patterns; excludes node_modules and .env",
        ),
        ignore_case(
            "ignore-easy-python-cache",
            "python-api",
            ["__pycache__/app.cpython.pyc", ".env"],
            "Add Python ignore rules",
            "commit contains .gitignore patterns; excludes pycache and .env",
        ),
        ignore_case(
            "ignore-easy-web-build",
            "static-site",
            ["dist/site.js", "dist/site.css"],
            "Add web build ignore rules",
            "commit contains .gitignore patterns; excludes dist outputs",
        ),
    ]
    medium_cases = [
        ignore_case(
            "ignore-medium-node-logs-build",
            "node-dashboard",
            ["node_modules/lib.js", "dist/app.js", "logs/debug.log", ".env.local"],
            "Ignore Node dependencies and build output",
            "excludes four ignored artifact paths",
        ),
        ignore_case(
            "ignore-medium-python-venv-cache",
            "data-tools",
            [".venv/pyvenv.cfg", "__pycache__/clean.cpython.pyc", "output/report.csv"],
            "Ignore Python environment artifacts",
            "excludes venv, cache, and output paths",
        ),
        ignore_case(
            "ignore-medium-java-target",
            "java-service",
            ["target/classes/App.class", "target/app.jar", "logs/server.log"],
            "Ignore Java build artifacts",
            "excludes target and log paths",
        ),
    ]
    hard_cases = [
        ignore_case(
            "ignore-hard-untrack-env",
            "backend-service",
            [".env", "logs/server.log"],
            "Stop tracking local environment files",
            ".env removed from committed tree but remains local/ignored; .gitignore committed",
            tracked_generated_path=".env",
            base_tree={**base, ".env": "secret-v1"},
        ),
        ignore_case(
            "ignore-hard-untrack-dist",
            "frontend-bundle",
            ["dist/app.js", "dist/app.css"],
            "Stop tracking build outputs",
            "dist/app.js removed from commit tree; build outputs remain local/ignored",
            tracked_generated_path="dist/app.js",
            base_tree={**base, "dist/app.js": "dist-old"},
        ),
        ignore_case(
            "ignore-hard-untrack-pycache",
            "script-runner",
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
        supporting=[".gitignore", "git status", "git diff", "git diff --staged"],
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
    ignored_paths: list[str],
    message: str,
    answer_anchor: str,
    *,
    tracked_generated_path: str = "none",
    base_tree: dict[str, Any] | None = None,
) -> dict[str, Any]:
    patterns = ignore_patterns_for_paths(ignored_paths)
    content = "\n".join(patterns) + "\n"
    working_tree: dict[str, Any] = {}
    for path in ignored_paths:
        if path == tracked_generated_path:
            continue
        working_tree[path] = {"status": "untracked", "content": f"{path}-local"}
    payload = {
        "case_id": case_id,
        "project": project,
        "gitignore_patterns": patterns,
        "gitignore_content": content,
        "working_tree": working_tree,
        "ignored_paths": ignored_paths,
        "target_files": [".gitignore"],
        "excluded_files": ignored_paths,
        "tracked_generated_path": tracked_generated_path,
        "required_commit_message": message,
        "answer_anchor": answer_anchor,
    }
    if base_tree is not None:
        payload["base_tree"] = base_tree
    return payload


def ignore_patterns_for_paths(paths: list[str]) -> list[str]:
    patterns: list[str] = []
    for path in paths:
        if path.startswith(".env"):
            pattern = ".env*"
        elif "/" in path:
            pattern = f"{path.split('/', 1)[0]}/"
        else:
            pattern = path
        if pattern not in patterns:
            patterns.append(pattern)
    return patterns


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
        {"type": "ignored_paths_present", "paths": "{{ignored_paths}}", "statuses": ["ignored"]},
        {"type": "gitignore_matches_paths", "paths": "{{ignored_paths}}"},
        {
            "type": "commit_tree_contains",
            "branch": "main",
            "tree": {".gitignore": "{{gitignore_content}}"},
        },
        {"type": "commit_tree_excludes", "branch": "main", "paths": "{{excluded_files}}"},
    ]
    solution = ["git add .gitignore", 'git commit -m "{{required_commit_message}}"']
    workspace_files = [{"path": ".gitignore", "content": "{{gitignore_content}}"}]
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
        solution_workspace_files=workspace_files,
        label="Ignore rules for {{project}}",
        slug_template="ignore-{{case_id}}",
    )


def partial_staging_scenario() -> dict[str, Any]:
    cases_easy = [
        partial_case(
            "partial-easy-billing",
            "invoice-tracker",
            ["src/billing.py"],
            ["billing-fix-hunk"],
            ["billing-experimental-hunk"],
            [],
            "Fix billing calculation rounding error",
            "commit contains billing-fix-hunk; working tree keeps billing-experimental-hunk",
            context="You modified billing.py. The file has two changed sections: a rounding fix at the top and some experimental print statements at the bottom. Your client is waiting on the fix only — stage just that hunk.",
        ),
        partial_case(
            "partial-easy-routes",
            "api-service",
            ["src/routes.py"],
            ["routes-handler-hunk"],
            ["routes-experimental-hunk"],
            [],
            "Update API route handlers",
            "commit contains routes-handler-hunk; working tree keeps routes-experimental-hunk",
            context="src/routes.py has two changed sections: updated route handlers (ready to commit) and a commented-out experimental auth middleware section (skip this for now). Use partial staging to commit only the handler update.",
        ),
        partial_case(
            "partial-easy-auth-validation",
            "auth-module",
            ["src/auth.py"],
            ["auth-validation-hunk"],
            ["auth-refactor-hunk"],
            [],
            "Isolate auth validation",
            "commit contains auth-validation-hunk; working tree keeps auth-refactor-hunk",
            context="src/auth.py has two hunks: a validation fix that's ready and a larger refactor that's still in progress. Stage only the validation fix and leave the refactor in the working tree.",
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
            context="src/search.py has two hunks: a ranking algorithm fix (ready) and some cleanup refactoring (not ready). Commit only the ranking fix.",
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
            context="src/export.py has two changed sections: a formatting fix (stage this) and some added logging statements (leave these out for now). Use git add -p to commit only the formatting change.",
        ),
    ]
    cases_medium = [
        partial_case(
            "partial-med-three-hunk",
            "oss-toolkit",
            ["src/parser.py"],
            ["parser-bugfix-hunk"],
            ["parser-refactor-hunk", "parser-experimental-hunk"],
            [],
            "Fix parser bug and refactor token handling",
            "bugfix hunk committed; refactor and experimental hunks remain in working tree",
            context="src/parser.py has three hunks: a bug fix (stage), a refactor (skip — not ready), and an experimental section (skip). Use partial staging to commit only the bug fix.",
        ),
        partial_case(
            "partial-medium-profile-validation",
            "profile-editor",
            ["src/profile.py"],
            ["profile-validation-hunk"],
            ["profile-copy-hunk", "profile-cleanup-hunk"],
            ["notes/profile-todo.md"],
            "Commit profile validation only",
            "validation hunk committed; two hunks and notes remain uncommitted",
            context="src/profile.py has three changed sections: a validation fix (stage), a copy update (skip), and a cleanup block (skip). A notes/profile-todo.md file is also present — leave it out. Stage only the validation fix.",
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
            context="src/payment.py has three changed sections: a rounding fix (stage), added logging (skip), and a comment update (skip). A tmp/payment-scratch.txt file is also in the working tree. Commit only the rounding fix.",
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
            context="src/dashboard.js has three hunks: a filter logic fix (stage), a theme update (skip), and some console.log statements (skip). A notes/dashboard-ideas.md is also present. Stage only the filter change.",
        ),
    ]
    cases_hard = [
        partial_case(
            "partial-hard-terraform",
            "infra-repo",
            ["terraform/main.tf"],
            ["terraform-network-hunk"],
            ["terraform-experimental-hunk"],
            ["terraform/debug.txt"],
            "Update network Terraform configuration",
            "network config hunk committed; experimental hunk and debug file remain",
            context="terraform/main.tf has two hunks: network configuration (stage) and experimental feature flags (skip). A terraform/debug.txt file is also in the workspace. Stage only the network hunk and leave everything else behind.",
        ),
        partial_case(
            "partial-hard-auth-cross-file",
            "auth-module",
            ["src/auth.py", "tests/test_auth.py"],
            ["auth-validation-hunk", "auth-validation-test-hunk"],
            ["auth-refactor-hunk", "auth-test-cleanup-hunk"],
            ["notes/auth-debug.md"],
            "Commit auth validation path",
            "two validation hunks committed across files; refactor/test cleanup and notes remain",
            context="Two files are modified: src/auth.py (validation fix hunk to stage, refactor hunk to skip) and tests/test_auth.py (validation test hunk to stage, test cleanup hunk to skip). A notes/auth-debug.md is also present. Stage only the validation path across both files.",
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
            context="Two files are modified: src/search.py (ranking fix to stage, cleanup to skip) and tests/test_search.py (ranking test to stage, fixture cleanup to skip). A tmp/search-output.txt is also present. Stage only the ranking change across both files.",
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
            context="Two files are modified: src/export.py (formatting fix to stage, logging additions to skip) and tests/test_export.py (formatting test to stage, test cleanup to skip). A notes/export-followup.md is also present. Stage only the formatting path.",
        ),
    ]
    return scenario_dict(
        lesson=(
            5,
            "partial-staging-and-git-add-p",
            "Partial Staging",
            "Stage selected hunks so each commit has one clear purpose.",
        ),
        slug="partial-staging-add-p",
        title="Partial Staging",
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
    *,
    context: str = "",
    review_context: bool = False,
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
    payload = {
        "case_id": case_id,
        "context": context,
        "project": project,
        "target_files": target_files,
        "target_hunks": target_hunks,
        "leftover_hunks": leftover_hunks,
        "target_hunk_map": target_hunk_map,
        "leftover_hunk_map": leftover_hunk_map,
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
    }
    if review_context:
        payload["commit_to_repair"] = "none"
    else:
        payload["unrelated_files"] = unrelated_files
    return payload


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
            "amend-easy-typo",
            "library-system",
            ["main.py"],
            "Initiall commit",
            "Initial commit",
            {},
            "amended tip message corrected to Initial commit; no new commit added",
            context="You committed with the message 'Initiall commit' — a typo. No file content needs to change, just the message. Amend the last commit to fix it.",
        ),
        amend_case(
            "amend-easy-forgot",
            "auth-service",
            ["src/login.py", "src/logout.py"],
            "Add auth module",
            "Add auth module",
            {"src/logout.py": "logout-v1"},
            "amended tip includes logout.py added to the existing auth commit; no extra commit",
            context="You committed login.py but forgot to include logout.py — it belongs in the same commit. Stage logout.py and amend the last commit to include it without changing the message.",
        ),
        amend_case(
            "amend-easy-login-copy-message",
            "login-copy",
            ["src/login.js"],
            "Update text",
            "Clarify login copy",
            {},
            "branch tip is amended commit with message Clarify login copy; no extra commit",
            context="Your last commit message says 'Update text' — too vague. It should be 'Clarify login copy'. No file content needs to change. Amend just the message.",
        ),
        amend_case(
            "amend-easy-readme-message",
            "setup-docs",
            ["README.md"],
            "Update README",
            "Clarify setup requirements",
            {},
            "amended tip message Clarify setup requirements; same tree",
            context="Your last commit message is 'Update README' — not specific enough. The correct message is 'Clarify setup requirements'. Amend the commit message without changing any files.",
        ),
        amend_case(
            "amend-easy-navbar-message",
            "style-polish",
            ["styles/navbar.css"],
            "CSS updates",
            "Adjust navbar spacing",
            {},
            "amended tip message Adjust navbar spacing; same tree",
            context="Your last commit message is 'CSS updates' — too generic. It should be 'Adjust navbar spacing'. No content changes needed — just fix the message.",
        ),
    ]
    medium = [
        amend_case(
            "amend-med-both",
            "oss-toolkit",
            ["src/parser.py", "docs/CHANGELOG.md"],
            "update stuff",
            "Add parser feature and update changelog",
            {"docs/CHANGELOG.md": "changelog-v2"},
            "amended tip has corrected message and changelog added; no extra commit",
            context="Your last commit message was 'update stuff' (too vague) AND you forgot to include docs/CHANGELOG.md. Stage the changelog and fix the message in one amend operation.",
        ),
        amend_case(
            "amend-medium-profile-missing-css",
            "profile-card",
            ["src/profile-card.js", "styles/profile-card.css"],
            "Update profile card layout",
            "Update profile card layout",
            {"styles/profile-card.css": "profile-css-v2"},
            "amended tip includes missing CSS without creating new commit",
            context="You committed profile-card.js but forgot to include styles/profile-card.css — it belongs in the same commit. Stage the missing CSS file and amend without changing the commit message.",
        ),
        amend_case(
            "amend-medium-export-doc",
            "export-flow",
            ["src/export.py", "docs/export.md"],
            "Document export flow update",
            "Document export flow update",
            {"docs/export.md": "export-docs-v2"},
            "amended tip includes export docs",
            context="You committed the export module code but forgot to include docs/export.md. Amend the last commit to add the documentation without changing the message.",
        ),
        amend_case(
            "amend-medium-search-template",
            "search-view",
            ["src/search.js", "templates/search.html"],
            "Refine search results view",
            "Refine search results view",
            {"templates/search.html": "search-template-v2"},
            "amended tip includes search template",
            context="You committed the search JavaScript but forgot to include templates/search.html — it belongs in the same snapshot. Stage the missing template and amend the commit without changing the message.",
        ),
    ]
    hard = [
        amend_case(
            "amend-hard-convention",
            "infra-repo",
            ["terraform/staging.tf"],
            "terraform configs have been updated for staging env",
            "Update Terraform staging environment configuration",
            {},
            "amended tip message corrected from passive verbose form to imperative convention; no extra commit",
            context="Your last commit message is 'terraform configs have been updated for staging env' — passive voice, lowercase, too verbose. Correct it to follow Git imperative convention. No file content changes needed.",
        ),
        amend_case(
            "amend-hard-profile-message-and-layout",
            "profile-card",
            ["src/profile-card.js", "styles/profile-layout.css"],
            "Update profile stuff",
            "Polish profile card layout",
            {"styles/profile-layout.css": "profile-layout-css-v3"},
            "amended tip has corrected message and missing layout CSS; old tip replaced",
            context="Your last commit has two problems: the message 'Update profile stuff' is too vague, and styles/profile-layout.css was left out by mistake. Fix both — correct the message and add the missing file in one amend.",
        ),
        amend_case(
            "amend-hard-auth-message-and-test",
            "auth-module",
            ["src/auth.py", "tests/test_auth.py"],
            "Auth changes",
            "Add auth validation coverage",
            {"tests/test_auth.py": "auth-test-v2"},
            "amended tip has corrected message and test path; no extra child commit",
            context="Your last commit message is 'Auth changes' (too vague) and it's missing tests/test_auth.py. Fix both issues in one amend: correct the message and add the missing test file.",
        ),
        amend_case(
            "amend-hard-export-message-and-doc",
            "export-flow",
            ["src/export.py", "docs/export.md"],
            "Export update",
            "Document export validation behavior",
            {"docs/export.md": "export-docs-v3"},
            "amended tip has corrected message and docs; old tip replaced",
            context="Your last commit message is 'Export update' (too vague) and docs/export.md is missing from the commit. Fix both: add the documentation file and correct the message in a single amend.",
        ),
    ]
    return scenario_dict(
        lesson=(
            6,
            "amending-commits",
            "Amending Commits",
            "Repair the latest commit message or contents before sharing it.",
        ),
        slug="amend-latest-commit",
        title="Amending Commits",
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
    *,
    context: str = "",
    review_context: bool = False,
) -> dict[str, Any]:
    tree_c1 = {"README.md": "readme-v1"}
    committed_files = [path for path in target_files if path not in working_tree]
    tree_c2 = {**tree_c1, **{path: f"{path}-committed-v1" for path in committed_files}}
    payload = {
        "case_id": case_id,
        "context": context,
        "project": project,
        "target_files": target_files,
        "commit_to_repair": "c2",
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
    if review_context:
        payload["excluded_files"] = []
        payload["target_hunks"] = []
        payload["leftover_hunks"] = []
    return payload


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
            "restore-easy-unstage",
            "library-system",
            {"notes.txt": "notes-draft"},
            {},
            ["notes.txt"],
            [],
            "notes.txt moved from staging to working tree; not discarded",
            context="You ran git add . and accidentally staged notes.txt along with your intended files. The commit isn't ready yet. Unstage notes.txt while keeping your working-tree changes.",
        ),
        {
            "case_id": "restore-easy-discard",
            "context": "You made some experimental edits to config.py trying out a new approach that didn't work. Discard all working-tree changes to config.py and get back to the last committed state.",
            "project": "startup-api",
            "keep_paths": [],
            "discard_paths": ["config.py"],
            "staging": {},
            "working_tree": {"config.py": "config-wrong-v2"},
            "solution_commands": ["git restore config.py"],
            "answer_anchor": "working-tree changes to config.py discarded; back to committed state",
        },
        restore_case(
            "restore-easy-unstage-app",
            "cleanup-lab",
            {"src/app.py": "app-change-v2"},
            {},
            ["src/app.py"],
            [],
            "src/app.py moves from staging to working_tree; no commit created",
            context="You staged src/app.py but realize you're not ready to commit it yet. Unstage it so it stays as a working-tree change without being discarded.",
        ),
        restore_case(
            "restore-easy-unstage-guide",
            "docs-lab",
            {"docs/guide.md": "guide-change-v2"},
            {},
            ["docs/guide.md"],
            [],
            "docs/guide.md unstaged and preserved",
            context="You staged docs/guide.md, but you want to revise it more before committing. Unstage it — your edits should remain in the working tree, not be discarded.",
        ),
        restore_case(
            "restore-easy-unstage-css",
            "style-lab",
            {"styles/site.css": "css-change-v2"},
            {},
            ["styles/site.css"],
            [],
            "styles/site.css unstaged and preserved",
            context="You staged styles/site.css but then realized another CSS change needs to be grouped with it. Unstage it for now so you can re-stage everything together later.",
        ),
    ]
    medium = [
        restore_case(
            "restore-med-unstage-discard",
            "oss-toolkit",
            {"experimental.py": "experimental-v1"},
            {"README.md": "readme-wrong-v2"},
            ["experimental.py"],
            ["README.md"],
            "experimental.py unstaged and preserved; README.md working-tree changes discarded",
            context="You staged experimental.py (keep it as a working-tree change, not in the next commit) and also have working-tree edits to README.md that you want to throw away entirely. First unstage experimental.py, then discard the README changes.",
        ),
        restore_case(
            "restore-medium-app-debug",
            "cleanup-lab",
            {"src/app.py": "app-change-v2"},
            {"debug.log": "debug-draft"},
            ["src/app.py"],
            ["debug.log"],
            "app.py preserved as working change; debug.log discarded",
            context="You staged src/app.py but aren't ready to commit it yet, and you also have a debug.log in the working tree that you want to get rid of. Unstage app.py to preserve your work, then discard debug.log.",
        ),
        restore_case(
            "restore-medium-docs-scratch",
            "docs-lab",
            {"docs/guide.md": "guide-change-v2"},
            {"tmp/scratch.txt": "scratch-draft"},
            ["docs/guide.md"],
            ["tmp/scratch.txt"],
            "guide preserved; scratch discarded",
            context="You staged docs/guide.md for a later commit and also have a tmp/scratch.txt that was just temporary notes. Unstage the guide to continue editing it, and discard the scratch file entirely.",
        ),
        restore_case(
            "restore-medium-css-build",
            "style-lab",
            {"styles/site.css": "css-change-v2"},
            {"dist/site.css": "dist-generated"},
            ["styles/site.css"],
            ["dist/site.css"],
            "source CSS preserved; generated dist discarded",
            context="You staged styles/site.css for revision and also have a generated dist/site.css in your working tree from an old build. Unstage the source CSS to keep working on it, and discard the generated dist file.",
        ),
    ]
    hard = [
        restore_case(
            "restore-hard-cleanup",
            "backend-api",
            {
                "debug.log": "debug-draft",
                "scratch/notes.txt": "notes-draft",
            },
            {"api/experimental.py": "experimental-wrong-v1"},
            ["debug.log", "scratch/notes.txt"],
            ["api/experimental.py"],
            "debug.log and notes.txt unstaged; experimental.py working-tree changes discarded",
            context="You have a noisy mixed state: debug.log and scratch/notes.txt are staged (unstage them — don't discard, just move back to working tree), and api/experimental.py has working-tree changes you want to throw away. Clean up without making a commit.",
        ),
        restore_case(
            "restore-hard-mixed-profile",
            "profile-card",
            {"src/profile-card.js": "profile-js-v2", "notes/profile-ideas.md": "notes-draft"},
            {"debug/profile.log": "debug-draft"},
            ["src/profile-card.js"],
            ["debug/profile.log"],
            "all staging cleared; profile-card.js preserved; debug log discarded; no commit",
            context="Two files are staged: src/profile-card.js (keep your edits as a working-tree change) and notes/profile-ideas.md (also keep, just unstage). A debug/profile.log in the working tree should be discarded entirely. Clean up without committing.",
        ),
        restore_case(
            "restore-hard-mixed-export",
            "export-flow",
            {"src/export.py": "export-code-v2", "notes/export-plan.md": "notes-draft"},
            {"tmp/export-output.txt": "generated-output"},
            ["src/export.py"],
            ["tmp/export-output.txt"],
            "export.py preserved; notes unstaged; generated output discarded; no commit",
            context="Two files are staged: src/export.py (keep the edits as a working-tree change) and notes/export-plan.md (also keep, just unstage). A tmp/export-output.txt generated file is in the working tree and should be discarded. No commit needed.",
        ),
        restore_case(
            "restore-hard-mixed-search",
            "search-view",
            {"src/search.js": "search-js-v2", "notes/search.md": "notes-draft"},
            {"debug/search.log": "search-debug"},
            ["src/search.js"],
            ["debug/search.log"],
            "search.js preserved; notes unstaged; debug log discarded; no commit",
            context="Two files are staged: src/search.js (preserve your edits, just unstage) and notes/search.md (also keep, just unstage). A debug/search.log in the working tree should be discarded entirely. Clean up without making a commit.",
        ),
    ]
    return scenario_dict(
        lesson=(
            7,
            "unstaging-and-discarding-changes",
            "Unstaging and Discarding Changes",
            "Move changes out of the index and safely discard unwanted work.",
        ),
        slug="unstage-and-discard-changes",
        title="Unstaging and Discarding Changes",
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
    *,
    context: str = "",
) -> dict[str, Any]:
    commands = [f"git restore --staged {' '.join(initial_staging)}"]
    if discard_paths:
        commands.append(f"git restore {' '.join(discard_paths)}")
    return {
        "case_id": case_id,
        "context": context,
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
            "cap1-easy-staged-with-ignore",
            "auth-service",
            ["src/auth.py", ".gitignore"],
            ["logs/auth.log"],
            "Add auth module",
            "commit contains auth.py + .gitignore; log file excluded",
            context="You added the auth module to the service. Stage src/auth.py and the .gitignore together — the logs/auth.log file is generated and must stay out of the commit.",
        ),
        review_clean_case(
            "cap1-easy-two-source-ignore",
            "data-pipeline",
            ["src/pipeline.py", ".gitignore"],
            ["output/results.csv"],
            "Add data pipeline module",
            "commit contains pipeline.py + .gitignore; output CSV excluded",
            context="You added the data pipeline module. Commit src/pipeline.py and .gitignore together — the output/results.csv is a generated artifact and must not be included.",
        ),
        review_clean_case(
            "review-easy-docs-ignore",
            "docs-portal",
            ["docs/intro.md", ".gitignore"],
            ["dist/site.html"],
            "Prepare docs portal intro",
            "commit contains docs/intro.md + .gitignore; excludes dist/site.html",
            context="You wrote the introductory docs page. Commit docs/intro.md and .gitignore together — dist/site.html is a build artifact and should remain excluded.",
        ),
        review_clean_case(
            "review-easy-profile-ignore",
            "profile-site",
            ["src/profile-card.js", ".gitignore"],
            ["dist/profile-card.js"],
            "Prepare profile card update",
            "commit contains profile-card.js + .gitignore; excludes dist artifact",
            context="You updated the profile card component. Commit src/profile-card.js and .gitignore as one focused snapshot — the dist/profile-card.js build artifact must be left out.",
        ),
        review_clean_case(
            "review-easy-export-ignore",
            "export-flow",
            ["src/export.py", ".gitignore"],
            ["output/export.csv"],
            "Prepare export workflow update",
            "commit contains export.py + .gitignore; excludes output CSV",
            context="You updated the export workflow module. Stage src/export.py and .gitignore for a focused commit — the output/export.csv file is generated output and must stay out.",
        ),
    ]
    medium_cases = [
        review_clean_case(
            "cap1-med-api-with-note",
            "backend-api",
            ["src/api.py", "tests/test_api.py", ".gitignore"],
            ["notes/api-design.md", "dist/api.js"],
            "Add API module with tests",
            "source/test/.gitignore committed; design note remains; dist ignored",
            context="You added the API module with its tests. Commit src/api.py, tests/test_api.py, and .gitignore together. A notes/api-design.md personal note should stay in your working tree — don't commit it. The dist/api.js build artifact is ignored and must stay out.",
            allowed_working_tree_paths=["notes/api-design.md"],
        ),
        review_clean_case(
            "review-medium-profile-with-note",
            "profile-card",
            ["src/profile-card.js", "styles/profile-card.css", ".gitignore"],
            ["notes/profile-ideas.md", "dist/profile-card.js"],
            "Finalize profile card update",
            "commit has two source files + .gitignore; note remains; dist ignored",
            context="You finalized the profile card update. Commit src/profile-card.js, styles/profile-card.css, and .gitignore as one snapshot. A notes/profile-ideas.md personal note can stay in your working tree. The dist/profile-card.js build artifact must stay out.",
            allowed_working_tree_paths=["notes/profile-ideas.md"],
        ),
        review_clean_case(
            "review-medium-search-with-output",
            "search-view",
            ["src/search.js", "templates/search.html", ".gitignore"],
            ["notes/search-ranking.md", "output/search-results.json"],
            "Finalize search results update",
            "source/template committed; note remains; output ignored",
            context="You finalized the search results view. Commit src/search.js, templates/search.html, and .gitignore. Your notes/search-ranking.md notes can stay in the working tree. The output/search-results.json generated file must remain excluded.",
            allowed_working_tree_paths=["notes/search-ranking.md"],
        ),
        review_clean_case(
            "review-medium-export-with-note",
            "export-flow",
            ["src/export.py", "docs/export.md", ".gitignore"],
            ["notes/export-plan.md", "output/export.csv"],
            "Finalize export documentation update",
            "code/docs/.gitignore committed; note remains; output ignored",
            context="You finalized the export module and its documentation. Commit src/export.py, docs/export.md, and .gitignore together. Your notes/export-plan.md personal notes can remain in the working tree. The output/export.csv generated file must stay out.",
            allowed_working_tree_paths=["notes/export-plan.md"],
        ),
    ]
    hard_partial_cases = [
        partial_case(
            "cap1-hard-infra-partial",
            "infra-repo",
            ["terraform/main.tf", "tests/test_infra.py"],
            ["infra-network-hunk", "infra-test-coverage-hunk"],
            ["infra-experimental-hunk", "infra-test-cleanup-hunk"],
            ["notes/infra-plan.md"],
            "Add network infrastructure and test coverage",
            "network and test coverage hunks committed; experimental/cleanup and notes remain",
            context="Two files are modified: terraform/main.tf (network config hunk to stage, experimental hunk to skip) and tests/test_infra.py (coverage test hunk to stage, cleanup hunk to skip). A notes/infra-plan.md is also present. Stage only the production-ready hunks across both files.",
            review_context=True,
        ),
        partial_case(
            "review-hard-auth-partial",
            "auth-module",
            ["src/auth.py", "tests/test_auth.py"],
            ["auth-validation-hunk", "auth-validation-test-hunk"],
            ["auth-refactor-hunk", "auth-test-cleanup-hunk"],
            ["notes/auth-debug.md"],
            "Finalize auth validation change",
            "only validation hunks committed; leftovers and notes remain",
            context="Two files are modified: src/auth.py (validation fix hunk to stage, refactor hunk to skip) and tests/test_auth.py (validation test hunk to stage, test cleanup hunk to skip). A notes/auth-debug.md is also present. Commit only the validation path.",
            review_context=True,
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
            context="Two files are modified: src/search.js (ranking fix hunk to stage, theme update hunk to skip) and tests/test_search.js (ranking test hunk to stage, fixture cleanup hunk to skip). A tmp/search-output.json is also present. Commit only the ranking change.",
            review_context=True,
        ),
    ]
    hard_amend_cases = [
        amend_case(
            "cap1-hard-api-amend",
            "backend-api",
            ["src/api.py", "tests/test_api.py"],
            "WIP api stuff",
            "Add API module with test coverage",
            {"tests/test_api.py": "test-api-v2"},
            "amended tip has corrected message and test file; no extra commit",
            context="Your last commit message is 'WIP api stuff' (not ready for review) and it's missing tests/test_api.py. Fix both: add the test file and correct the message in one amend operation.",
            review_context=True,
        ),
        amend_case(
            "review-hard-export-amend",
            "export-flow",
            ["src/export.py", "docs/export.md"],
            "Export update",
            "Finalize export validation behavior",
            {"docs/export.md": "export-docs-final"},
            "branch tip is amended commit with corrected message and docs; no extra commit",
            context="Your last commit message is 'Export update' (too vague) and it's missing docs/export.md. Amend the commit to add the documentation and correct the message — without creating a new commit.",
            review_context=True,
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
        explanation="The review scenario combines diagnostics, staging, committing, ignore rules, partial staging, restore, or amend within one local workflow task.",
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
    context: str = "",
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
        "context": context,
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
    templates,
    completion_type=COMPLETION_STATE_BASED,
    required_attempts=None,
):
    payload = {
        "policy": policy,
        "narrative": narrative,
        "task": task,
        "templates": templates,
        "completion_type": completion_type,
    }
    if required_attempts is not None:
        payload["required_successful_attempts"] = required_attempts
    return payload


class Command(BaseCommand):
    help = "Seed Module 1 scenario skill focuses, difficulties, policies, and authored variants."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing Module 1 content and sessions before seeding.",
        )
        parser.add_argument(
            "--confirm",
            action="store_true",
            help="Required with --reset to confirm development data deletion.",
        )
        parser.add_argument(
            "--validate-build",
            action="store_true",
            help="Validate every seeded authored practice variant after seeding.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["reset"]:
            self._reset_module_one(confirm=options["confirm"])

        seed_git_command_content_library()

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
        ) in MODULE_ONE_SCENARIO_ANCHORS:
            lesson, _ = Lesson.objects.update_or_create(
                unit=unit,
                slug=lesson_slug,
                defaults={
                    "title": lesson_title,
                    "subtitle": lesson_subtitle,
                    "content_html": self._anchor_html(lesson_title, lesson_subtitle),
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
            if not spec["difficulties"]:
                DifficultyInstance.objects.filter(scenario=scenario).update(is_published=False)
                ScenarioVariant.objects.filter(scenario=scenario).update(is_published=False)
                continue

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
                variants = self._render_authored_variants(
                    scenario=scenario,
                    difficulty_instance=difficulty_instance,
                    dspec=dspec,
                )
                if not variants:
                    raise CommandError(
                        f"{scenario.slug}/{difficulty}: no authored variants were rendered"
                    )
                self._ensure_variant_target_rules(
                    scenario=scenario,
                    difficulty=difficulty,
                    variants=variants,
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

        self.stdout.write(self.style.SUCCESS("Seeded Module 1 authored scenario variants."))

        if options["validate_build"]:
            self._validate_builds()

    def _render_authored_variants(
        self,
        *,
        scenario: ScenarioSkillFocus,
        difficulty_instance: DifficultyInstance,
        dspec: dict[str, Any],
    ) -> list[ScenarioVariant]:
        materializer = StaticCaseMaterializer()
        variants: list[ScenarioVariant] = []
        seen_semantic_keys: set[str] = set()
        seen_slugs: set[str] = set()
        for template in dspec["templates"]:
            cases = template.get("cases", [])
            for index, case in enumerate(cases, start=1):
                try:
                    variant = materializer.materialize_variant(
                        difficulty_instance=difficulty_instance,
                        template=template,
                        case=case,
                        index=index,
                    )
                except (KeyError, ScenarioVariantBuildError) as exc:
                    case_id = case.get("case_id", "unknown")
                    raise CommandError(
                        f"{scenario.slug}/{difficulty_instance.difficulty}/{template['slug']}/{case_id}: "
                        f"could not render authored variant: {exc}"
                    ) from exc
                if variant.semantic_key in seen_semantic_keys:
                    raise CommandError(
                        f"{scenario.slug}/{difficulty_instance.difficulty}: duplicate semantic_key "
                        f"{variant.semantic_key}"
                    )
                if variant.slug in seen_slugs:
                    raise CommandError(
                        f"{scenario.slug}/{difficulty_instance.difficulty}: duplicate variant slug "
                        f"{variant.slug}"
                    )
                seen_semantic_keys.add(variant.semantic_key)
                seen_slugs.add(variant.slug)
                variants.append(variant)
        return variants

    def _validate_seed_specs(self, specs: list[dict[str, Any]]) -> None:
        template_materializer = StaticTemplateMaterializer()
        case_materializer = StaticCaseMaterializer()
        failures: list[str] = []
        for spec in specs:
            rendered_solution_sequences_by_difficulty: dict[str, set[tuple[str, ...]]] = {}
            for difficulty, dspec in spec["difficulties"].items():
                rendered_solutions: dict[str, list[str]] = {}
                rendered_target_rules: dict[str, list[str]] = {}
                rendered_target_states: dict[str, list[str]] = {}
                for template in dspec["templates"]:
                    cases = template.get("cases", [])
                    if not cases:
                        failures.append(
                            f"{spec['slug']}/{difficulty}/{template['slug']}: authored template has no cases"
                        )
                        continue
                    case_ids = [case.get("case_id") for case in cases]
                    if any(not case_id for case_id in case_ids):
                        failures.append(
                            f"{spec['slug']}/{difficulty}/{template['slug']}: every case needs a stable case_id"
                        )
                    if len(set(case_ids)) != len(case_ids):
                        failures.append(
                            f"{spec['slug']}/{difficulty}/{template['slug']}: duplicate case_id"
                        )
                    anchors = [case.get("answer_anchor") for case in cases]
                    if len(set(json.dumps(anchor, sort_keys=True) for anchor in anchors)) != len(
                        anchors
                    ):
                        failures.append(
                            f"{spec['slug']}/{difficulty}/{template['slug']}: duplicate answer_anchor"
                        )
                    placeholders = self._template_placeholders(template)
                    for case in cases:
                        case_id = case.get("case_id", "unknown")
                        available_fields = set(case) | {"index"}
                        missing = sorted(placeholders - available_fields)
                        if missing:
                            failures.append(
                                f"{spec['slug']}/{difficulty}/{template['slug']}/{case_id}: missing case fields {missing}"
                            )
                        unused = sorted(
                            set(case) - placeholders - VALIDATION_ONLY_CASE_FIELDS
                        )
                        if unused:
                            failures.append(
                                f"{spec['slug']}/{difficulty}/{template['slug']}/{case_id}: unused case fields {unused}"
                            )
                        if missing:
                            continue
                        context = {**case, "index": 1}
                        try:
                            rendered_solution = template_materializer.render(
                                template.get("solution_commands_template", []),
                                context,
                            )
                            rendered_workspace_files = template_materializer.render(
                                template.get("solution_workspace_files_template", []),
                                context,
                            )
                            rendered_rule = template_materializer.render(
                                template.get("target_rule_template", {}),
                                context,
                            )
                            if not rendered_rule:
                                raise ScenarioVariantBuildError(
                                    "authored variant has no target_rule"
                                )
                            rendered_initial = case_materializer.simulator.normalize_state(
                                template_materializer.render(
                                    template.get("initial_state_template", {}),
                                    context,
                                )
                            )
                            rendered_target_state = case_materializer._target_state_from_solution(
                                rendered_initial,
                                list(rendered_solution),
                                workspace_files=list(rendered_workspace_files),
                            )
                        except (KeyError, ScenarioVariantBuildError) as exc:
                            failures.append(
                                f"{spec['slug']}/{difficulty}/{template['slug']}/{case_id}: could not render validation target: {exc}"
                            )
                            continue
                        solution_key = json.dumps(rendered_solution, sort_keys=True)
                        rendered_solutions.setdefault(solution_key, []).append(str(case_id))
                        sequence_tuple = tuple(
                            normalize_preview_identity(command)
                            for command in rendered_solution
                            if isinstance(command, str) and command.strip()
                        )
                        if sequence_tuple:
                            rendered_solution_sequences_by_difficulty.setdefault(difficulty, set()).add(sequence_tuple)
                        rule_key = json.dumps(rendered_rule, sort_keys=True)
                        rendered_target_rules.setdefault(rule_key, []).append(str(case_id))
                        state_key = json.dumps(rendered_target_state, sort_keys=True)
                        rendered_target_states.setdefault(state_key, []).append(str(case_id))
                for sequence, case_ids_for_sequence in rendered_solutions.items():
                    if len(case_ids_for_sequence) <= 1:
                        continue
                    waived_cases = [
                        case
                        for template in dspec["templates"]
                        for case in template.get("cases", [])
                        if case.get("case_id") in case_ids_for_sequence
                        and case.get("duplicate_solution_waiver")
                    ]
                    if len(waived_cases) != len(case_ids_for_sequence):
                        failures.append(
                            f"{spec['slug']}/{difficulty}: duplicate solution sequence {sequence} in cases {case_ids_for_sequence}"
                        )
                for rule, case_ids_for_rule in rendered_target_rules.items():
                    if len(case_ids_for_rule) > 1:
                        failures.append(
                            f"{spec['slug']}/{difficulty}: duplicate target rule {rule} in cases {case_ids_for_rule}"
                        )
                for state, case_ids_for_state in rendered_target_states.items():
                    if len(case_ids_for_state) > 1:
                        failures.append(
                            f"{spec['slug']}/{difficulty}: duplicate target state {state} in cases {case_ids_for_state}"
                        )
            sequence_owner: dict[tuple[str, ...], str] = {}
            for difficulty, sequences in rendered_solution_sequences_by_difficulty.items():
                for sequence in sequences:
                    if sequence in sequence_owner and sequence_owner[sequence] != difficulty:
                        failures.append(
                            f"{spec['slug']}: exact same solution sequence reused in {sequence_owner[sequence]} and {difficulty}: {list(sequence)}"
                        )
                    sequence_owner[sequence] = difficulty
        if failures:
            raise CommandError("Module 1 seed validation failed:\n" + "\n".join(failures))

    def _template_placeholders(self, template: dict[str, Any]) -> set[str]:
        placeholders: set[str] = set()
        for key in (
            "slug_template",
            "label_template",
            "structure_key",
            "initial_state_template",
            "target_rule_template",
            "solution_commands_template",
            "solution_workspace_files_template",
            "student_context_template",
        ):
            self._collect_placeholders(placeholders, template.get(key))
        return placeholders

    def _collect_placeholders(self, placeholders: set[str], value: Any) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                self._collect_placeholders(placeholders, key)
                self._collect_placeholders(placeholders, item)
            return
        if isinstance(value, (list, tuple)):
            for item in value:
                self._collect_placeholders(placeholders, item)
            return
        if not isinstance(value, str):
            return
        placeholders.update(match.group(1) for match in PLACEHOLDER_RE.finditer(value))

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
        DifficultyInstance.objects.filter(scenario__learning_unit=unit).delete()
        ScenarioSkillFocus.objects.filter(learning_unit=unit).delete()
        OrientationProgress.objects.filter(lesson__unit=unit).delete()
        unit.lessons.all().delete()
        unit.delete()

    def _anchor_html(self, title: str, subtitle: str) -> str:
        if title == "Inspecting Repository State":
            return f"""
<section class=\"internal-scenario-anchor\">
  <h1>{title}</h1>
  <p>{subtitle}</p>
  <p>Internal scenario anchor for diagnostic command preview ordering. Students start practice from Scenario Skill Focus cards on the Modules page.</p>
</section>
""".strip()
        return f"""
<section class=\"internal-scenario-anchor\">
  <h1>{title}</h1>
  <p>{subtitle}</p>
  <p>Internal scenario anchor for ordering Module 1 Scenario Skill Focus cards. Concept and command prep belongs in the Skill Focus Preview modal before students start an authored practice variant.</p>
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

    def _command_preview_config(self, spec: dict[str, Any]) -> dict[str, Any]:
        commands = self._demo_commands(spec)
        preview_commands = self._preview_commands(spec, fallback_commands=commands)
        demo_state = self._demo_state(spec)

        normalized_commands = [command.strip().lower() for command in commands]
        diagnostic = bool(commands) and all(command in {item.lower() for item in DIAG_PATTERNS} for command in normalized_commands)
        return {
            "schema_version": 2,
            "title": f"{spec['focus']} command preview",
            "intro": spec["explanation"],
            "purpose": "Understand what this skill changes, what it only reports, and what to inspect before entering an authored practice scenario.",
            "focus_label": spec["focus"],
            "command_title": spec["title"],
            "command_refs": self._preview_command_refs(preview_commands),
            "supported_demo_commands": commands,
            "demo_repository_state": demo_state,
            "demo_dag_config": {},
            "diagnostic": diagnostic,
            "counted": not diagnostic,
        }

    def _preview_command_refs(self, commands: list[str]) -> list[dict[str, Any]]:
        refs: list[dict[str, Any]] = []
        seen: set[tuple[str, str, tuple[str, ...]]] = set()
        for command in commands:
            normalized = " ".join(str(command).strip().lower().split())
            if not normalized.startswith("git "):
                continue
            preview_syntax = command_preview_syntax_for_command(command)
            key = command_content_key_for_command(preview_syntax or command)
            include_section_ids = command_preview_section_ids_for_command(preview_syntax or command)
            identity = (key, preview_syntax, tuple(include_section_ids))
            if not key or identity in seen:
                continue
            seen.add(identity)
            refs.append(
                {
                    "id": f"{key}-{len(refs) + 1}",
                    "key": key,
                    "command": preview_syntax or command,
                    "include_section_ids": include_section_ids,
                    "summary": "This command guide is included because this exact syntax appears in the authored practice variants for this skill focus.",
                }
            )
        return refs

    def _preview_commands(
        self,
        spec: dict[str, Any],
        *,
        fallback_commands: list[str],
    ) -> list[str]:
        """Preview only the command syntax introduced by this authored scenario, plus safe diagnostics."""
        authored_commands = self._authored_solution_commands(spec)
        if spec.get("difficulties") and authored_commands:
            commands = [
                *list(spec.get("primary", [])),
                *authored_commands,
                *list(spec.get("supporting", [])),
            ]
        else:
            commands = [*list(spec.get("primary", [])), *list(spec.get("supporting", []))] or fallback_commands

        seen_syntax: set[str] = set()
        unique: list[str] = []
        for command in commands:
            preview_syntax = command_preview_syntax_for_command(command)
            key = normalize_preview_identity(preview_syntax or command)
            if not key or key in seen_syntax:
                continue
            seen_syntax.add(key)
            unique.append(preview_syntax or command)
        return unique

    def _authored_solution_commands(self, spec: dict[str, Any]) -> list[str]:
        renderer = StaticTemplateMaterializer()
        commands: list[str] = []
        for dspec in spec.get("difficulties", {}).values():
            for template in dspec.get("templates", []):
                for index, case in enumerate(template.get("cases", []), start=1):
                    context = {**case, "index": index}
                    rendered = renderer.render(
                        template.get("solution_commands_template", []),
                        context,
                    )
                    for command in rendered or []:
                        if isinstance(command, str) and command.strip():
                            commands.append(command.strip())
        return commands

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
                "git branch -v",
                "git log --oneline --graph --all",
                "git show HEAD",
                "git show --name-only",
                "git reflog",
            ],
            "git init": ["git status", "git init", "git init demo-project", "git init -b main"],
            "git clone": [
                "git clone https://example.test/demo/repository.git demo-repository",
                "git clone https://example.test/demo/repository.git",
                "git clone --depth 1 https://example.test/demo/repository.git demo-repository",
                "git remote -v",
                "git log --oneline",
                "git status",
            ],
            "git commit": [
                "git status",
                "git diff",
                "git add demo.txt",
                "git add .",
                "git add -A",
                "git diff --staged",
                'git commit -m "Demo snapshot"',
                "git log --oneline",
            ],
            ".gitignore": [
                "git status",
                "git status --ignored",
                "git add .gitignore",
                "git check-ignore -v .env",
                "git ls-files",
                "git rm --cached .env",
                'git commit -m "Demo ignore rules"',
            ],
            "git add -p": [
                "git status",
                "git add -p",
                "git add -p demo.txt",
                "git add --patch demo.txt",
                "git diff --staged",
                'git commit -m "Demo selected hunk"',
            ],
            "git commit --amend": [
                "git log --oneline",
                "git status",
                "git add demo.txt",
                'git commit --amend -m "Demo amended snapshot"',
                "git commit --amend",
                "git commit --amend --no-edit",
                "git show",
            ],
            "git restore": [
                "git status",
                "git restore --staged staged.txt",
                "git restore --staged .",
                "git restore --staged staged.txt baseline.txt",
                "git restore demo.txt",
                "git restore .",
                "git restore demo.txt baseline.txt",
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

    def _preview_section_id(self, command: str) -> str:
        return (
            command.strip()
            .lower()
            .replace('"', "")
            .replace(".", "dot")
            .replace(" ", "-")
            .replace("/", "-")
        )

    def _validate_builds(self):
        validator = AuthoredVariantValidator()
        failures = []
        for difficulty in DifficultyInstance.objects.select_related("scenario").filter(
            scenario__learning_unit__slug="local-repository-foundations",
            is_published=True,
        ).order_by("scenario__sort_order", "difficulty"):
            variants = list(difficulty.variants.filter(is_published=True).order_by("id"))
            if not variants:
                failures.append(
                    f"{difficulty.scenario.slug}/{difficulty.difficulty}: no authored variants"
                )
                continue
            semantic_keys = {variant.semantic_key for variant in variants}
            if len(semantic_keys) != len(variants):
                failures.append(
                    f"{difficulty.scenario.slug}/{difficulty.difficulty}: duplicate semantic keys"
                )
            for variant in variants:
                try:
                    validator.validate(
                        variant=variant,
                        difficulty_instance=difficulty,
                        scenario=difficulty.scenario,
                    )
                    self.stdout.write(
                        f"Validated {difficulty.scenario.slug}/{difficulty.difficulty}: {variant.slug}"
                    )
                except ScenarioVariantBuildError as exc:
                    failures.append(
                        f"{difficulty.scenario.slug}/{difficulty.difficulty}/{variant.slug}: {exc}"
                    )
        if failures:
            raise CommandError("Variant validation failed:\n" + "\n".join(failures))
        self.stdout.write(
            self.style.SUCCESS(
                "All Module 1 authored practice variants are valid."
            )
        )

    def _ensure_variant_target_rules(
        self,
        *,
        scenario: ScenarioSkillFocus,
        difficulty: str,
        variants: list[ScenarioVariant],
    ) -> None:
        missing = [variant.slug for variant in variants if not variant.target_rule]
        if missing:
            raise CommandError(
                f"{scenario.slug}/{difficulty}: authored variants missing target_rule: "
                + ", ".join(missing)
            )
