from __future__ import annotations

import json
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
    CommandLog,
    CompletionRecord,
    DifficultyInstance,
    ScenarioSession,
    ScenarioSkillFocus,
    ScenarioVariant,
    StepLog,
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
    "git branch -a",
    "git reflog",
    "git check-ignore -v <path>",
    "git ls-files",
    "git stash list",
    "git fetch --dry-run",
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


MODULE_TWO_SCENARIO_ANCHORS = [
    (
        1,
        "creating-and-switching-branches",
        "Creating and Switching Branches",
        "Isolate work by creating branches from the right commit and moving HEAD to them.",
    ),
    (
        2,
        "branch-naming-and-housekeeping",
        "Branch Naming Conventions",
        "Apply team branch naming conventions correctly and recognize names that violate them.",
    ),
    (
        3,
        "stashing-work-in-progress",
        "Stashing Work in Progress",
        "Temporarily shelve uncommitted changes to switch context and restore work cleanly.",
    ),
    (
        4,
        "pushing-to-a-remote",
        "Pushing to a Remote",
        "Publish local commits to a shared remote repository and set up tracking.",
    ),
    (
        5,
        "fetching-and-pulling",
        "Fetching and Pulling from a Remote",
        "Bring remote changes into the local repository and keep local branches up to date.",
    ),
    (
        6,
        "reconciling-diverged-histories",
        "Reconciling Diverged Local and Remote Histories",
        "Integrate remote commits that blocked your push, then complete the push successfully.",
    ),
    (
        7,
        "fast-forward-vs-three-way-merges",
        "Fast-Forward vs Three-Way Merges",
        "Choose the right merge strategy to produce the history shape the team requires.",
    ),
    (
        8,
        "squash-merging",
        "Squash Merging",
        "Land a feature branch as a single tidy commit on the target branch.",
    ),
    (
        9,
        "deleting-and-recovering-remote-branches",
        "Deleting and Recovering Remote Branches",
        "Manage remote branch lifecycle: remove finished branches and restore accidentally deleted ones.",
    ),
]


def commit(
    commit_id: str, message: str, tree: dict[str, Any], parents: list[str] | None = None
) -> dict[str, Any]:
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
        "partial_hunks": {},
        "operation_metadata": {},
    }
    if extra:
        state.update(extra)
    return state


def student_context_template(kind: str) -> dict[str, Any]:
    templates: dict[str, dict[str, Any]] = {
        "branch-create": {
            "story": (
                "Work is ready to begin on {{project}}. "
                "The team isolates all new work on dedicated branches to keep the main line stable."
            ),
            "required_details": [
                {"label": "Project", "value": "{{project}}"},
                {"label": "New branch", "value": "{{new_branch}}"},
                {"label": "Branch from", "value": "{{source_point}}"},
            ],
        },
        "branch-manage": {
            "story": (
                "{{project}} has accumulated branches over several sprints. "
                "The team keeps the branch list clean after work is integrated."
            ),
            "required_details": [
                {"label": "Project", "value": "{{project}}"},
                {"label": "Action", "value": "{{manage_action}}"},
            ],
        },
        "stash": {
            "story": (
                "Mid-task on {{project}}, an urgent context switch is required. "
                "The in-progress work is not ready to commit."
            ),
            "required_details": [
                {"label": "Project", "value": "{{project}}"},
                {"label": "Current branch", "value": "{{source_branch}}"},
                {"label": "Target branch", "value": "{{target_branch}}"},
            ],
        },
        "push": {
            "story": (
                "Local {{project}} work is complete. "
                "The team needs access to it via the shared remote repository."
            ),
            "required_details": [
                {"label": "Project", "value": "{{project}}"},
                {"label": "Branch to share", "value": "{{branch_name}}"},
                {"label": "Remote", "value": "origin"},
                {"label": "Remote branch", "value": "origin/{{branch_name}}"},
            ],
        },
        "fetch-pull": {
            "story": (
                "{{project}} is a shared repository. "
                "The local copy may be behind the team's latest work on the remote."
            ),
            "required_details": [
                {"label": "Project", "value": "{{project}}"},
                {"label": "Branch", "value": "{{branch_name}}"},
                {"label": "Remote", "value": "origin"},
                {"label": "Remote branch", "value": "origin/{{branch_name}}"},
            ],
        },
        "reconcile": {
            "story": (
                "You tried to push {{project}} changes to origin but the push was rejected. "
                "A teammate has pushed commits to the same branch since your last sync — "
                "you must reconcile the divergence before your push will be accepted."
            ),
            "required_details": [
                {"label": "Project", "value": "{{project}}"},
                {"label": "Branch", "value": "{{branch_name}}"},
                {"label": "Remote", "value": "origin"},
                {"label": "Remote branch", "value": "origin/{{branch_name}}"},
            ],
        },
        "merge-type": {
            "story": (
                "A {{project}} branch is ready to merge. "
                "The team has a stated policy about whether the history should stay linear "
                "or show an explicit merge point."
            ),
            "required_details": [
                {"label": "Project", "value": "{{project}}"},
                {"label": "Source branch", "value": "{{source_branch}}"},
                {"label": "Target branch", "value": "{{target_branch}}"},
                {"label": "History requirement", "value": "{{merge_requirement}}"},
            ],
        },
        "squash-merge": {
            "story": (
                "{{project}} has a completed feature branch with several intermediate commits. "
                "Landing it as a single commit on the main line keeps the history clean."
            ),
            "required_details": [
                {"label": "Project", "value": "{{project}}"},
                {"label": "Feature branch", "value": "{{source_branch}}"},
                {"label": "Landing branch", "value": "{{target_branch}}"},
                {"label": "Required commit message", "value": "{{commit_message}}"},
            ],
        },
        "remote-branch": {
            "story": (
                "{{project}} has remote branches that need lifecycle management. "
                "Some are finished and should be removed; others need recovery."
            ),
            "required_details": [
                {"label": "Project", "value": "{{project}}"},
                {"label": "Branch", "value": "{{branch_name}}"},
                {"label": "Remote", "value": "origin"},
                {"label": "Required outcome", "value": "{{action_required}}"},
            ],
        },
        "branch-naming": {
            "story": (
                "You are working on {{project}}. "
                "The team follows a specific branch naming convention — "
                "branches that do not conform are rejected by the CI pipeline or flagged in code review."
            ),
            "required_details": [
                {"label": "Project", "value": "{{project}}"},
                {"label": "Convention", "value": "{{convention}}"},
                {"label": "Required branch", "value": "{{required_branch}}"},
            ],
        },
    }
    return templates[kind]


