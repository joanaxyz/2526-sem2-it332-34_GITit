"""Chapter 6 authored adventure levels."""

from __future__ import annotations

from .chapter_3_branching import BRANCH_BASE
from .common import *  # noqa: F403

STASH_REPO = repo(
    commits=BRANCH_BASE,
    branches={"main": "c2", "hotfix/navbar": "c1"},
    # Plain `git stash` shelves tracked changes only; both files are tracked
    # (present in c2) so the working tree ends up clean. (Untracked stashing is a
    # separate `git stash -u` scenario.)
    working_tree={
        "src/app.py": "work in progress",
        "src/dashboard.py": "dashboard wip",
    },
)

STASHED_REPO = repo(
    commits=BRANCH_BASE,
    branches={"main": "c2"},
    stash_stack=[
        {
            "message": "WIP on main: c2 Add dashboard",
            "working_tree": {"src/app.py": "work in progress"},
            "staging": {},
            "head_commit": "c2",
        }
    ],
)

CHERRY_REPO = repo(
    commits=[
        commit("c0", "Initial project", [], {"README.md": "base", "src/app.py": "v1"}),
        commit(
            "c1",
            "Add docs",
            ["c0"],
            {"README.md": "base", "src/app.py": "v1", "docs/guide.md": "guide"},
        ),
        commit(
            "c2",
            "Patch auth guard",
            ["c0"],
            {"README.md": "base", "src/app.py": "v1", "src/auth.py": "guard"},
        ),
    ],
    branches={"main": "c1", "hotfix/auth-guard": "c2"},
)

