"""Chapter 5 authored adventure levels."""

from __future__ import annotations

from .common import *  # noqa: F403

RECOVERY_COMMITS = [
    commit("c0", "Initial project", [], {"README.md": "base", "src/app.py": "v1"}),
    commit(
        "c1",
        "Add login form",
        ["c0"],
        {"README.md": "base", "src/app.py": "v1", "src/login.py": "login"},
    ),
    commit(
        "c2",
        "Add broken analytics",
        ["c1"],
        {
            "README.md": "base",
            "src/app.py": "v1",
            "src/login.py": "login",
            "src/analytics.py": "broken",
        },
    ),
]

LEVELS = [
    # Chapter 5 - Undoing and Recovery
    q(
        "git-commit/amend",
        "amend-latest-commit-message",
        "Amend the latest local commit",
        "The latest local commit has the right content but the message is unclear and has not been shared yet.",
        "Replace the latest commit with a clearer message.",
        [
            v(
                "amend-message-copy",
                "Fix message",
                repo(
                    commits=[
                        commit("c0", "Initial project", [], BASE_TREE),
                        commit("c1", "wip", ["c0"], {**BASE_TREE, "README.md": "Better intro"}),
                    ],
                    branches={"main": "c1"},
                ),
                ["git commit --amend -m 'Update onboarding copy'"],
                ev(
                    {
                        "rules": [
                            {"type": "commit_replaced_by_amend"},
                            {
                                "type": "latest_commit_message_contains",
                                "branch": "main",
                                "text": "Update onboarding copy",
                            },
                        ]
                    },
                    required=["git commit --amend"],
                ),
                details=[{"label": "New commit message", "value": "Update onboarding copy"}],
            ),
            v(
                "amend-message-docs",
                "Fix docs message",
                repo(
                    commits=[
                        commit("c0", "Initial project", [], BASE_TREE),
                        commit("c1", "docs", ["c0"], {**BASE_TREE, "docs/guide.md": "Guide"}),
                    ],
                    branches={"main": "c1"},
                ),
                ["git commit --amend -m 'Add setup guide'"],
                ev(
                    {
                        "rules": [
                            {"type": "commit_replaced_by_amend"},
                            {
                                "type": "latest_commit_message_contains",
                                "branch": "main",
                                "text": "Add setup guide",
                            },
                        ]
                    },
                    required=["git commit --amend"],
                ),
                details=[{"label": "New commit message", "value": "Add setup guide"}],
            ),
        ],
        checks=[
            {
                "label": "The latest local commit was replaced.",
                "requirement": {"rules": [{"type": "commit_replaced_by_amend"}]},
            }
        ],
        workflow=True,
    ),
    q(
        "git-reset/hard-head",
        "reset-hard-one-parent",
        "Move back one commit and clean files",
        "The latest local commit is disposable and should be removed with its file changes.",
        "Move the current branch back one parent and clean the working tree.",
        [
            v(
                "reset-head-analytics",
                "Drop analytics",
                repo(
                    commits=RECOVERY_COMMITS,
                    branches={"main": "c2"},
                    working_tree={"scratch.txt": {"status": "untracked", "content": "tmp"}},
                    staging={"README.md": "staged draft"},
                ),
                ["git reset --hard HEAD~1"],
                ev(
                    {
                        "rules": [{"type": "branch_moved_to", "branch": "main", "commit": "c1"}],
                        "working_tree_clean": True,
                        "staging_empty": True,
                    },
                    required=["git reset --hard"],
                ),
            ),
            v(
                "reset-head-login",
                "Drop login",
                repo(
                    commits=RECOVERY_COMMITS[:2],
                    branches={"main": "c1"},
                    working_tree={"notes.txt": {"status": "untracked", "content": "tmp"}},
                ),
                ["git reset --hard HEAD~1"],
                ev(
                    {
                        "rules": [{"type": "branch_moved_to", "branch": "main", "commit": "c0"}],
                        "working_tree_clean": True,
                        "staging_empty": True,
                    },
                    required=["git reset --hard"],
                ),
            ),
        ],
        checks=[
            {
                "label": "The branch moved backward and local dirt is gone.",
                "requirement": {
                    "working_tree_clean": True,
                    "staging_empty": True,
                    "rules": [meta_equals("last_reset_mode", "hard")],
                },
            }
        ],
        prerequisites=["amend-latest-commit-message"],
        workflow=True,
    ),
    q(
        "git-reset/hard",
        "reset-hard-specific-commit",
        "Reset hard to a named commit",
        "A local branch should return to a specific known-good checkpoint.",
        "Move the branch to the requested commit and clean local changes.",
        [
            v(
                "reset-hard-c0",
                "Back to base",
                repo(
                    commits=RECOVERY_COMMITS,
                    branches={"main": "c2"},
                    working_tree={"src/app.py": "local debug"},
                ),
                ["git reset --hard c0"],
                ev(
                    {
                        "rules": [{"type": "branch_moved_to", "branch": "main", "commit": "c0"}],
                        "working_tree_clean": True,
                        "staging_empty": True,
                    },
                    required=["git reset --hard"],
                ),
                details=[{"label": "Reset to commit", "value": "c0"}],
            ),
            v(
                "reset-hard-c1",
                "Back to login",
                repo(
                    commits=RECOVERY_COMMITS,
                    branches={"main": "c2"},
                    staging={"README.md": "staged"},
                ),
                ["git reset --hard c1"],
                ev(
                    {
                        "rules": [{"type": "branch_moved_to", "branch": "main", "commit": "c1"}],
                        "working_tree_clean": True,
                        "staging_empty": True,
                    },
                    required=["git reset --hard"],
                ),
                details=[{"label": "Reset to commit", "value": "c1"}],
            ),
        ],
        checks=[
            {
                "label": "The branch now points at the named checkpoint and local changes are clean.",
                "requirement": {
                    "working_tree_clean": True,
                    "staging_empty": True,
                    "rules": [meta_equals("last_reset_mode", "hard")],
                },
            }
        ],
        prerequisites=["reset-hard-one-parent"],
        workflow=True,
    ),
    q(
        "git-revert/one-commit",
        "revert-shared-commit",
        "Revert a shared commit safely",
        "A bad commit may already be visible to others, so history should be preserved while undoing its effect.",
        "Create a new commit that reverses the requested earlier commit.",
        [
            v(
                "revert-analytics",
                "Revert analytics",
                repo(commits=RECOVERY_COMMITS, branches={"main": "c2"}),
                ["git revert c2"],
                ev(
                    {
                        "rules": [
                            {"type": "new_revert_commit_exists"},
                            {"type": "revert_preserves_history", "branch": "main", "commit": "c2"},
                        ],
                        "min_commits_on_branch": {"main": 4},
                    },
                    required=["git revert"],
                ),
                details=[{"label": "Commit to revert", "value": "c2"}],
            ),
            v(
                "revert-login",
                "Revert login",
                repo(commits=RECOVERY_COMMITS, branches={"main": "c2"}),
                ["git revert c1"],
                ev(
                    {
                        "rules": [
                            {"type": "new_revert_commit_exists"},
                            {"type": "revert_preserves_history", "branch": "main", "commit": "c1"},
                        ],
                        "min_commits_on_branch": {"main": 4},
                    },
                    required=["git revert"],
                ),
                details=[{"label": "Commit to revert", "value": "c1"}],
            ),
        ],
        checks=[
            {
                "label": "A new revert commit exists and the old commit remains in history.",
                "requirement": {"rules": [{"type": "new_revert_commit_exists"}]},
            }
        ],
        prerequisites=["reset-hard-specific-commit"],
        workflow=True,
    ),
    q(
        "git-revert/no-edit",
        "revert-with-generated-message",
        "Revert using the generated message",
        "A quick rollback should use the standard generated revert message so the reason stays traceable.",
        "Create the revert commit using the generated message.",
        [
            v(
                "revert-noedit-analytics",
                "Generated analytics revert",
                repo(commits=RECOVERY_COMMITS, branches={"main": "c2"}),
                ["git revert --no-edit c2"],
                ev(
                    {
                        "rules": [
                            {"type": "new_revert_commit_exists"},
                            meta_equals("last_revert_no_edit", True),
                        ]
                    },
                    required=["git revert --no-edit"],
                ),
                details=[{"label": "Commit to revert", "value": "c2"}],
            ),
            v(
                "revert-noedit-login",
                "Generated login revert",
                repo(commits=RECOVERY_COMMITS, branches={"main": "c2"}),
                ["git revert --no-edit c1"],
                ev(
                    {
                        "rules": [
                            {"type": "new_revert_commit_exists"},
                            meta_equals("last_revert_no_edit", True),
                        ]
                    },
                    required=["git revert --no-edit"],
                ),
                details=[{"label": "Commit to revert", "value": "c1"}],
            ),
        ],
        checks=[
            {
                "label": "The generated revert path was used.",
                "requirement": {"rules": [meta_equals("last_revert_no_edit", True)]},
            }
        ],
        prerequisites=["revert-shared-commit"],
        workflow=True,
    ),
    q(
        "git-reflog/head",
        "inspect-reflog-for-recovery",
        "Inspect recent HEAD movements",
        "A branch moved unexpectedly, and the fastest clue is the local movement log.",
        "Inspect recent HEAD movements without changing repository state.",
        [
            v(
                "reflog-after-reset",
                "After reset",
                repo(
                    commits=RECOVERY_COMMITS,
                    branches={"main": "c1"},
                    reflog=[
                        {"ref": "HEAD@{0}", "target": "c2", "message": "commit"},
                        {"ref": "HEAD@{1}", "target": "c1", "message": "reset: moving to HEAD~1"},
                    ],
                ),
                ["git reflog"],
                ev({"repository_state_unchanged": True}, required=["git reflog"]),
            ),
            v(
                "reflog-after-amend",
                "After amend",
                repo(
                    commits=RECOVERY_COMMITS,
                    branches={"main": "c2"},
                    reflog=[
                        {
                            "ref": "HEAD@{0}",
                            "target": "c1",
                            "message": "commit --amend: replaced c1",
                        }
                    ],
                ),
                ["git reflog"],
                ev({"repository_state_unchanged": True}, required=["git reflog"]),
            ),
        ],
        checks=[
            {
                "label": "Reflog was inspected without mutation.",
                "requirement": {
                    "repository_state_unchanged": True,
                    "required_commands": ["git reflog"],
                },
            }
        ],
        prerequisites=["reset-hard-one-parent"],
        min_counted_commands=0,
        max_counted_commands=2,
    ),
]