def bp(
    *,
    slug: str,
    kind: str,
    signature: str,
    subtemplate: str,
    cases: list[dict[str, Any]],
    initial_state: Any,
    target_rule: dict[str, Any],
    solution: Any,
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


# ── Lesson 2.1: Creating and Switching Branches ───────────────────────────────

def _bc_easy_cases() -> list[dict[str, Any]]:
    """Three Easy branch-create cases: single-commit repo, create at HEAD, distinct naming patterns."""
    entries = [
        ("v21e-auth",  "feature/auth",  "ticketing-app",      "HEAD (latest commit on main)"),
        ("v21e-login", "bugfix/login",  "auth-service",       "HEAD (latest commit on main)"),
        ("v21e-ui",    "experiment/ui", "dashboard-frontend", "HEAD (latest commit on main)"),
    ]
    return [
        {
            "case_id": case_id,
            "new_branch": new_branch,
            "project": project,
            "source_point": source_point,
            "answer_anchor": f"created {new_branch} from HEAD on single-commit main; HEAD on {new_branch}",
        }
        for case_id, new_branch, project, source_point in entries
    ]


def _bc_medium_cases() -> list[dict[str, Any]]:
    """Three Medium branch-create cases: 2-, 3-, and 4-commit histories to vary depth."""
    return [
        {
            "case_id": "v21m-payments",
            "new_branch": "feature/payments",
            "project": "e-commerce",
            "source_point": "HEAD (c2, tip of 2-commit main)",
            "head_commit": "c2",
            "initial_state": repo_with_head(
                commits=[
                    commit("c1", "Bootstrap e-commerce app", {"README.md": "readme-v1"}),
                    commit("c2", "Add product catalog", {"README.md": "readme-v1", "src/catalog.py": "catalog-v1"}, ["c1"]),
                ],
                head="c2",
                branch="main",
            ),
            "answer_anchor": "created feature/payments from 2-commit main (c2); HEAD on feature/payments",
        },
        {
            "case_id": "v21m-notifications",
            "new_branch": "feature/notifications",
            "project": "messaging-app",
            "source_point": "HEAD (c3, tip of 3-commit main)",
            "head_commit": "c3",
            "initial_state": repo_with_head(
                commits=[
                    commit("c1", "Bootstrap messaging service", {"README.md": "readme-v1"}),
                    commit("c2", "Add message queue", {"README.md": "readme-v1", "src/queue.py": "queue-v1"}, ["c1"]),
                    commit("c3", "Add delivery tracking", {"README.md": "readme-v1", "src/queue.py": "queue-v1", "src/tracking.py": "tracking-v1"}, ["c2"]),
                ],
                head="c3",
                branch="main",
            ),
            "answer_anchor": "created feature/notifications from 3-commit main (c3); HEAD on feature/notifications",
        },
        {
            "case_id": "v21m-export",
            "new_branch": "feature/export",
            "project": "report-generator",
            "source_point": "HEAD (c4, tip of 4-commit main)",
            "head_commit": "c4",
            "initial_state": repo_with_head(
                commits=[
                    commit("c1", "Bootstrap report generator", {"README.md": "readme-v1"}),
                    commit("c2", "Add data ingestion", {"README.md": "readme-v1", "src/ingest.py": "ingest-v1"}, ["c1"]),
                    commit("c3", "Add aggregation engine", {"README.md": "readme-v1", "src/ingest.py": "ingest-v1", "src/aggregate.py": "agg-v1"}, ["c2"]),
                    commit("c4", "Add report renderer", {"README.md": "readme-v1", "src/ingest.py": "ingest-v1", "src/aggregate.py": "agg-v1", "src/render.py": "render-v1"}, ["c3"]),
                ],
                head="c4",
                branch="main",
            ),
            "answer_anchor": "created feature/export from 4-commit main (c4); HEAD on feature/export",
        },
    ]


def _bc_hard_cases() -> list[dict[str, Any]]:
    """Three Hard branch-create cases: non-HEAD start-point, detached HEAD rescue, multi-branch context."""
    return [
        # Case 1: Branch from non-HEAD commit using start_point
        {
            "case_id": "v21h-hotfix-c1",
            "new_branch": "hotfix/critical",
            "project": "order-service",
            "source_point": "commit c1 (not the current HEAD c2)",
            "target_commit": "c1",
            "initial_state": repo_with_head(
                commits=[
                    commit("c1", "Release v1.0 snapshot", {"README.md": "readme-v1", "src/orders.py": "orders-v1"}),
                    commit("c2", "Add bulk order support", {"README.md": "readme-v1", "src/orders.py": "orders-v2", "src/bulk.py": "bulk-v1"}, ["c1"]),
                ],
                head="c2",
                branch="main",
            ),
            "solution_commands": ["git switch -c hotfix/critical c1"],
            "answer_anchor": "created hotfix/critical at c1 (not HEAD c2) using switch -c with start-point",
        },
        # Case 2: Detached HEAD — save work by creating branch
        {
            "case_id": "v21h-detach-save",
            "new_branch": "saved-work",
            "project": "experiment-lab",
            "source_point": "the detached HEAD position (c2)",
            "target_commit": "c2",
            "initial_state": repo_with_head(
                commits=[
                    commit("c1", "Initial experiment setup", {"README.md": "readme-v1"}),
                    commit("c2", "Experimental changes at detached HEAD", {"README.md": "readme-v1", "src/experiment.py": "exp-v1"}, ["c1"]),
                    commit("c3", "Latest main progress", {"README.md": "readme-v2", "src/main.py": "main-v1"}, ["c1"]),
                ],
                head="c3",
                branch="main",
                extra={
                    "head": {"type": "detached", "target": "c2"},
                },
            ),
            "solution_commands": ["git switch -c saved-work"],
            "answer_anchor": "created saved-work at detached HEAD (c2) to rescue uncommitted exploration",
        },
        # Case 3: Create feature from a non-main branch (develop branch)
        {
            "case_id": "v21h-from-develop",
            "new_branch": "feature/workspace",
            "project": "ide-platform",
            "source_point": "HEAD of the develop branch (c3, one commit ahead of main at c2)",
            "target_commit": "c3",
            "initial_state": repo_with_head(
                commits=[
                    commit("c1", "Bootstrap IDE platform", {"README.md": "readme-v1"}),
                    commit("c2", "Stable main snapshot", {"README.md": "readme-v1", "src/editor.py": "editor-v1"}, ["c1"]),
                    commit("c3", "Develop: add plugin system", {"README.md": "readme-v1", "src/editor.py": "editor-v1", "src/plugins.py": "plugins-v1"}, ["c2"]),
                ],
                head="c2",
                branch="main",
                extra={
                    "branches": {"main": "c2", "develop": "c3"},
                    "head": {"type": "branch", "name": "develop"},
                },
            ),
            "solution_commands": ["git switch -c feature/workspace"],
            "answer_anchor": "created feature/workspace from develop tip (c3); HEAD already on develop, not main",
        },
    ]


def branch_create_scenario() -> dict[str, Any]:
    easy_state = repo_with_head(
        commits=[
            commit("c1", "Initial project snapshot", {"README.md": "readme-v1", "src/app.py": "app-v1"}),
        ],
        head="c1",
        branch="main",
    )

    easy_bp = bp(
        slug="branch-create-easy",
        kind="branch-create",
        signature="module2.branch-create.easy",
        subtemplate="create-at-head-single",
        cases=_bc_easy_cases(),
        initial_state=easy_state,
        target_rule={
            "skip_required_commands": True,
            "head_branch": "{{new_branch}}",
            "branch_exists": ["{{new_branch}}"],
            "branch_points_to": {"{{new_branch}}": "c1"},
        },
        solution=["git switch -c {{new_branch}}"],
        label="Create {{new_branch}} and switch to it",
        slug_template="branch-create-easy-{{case_id}}",
    )

    medium_bp = bp(
        slug="branch-create-medium",
        kind="branch-create",
        signature="module2.branch-create.medium",
        subtemplate="create-at-head-multi",
        cases=_bc_medium_cases(),
        initial_state="{{initial_state}}",
        target_rule={
            "skip_required_commands": True,
            "head_branch": "{{new_branch}}",
            "branch_exists": ["{{new_branch}}"],
            "branch_points_to": {"{{new_branch}}": "{{head_commit}}"},
        },
        solution=["git switch -c {{new_branch}}"],
        label="Create {{new_branch}} from current HEAD",
        slug_template="branch-create-medium-{{case_id}}",
    )

    hard_bp = bp(
        slug="branch-create-hard",
        kind="branch-create",
        signature="module2.branch-create.hard",
        subtemplate="create-non-head",
        cases=_bc_hard_cases(),
        initial_state="{{initial_state}}",
        target_rule={
            "skip_required_commands": True,
            "rules": [
                {"type": "head_branch_equals", "branch": "{{new_branch}}"},
                {"type": "branch_points_to", "branch": "{{new_branch}}", "commit": "{{target_commit}}"},
            ],
        },
        solution="{{solution_commands}}",
        label="Create {{new_branch}} at {{source_point}}",
        slug_template="branch-create-hard-{{case_id}}",
    )

    return scenario_dict(
        lesson=(
            1,
            "creating-and-switching-branches",
            "Creating and Switching Branches",
            "Isolate work by creating branches from the right commit and moving HEAD to them.",
        ),
        slug="create-and-switch-branch",
        title="Creating and Switching Branches",
        focus="git switch, git branch, git checkout",
        summary="Isolate new work by creating a named branch from the correct commit and making it the active context.",
        explanation=(
            "Branch creation and switching are the foundation of all parallel work. "
            "The key questions are: where should the new branch start, and how do you move HEAD there in one step or two?"
        ),
        primary=["git switch", "git checkout -b"],
        supporting=["git branch", "git log --oneline --graph --all", "git branch -v", "git status"],
        concepts=["branch", "HEAD", "switch", "create-and-switch", "start-point", "detached-HEAD"],
        difficulties={
            DIFFICULTY_EASY: diff(
                (1, 2),
                "Create a branch at the current HEAD and make it your working context.",
                "Your team needs a dedicated line of work separated from main. Set up the branch and move to it.",
                [easy_bp],
            ),
            DIFFICULTY_MEDIUM: diff(
                (1, 2),
                "Create a branch at the current HEAD of a multi-commit repository.",
                "Inspect the history to confirm your starting point, then create the branch and move to it.",
                [medium_bp],
            ),
            DIFFICULTY_HARD: diff(
                (1, 3),
                "Create a branch that starts at a specific commit — not necessarily the current HEAD.",
                "Read the repository history carefully to identify the correct starting point before creating the branch.",
                [hard_bp],
            ),
        },
    )


# ── Lesson 2.2: Branch Naming Conventions ────────────────────────────────────

def _bn_easy_cases() -> list[dict[str, Any]]:
    """Five Easy branch-naming cases: convention + exact required branch name both given in brief."""
    return [
        {
            "case_id": "bn-easy-corp-jira",
            "project": "ticketing-app",
            "convention": "PROJ-{ticket-number}/{kebab-case-description}",
            "required_branch": "PROJ-418/password-reset",
            "answer_anchor": "created PROJ-418/password-reset; HEAD on new branch (Jira convention, exact name given)",
        },
        {
            "case_id": "bn-easy-startup-feat",
            "project": "e-commerce",
            "convention": "feature/<description> or bugfix/<description> or hotfix/<description> or chore/<description>",
            "required_branch": "feature/shopping-cart",
            "answer_anchor": "created feature/shopping-cart; HEAD on new branch (type/description convention)",
        },
        {
            "case_id": "bn-easy-oss-user",
            "project": "oss-toolkit",
            "convention": "<github-username>/<kebab-case-description>",
            "required_branch": "jdelacruz/fix-parser-edge-case",
            "answer_anchor": "created jdelacruz/fix-parser-edge-case; HEAD on new branch (username-prefix convention)",
        },
        {
            "case_id": "bn-easy-cap-initials",
            "project": "library-system",
            "convention": "feature/<member-initials>/<short-description>",
            "required_branch": "feature/jm/database-models",
            "answer_anchor": "created feature/jm/database-models; HEAD on new branch (initials-scoped convention)",
        },
        {
            "case_id": "bn-easy-free-client",
            "project": "client-portal",
            "convention": "client/{ticket-id}-{description}",
            "required_branch": "client/55-contact-form-redesign",
            "answer_anchor": "created client/55-contact-form-redesign; HEAD on new branch (client-ticket convention)",
        },
    ]


def _bn_medium_cases() -> list[dict[str, Any]]:
    """Four Medium branch-naming cases: convention stated + task description given; student constructs slug."""
    return [
        {
            "case_id": "bn-med-corp-notif",
            "project": "ticketing-app",
            "convention": "PROJ-{ticket-number}/{kebab-case-description}",
            "required_branch": "PROJ-512/email-notification",
            "answer_anchor": "created PROJ-512/email-notification; student derived slug from task description",
        },
        {
            "case_id": "bn-med-startup-bugfix",
            "project": "retail-app",
            "convention": "feature/<desc> or bugfix/<desc> or hotfix/<desc> or chore/<desc>",
            "required_branch": "bugfix/login-redirect",
            "answer_anchor": "created bugfix/login-redirect; student chose correct type prefix for a bug fix",
        },
        {
            "case_id": "bn-med-devops-scope",
            "project": "api-gateway",
            "convention": "<type>/<scope>/<description> — type: feat, fix, chore, infra",
            "required_branch": "infra/api-gateway/log-rotation",
            "answer_anchor": "created infra/api-gateway/log-rotation; student applied three-part scoped convention",
        },
        {
            "case_id": "bn-med-oss-infer",
            "project": "oss-toolkit",
            "convention": "inferred from existing branches: fix/<desc> or feat/<desc>",
            "required_branch": "fix/tokenizer-crash",
            "answer_anchor": "created fix/tokenizer-crash; student inferred convention from git branch -a output",
        },
    ]


def _bn_hard_cases() -> list[dict[str, Any]]:
    """Four Hard branch-naming cases: wrong branch already exists; student identifies violation and corrects it."""
    return [
        {
            "case_id": "bn-hard-oss-rename",
            "project": "oss-toolkit",
            "convention": "fix/<kebab-case-description> or feat/<kebab-case-description>",
            "required_branch": "fix/renderer-memory-leak",
            "wrong_branch": "myFix",
            "initial_state": repo_with_head(
                commits=[
                    commit("c1", "Bootstrap OSS project", {"README.md": "v1", "src/renderer.py": "rend-v1"}),
                ],
                head="c1",
                branch="myFix",
                extra={"branches": {"myFix": "c1", "main": "c1"}},
            ),
            "answer_anchor": "deleted myFix (CamelCase + no type prefix), created fix/renderer-memory-leak; HEAD on correct branch",
        },
        {
            "case_id": "bn-hard-corp-rename",
            "project": "ticketing-app",
            "convention": "PROJ-{ticket-number}/{kebab-case-description}",
            "required_branch": "PROJ-301/auth-module-update",
            "wrong_branch": "auth-update",
            "initial_state": repo_with_head(
                commits=[
                    commit("c1", "Bootstrap project", {"README.md": "v1", "src/auth.py": "auth-v1"}),
                ],
                head="c1",
                branch="main",
                extra={"branches": {"main": "c1", "auth-update": "c1"}},
            ),
            "answer_anchor": "deleted auth-update (missing PROJ ticket prefix), created PROJ-301/auth-module-update from main",
        },
        {
            "case_id": "bn-hard-startup-prefix",
            "project": "e-commerce",
            "convention": "feature/<desc> or bugfix/<desc> or hotfix/<desc> or chore/<desc> — no other prefixes",
            "required_branch": "bugfix/cart-total",
            "wrong_branch": "fix/cart-total",
            "initial_state": repo_with_head(
                commits=[
                    commit("c1", "Bootstrap e-commerce app", {"README.md": "v1", "src/cart.py": "cart-v1"}),
                ],
                head="c1",
                branch="main",
                extra={"branches": {"main": "c1", "fix/cart-total": "c1"}},
            ),
            "answer_anchor": "deleted fix/cart-total (invalid prefix), created bugfix/cart-total; HEAD on correct branch",
        },
        {
            "case_id": "bn-hard-qa-camel",
            "project": "qa-test-suite",
            "convention": "test/<kebab-case-description>",
            "required_branch": "test/login-flow",
            "wrong_branch": "test/LoginFlow",
            "initial_state": repo_with_head(
                commits=[
                    commit("c1", "Bootstrap QA suite", {"README.md": "v1", "tests/login.py": "test-v1"}),
                ],
                head="c1",
                branch="main",
                extra={"branches": {"main": "c1", "test/LoginFlow": "c1"}},
            ),
            "answer_anchor": "deleted test/LoginFlow (CamelCase violates kebab-case requirement), created test/login-flow",
        },
    ]


def branch_naming_scenario() -> dict[str, Any]:
    # Easy: single-commit main; student creates the exactly-named branch from HEAD
    easy_state = repo_with_head(
        commits=[
            commit("c1", "Initial project snapshot", {"README.md": "v1", "src/app.py": "app-v1"}),
        ],
        head="c1",
        branch="main",
    )

    easy_bp = bp(
        slug="branch-naming-easy",
        kind="branch-naming",
        signature="module2.branch-naming.easy",
        subtemplate="create-named-branch",
        cases=_bn_easy_cases(),
        initial_state=easy_state,
        target_rule={
            "skip_required_commands": True,
            "head_branch": "{{required_branch}}",
            "branch_exists": ["{{required_branch}}"],
            "branch_points_to": {"{{required_branch}}": "c1"},
        },
        solution=["git switch -c {{required_branch}}"],
        label="Create {{required_branch}} following the team convention",
        slug_template="branch-naming-easy-{{case_id}}",
    )

    # Medium: single-commit main; student constructs the slug from convention + task description
    medium_state = repo_with_head(
        commits=[
            commit("c1", "Initial project snapshot", {"README.md": "v1", "src/app.py": "app-v1"}),
        ],
        head="c1",
        branch="main",
    )

    medium_bp = bp(
        slug="branch-naming-medium",
        kind="branch-naming",
        signature="module2.branch-naming.medium",
        subtemplate="construct-named-branch",
        cases=_bn_medium_cases(),
        initial_state=medium_state,
        target_rule={
            "skip_required_commands": True,
            "head_branch": "{{required_branch}}",
            "branch_exists": ["{{required_branch}}"],
            "branch_points_to": {"{{required_branch}}": "c1"},
        },
        solution=["git switch -c {{required_branch}}"],
        label="Construct and create {{required_branch}} from the convention",
        slug_template="branch-naming-medium-{{case_id}}",
    )

    # Hard: wrong branch already exists; student deletes it and creates the correct one
    hard_bp = bp(
        slug="branch-naming-hard",
        kind="branch-naming",
        signature="module2.branch-naming.hard",
        subtemplate="correct-branch-name-violation",
        cases=_bn_hard_cases(),
        initial_state="{{initial_state}}",
        target_rule={
            "skip_required_commands": True,
            "head_branch": "{{required_branch}}",
            "branch_exists": ["{{required_branch}}"],
            "branch_absent": ["{{wrong_branch}}"],
        },
        solution=["git branch -D {{wrong_branch}}", "git switch -c {{required_branch}}"],
        label="Delete {{wrong_branch}} and create correctly-named {{required_branch}}",
        slug_template="branch-naming-hard-{{case_id}}",
    )

    return scenario_dict(
        lesson=(
            2,
            "branch-naming-and-housekeeping",
            "Branch Naming Conventions",
            "Apply team branch naming conventions correctly and recognize names that violate them.",
        ),
        slug="branch-naming-conventions",
        title="Branch Naming Conventions",
        focus="git switch -c",
        summary=(
            "Different teams use different branch naming conventions. "
            "Creating a branch with the wrong name breaks CI pipelines, confuses reviewers, "
            "and gets flagged in code review. The skill is reading the convention and applying it exactly."
        ),
        explanation=(
            "Branch names are not arbitrary — teams use them to link work to tickets, identify contributors, "
            "and automate CI checks. Common patterns include PROJ-{ticket}/{description}, "
            "type/description (feature/, bugfix/, hotfix/), and username/description for OSS forks. "
            "Kebab-case is the standard: no CamelCase, no underscores, no spaces."
        ),
        primary=["git switch -c"],
        supporting=["git branch", "git branch -v", "git branch -a", "git log --oneline --graph --all", "git status"],
        concepts=["branch-naming", "naming-convention", "kebab-case", "convention-violation", "ci-pipeline"],
        difficulties={
            DIFFICULTY_EASY: diff(
                (1, 2),
                "Create a branch whose exact name is given — apply the convention precisely.",
                "Your team lead has told you both the convention and the required branch name. "
                "Create it exactly as specified — wrong casing, wrong separators, or wrong order will fail.",
                [easy_bp],
            ),
            DIFFICULTY_MEDIUM: diff(
                (1, 3),
                "Construct the correct branch name from the convention and task description.",
                "You know the convention and the task. Derive the branch name yourself — "
                "there is only one correct slug. Abbreviations, wrong casing, and wrong type prefixes all fail.",
                [medium_bp],
            ),
            DIFFICULTY_HARD: diff(
                (2, 4),
                "Identify a branch name that violates the convention and correct it.",
                "A branch already exists with the wrong name. Figure out what the violation is, "
                "delete the non-compliant branch, and create a correctly-named replacement.",
                [hard_bp],
            ),
        },
    )


# ── Lesson 2.3: Stashing Work in Progress ────────────────────────────────────

def _stash_easy_cases() -> list[dict[str, Any]]:
    """Three Easy stash cases: dirty feature branch, stash and switch to a clean branch."""
    entries = [
        ("v23e-auth",    "feature/auth",    "main",        "ticketing-app",      "src/auth.py",   "auth-wip"),
        ("v23e-notify",  "feature/notify",  "develop",     "messaging-service",  "src/notify.py", "notify-wip"),
        ("v23e-cache",   "feature/cache",   "release/v2",  "data-store",         "src/cache.py",  "cache-wip"),
    ]
    return [
        {
            "case_id": case_id,
            "source_branch": source_branch,
            "target_branch": target_branch,
            "project": project,
            "initial_state": repo_with_head(
                commits=[commit("c1", f"Initial {project} snapshot", {"README.md": "v1"})],
                head="c1",
                branch=source_branch,
                working_tree={stash_path: wip_content},
                extra={"branches": {source_branch: "c1", target_branch: "c1"}},
            ),
            "answer_anchor": f"stashed {stash_path} from {source_branch}, switched to {target_branch}",
        }
        for case_id, source_branch, target_branch, project, stash_path, wip_content in entries
    ]


def _stash_medium_cases() -> list[dict[str, Any]]:
    """Three Medium stash cases: stash, switch to target, switch back, pop to restore work."""
    return [
        {
            "case_id": "v23m-to-main",
            "source_branch": "feature/payments",
            "target_branch": "main",
            "project": "e-commerce",
            "stash_path": "src/payments.py",
            "initial_state": repo_with_head(
                commits=[
                    commit("c1", "Payment feature in progress", {"README.md": "v1"}),
                    commit("c2", "Main moves forward", {"README.md": "v1", "src/app.py": "app-v1"}, ["c1"]),
                ],
                head="c1",
                branch="feature/payments",
                working_tree={"src/payments.py": "pay-wip"},
                extra={"branches": {"feature/payments": "c1", "main": "c2"}},
            ),
            "answer_anchor": "stashed payments work, checked main, switched back, popped stash",
        },
        {
            "case_id": "v23m-to-hotfix",
            "source_branch": "feature/orders",
            "target_branch": "hotfix/fix-tax",
            "project": "retail-app",
            "stash_path": "src/orders.py",
            "initial_state": repo_with_head(
                commits=[
                    commit("c1", "Orders feature base", {"README.md": "v1"}),
                    commit("c2", "Hotfix branch tip", {"README.md": "v1", "src/tax.py": "tax-fix"}, ["c1"]),
                ],
                head="c1",
                branch="feature/orders",
                working_tree={"src/orders.py": "ord-wip"},
                extra={"branches": {"feature/orders": "c1", "hotfix/fix-tax": "c2"}},
            ),
            "answer_anchor": "stashed orders work, checked hotfix, switched back, popped stash",
        },
        {
            "case_id": "v23m-to-release",
            "source_branch": "feature/analytics",
            "target_branch": "release/v2",
            "project": "analytics-hub",
            "stash_path": "src/analytics.py",
            "initial_state": repo_with_head(
                commits=[
                    commit("c1", "Analytics feature base", {"README.md": "v1"}),
                    commit("c2", "Release v2 preparation", {"README.md": "v1", "src/release.py": "rel-v2"}, ["c1"]),
                ],
                head="c1",
                branch="feature/analytics",
                working_tree={"src/analytics.py": "ana-wip"},
                extra={"branches": {"feature/analytics": "c1", "release/v2": "c2"}},
            ),
            "answer_anchor": "stashed analytics work, checked release branch, switched back, popped stash",
        },
    ]


def _stash_hard_cases() -> list[dict[str, Any]]:
    """Three Hard stash cases: stash, switch, switch back, DROP (discard — work is cancelled)."""
    return [
        {
            "case_id": "v23h-dropped-auth",
            "source_branch": "feature/auth-rework",
            "target_branch": "main",
            "project": "identity-service",
            "initial_state": repo_with_head(
                commits=[
                    commit("c1", "Auth rework in progress", {"README.md": "v1"}),
                    commit("c2", "Main moves forward", {"README.md": "v1", "src/app.py": "app-v1"}, ["c1"]),
                ],
                head="c1",
                branch="feature/auth-rework",
                working_tree={"src/auth.py": "auth-wip"},
                extra={"branches": {"feature/auth-rework": "c1", "main": "c2"}},
            ),
            "answer_anchor": "stashed auth work, checked main, returned to feature, dropped stash (work cancelled)",
        },
        {
            "case_id": "v23h-dropped-api",
            "source_branch": "feature/api-v2",
            "target_branch": "hotfix/urgent",
            "project": "api-gateway",
            "initial_state": repo_with_head(
                commits=[
                    commit("c1", "API v2 prototype started", {"README.md": "v1"}),
                    commit("c2", "Hotfix committed", {"README.md": "v1", "src/fix.py": "fix-v1"}, ["c1"]),
                ],
                head="c1",
                branch="feature/api-v2",
                working_tree={"src/api_v2.py": "api-wip"},
                extra={"branches": {"feature/api-v2": "c1", "hotfix/urgent": "c2"}},
            ),
            "answer_anchor": "stashed api work, checked hotfix, returned to feature, dropped stash (work cancelled)",
        },
        {
            "case_id": "v23h-dropped-refactor",
            "source_branch": "feature/refactor",
            "target_branch": "release/v1",
            "project": "payment-engine",
            "initial_state": repo_with_head(
                commits=[
                    commit("c1", "Refactor started", {"README.md": "v1"}),
                    commit("c2", "Release v1 stable", {"README.md": "v1", "src/app.py": "app-v1"}, ["c1"]),
                ],
                head="c1",
                branch="feature/refactor",
                working_tree={"src/core.py": "core-wip"},
                extra={"branches": {"feature/refactor": "c1", "release/v1": "c2"}},
            ),
            "answer_anchor": "stashed refactor work, checked release/v1, returned to feature, dropped stash (work cancelled)",
        },
    ]


def stash_scenario() -> dict[str, Any]:
    easy_bp = bp(
        slug="stash-save-easy",
        kind="stash",
        signature="module2.stash.easy",
        subtemplate="stash-and-switch",
        cases=_stash_easy_cases(),
        initial_state="{{initial_state}}",
        target_rule={
            "skip_required_commands": True,
            "working_tree_clean": True,
            "head_branch": "{{target_branch}}",
        },
        solution=["git stash", "git switch {{target_branch}}"],
        label="Stash work on {{source_branch}} and switch to {{target_branch}}",
        slug_template="stash-save-easy-{{case_id}}",
    )

    medium_bp = bp(
        slug="stash-save-medium",
        kind="stash",
        signature="module2.stash.medium",
        subtemplate="stash-switch-back-pop",
        cases=_stash_medium_cases(),
        initial_state="{{initial_state}}",
        target_rule={
            "skip_required_commands": True,
            "stash_stack_empty": True,
            "head_branch": "{{source_branch}}",
            "working_tree_contains": ["{{stash_path}}"],
        },
        solution=["git stash", "git switch {{target_branch}}", "git switch {{source_branch}}", "git stash pop"],
        label="Stash, check {{target_branch}}, return to {{source_branch}} and restore",
        slug_template="stash-save-medium-{{case_id}}",
    )

    hard_bp = bp(
        slug="stash-save-hard",
        kind="stash",
        signature="module2.stash.hard",
        subtemplate="stash-switch-back-drop",
        cases=_stash_hard_cases(),
        initial_state="{{initial_state}}",
        target_rule={
            "skip_required_commands": True,
            "stash_stack_empty": True,
            "head_branch": "{{source_branch}}",
            "working_tree_clean": True,
        },
        solution=["git stash", "git switch {{target_branch}}", "git switch {{source_branch}}", "git stash drop"],
        label="Stash, check {{target_branch}}, return to {{source_branch}} and discard stash",
        slug_template="stash-save-hard-{{case_id}}",
    )

    return scenario_dict(
        lesson=(
            3,
            "stashing-work-in-progress",
            "Stashing Work in Progress",
            "Temporarily shelve uncommitted changes to switch context and restore work cleanly.",
        ),
        slug="stash-and-restore-work",
        title="Stashing Work in Progress",
        focus="git stash, git stash pop",
        summary="Save uncommitted changes to the stash stack so you can switch context cleanly, then restore or discard them when ready.",
        explanation=(
            "Stash is a temporary shelf for work that isn't ready to commit. "
            "The key distinction: pop restores your work and removes it from the stash, "
            "while drop discards the stash entry without restoring anything."
        ),
        primary=["git stash", "git stash pop"],
        supporting=["git stash apply", "git stash drop", "git switch", "git branch", "git status"],
        concepts=["stash", "context-switch", "working-tree", "stash-pop", "stash-drop"],
        difficulties={
            DIFFICULTY_EASY: diff(
                (2, 3),
                "Shelve your in-progress work and switch to another branch.",
                "You have uncommitted changes and need to move to a different branch. Save your work first.",
                [easy_bp],
            ),
            DIFFICULTY_MEDIUM: diff(
                (4, 6),
                "Stash your work, check another branch, then return and restore.",
                "An urgent context switch requires you to leave your feature branch temporarily. Preserve your work, check the other branch, then come back and pick up where you left off.",
                [medium_bp],
            ),
            DIFFICULTY_HARD: diff(
                (4, 6),
                "Stash your work, inspect another branch, then discard the stashed changes.",
                "After stashing your work and checking another branch, you learn the task has been cancelled. Return to your feature branch and clean up the stash.",
                [hard_bp],
            ),
        },
    )


# ── Lesson 2.4: Pushing to a Remote ──────────────────────────────────────────

def _push_easy_cases() -> list[dict[str, Any]]:
    """Three Easy push cases: first-time push of a local branch to origin."""
    entries = [
        ("v24e-auth",    "feature/auth",    "ticketing-app",      "src/auth.py",    "feat-auth-v1"),
        ("v24e-orders",  "feature/orders",  "e-commerce",         "src/orders.py",  "feat-orders-v1"),
        ("v24e-parser",  "feature/parser",  "data-pipeline",      "src/parser.py",  "feat-parser-v1"),
    ]
    return [
        {
            "case_id": case_id,
            "branch_name": branch_name,
            "project": project,
            "initial_state": repo_with_head(
                commits=[
                    commit("c1", "Bootstrap project", {"README.md": "v1"}),
                    commit("c2", f"Implement feature", {"README.md": "v1", src_path: src_content}, ["c1"]),
                ],
                head="c2",
                branch=branch_name,
                remotes={"origin": f"https://github.com/team/{project}.git"},
                extra={"branches": {branch_name: "c2", "main": "c1"}},
            ),
            "answer_anchor": f"pushed {branch_name} to origin for the first time",
        }
        for case_id, branch_name, project, src_path, src_content in entries
    ]


def _push_medium_cases() -> list[dict[str, Any]]:
    """Three Medium push cases: push and set upstream tracking with -u."""
    entries = [
        ("v24m-auth",    "feature/auth",    "ticketing-app",   "src/auth.py",    "feat-auth-v1"),
        ("v24m-orders",  "feature/orders",  "e-commerce",      "src/orders.py",  "feat-orders-v1"),
        ("v24m-parser",  "feature/parser",  "data-pipeline",   "src/parser.py",  "feat-parser-v1"),
    ]
    return [
        {
            "case_id": case_id,
            "branch_name": branch_name,
            "project": project,
            "initial_state": repo_with_head(
                commits=[
                    commit("c1", "Bootstrap project", {"README.md": "v1"}),
                    commit("c2", "Implement feature", {"README.md": "v1", src_path: src_content}, ["c1"]),
                ],
                head="c2",
                branch=branch_name,
                remotes={"origin": f"https://github.com/team/{project}.git"},
                extra={"branches": {branch_name: "c2", "main": "c1"}},
            ),
            "answer_anchor": f"pushed {branch_name} to origin with -u, upstream tracking set",
        }
        for case_id, branch_name, project, src_path, src_content in entries
    ]


def _push_hard_cases() -> list[dict[str, Any]]:
    """Three Hard push cases: diverged remote (post-rebase) requires --force-with-lease."""
    entries = [
        ("v24h-auth",    "feature/auth",    "ticketing-app",   "src/auth.py"),
        ("v24h-orders",  "feature/orders",  "e-commerce",      "src/orders.py"),
        ("v24h-parser",  "feature/parser",  "data-pipeline",   "src/parser.py"),
    ]
    return [
        {
            "case_id": case_id,
            "branch_name": branch_name,
            "project": project,
            "initial_state": repo_with_head(
                commits=[
                    commit("c1", "Common ancestor", {"README.md": "v1"}),
                    commit("c2", "Original feature commit (remote still here)", {"README.md": "v1", src_path: "old-v1"}, ["c1"]),
                    commit("c3", "Rebased feature commit (local, diverged from remote)", {"README.md": "v1", src_path: "new-v1"}, ["c1"]),
                ],
                head="c3",
                branch=branch_name,
                remotes={"origin": f"https://github.com/team/{project}.git"},
                remote_branches={f"origin/{branch_name}": "c2"},
                upstream_tracking={branch_name: f"origin/{branch_name}"},
                extra={"branches": {branch_name: "c3", "main": "c1"}},
            ),
            "answer_anchor": f"force-pushed {branch_name} after rebase rewrote history (remote diverged at c2)",
        }
        for case_id, branch_name, project, src_path in entries
    ]


def push_scenario() -> dict[str, Any]:
    easy_bp = bp(
        slug="push-first-easy",
        kind="push",
        signature="module2.push.easy",
        subtemplate="first-push-no-tracking",
        cases=_push_easy_cases(),
        initial_state="{{initial_state}}",
        target_rule={
            "skip_required_commands": True,
            "remote_branch_matches_local": {"origin/{{branch_name}}": "{{branch_name}}"},
        },
        solution=["git push origin {{branch_name}}"],
        label="Push {{branch_name}} to origin for the first time",
        slug_template="push-first-easy-{{case_id}}",
    )

    medium_bp = bp(
        slug="push-tracking-medium",
        kind="push",
        signature="module2.push.medium",
        subtemplate="push-with-upstream",
        cases=_push_medium_cases(),
        initial_state="{{initial_state}}",
        target_rule={
            "skip_required_commands": True,
            "remote_branch_matches_local": {"origin/{{branch_name}}": "{{branch_name}}"},
            "upstream_tracking_set": ["{{branch_name}}"],
        },
        solution=["git push -u origin {{branch_name}}"],
        label="Push {{branch_name}} and set upstream tracking",
        slug_template="push-tracking-medium-{{case_id}}",
    )

    hard_bp = bp(
        slug="push-force-hard",
        kind="push",
        signature="module2.push.hard",
        subtemplate="force-push-diverged",
        cases=_push_hard_cases(),
        initial_state="{{initial_state}}",
        target_rule={
            "skip_required_commands": True,
            "remote_branch_matches_local": {"origin/{{branch_name}}": "{{branch_name}}"},
        },
        solution=["git push --force-with-lease origin {{branch_name}}"],
        label="Force-push rebased {{branch_name}} safely",
        slug_template="push-force-hard-{{case_id}}",
    )

    return scenario_dict(
        lesson=(
            4,
            "pushing-to-a-remote",
            "Pushing to a Remote",
            "Publish local commits to a shared remote repository and set up tracking.",
        ),
        slug="push-branch-to-remote",
        title="Pushing to a Remote",
        focus="git push",
        summary="Share local commits with the team by pushing the branch to a remote, optionally configuring upstream tracking.",
        explanation=(
            "Pushing publishes local commits to a shared remote so others can access them. "
            "The -u flag sets up upstream tracking, enabling future git push and git pull without specifying remote and branch. "
            "After a rebase that rewrites history, a normal push is rejected — --force-with-lease overrides safely."
        ),
        primary=["git push"],
        supporting=["git remote", "git remote -v", "git branch -v", "git log --oneline --graph --all", "git status"],
        concepts=["push", "remote", "upstream-tracking", "force-push", "non-fast-forward"],
        difficulties={
            DIFFICULTY_EASY: diff(
                (1, 2),
                "Push a new local branch to origin for the first time.",
                "Your feature work is ready to share. Publish the branch to the remote so teammates can access it.",
                [easy_bp],
            ),
            DIFFICULTY_MEDIUM: diff(
                (1, 2),
                "Push and configure upstream tracking so future pushes and pulls work without arguments.",
                "Push the branch and link it to its remote counterpart so you can sync with just git push or git pull.",
                [medium_bp],
            ),
            DIFFICULTY_HARD: diff(
                (1, 3),
                "Publish a rebased branch whose history diverges from the remote.",
                "After rebasing, a normal push is rejected because the remote history no longer matches. Use the safe force-push option.",
                [hard_bp],
            ),
        },
    )


# ── Lesson 2.5: Fetching and Pulling ─────────────────────────────────────────

def _fetch_pull_easy_cases() -> list[dict[str, Any]]:
    """Three Easy cases: fetch to update remote tracking refs (no local change)."""
    entries = [
        ("v25e-main",    "main",         "ticketing-app",  "src/feature.py"),
        ("v25e-feature", "feature/auth", "auth-service",   "src/auth.py"),
        ("v25e-develop", "develop",      "api-gateway",    "src/api.py"),
    ]
    return [
        {
            "case_id": case_id,
            "branch_name": branch_name,
            "project": project,
            "duplicate_solution_waiver": True,
            "initial_state": repo_with_head(
                commits=[
                    commit("c1", "Baseline snapshot", {"README.md": "v1"}),
                    commit("c2", "New remote work not yet fetched", {"README.md": "v1", src_path: "remote-v1"}, ["c1"]),
                ],
                head="c1",
                branch=branch_name,
                remotes={"origin": f"https://github.com/team/{project}.git"},
                remote_branches={f"origin/{branch_name}": "c1"},
                extra={
                    "branches": {branch_name: "c1"},
                    "remote_updates": {f"origin/{branch_name}": "c2"},
                },
            ),
            "answer_anchor": f"fetched origin, remote_branches[origin/{branch_name}] updated to c2",
        }
        for case_id, branch_name, project, src_path in entries
    ]


def _fetch_pull_medium_cases() -> list[dict[str, Any]]:
    """Three Medium cases: pull (fast-forward merge) to integrate remote commits into local."""
    entries = [
        ("v25m-main",    "main",         "ticketing-app",  "src/feature.py"),
        ("v25m-feature", "feature/auth", "auth-service",   "src/auth.py"),
        ("v25m-develop", "develop",      "api-gateway",    "src/api.py"),
    ]
    return [
        {
            "case_id": case_id,
            "branch_name": branch_name,
            "project": project,
            "initial_state": repo_with_head(
                commits=[
                    commit("c1", "Baseline snapshot", {"README.md": "v1"}),
                    commit("c2", "Teammate committed to remote", {"README.md": "v1", src_path: "remote-v1"}, ["c1"]),
                ],
                head="c1",
                branch=branch_name,
                remotes={"origin": f"https://github.com/team/{project}.git"},
                remote_branches={f"origin/{branch_name}": "c1"},
                upstream_tracking={branch_name: f"origin/{branch_name}"},
                extra={
                    "branches": {branch_name: "c1"},
                    "remote_updates": {f"origin/{branch_name}": "c2"},
                },
            ),
            "answer_anchor": f"pulled origin/{branch_name}, local {branch_name} fast-forwarded to c2",
        }
        for case_id, branch_name, project, src_path in entries
    ]


def _fetch_pull_hard_cases() -> list[dict[str, Any]]:
    """Three Hard cases: fetch first to inspect, then pull to integrate."""
    entries = [
        ("v25h-main",    "main",         "ticketing-app",  "src/feature.py"),
        ("v25h-feature", "feature/auth", "auth-service",   "src/auth.py"),
        ("v25h-develop", "develop",      "api-gateway",    "src/api.py"),
    ]
    return [
        {
            "case_id": case_id,
            "branch_name": branch_name,
            "project": project,
            "initial_state": repo_with_head(
                commits=[
                    commit("c1", "Baseline snapshot", {"README.md": "v1"}),
                    commit("c2", "Teammate committed to remote", {"README.md": "v1", src_path: "remote-v1"}, ["c1"]),
                ],
                head="c1",
                branch=branch_name,
                remotes={"origin": f"https://github.com/team/{project}.git"},
                remote_branches={f"origin/{branch_name}": "c1"},
                upstream_tracking={branch_name: f"origin/{branch_name}"},
                extra={
                    "branches": {branch_name: "c1"},
                    "remote_updates": {f"origin/{branch_name}": "c2"},
                },
            ),
            "answer_anchor": f"fetched origin first, then pulled origin/{branch_name} to update local to c2",
        }
        for case_id, branch_name, project, src_path in entries
    ]


def fetch_pull_scenario() -> dict[str, Any]:
    easy_bp = bp(
        slug="fetch-update-easy",
        kind="fetch-pull",
        signature="module2.fetch-pull.easy",
        subtemplate="fetch-remote-tracking",
        cases=_fetch_pull_easy_cases(),
        initial_state="{{initial_state}}",
        target_rule={
            "skip_required_commands": True,
            "remote_tracking_updated": True,
            "remote_branch_points_to": {"origin/{{branch_name}}": "c2"},
        },
        solution=["git fetch origin"],
        label="Fetch from origin to update remote tracking for {{branch_name}}",
        slug_template="fetch-update-easy-{{case_id}}",
    )

    medium_bp = bp(
        slug="pull-integrate-medium",
        kind="fetch-pull",
        signature="module2.fetch-pull.medium",
        subtemplate="pull-fast-forward",
        cases=_fetch_pull_medium_cases(),
        initial_state="{{initial_state}}",
        target_rule={
            "skip_required_commands": True,
            "remote_branch_matches_local": {"origin/{{branch_name}}": "{{branch_name}}"},
        },
        solution=["git pull origin {{branch_name}}"],
        label="Pull remote commits into local {{branch_name}}",
        slug_template="pull-integrate-medium-{{case_id}}",
    )

    hard_bp = bp(
        slug="fetch-then-pull-hard",
        kind="fetch-pull",
        signature="module2.fetch-pull.hard",
        subtemplate="fetch-inspect-then-pull",
        cases=_fetch_pull_hard_cases(),
        initial_state="{{initial_state}}",
        target_rule={
            "skip_required_commands": True,
            "remote_branch_matches_local": {"origin/{{branch_name}}": "{{branch_name}}"},
        },
        solution=["git fetch origin", "git pull origin {{branch_name}}"],
        label="Fetch to inspect, then pull {{branch_name}} to integrate",
        slug_template="fetch-then-pull-hard-{{case_id}}",
    )

    return scenario_dict(
        lesson=(
            5,
            "fetching-and-pulling",
            "Fetching and Pulling from a Remote",
            "Bring remote changes into the local repository and keep local branches up to date.",
        ),
        slug="fetch-and-pull-updates",
        title="Fetching and Pulling from a Remote",
        focus="git fetch, git pull",
        summary="Synchronise the local repository with the remote: fetch updates remote tracking refs without touching local branches; pull fetches and then integrates the remote commits.",
        explanation=(
            "git fetch downloads remote changes and updates origin/* refs but does not modify any local branch. "
            "git pull fetches and then merges (or rebases) the remote changes into the current branch. "
            "Fetching first lets you inspect what changed before deciding how to integrate."
        ),
        primary=["git fetch", "git pull"],
        supporting=["git remote", "git remote -v", "git status", "git log --oneline --graph --all", "git branch -v"],
        concepts=["fetch", "pull", "remote-tracking", "fast-forward", "upstream"],
        difficulties={
            DIFFICULTY_EASY: diff(
                (1, 2),
                "Update remote tracking refs by fetching from origin.",
                "Your remote tracking refs may be stale. Fetch to see what your teammates have pushed, without modifying your local branches.",
                [easy_bp],
            ),
            DIFFICULTY_MEDIUM: diff(
                (1, 2),
                "Pull remote commits to fast-forward the local branch.",
                "A teammate has pushed new commits. Pull to integrate them into your local branch.",
                [medium_bp],
            ),
            DIFFICULTY_HARD: diff(
                (2, 4),
                "Fetch first to inspect what changed, then pull to integrate.",
                "You want to see what is on the remote before integrating it. Fetch to update remote tracking refs, review, then pull.",
                [hard_bp],
            ),
        },
    )


# ── Lesson 2.6: Reconciling Diverged Local and Remote Histories ───────────────

def _reconcile_easy_cases() -> list[dict[str, Any]]:
    """Three Easy cases: push rejected — local and remote each added a different file — pull then push."""
    entries = [
        ("v26e-auth",     "feature/auth",     "ticketing-app",  "src/auth.py",    "src/tests.py"),
        ("v26e-payments", "feature/payments", "e-commerce",     "src/payments.py","src/invoice.py"),
        ("v26e-hotfix",   "hotfix/critical",  "order-service",  "src/fix.py",     "src/hotfix_tests.py"),
    ]
    return [
        {
            "case_id": case_id,
            "branch_name": branch_name,
            "project": project,
            "initial_state": repo_with_head(
                commits=[
                    commit("c1", "Common base", {"README.md": "v1"}),
                    commit("c2", "Local work (non-overlapping)", {"README.md": "v1", local_path: "local-v1"}, ["c1"]),
                    commit("c3", "Teammate pushed to remote (non-overlapping)", {"README.md": "v1", remote_path: "remote-v1"}, ["c1"]),
                ],
                head="c2",
                branch=branch_name,
                remotes={"origin": f"https://github.com/team/{project}.git"},
                remote_branches={f"origin/{branch_name}": "c1"},
                upstream_tracking={branch_name: f"origin/{branch_name}"},
                extra={
                    "branches": {branch_name: "c2"},
                    "remote_updates": {f"origin/{branch_name}": "c3"},
                },
            ),
            "answer_anchor": f"pull reconciled diverged {branch_name} with origin (no conflict), then push succeeded",
        }
        for case_id, branch_name, project, local_path, remote_path in entries
    ]


def _reconcile_medium_cases() -> list[dict[str, Any]]:
    """Three Medium cases: fetch then merge explicitly, then push."""
    entries = [
        ("v26m-auth",     "feature/auth",     "ticketing-app",  "src/auth.py",    "src/tests.py"),
        ("v26m-payments", "feature/payments", "e-commerce",     "src/payments.py","src/invoice.py"),
        ("v26m-hotfix",   "hotfix/critical",  "order-service",  "src/fix.py",     "src/hotfix_tests.py"),
    ]
    return [
        {
            "case_id": case_id,
            "branch_name": branch_name,
            "project": project,
            "initial_state": repo_with_head(
                commits=[
                    commit("c1", "Common base", {"README.md": "v1"}),
                    commit("c2", "Local work (non-overlapping)", {"README.md": "v1", local_path: "local-v1"}, ["c1"]),
                    commit("c3", "Teammate pushed to remote (non-overlapping)", {"README.md": "v1", remote_path: "remote-v1"}, ["c1"]),
                ],
                head="c2",
                branch=branch_name,
                remotes={"origin": f"https://github.com/team/{project}.git"},
                remote_branches={f"origin/{branch_name}": "c1"},
                upstream_tracking={branch_name: f"origin/{branch_name}"},
                extra={
                    "branches": {branch_name: "c2"},
                    "remote_updates": {f"origin/{branch_name}": "c3"},
                },
            ),
            "answer_anchor": f"fetched origin, merged origin/{branch_name} (no conflict), then pushed",
        }
        for case_id, branch_name, project, local_path, remote_path in entries
    ]


def _reconcile_hard_cases() -> list[dict[str, Any]]:
    """Three Hard cases: HEAD on wrong branch — switch first, then fetch+merge, then push."""
    entries = [
        ("v26h-auth",     "feature/auth",     "ticketing-app",  "src/auth.py",    "src/tests.py"),
        ("v26h-payments", "feature/payments", "e-commerce",     "src/payments.py","src/invoice.py"),
        ("v26h-hotfix",   "hotfix/critical",  "order-service",  "src/fix.py",     "src/hotfix_tests.py"),
    ]
    return [
        {
            "case_id": case_id,
            "branch_name": branch_name,
            "project": project,
            "initial_state": repo_with_head(
                commits=[
                    commit("c1", "Common base", {"README.md": "v1"}),
                    commit("c2", "Local work on target branch (non-overlapping)", {"README.md": "v1", local_path: "local-v1"}, ["c1"]),
                    commit("c3", "Teammate pushed to remote (non-overlapping)", {"README.md": "v1", remote_path: "remote-v1"}, ["c1"]),
                ],
                head="c1",
                branch="feature/current",
                remotes={"origin": f"https://github.com/team/{project}.git"},
                remote_branches={f"origin/{branch_name}": "c1"},
                upstream_tracking={branch_name: f"origin/{branch_name}"},
                extra={
                    "branches": {"feature/current": "c1", branch_name: "c2"},
                    "remote_updates": {f"origin/{branch_name}": "c3"},
                },
            ),
            "answer_anchor": f"switched to {branch_name}, fetched, merged origin/{branch_name} (no conflict), pushed",
        }
        for case_id, branch_name, project, local_path, remote_path in entries
    ]


def reconcile_scenario() -> dict[str, Any]:
    easy_bp = bp(
        slug="reconcile-merge-easy",
        kind="reconcile",
        signature="module2.reconcile.easy",
        subtemplate="pull-then-push",
        cases=_reconcile_easy_cases(),
        initial_state="{{initial_state}}",
        target_rule={
            "skip_required_commands": True,
            "conflict_free": True,
            "head_branch": "{{branch_name}}",
            "remote_branch_matches_local": {"origin/{{branch_name}}": "{{branch_name}}"},
        },
        solution=["git pull origin {{branch_name}}", "git push origin {{branch_name}}"],
        label="Pull to reconcile then push {{branch_name}}",
        slug_template="reconcile-merge-easy-{{case_id}}",
    )

    medium_bp = bp(
        slug="reconcile-fetch-merge-medium",
        kind="reconcile",
        signature="module2.reconcile.medium",
        subtemplate="fetch-merge-push",
        cases=_reconcile_medium_cases(),
        initial_state="{{initial_state}}",
        target_rule={
            "skip_required_commands": True,
            "conflict_free": True,
            "head_branch": "{{branch_name}}",
            "remote_branch_matches_local": {"origin/{{branch_name}}": "{{branch_name}}"},
        },
        solution=["git fetch origin", "git merge origin/{{branch_name}}", "git push origin {{branch_name}}"],
        label="Fetch, merge remote, then push {{branch_name}}",
        slug_template="reconcile-fetch-merge-medium-{{case_id}}",
    )

    hard_bp = bp(
        slug="reconcile-switch-merge-hard",
        kind="reconcile",
        signature="module2.reconcile.hard",
        subtemplate="switch-fetch-merge-push",
        cases=_reconcile_hard_cases(),
        initial_state="{{initial_state}}",
        target_rule={
            "skip_required_commands": True,
            "conflict_free": True,
            "head_branch": "{{branch_name}}",
            "remote_branch_matches_local": {"origin/{{branch_name}}": "{{branch_name}}"},
        },
        solution=["git switch {{branch_name}}", "git fetch origin", "git merge origin/{{branch_name}}", "git push origin {{branch_name}}"],
        label="Switch, fetch, merge, then push {{branch_name}}",
        slug_template="reconcile-switch-merge-hard-{{case_id}}",
    )

    return scenario_dict(
        lesson=(
            6,
            "reconciling-diverged-histories",
            "Reconciling Diverged Local and Remote Histories",
            "Integrate remote commits that blocked your push, then complete the push successfully.",
        ),
        slug="reconcile-diverged-branches",
        title="Reconciling Diverged Local and Remote Histories",
        focus="git fetch, git merge, git pull, git push",
        summary="When a push is rejected because the remote has diverged, reconcile by pulling (or fetch+merge) to integrate the remote commits, then push successfully.",
        explanation=(
            "A rejected push means the remote branch has commits your local branch does not. "
            "Git refuses to overwrite them. The fix is to integrate the remote commits first — "
            "either with git pull (fetch + merge in one step) or explicitly with git fetch then git merge origin/<branch>. "
            "Once reconciled, git push succeeds."
        ),
        primary=["git pull", "git fetch", "git merge", "git push"],
        supporting=["git log --oneline --graph --all", "git branch -v", "git switch", "git status"],
        concepts=["diverged", "rejected-push", "reconcile", "remote-tracking", "ahead-behind"],
        difficulties={
            DIFFICULTY_EASY: diff(
                (2, 3),
                "Pull to reconcile the diverged remote, then push.",
                "Your push was rejected because a teammate committed to the same branch. Pull to integrate their work, then push.",
                [easy_bp],
            ),
            DIFFICULTY_MEDIUM: diff(
                (3, 5),
                "Fetch, inspect, merge the remote tracking branch, then push.",
                "Your push was rejected. Fetch to update remote tracking refs, merge origin/<branch> into your local branch, then push.",
                [medium_bp],
            ),
            DIFFICULTY_HARD: diff(
                (4, 6),
                "Switch to the correct branch, then fetch, merge, and push.",
                "You are on the wrong branch. Switch to the branch that was rejected, then reconcile with the remote and push.",
                [hard_bp],
            ),
        },
    )


# ── Lesson 2.7: Fast-Forward vs Three-Way Merges ─────────────────────────────

def _ff_merge_easy_cases() -> list[dict[str, Any]]:
    """Three Easy cases: linear history, default FF merge."""
    entries = [
        ("v27e-auth",     "main",       "feature/auth",        "ticketing-app",  "src/auth.py",    "auth-v1"),
        ("v27e-payments", "develop",    "feature/payments",    "e-commerce",     "src/payments.py","pay-v1"),
        ("v27e-hotfix",   "release/v2", "hotfix/fix-critical", "order-service",  "src/fix.py",     "fix-v1"),
    ]
    return [
        {
            "case_id": case_id,
            "target_branch": target_branch,
            "source_branch": source_branch,
            "project": project,
            "merge_requirement": "linear (fast-forward)",
            "initial_state": repo_with_head(
                commits=[
                    commit("c1", "Project base commit", {"README.md": "v1"}),
                    commit("c2", "Feature branch complete", {"README.md": "v1", src_path: src_content}, ["c1"]),
                ],
                head="c1",
                branch=target_branch,
                extra={"branches": {target_branch: "c1", source_branch: "c2"}},
            ),
            "answer_anchor": f"fast-forward merged {source_branch} into {target_branch} (HEAD moves to c2)",
        }
        for case_id, target_branch, source_branch, project, src_path, src_content in entries
    ]


def _ff_merge_medium_cases() -> list[dict[str, Any]]:
    """Three Medium cases: same linear history, force merge commit with --no-ff."""
    entries = [
        ("v27m-auth",     "main",       "feature/auth",        "ticketing-app",  "src/auth.py",    "auth-v1"),
        ("v27m-payments", "develop",    "feature/payments",    "e-commerce",     "src/payments.py","pay-v1"),
        ("v27m-hotfix",   "release/v2", "hotfix/fix-critical", "order-service",  "src/fix.py",     "fix-v1"),
    ]
    return [
        {
            "case_id": case_id,
            "target_branch": target_branch,
            "source_branch": source_branch,
            "project": project,
            "merge_requirement": "preserve branch history (no fast-forward)",
            "initial_state": repo_with_head(
                commits=[
                    commit("c1", "Project base commit", {"README.md": "v1"}),
                    commit("c2", "Feature branch complete", {"README.md": "v1", src_path: src_content}, ["c1"]),
                ],
                head="c1",
                branch=target_branch,
                extra={"branches": {target_branch: "c1", source_branch: "c2"}},
            ),
            "answer_anchor": f"no-ff merged {source_branch} into {target_branch} (merge commit created)",
        }
        for case_id, target_branch, source_branch, project, src_path, src_content in entries
    ]


def _ff_merge_hard_cases() -> list[dict[str, Any]]:
    """Three Hard cases: diverged histories, HEAD on wrong branch, switch then --no-ff merge."""
    return [
        {
            "case_id": "v27h-auth",
            "target_branch": "main",
            "source_branch": "feature/auth",
            "project": "ticketing-app",
            "merge_requirement": "explicit merge commit required",
            "initial_state": repo_with_head(
                commits=[
                    commit("c1", "Common base", {"README.md": "v1"}),
                    commit("c2", "Auth feature diverged", {"README.md": "v1", "src/auth.py": "auth-v1"}, ["c1"]),
                    commit("c3", "Main diverged", {"README.md": "v1", "src/app.py": "app-v1"}, ["c1"]),
                ],
                head="c1",
                branch="feature/current",
                extra={"branches": {"feature/current": "c1", "main": "c3", "feature/auth": "c2"}},
            ),
            "answer_anchor": "switched to main, no-ff merged feature/auth (4 reachable commits)",
        },
        {
            "case_id": "v27h-payments",
            "target_branch": "develop",
            "source_branch": "feature/payments",
            "project": "e-commerce",
            "merge_requirement": "explicit merge commit required",
            "initial_state": repo_with_head(
                commits=[
                    commit("c1", "Common base", {"README.md": "v1"}),
                    commit("c2", "Payments diverged", {"README.md": "v1", "src/payments.py": "pay-v1"}, ["c1"]),
                    commit("c3", "Develop diverged", {"README.md": "v1", "src/core.py": "core-v1"}, ["c1"]),
                ],
                head="c1",
                branch="feature/current",
                extra={"branches": {"feature/current": "c1", "develop": "c3", "feature/payments": "c2"}},
            ),
            "answer_anchor": "switched to develop, no-ff merged feature/payments (4 reachable commits)",
        },
        {
            "case_id": "v27h-hotfix",
            "target_branch": "release/v1",
            "source_branch": "hotfix/critical",
            "project": "order-service",
            "merge_requirement": "explicit merge commit required",
            "initial_state": repo_with_head(
                commits=[
                    commit("c1", "Common base", {"README.md": "v1"}),
                    commit("c2", "Hotfix diverged", {"README.md": "v1", "src/fix.py": "fix-v1"}, ["c1"]),
                    commit("c3", "Release diverged", {"README.md": "v1", "src/release.py": "rel-v1"}, ["c1"]),
                ],
                head="c1",
                branch="feature/current",
                extra={"branches": {"feature/current": "c1", "release/v1": "c3", "hotfix/critical": "c2"}},
            ),
            "answer_anchor": "switched to release/v1, no-ff merged hotfix/critical (4 reachable commits)",
        },
    ]


def ff_merge_scenario() -> dict[str, Any]:
    easy_bp = bp(
        slug="ff-merge-easy",
        kind="merge-type",
        signature="module2.ff-merge.easy",
        subtemplate="fast-forward-merge",
        cases=_ff_merge_easy_cases(),
        initial_state="{{initial_state}}",
        target_rule={
            "skip_required_commands": True,
            "conflict_free": True,
            "head_branch": "{{target_branch}}",
            "min_commits_on_branch": {"{{target_branch}}": 2},
        },
        solution=["git merge {{source_branch}}"],
        label="Fast-forward merge {{source_branch}} into {{target_branch}}",
        slug_template="ff-merge-easy-{{case_id}}",
    )

    medium_bp = bp(
        slug="noff-merge-medium",
        kind="merge-type",
        signature="module2.ff-merge.medium",
        subtemplate="no-ff-merge-linear",
        cases=_ff_merge_medium_cases(),
        initial_state="{{initial_state}}",
        target_rule={
            "skip_required_commands": True,
            "conflict_free": True,
            "head_branch": "{{target_branch}}",
            "min_commits_on_branch": {"{{target_branch}}": 3},
        },
        solution=["git merge --no-ff {{source_branch}}"],
        label="Force merge commit when integrating {{source_branch}} into {{target_branch}}",
        slug_template="noff-merge-medium-{{case_id}}",
    )

    hard_bp = bp(
        slug="noff-merge-hard",
        kind="merge-type",
        signature="module2.ff-merge.hard",
        subtemplate="switch-then-noff-merge",
        cases=_ff_merge_hard_cases(),
        initial_state="{{initial_state}}",
        target_rule={
            "skip_required_commands": True,
            "conflict_free": True,
            "head_branch": "{{target_branch}}",
            "min_commits_on_branch": {"{{target_branch}}": 4},
        },
        solution=["git switch {{target_branch}}", "git merge --no-ff {{source_branch}}"],
        label="Switch to {{target_branch}} and no-ff merge {{source_branch}}",
        slug_template="noff-merge-hard-{{case_id}}",
    )

    return scenario_dict(
        lesson=(
            7,
            "fast-forward-vs-three-way-merges",
            "Fast-Forward vs Three-Way Merges",
            "Choose the right merge strategy to produce the history shape the team requires.",
        ),
        slug="fast-forward-vs-noff-merge",
        title="Fast-Forward vs Three-Way Merges",
        focus="git merge, git merge --no-ff",
        summary=(
            "A fast-forward merge advances the branch pointer when no divergence exists. "
            "The --no-ff flag forces a merge commit even for linear histories, preserving the explicit integration point."
        ),
        explanation=(
            "When a branch is a direct linear descendant of the target, git merge performs a fast-forward by default: "
            "the target pointer simply moves forward to the tip of the source branch. "
            "Use --no-ff to always create a merge commit — a common team convention "
            "to maintain a clear record of when feature branches were integrated."
        ),
        primary=["git merge", "git merge --no-ff"],
        supporting=["git log --oneline --graph --all", "git branch -v", "git switch", "git status"],
        concepts=["merge", "fast-forward", "no-ff", "merge-commit", "linear-history"],
        difficulties={
            DIFFICULTY_EASY: diff(
                (1, 2),
                "Merge a feature branch that is a linear descendant of the target.",
                "The feature branch has no divergence from the target. Merge it in, allowing a fast-forward.",
                [easy_bp],
            ),
            DIFFICULTY_MEDIUM: diff(
                (1, 2),
                "Force a merge commit on a linear branch to preserve branch history.",
                "The feature branch is ahead of the target with no divergence, but team policy requires an explicit merge commit.",
                [medium_bp],
            ),
            DIFFICULTY_HARD: diff(
                (2, 4),
                "Switch to the target branch and no-ff merge a diverged feature.",
                "You are currently on a different branch and histories have diverged. Move to the correct target first, then merge with an explicit merge commit.",
                [hard_bp],
            ),
        },
    )


# ── Lesson 2.8: Squash Merging ───────────────────────────────────────────────

def _squash_easy_cases() -> list[dict[str, Any]]:
    """Three Easy cases: squash a local feature branch (multiple commits) onto target, then commit."""
    return [
        {
            "case_id": "v28e-auth",
            "target_branch": "main",
            "source_branch": "feature/auth",
            "project": "ticketing-app",
            "commit_message": "Squash auth feature into main",
            "initial_state": repo_with_head(
                commits=[
                    commit("c1", "Bootstrap project", {"README.md": "v1"}),
                    commit("c2", "Auth: add login", {"README.md": "v1", "src/auth.py": "auth-v1"}, ["c1"]),
                    commit("c3", "Auth: add logout", {"README.md": "v1", "src/auth.py": "auth-v2"}, ["c2"]),
                ],
                head="c1",
                branch="main",
                extra={"branches": {"main": "c1", "feature/auth": "c3"}},
            ),
            "answer_anchor": "squash merged feature/auth (c2,c3) onto main as single commit",
        },
        {
            "case_id": "v28e-orders",
            "target_branch": "develop",
            "source_branch": "feature/orders",
            "project": "e-commerce",
            "commit_message": "Squash orders feature into develop",
            "initial_state": repo_with_head(
                commits=[
                    commit("c1", "Bootstrap project", {"README.md": "v1"}),
                    commit("c2", "Orders: add create", {"README.md": "v1", "src/orders.py": "ord-v1"}, ["c1"]),
                    commit("c3", "Orders: add cancel", {"README.md": "v1", "src/orders.py": "ord-v2"}, ["c2"]),
                ],
                head="c1",
                branch="develop",
                extra={"branches": {"develop": "c1", "feature/orders": "c3"}},
            ),
            "answer_anchor": "squash merged feature/orders onto develop as single commit",
        },
        {
            "case_id": "v28e-parser",
            "target_branch": "release/v2",
            "source_branch": "feature/parser",
            "project": "data-pipeline",
            "commit_message": "Squash parser feature into release/v2",
            "initial_state": repo_with_head(
                commits=[
                    commit("c1", "Bootstrap project", {"README.md": "v1"}),
                    commit("c2", "Parser: initial impl", {"README.md": "v1", "src/parser.py": "par-v1"}, ["c1"]),
                    commit("c3", "Parser: add error handling", {"README.md": "v1", "src/parser.py": "par-v2"}, ["c2"]),
                ],
                head="c1",
                branch="release/v2",
                extra={"branches": {"release/v2": "c1", "feature/parser": "c3"}},
            ),
            "answer_anchor": "squash merged feature/parser onto release/v2 as single commit",
        },
    ]


def _squash_medium_cases() -> list[dict[str, Any]]:
    """Three Medium cases: fetch a remote feature branch, then squash-merge it onto the target."""
    return [
        {
            "case_id": "v28m-auth",
            "target_branch": "main",
            "source_branch": "origin/feature/auth",
            "project": "ticketing-app",
            "commit_message": "Squash remote auth feature into main",
            "initial_state": repo_with_head(
                commits=[
                    commit("c1", "Bootstrap project", {"README.md": "v1"}),
                    commit("c2", "Auth feature (remote)", {"README.md": "v1", "src/auth.py": "auth-v1"}, ["c1"]),
                ],
                head="c1",
                branch="main",
                remotes={"origin": "https://github.com/team/ticketing-app.git"},
                remote_branches={"origin/feature/auth": "c1"},
                extra={
                    "branches": {"main": "c1"},
                    "remote_updates": {"origin/feature/auth": "c2"},
                },
            ),
            "answer_anchor": "fetched origin, squash merged origin/feature/auth onto main as single commit",
        },
        {
            "case_id": "v28m-orders",
            "target_branch": "develop",
            "source_branch": "origin/feature/orders",
            "project": "e-commerce",
            "commit_message": "Squash remote orders feature into develop",
            "initial_state": repo_with_head(
                commits=[
                    commit("c1", "Bootstrap project", {"README.md": "v1"}),
                    commit("c2", "Orders feature (remote)", {"README.md": "v1", "src/orders.py": "ord-v1"}, ["c1"]),
                ],
                head="c1",
                branch="develop",
                remotes={"origin": "https://github.com/team/e-commerce.git"},
                remote_branches={"origin/feature/orders": "c1"},
                extra={
                    "branches": {"develop": "c1"},
                    "remote_updates": {"origin/feature/orders": "c2"},
                },
            ),
            "answer_anchor": "fetched origin, squash merged origin/feature/orders onto develop",
        },
        {
            "case_id": "v28m-parser",
            "target_branch": "release/v2",
            "source_branch": "origin/feature/parser",
            "project": "data-pipeline",
            "commit_message": "Squash remote parser feature into release/v2",
            "initial_state": repo_with_head(
                commits=[
                    commit("c1", "Bootstrap project", {"README.md": "v1"}),
                    commit("c2", "Parser feature (remote)", {"README.md": "v1", "src/parser.py": "par-v1"}, ["c1"]),
                ],
                head="c1",
                branch="release/v2",
                remotes={"origin": "https://github.com/team/data-pipeline.git"},
                remote_branches={"origin/feature/parser": "c1"},
                extra={
                    "branches": {"release/v2": "c1"},
                    "remote_updates": {"origin/feature/parser": "c2"},
                },
            ),
            "answer_anchor": "fetched origin, squash merged origin/feature/parser onto release/v2",
        },
    ]


def _squash_hard_cases() -> list[dict[str, Any]]:
    """Three Hard cases: squash-merge then delete the source branch (full cleanup)."""
    return [
        {
            "case_id": "v28h-auth",
            "target_branch": "main",
            "source_branch": "feature/auth",
            "project": "ticketing-app",
            "commit_message": "Squash auth feature into main",
            "initial_state": repo_with_head(
                commits=[
                    commit("c1", "Bootstrap project", {"README.md": "v1"}),
                    commit("c2", "Auth: add login", {"README.md": "v1", "src/auth.py": "auth-v1"}, ["c1"]),
                    commit("c3", "Auth: add logout", {"README.md": "v1", "src/auth.py": "auth-v2"}, ["c2"]),
                ],
                head="c1",
                branch="main",
                extra={"branches": {"main": "c1", "feature/auth": "c3"}},
            ),
            "answer_anchor": "squash merged feature/auth onto main, then deleted feature/auth branch",
        },
        {
            "case_id": "v28h-orders",
            "target_branch": "develop",
            "source_branch": "feature/orders",
            "project": "e-commerce",
            "commit_message": "Squash orders feature into develop",
            "initial_state": repo_with_head(
                commits=[
                    commit("c1", "Bootstrap project", {"README.md": "v1"}),
                    commit("c2", "Orders: add create", {"README.md": "v1", "src/orders.py": "ord-v1"}, ["c1"]),
                    commit("c3", "Orders: add cancel", {"README.md": "v1", "src/orders.py": "ord-v2"}, ["c2"]),
                ],
                head="c1",
                branch="develop",
                extra={"branches": {"develop": "c1", "feature/orders": "c3"}},
            ),
            "answer_anchor": "squash merged feature/orders onto develop, then deleted feature/orders",
        },
        {
            "case_id": "v28h-parser",
            "target_branch": "release/v2",
            "source_branch": "feature/parser",
            "project": "data-pipeline",
            "commit_message": "Squash parser feature into release/v2",
            "initial_state": repo_with_head(
                commits=[
                    commit("c1", "Bootstrap project", {"README.md": "v1"}),
                    commit("c2", "Parser: initial impl", {"README.md": "v1", "src/parser.py": "par-v1"}, ["c1"]),
                    commit("c3", "Parser: add error handling", {"README.md": "v1", "src/parser.py": "par-v2"}, ["c2"]),
                ],
                head="c1",
                branch="release/v2",
                extra={"branches": {"release/v2": "c1", "feature/parser": "c3"}},
            ),
            "answer_anchor": "squash merged feature/parser onto release/v2, then deleted branch",
        },
    ]


def squash_scenario() -> dict[str, Any]:
    easy_bp = bp(
        slug="squash-merge-easy",
        kind="squash-merge",
        signature="module2.squash.easy",
        subtemplate="squash-and-commit",
        cases=_squash_easy_cases(),
        initial_state="{{initial_state}}",
        target_rule={
            "skip_required_commands": True,
            "conflict_free": True,
            "head_branch": "{{target_branch}}",
            "working_tree_clean": True,
            "min_commits_on_branch": {"{{target_branch}}": 2},
        },
        solution=["git merge --squash {{source_branch}}", "git commit -m \"{{commit_message}}\""],
        label="Squash-merge {{source_branch}} onto {{target_branch}} as a single commit",
        slug_template="squash-merge-easy-{{case_id}}",
    )

    medium_bp = bp(
        slug="squash-merge-medium",
        kind="squash-merge",
        signature="module2.squash.medium",
        subtemplate="fetch-then-squash-commit",
        cases=_squash_medium_cases(),
        initial_state="{{initial_state}}",
        target_rule={
            "skip_required_commands": True,
            "conflict_free": True,
            "head_branch": "{{target_branch}}",
            "working_tree_clean": True,
            "min_commits_on_branch": {"{{target_branch}}": 2},
        },
        solution=["git fetch origin", "git merge --squash {{source_branch}}", "git commit -m \"{{commit_message}}\""],
        label="Fetch then squash-merge {{source_branch}} onto {{target_branch}}",
        slug_template="squash-merge-medium-{{case_id}}",
    )

    hard_bp = bp(
        slug="squash-merge-hard",
        kind="squash-merge",
        signature="module2.squash.hard",
        subtemplate="squash-commit-delete",
        cases=_squash_hard_cases(),
        initial_state="{{initial_state}}",
        target_rule={
            "skip_required_commands": True,
            "conflict_free": True,
            "head_branch": "{{target_branch}}",
            "working_tree_clean": True,
            "min_commits_on_branch": {"{{target_branch}}": 2},
            "branch_absent": ["{{source_branch}}"],
        },
        solution=["git merge --squash {{source_branch}}", "git commit -m \"{{commit_message}}\"", "git branch -D {{source_branch}}"],
        label="Squash-merge {{source_branch}} then delete the source branch",
        slug_template="squash-merge-hard-{{case_id}}",
    )

    return scenario_dict(
        lesson=(
            8,
            "squash-merging",
            "Squash Merging",
            "Land a feature branch as a single tidy commit on the target branch.",
        ),
        slug="squash-merge-feature",
        title="Squash Merging",
        focus="git merge --squash",
        summary=(
            "A squash merge collapses all commits from a feature branch into a single staged changeset "
            "on the target branch, which you then commit with a clean message."
        ),
        explanation=(
            "git merge --squash stages all the changes from the source branch without creating a merge commit or preserving the source branch's individual commits. "
            "You must then run git commit to record the squashed changes. "
            "The source branch pointer is unaffected — delete it separately when done."
        ),
        primary=["git merge --squash"],
        supporting=["git fetch", "git log --oneline --graph --all", "git branch -v", "git branch -D", "git status"],
        concepts=["squash-merge", "clean-history", "single-commit", "staging"],
        difficulties={
            DIFFICULTY_EASY: diff(
                (2, 3),
                "Squash a local feature branch onto the target branch.",
                "The feature branch has several intermediate commits. Land them as a single clean commit on the target.",
                [easy_bp],
            ),
            DIFFICULTY_MEDIUM: diff(
                (3, 5),
                "Fetch a remote feature branch then squash-merge it.",
                "The feature work is on the remote. Fetch it first, then squash-merge to land it as one commit on the target.",
                [medium_bp],
            ),
            DIFFICULTY_HARD: diff(
                (3, 5),
                "Squash-merge the feature branch and clean up the source branch.",
                "After landing the squash commit, the feature branch is no longer needed. Remove it to keep the branch list tidy.",
                [hard_bp],
            ),
        },
    )


# ── Lesson 2.9: Deleting and Recovering Remote Branches ──────────────────────

def _remote_branch_easy_cases() -> list[dict[str, Any]]:
    """Three Easy cases: delete a remote branch that was merged and is no longer needed."""
    entries = [
        ("v29e-auth",   "feature/auth",   "ticketing-app",  "src/auth.py",    "auth-v1"),
        ("v29e-orders", "feature/orders", "e-commerce",     "src/orders.py",  "ord-v1"),
        ("v29e-parser", "feature/parser", "data-pipeline",  "src/parser.py",  "par-v1"),
    ]
    return [
        {
            "case_id": case_id,
            "branch_name": branch_name,
            "project": project,
            "action_required": f"delete {branch_name} from remote",
            "initial_state": repo_with_head(
                commits=[
                    commit("c1", "Merge commit on main", {"README.md": "v1", src_path: src_content}),
                    commit("c2", f"Feature tip (still on remote)", {"README.md": "v1", src_path: src_content}, ["c1"]),
                ],
                head="c1",
                branch="main",
                remotes={"origin": f"https://github.com/team/{project}.git"},
                remote_branches={f"origin/{branch_name}": "c2"},
                extra={"branches": {"main": "c1", branch_name: "c2"}},
            ),
            "answer_anchor": f"deleted origin/{branch_name} from remote (merged branch cleanup)",
        }
        for case_id, branch_name, project, src_path, src_content in entries
    ]


def _remote_branch_medium_cases() -> list[dict[str, Any]]:
    """Three Medium cases: a teammate deleted the remote branch; prune stale local tracking refs."""
    entries = [
        ("v29m-auth",   "feature/auth",   "ticketing-app",  "src/auth.py",    "auth-v1"),
        ("v29m-orders", "feature/orders", "e-commerce",     "src/orders.py",  "ord-v1"),
        ("v29m-parser", "feature/parser", "data-pipeline",  "src/parser.py",  "par-v1"),
    ]
    return [
        {
            "case_id": case_id,
            "branch_name": branch_name,
            "project": project,
            "action_required": f"prune stale remote tracking ref for {branch_name}",
            "duplicate_solution_waiver": True,
            "initial_state": repo_with_head(
                commits=[
                    commit("c1", "Main at latest", {"README.md": "v1", src_path: src_content}),
                    commit("c2", "Feature tip (already deleted on remote)", {"README.md": "v1", src_path: src_content}, ["c1"]),
                ],
                head="c1",
                branch="main",
                remotes={"origin": f"https://github.com/team/{project}.git"},
                remote_branches={f"origin/{branch_name}": "c2"},
                extra={
                    "branches": {"main": "c1", branch_name: "c2"},
                    "remote_stale_branches": [f"origin/{branch_name}"],
                },
            ),
            "answer_anchor": f"pruned stale origin/{branch_name} tracking ref via fetch --prune",
        }
        for case_id, branch_name, project, src_path, src_content in entries
    ]


def _remote_branch_hard_cases() -> list[dict[str, Any]]:
    """Three Hard cases: delete both the remote branch and the local branch (full cleanup).

    The feature was already merged (main has a merge commit containing the feature tip),
    so git branch -d (safe delete) succeeds.
    """
    entries = [
        ("v29h-auth",   "feature/auth",   "ticketing-app",  "src/auth.py",    "auth-v1"),
        ("v29h-orders", "feature/orders", "e-commerce",     "src/orders.py",  "ord-v1"),
        ("v29h-parser", "feature/parser", "data-pipeline",  "src/parser.py",  "par-v1"),
    ]
    return [
        {
            "case_id": case_id,
            "branch_name": branch_name,
            "project": project,
            "action_required": f"delete {branch_name} from remote and locally",
            "initial_state": repo_with_head(
                commits=[
                    commit("c1", "Base commit", {"README.md": "v1"}),
                    commit("c2", "Feature work (merged)", {"README.md": "v1", src_path: src_content}, ["c1"]),
                    commit("c3", "Merge feature into main", {"README.md": "v1", src_path: src_content}, ["c1", "c2"]),
                ],
                head="c3",
                branch="main",
                remotes={"origin": f"https://github.com/team/{project}.git"},
                remote_branches={f"origin/{branch_name}": "c2"},
                upstream_tracking={branch_name: f"origin/{branch_name}"},
                extra={"branches": {"main": "c3", branch_name: "c2"}},
            ),
            "answer_anchor": f"deleted origin/{branch_name} from remote and {branch_name} locally (safe -d)",
        }
        for case_id, branch_name, project, src_path, src_content in entries
    ]


def remote_branch_scenario() -> dict[str, Any]:
    easy_bp = bp(
        slug="remote-delete-easy",
        kind="remote-branch",
        signature="module2.remote-branch.easy",
        subtemplate="delete-remote-branch",
        cases=_remote_branch_easy_cases(),
        initial_state="{{initial_state}}",
        target_rule={
            "skip_required_commands": True,
            "remote_branch_absent": ["origin/{{branch_name}}"],
        },
        solution=["git push origin --delete {{branch_name}}"],
        label="Delete the remote branch origin/{{branch_name}}",
        slug_template="remote-delete-easy-{{case_id}}",
    )

    medium_bp = bp(
        slug="remote-prune-medium",
        kind="remote-branch",
        signature="module2.remote-branch.medium",
        subtemplate="prune-stale-tracking-refs",
        cases=_remote_branch_medium_cases(),
        initial_state="{{initial_state}}",
        target_rule={
            "skip_required_commands": True,
            "remote_branch_absent": ["origin/{{branch_name}}"],
        },
        solution=["git fetch --prune origin"],
        label="Prune the stale remote tracking ref for origin/{{branch_name}}",
        slug_template="remote-prune-medium-{{case_id}}",
    )

    hard_bp = bp(
        slug="remote-cleanup-hard",
        kind="remote-branch",
        signature="module2.remote-branch.hard",
        subtemplate="delete-remote-and-local",
        cases=_remote_branch_hard_cases(),
        initial_state="{{initial_state}}",
        target_rule={
            "skip_required_commands": True,
            "remote_branch_absent": ["origin/{{branch_name}}"],
            "branch_absent": ["{{branch_name}}"],
        },
        solution=["git push origin --delete {{branch_name}}", "git branch -d {{branch_name}}"],
        label="Delete {{branch_name}} from both remote and local",
        slug_template="remote-cleanup-hard-{{case_id}}",
    )

    return scenario_dict(
        lesson=(
            9,
            "deleting-and-recovering-remote-branches",
            "Deleting and Recovering Remote Branches",
            "Manage remote branch lifecycle: remove finished branches and prune stale tracking refs.",
        ),
        slug="remote-branch-lifecycle",
        title="Deleting and Recovering Remote Branches",
        focus="git push --delete, git fetch --prune",
        summary=(
            "Delete finished remote branches to keep the shared repository tidy, "
            "and prune stale local tracking refs when teammates delete branches on the remote."
        ),
        explanation=(
            "git push origin --delete <branch> removes the branch from the remote server. "
            "git fetch --prune removes any local remote-tracking refs (origin/*) that no longer exist on the remote. "
            "After merging a feature branch, a full cleanup removes both the remote branch and the local copy."
        ),
        primary=["git push --delete", "git fetch --prune"],
        supporting=["git branch -a", "git remote -v", "git branch -d", "git log --oneline --graph --all"],
        concepts=["remote-branch", "push-delete", "fetch-prune", "branch-cleanup", "tracking-refs"],
        difficulties={
            DIFFICULTY_EASY: diff(
                (1, 2),
                "Delete a merged remote branch.",
                "The feature branch was merged and is no longer needed on the remote. Remove it.",
                [easy_bp],
            ),
            DIFFICULTY_MEDIUM: diff(
                (1, 2),
                "Prune a stale remote tracking ref that no longer exists on the remote.",
                "A teammate deleted the remote branch. Your local remote tracking ref is stale. Clean it up with fetch --prune.",
                [medium_bp],
            ),
            DIFFICULTY_HARD: diff(
                (2, 3),
                "Delete the remote branch and clean up the local branch.",
                "After a feature is merged, remove both the remote branch and the local branch to keep the repository tidy.",
                [hard_bp],
            ),
        },
    )


def base_scenarios_m2() -> list[dict[str, Any]]:
    return [
        branch_create_scenario(),
        branch_naming_scenario(),
        stash_scenario(),
        push_scenario(),
        fetch_pull_scenario(),
        reconcile_scenario(),
        ff_merge_scenario(),
        squash_scenario(),
        remote_branch_scenario(),
    ]


class Command(BaseCommand):
    help = "Seed Module 2 scenario skill focuses, difficulties, policies, and authored variants."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing Module 2 content and sessions before seeding.",
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
            self._reset_module_two(confirm=options["confirm"])

        seed_git_command_content_library()

        unit, _ = LearningUnit.objects.update_or_create(
            slug="branching-and-collaboration",
            defaults={
                "number": 2,
                "title": "Branching and Collaboration",
                "description": (
                    "Create, switch, and delete branches; stash work in progress; "
                    "push and pull with remotes; merge, squash-merge, and reconcile diverged histories "
                    "through scenario practice."
                ),
                "is_orientation": False,
                "is_published": True,
                "sort_order": 2,
            },
        )

        lesson_by_order = {}
        for (
            lesson_order,
            lesson_slug,
            lesson_title,
            lesson_subtitle,
        ) in MODULE_TWO_SCENARIO_ANCHORS:
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

        specs = base_scenarios_m2()
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
                min_count, _ = dspec["policy"]
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

        self.stdout.write(self.style.SUCCESS("Seeded Module 2 authored scenario variants."))

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
                    if len(set(json.dumps(anchor, sort_keys=True) for anchor in anchors)) != len(anchors):
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
                for solution_key, case_ids_for_solution in rendered_solutions.items():
                    if len(case_ids_for_solution) > 1:
                        waived = all(
                            any(case.get("case_id") == cid and case.get("duplicate_solution_waiver")
                                for case in template.get("cases", []))
                            for cid in case_ids_for_solution
                        )
                        if not waived:
                            failures.append(
                                f"{spec['slug']}/{difficulty}: duplicate solution in cases {case_ids_for_solution}"
                            )
                for rule, case_ids_for_rule in rendered_target_rules.items():
                    if len(case_ids_for_rule) > 1:
                        failures.append(
                            f"{spec['slug']}/{difficulty}: duplicate target rule in cases {case_ids_for_rule}"
                        )
                for state, case_ids_for_state in rendered_target_states.items():
                    if len(case_ids_for_state) > 1:
                        failures.append(
                            f"{spec['slug']}/{difficulty}: duplicate target state in cases {case_ids_for_state}"
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
            raise CommandError("Module 2 seed validation failed:\n" + "\n".join(failures))

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

    def _delete_sessions_chunked(self, unit, chunk_size: int = 200):
        """Delete ScenarioSessions in chunks to avoid statement-timeout on large cascade."""
        step_qs = StepLog.objects.filter(session__learning_unit=unit)
        while True:
            chunk = list(step_qs.values_list("id", flat=True)[:chunk_size])
            if not chunk:
                break
            CommandLog.objects.filter(step_log_id__in=chunk).delete()
            StepLog.objects.filter(id__in=chunk).delete()
        ScenarioSession.objects.filter(learning_unit=unit).delete()

    def _reset_module_two(self, *, confirm: bool):
        if not settings.DEBUG:
            raise CommandError("--reset is only available when DEBUG=True.")
        if not confirm:
            raise CommandError("Pass --confirm with --reset to clear Module 2 seeded data.")
        # Delete any unit occupying the Module 2 slot (by slug or by number=2).
        candidates = LearningUnit.objects.filter(
            slug="branching-and-collaboration"
        ) | LearningUnit.objects.filter(number=2)
        for unit in candidates.distinct():
            CompletionRecord.objects.filter(scenario__learning_unit=unit).delete()
            self._delete_sessions_chunked(unit)
            ScenarioVariant.objects.filter(scenario__learning_unit=unit).delete()
            DifficultyInstance.objects.filter(scenario__learning_unit=unit).delete()
            ScenarioSkillFocus.objects.filter(learning_unit=unit).delete()
            OrientationProgress.objects.filter(lesson__unit=unit).delete()
            unit.lessons.all().delete()
            unit.delete()

    def _anchor_html(self, title: str, subtitle: str) -> str:
        return (
            f'<section class="internal-scenario-anchor">'
            f"<h1>{title}</h1>"
            f"<p>{subtitle}</p>"
            f"<p>Internal scenario anchor for ordering Module 2 Scenario Skill Focus cards.</p>"
            f"</section>"
        )

    def _demo_state(self, spec: dict[str, Any]) -> dict[str, Any]:
        return repo_with_head(
            commits=[
                commit("c1", "Initial project snapshot", {"README.md": "readme-v1", "src/app.py": "app-v1"}),
                commit("c2", "Add feature scaffold", {"README.md": "readme-v1", "src/app.py": "app-v1", "src/feature.py": "feature-v1"}, ["c1"]),
            ],
            head="c2",
            branch="main",
            remotes={"origin": "https://example.test/demo/repository.git"},
            remote_branches={"origin/main": "c2"},
            upstream_tracking={"main": "origin/main"},
            extra={
                "branches": {"main": "c2", "feature/demo": "c2"},
            },
        )

    def _command_preview_config(self, spec: dict[str, Any]) -> dict[str, Any]:
        commands = self._demo_commands(spec)
        preview_commands = self._preview_commands(spec, fallback_commands=commands)
        demo_state = self._demo_state(spec)
        normalized_commands = [command.strip().lower() for command in commands]
        diagnostic = bool(commands) and all(
            command in {item.lower() for item in DIAG_PATTERNS} for command in normalized_commands
        )
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
        authored_commands = self._authored_solution_commands(spec)
        if spec.get("difficulties") and authored_commands:
            commands = [
                *list(spec.get("primary", [])),
                *authored_commands,
                *list(spec.get("supporting", [])),
            ]
        else:
            commands = (
                [*list(spec.get("primary", [])), *list(spec.get("supporting", []))]
                or fallback_commands
            )

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
        focus = " ".join(str(spec.get("focus", "")).split()).lower()
        mapping = {
            "git switch -c": [
                "git switch -c feature/my-feature",
                "git branch -D wrong-branch-name",
                "git branch -a",
                "git log --oneline --graph --all",
            ],
            "git switch, git branch, git checkout": [
                "git branch",
                "git switch feature/demo",
                "git switch -c feature/new",
                "git checkout -b feature/legacy",
                "git log --oneline --graph --all",
            ],
            "git branch": [
                "git branch",
                "git branch -v",
                "git branch -d feature/demo",
                "git branch -a",
            ],
            "git stash": [
                "git stash",
                "git stash list",
                "git stash pop",
                "git stash apply",
                "git stash drop",
            ],
            "git push": [
                "git push -u origin feature/demo",
                "git push origin feature/demo",
                "git push --force-with-lease origin feature/demo",
                "git push origin --delete feature/old",
            ],
            "git fetch, git pull": [
                "git fetch",
                "git pull",
                "git pull --rebase",
                "git fetch --prune",
            ],
            "git merge": [
                "git merge feature/demo",
                "git merge --no-ff feature/demo",
                "git pull --rebase",
            ],
            "git merge --no-ff": [
                "git merge feature/demo",
                "git merge --no-ff feature/demo",
            ],
            "git merge --squash": [
                "git merge --squash feature/demo",
                "git commit",
            ],
            "git push origin --delete": [
                "git push origin --delete feature/old",
                "git push -u origin feature/demo",
                "git fetch --prune",
            ],
        }
        for key, cmds in mapping.items():
            if key in focus:
                return cmds
        return list(spec.get("primary", [])) + list(spec.get("supporting", []))

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

    def _validate_builds(self):
        validator = AuthoredVariantValidator()
        failures = []
        for difficulty in DifficultyInstance.objects.select_related("scenario").filter(
            scenario__learning_unit__slug="branching-and-collaboration",
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
            self.style.SUCCESS("All Module 2 authored practice variants are valid.")
        )