LEVELS = [
    # Chapter 6 - Temporary Work and Patch Movement
    q(
        "git-stash/push",
        "stash-local-work",
        "Shelve unfinished local work",
        "You need to leave your current branch, but unfinished edits would block the switch.",
        "Shelve the local work and leave the working tree clean.",
        [
            v(
                "stash-app-wip",
                "App WIP",
                STASH_REPO,
                ["git stash"],
                ev(
                    {
                        "working_tree_clean": True,
                        "staging_empty": True,
                        "rules": [
                            {"type": "stash_top_contains", "paths": ["src/app.py", "src/dashboard.py"]}
                        ],
                    },
                    required=["git stash"],
                ),
            ),
            v(
                "stash-readme-wip",
                "Readme WIP",
                repo(
                    commits=BRANCH_BASE,
                    branches={"main": "c2"},
                    working_tree={"README.md": "draft"},
                ),
                ["git stash push"],
                ev(
                    {
                        "working_tree_clean": True,
                        "staging_empty": True,
                        "rules": [{"type": "stash_top_contains", "paths": ["README.md"]}],
                    },
                    required=["git stash"],
                ),
            ),
        ],
        checks=[
            {
                "label": "Working tree is clean and the shelved work is on top of the stash.",
                "requirement": {"working_tree_clean": True, "staging_empty": True},
            }
        ],
        workflow=True,
    ),
    q(
        "git-stash/list",
        "list-stashed-work",
        "List saved stashes",
        "There may be saved work from earlier; inspect it before applying anything.",
        "Inspect the saved stash entries without changing repository state.",
        [
            v(
                "stash-list-one",
                "One stash",
                STASHED_REPO,
                ["git stash list"],
                ev({"repository_state_unchanged": True}, required=["git stash list"]),
            ),
            v(
                "stash-list-two",
                "Two stashes",
                repo(
                    commits=BRANCH_BASE,
                    branches={"main": "c2"},
                    stash_stack=[
                        {
                            "message": "WIP one",
                            "working_tree": {"a": "1"},
                            "staging": {},
                            "head_commit": "c2",
                        },
                        {
                            "message": "WIP two",
                            "working_tree": {"b": "2"},
                            "staging": {},
                            "head_commit": "c2",
                        },
                    ],
                ),
                ["git stash list"],
                ev({"repository_state_unchanged": True}, required=["git stash list"]),
            ),
        ],
        checks=[
            {
                "label": "Stash entries were inspected without mutation.",
                "requirement": {"repository_state_unchanged": True},
            }
        ],
        prerequisites=["stash-local-work"],
        min_counted_commands=0,
        max_counted_commands=2,
    ),
    q(
        "git-stash/pop",
        "pop-top-stash",
        "Restore and remove the top stash",
        "You are back on the right branch and want the most recent shelved work restored, not kept twice.",
        "Restore the top saved work and remove that stash entry.",
        [
            v(
                "stash-pop-app",
                "Pop app work",
                STASHED_REPO,
                ["git stash pop"],
                ev(
                    {
                        "working_tree_contains": ["src/app.py"],
                        "stash_stack_empty": True,
                        "rules": [{"type": "stash_pop_restored_paths", "paths": ["src/app.py"]}],
                    },
                    required=["git stash pop"],
                ),
            ),
            v(
                "stash-pop-readme",
                "Pop readme work",
                repo(
                    commits=BRANCH_BASE,
                    branches={"main": "c2"},
                    stash_stack=[
                        {
                            "message": "WIP readme",
                            "working_tree": {"README.md": "draft"},
                            "staging": {},
                            "head_commit": "c2",
                        }
                    ],
                ),
                ["git stash pop"],
                ev(
                    {
                        "working_tree_contains": ["README.md"],
                        "stash_stack_empty": True,
                        "rules": [{"type": "stash_pop_restored_paths", "paths": ["README.md"]}],
                    },
                    required=["git stash pop"],
                ),
            ),
        ],
        checks=[
            {
                "label": "Saved work returned and the stash stack is empty.",
                "requirement": {"stash_stack_empty": True},
            }
        ],
        prerequisites=["list-stashed-work"],
        workflow=True,
    ),
    q(
        "git-stash/apply",
        "apply-top-stash",
        "Restore a stash but keep it saved",
        "You want to try the saved work again while keeping the stash as a backup.",
        "Restore the top saved work without deleting the stash entry.",
        [
            v(
                "stash-apply-app",
                "Apply app work",
                STASHED_REPO,
                ["git stash apply"],
                ev(
                    {
                        "working_tree_contains": ["src/app.py"],
                        "rules": [{"type": "stash_top_contains", "paths": ["src/app.py"]}],
                    },
                    required=["git stash apply"],
                ),
            ),
            v(
                "stash-apply-readme",
                "Apply readme work",
                repo(
                    commits=BRANCH_BASE,
                    branches={"main": "c2"},
                    stash_stack=[
                        {
                            "message": "WIP readme",
                            "working_tree": {"README.md": "draft"},
                            "staging": {},
                            "head_commit": "c2",
                        }
                    ],
                ),
                ["git stash apply"],
                ev(
                    {
                        "working_tree_contains": ["README.md"],
                        "rules": [{"type": "stash_top_contains", "paths": ["README.md"]}],
                    },
                    required=["git stash apply"],
                ),
            ),
        ],
        checks=[
            {
                "label": "Saved work returned to the working tree (the stash is kept).",
                "requirement": {"working_tree_dirty": True},
            }
        ],
        prerequisites=["list-stashed-work"],
        workflow=True,
    ),
    q(
        "git-stash/drop",
        "drop-top-stash",
        "Delete the top stash entry",
        "An old stash is no longer needed and should not be accidentally applied later.",
        "Remove the top stash entry.",
        [
            v(
                "stash-drop-app",
                "Drop app stash",
                STASHED_REPO,
                ["git stash drop"],
                ev(
                    {
                        "stash_stack_empty": True,
                        "rules": [meta_equals("last_stash_operation", "drop")],
                    },
                    required=["git stash drop"],
                ),
            ),
            v(
                "stash-drop-readme",
                "Drop readme stash",
                repo(
                    commits=BRANCH_BASE,
                    branches={"main": "c2"},
                    stash_stack=[
                        {
                            "message": "WIP readme",
                            "working_tree": {"README.md": "draft"},
                            "staging": {},
                            "head_commit": "c2",
                        }
                    ],
                ),
                ["git stash drop"],
                ev(
                    {
                        "stash_stack_empty": True,
                        "rules": [meta_equals("last_stash_operation", "drop")],
                    },
                    required=["git stash drop"],
                ),
            ),
        ],
        checks=[
            {"label": "The top stash entry is gone.", "requirement": {"stash_stack_empty": True}}
        ],
        prerequisites=["list-stashed-work"],
        workflow=True,
    ),
    q(
        "git-cherry-pick/one-commit",
        "cherry-pick-one-commit",
        "Copy one commit onto the current branch",
        "A useful fix exists on another branch, but the rest of that branch is not ready.",
        "Apply only the requested commit onto the current branch.",
        [
            v(
                "pick-auth-guard",
                "Auth guard fix",
                CHERRY_REPO,
                ["git cherry-pick c2"],
                ev(
                    {
                        "rules": [
                            {"type": "cherry_pick_created_new_commit", "source": "c2"},
                            {"type": "cherry_pick_copied_changes_from", "source": "c2"},
                        ]
                    },
                    required=["git cherry-pick"],
                ),
                details=[{"label": "Commit to copy", "value": "c2"}],
            ),
            v(
                "pick-docs",
                "Docs copy",
                repo(
                    commits=[
                        commit("c0", "Initial", [], {"README.md": "base"}),
                        commit(
                            "c1", "Main work", ["c0"], {"README.md": "base", "src/app.py": "v1"}
                        ),
                        commit(
                            "c2",
                            "Add guide",
                            ["c0"],
                            {"README.md": "base", "docs/guide.md": "guide"},
                        ),
                    ],
                    branches={"main": "c1", "docs/guide": "c2"},
                ),
                ["git cherry-pick c2"],
                ev(
                    {
                        "rules": [
                            {"type": "cherry_pick_created_new_commit", "source": "c2"},
                            {"type": "cherry_pick_copied_changes_from", "source": "c2"},
                        ]
                    },
                    required=["git cherry-pick"],
                ),
                details=[{"label": "Commit to copy", "value": "c2"}],
            ),
        ],
        checks=[
            {
                "label": "A new commit copied the requested source changes.",
                "requirement": {
                    "rules": [{"type": "cherry_pick_created_new_commit", "source": "c2"}]
                },
            }
        ],
        prerequisites=["stash-local-work"],
        workflow=True,
    ),
    q(
        "git-cherry-pick/no-commit",
        "cherry-pick-without-commit",
        "Stage a picked commit without committing",
        "You need the changes from another commit, but you want to inspect them before saving a new checkpoint.",
        "Apply the requested commit into staging without creating a commit yet.",
        [
            v(
                "pick-n-auth",
                "Stage auth guard",
                CHERRY_REPO,
                ["git cherry-pick --no-commit c2"],
                ev(
                    {
                        "staging_contains": ["src/auth.py"],
                        "rules": [meta_equals("last_cherry_pick_no_commit", True)],
                    },
                    required=["git cherry-pick --no-commit"],
                ),
                details=[{"label": "Commit to copy", "value": "c2"}],
            ),
            v(
                "pick-n-docs",
                "Stage guide",
                repo(
                    commits=[
                        commit("c0", "Initial", [], {"README.md": "base"}),
                        commit(
                            "c1", "Main work", ["c0"], {"README.md": "base", "src/app.py": "v1"}
                        ),
                        commit(
                            "c2",
                            "Add guide",
                            ["c0"],
                            {"README.md": "base", "docs/guide.md": "guide"},
                        ),
                    ],
                    branches={"main": "c1", "docs/guide": "c2"},
                ),
                ["git cherry-pick -n c2"],
                ev(
                    {
                        "staging_contains": ["docs/guide.md"],
                        "rules": [meta_equals("last_cherry_pick_no_commit", True)],
                    },
                    required=["git cherry-pick -n"],
                ),
                details=[{"label": "Commit to copy", "value": "c2"}],
            ),
        ],
        checks=[
            {
                "label": "Picked changes are staged and no commit was created automatically.",
                "requirement": {"rules": [meta_equals("last_cherry_pick_no_commit", True)]},
            }
        ],
        prerequisites=["cherry-pick-one-commit"],
        workflow=True,
    ),
]
