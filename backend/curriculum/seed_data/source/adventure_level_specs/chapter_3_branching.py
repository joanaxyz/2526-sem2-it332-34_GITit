"""Chapter 3 authored adventure levels."""

from __future__ import annotations

from .common import *  # noqa: F403

BRANCH_BASE = [
    commit("c0", "Initial project", [], {"README.md": "base"}),
    commit("c1", "Add app shell", ["c0"], {"README.md": "base", "src/app.py": "v1"}),
    commit(
        "c2",
        "Add dashboard",
        ["c1"],
        {"README.md": "base", "src/app.py": "v1", "src/dashboard.py": "v1"},
    ),
]

LEVELS = [
    # Chapter 3 - Branch Navigation
    q(
        "git-branch/list",
        "list-local-branches",
        "List local branches",
        "Before switching work streams, you need to see which local branch names already exist.",
        "Inspect local branch names without changing repository state.",
        [
            v(
                "branch-list-feature",
                "Feature branches",
                repo(commits=BRANCH_BASE, branches={"main": "c2", "feature/login": "c2"}),
                ["git branch"],
                ev({"repository_state_unchanged": True}, required=["git branch"]),
            ),
            v(
                "branch-list-hotfix",
                "Hotfix branches",
                repo(commits=BRANCH_BASE, branches={"main": "c2", "hotfix/copy": "c1"}),
                ["git branch"],
                ev({"repository_state_unchanged": True}, required=["git branch"]),
            ),
        ],
        checks=[
            {
                "label": "Branches were inspected without mutation.",
                "requirement": {
                    "repository_state_unchanged": True,
                    "required_commands": ["git branch"],
                },
            }
        ],
        min_counted_commands=0,
        max_counted_commands=2,
    ),
    q(
        "git-branch/create",
        "create-branch-pointer",
        "Create a branch without switching",
        "A teammate needs a branch pointer prepared, but you should keep working on the current branch for now.",
        "Create the requested branch while leaving HEAD where it is.",
        [
            v(
                "branch-create-profile",
                "Profile branch",
                repo(commits=BRANCH_BASE, branches={"main": "c2"}),
                ["git branch feature/profile"],
                ev(
                    {
                        "branch_exists": ["feature/profile"],
                        "head_branch": "main",
                        "branch_points_to": {"feature/profile": "c2"},
                    },
                    required=["git branch"],
                ),
                details=[{"label": "Branch to create", "value": "feature/profile"}],
            ),
            v(
                "branch-create-docs",
                "Docs branch",
                repo(commits=BRANCH_BASE, branches={"main": "c2"}),
                ["git branch docs-refresh"],
                ev(
                    {
                        "branch_exists": ["docs-refresh"],
                        "head_branch": "main",
                        "branch_points_to": {"docs-refresh": "c2"},
                    },
                    required=["git branch"],
                ),
                details=[{"label": "Branch to create", "value": "docs-refresh"}],
            ),
        ],
        checks=[
            {
                "label": "A new branch pointer was created.",
                "requirement": {"local_branches_min": 2},
            }
        ],
        prerequisites=["list-local-branches"],
        workflow=True,
    ),
    q(
        "git-branch/create-at-start",
        "create-branch-at-start-point",
        "Create a branch at an older start point",
        "A hotfix needs to start from a stable commit instead of the latest work on main.",
        "Create the requested branch pointer at the specified existing commit.",
        [
            v(
                "branch-start-c1",
                "Hotfix from c1",
                repo(commits=BRANCH_BASE, branches={"main": "c2"}),
                ["git branch hotfix/login c1"],
                ev(
                    {
                        "branch_exists": ["hotfix/login"],
                        "branch_points_to": {"hotfix/login": "c1"},
                        "head_branch": "main",
                    },
                    required=["git branch"],
                ),
                details=[
                    {"label": "Branch to create", "value": "hotfix/login"},
                    {"label": "Start point", "value": "c1"},
                ],
            ),
            v(
                "branch-start-c0",
                "Archive from c0",
                repo(commits=BRANCH_BASE, branches={"main": "c2"}),
                ["git branch archive/base c0"],
                ev(
                    {
                        "branch_exists": ["archive/base"],
                        "branch_points_to": {"archive/base": "c0"},
                        "head_branch": "main",
                    },
                    required=["git branch"],
                ),
                details=[
                    {"label": "Branch to create", "value": "archive/base"},
                    {"label": "Start point", "value": "c0"},
                ],
            ),
        ],
        checks=[
            {
                "label": "A new branch pointer was created at the requested commit.",
                "requirement": {"local_branches_min": 2},
            }
        ],
        prerequisites=["create-branch-pointer"],
        workflow=True,
    ),
    q(
        "git-switch/existing",
        "switch-existing-branch",
        "Switch to an existing branch",
        "The next task belongs on a branch that already exists locally.",
        "Move HEAD to the requested branch without creating a new one.",
        [
            v(
                "switch-docs",
                "Docs handoff",
                repo(commits=BRANCH_BASE, branches={"main": "c2", "docs-refresh": "c2"}),
                ["git switch docs-refresh"],
                ev({"head_branch": "docs-refresh", "staging_empty": True}, required=["git switch"]),
                details=[{"label": "Branch to switch to", "value": "docs-refresh"}],
            ),
            v(
                "switch-feature",
                "Feature handoff",
                repo(commits=BRANCH_BASE, branches={"main": "c2", "feature/profile": "c2"}),
                ["git switch feature/profile"],
                ev(
                    {"head_branch": "feature/profile", "staging_empty": True},
                    required=["git switch"],
                ),
                details=[{"label": "Branch to switch to", "value": "feature/profile"}],
            ),
        ],
        checks=[
            {
                "label": "HEAD moved onto the requested branch.",
                "requirement": {"head_branch_changed": True},
            }
        ],
        prerequisites=["list-local-branches"],
        workflow=True,
    ),
    q(
        "git-switch/create",
        "create-and-switch-branch",
        "Create a branch and switch to it",
        "A new task starts now, so the branch should be created and checked out immediately.",
        "Create the requested branch and move HEAD onto it.",
        [
            v(
                "switch-create-auth",
                "Auth branch",
                repo(commits=BRANCH_BASE, branches={"main": "c2"}),
                ["git switch -c feature/auth"],
                ev(
                    {"branch_exists": ["feature/auth"], "head_branch": "feature/auth"},
                    required=["git switch -c"],
                ),
                details=[{"label": "Branch to create", "value": "feature/auth"}],
            ),
            v(
                "switch-create-ui",
                "UI branch",
                repo(commits=BRANCH_BASE, branches={"main": "c2"}),
                ["git switch --create feature/ui-polish"],
                ev(
                    {"branch_exists": ["feature/ui-polish"], "head_branch": "feature/ui-polish"},
                    required=["git switch --create"],
                ),
                details=[{"label": "Branch to create", "value": "feature/ui-polish"}],
            ),
        ],
        checks=[
            {
                "label": "The new branch was created.",
                "requirement": {"local_branches_min": 2},
            },
            {
                "label": "HEAD moved onto the new branch.",
                "requirement": {"head_branch_changed": True},
            },
        ],
        prerequisites=["create-branch-pointer"],
        workflow=True,
    ),
    q(
        "git-checkout/legacy-create",
        "legacy-create-and-switch",
        "Use legacy create-and-switch spelling",
        "An older team note uses the legacy branch command form, and you need to recognize the equivalent operation.",
        "Create the requested branch and move HEAD onto it using the legacy spelling.",
        [
            v(
                "checkout-create-legacy",
                "Legacy branch",
                repo(commits=BRANCH_BASE, branches={"main": "c2"}),
                ["git checkout -b feature/legacy-ui"],
                ev(
                    {"branch_exists": ["feature/legacy-ui"], "head_branch": "feature/legacy-ui"},
                    required=["git checkout -b"],
                ),
                details=[{"label": "Branch to create", "value": "feature/legacy-ui"}],
            ),
            v(
                "checkout-create-hotfix",
                "Legacy hotfix",
                repo(commits=BRANCH_BASE, branches={"main": "c2"}),
                ["git checkout -b hotfix/navbar c1"],
                ev(
                    {
                        "branch_exists": ["hotfix/navbar"],
                        "head_branch": "hotfix/navbar",
                        "branch_points_to": {"hotfix/navbar": "c1"},
                    },
                    required=["git checkout -b"],
                ),
                details=[
                    {"label": "Branch to create", "value": "hotfix/navbar"},
                    {"label": "Start point", "value": "c1"},
                ],
            ),
        ],
        checks=[
            {
                "label": "The new branch was created.",
                "requirement": {"local_branches_min": 2},
            },
            {
                "label": "HEAD moved onto the new branch.",
                "requirement": {"head_branch_changed": True},
            },
        ],
        prerequisites=["create-and-switch-branch"],
        workflow=True,
    ),
    q(
        "git-switch/detach",
        "inspect-detached-commit",
        "Detach HEAD at a commit for inspection",
        "You need to inspect an older snapshot without moving any branch pointer.",
        "Move HEAD directly to the requested commit while keeping branch pointers unchanged.",
        [
            v(
                "switch-detach-c1",
                "Inspect c1",
                repo(commits=BRANCH_BASE, branches={"main": "c2"}),
                ["git switch --detach c1"],
                ev(
                    {
                        "rules": [{"type": "head_detached_at", "commit": "c1"}],
                        "branch_points_to": {"main": "c2"},
                    },
                    required=["git switch --detach"],
                ),
                details=[{"label": "Commit to inspect", "value": "c1"}],
            ),
            v(
                "switch-detach-c0",
                "Inspect c0",
                repo(commits=BRANCH_BASE, branches={"main": "c2"}),
                ["git switch --detach c0"],
                ev(
                    {
                        "rules": [{"type": "head_detached_at", "commit": "c0"}],
                        "branch_points_to": {"main": "c2"},
                    },
                    required=["git switch --detach"],
                ),
                details=[{"label": "Commit to inspect", "value": "c0"}],
            ),
        ],
        checks=[
            {
                "label": "HEAD is detached at the requested commit.",
                "requirement": {"head_detached": True},
            }
        ],
        prerequisites=["switch-existing-branch"],
        workflow=True,
    ),
    q(
        "git-branch/delete",
        "delete-merged-branch",
        "Delete a safe local branch pointer",
        "A branch has already been integrated, so keeping the old local pointer creates clutter.",
        "Remove the requested local branch pointer while staying on the current branch.",
        [
            v(
                "branch-delete-docs",
                "Delete docs branch",
                repo(commits=BRANCH_BASE, branches={"main": "c2", "docs-refresh": "c1"}),
                ["git branch -d docs-refresh"],
                ev(
                    {"branch_absent": ["docs-refresh"], "head_branch": "main"},
                    required=["git branch -d"],
                ),
                details=[{"label": "Branch to delete", "value": "docs-refresh"}],
            ),
            v(
                "branch-delete-old",
                "Delete old branch",
                repo(commits=BRANCH_BASE, branches={"main": "c2", "old/navbar": "c1"}),
                ["git branch --delete old/navbar"],
                ev(
                    {"branch_absent": ["old/navbar"], "head_branch": "main"},
                    required=["git branch --delete"],
                ),
                details=[{"label": "Branch to delete", "value": "old/navbar"}],
            ),
        ],
        checks=[
            {
                "label": "The branch pointer was removed.",
                "requirement": {"local_branches_at_most": 1},
            }
        ],
        prerequisites=["switch-existing-branch"],
        workflow=True,
    ),
]
