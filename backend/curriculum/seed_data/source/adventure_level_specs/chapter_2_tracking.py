"""Chapter 2 authored adventure levels."""

from __future__ import annotations

from .common import *  # noqa: F403

LEVELS = [
    # Chapter 2 - Tracking Changes and Snapshots
    q(
        "git-diff/working",
        "inspect-working-diff",
        "Review an edit, then save it",
        "You edited a tracked file and want to confirm the exact change before committing it.",
        "Use a diff to review the unstaged edit, then stage and commit it.",
        [
            v(
                "diff-working-app",
                "App edit",
                repo(commits=BASE, working_tree={"src/app.py": "print('hello level')\n"}),
                ["git diff", "git add src/app.py", "git commit -m 'Update greeting'"],
                ev(
                    {
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["src/app.py"],
                            "message_contains": ["Update greeting"],
                        },
                        "working_tree_clean": True,
                    },
                    required=["git diff", "git commit"],
                ),
            ),
            v(
                "diff-working-readme",
                "Readme edit",
                repo(commits=BASE, working_tree={"README.md": "Updated project notes"}),
                ["git diff", "git add README.md", "git commit -m 'Refresh project notes'"],
                ev(
                    {
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["README.md"],
                            "message_contains": ["Refresh project notes"],
                        },
                        "working_tree_clean": True,
                    },
                    required=["git diff", "git commit"],
                ),
            ),
        ],
        checks=[
            {
                "label": "The reviewed edit is committed.",
                "requirement": {"min_commits_on_branch": {"main": 2}},
            },
            {
                "label": "Nothing is left uncommitted.",
                "requirement": {"working_tree_clean": True},
            },
        ],
        min_counted_commands=1,
        max_counted_commands=4,
        workflow=True,
    ),
    q(
        "git-add/file",
        "stage-one-file",
        "Save only the file that is ready",
        "Two files are changed, but only one is ready to ship; the other still needs work.",
        "Stage just the ready file and commit it, leaving the unfinished work behind.",
        [
            v(
                "stage-file-app",
                "Ship app, hold readme",
                repo(
                    commits=BASE,
                    working_tree={"src/app.py": "print('ready')\n", "README.md": "draft notes"},
                ),
                ["git status", "git add src/app.py", "git commit -m 'Ship app update'"],
                ev(
                    {
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["src/app.py"],
                            "message_contains": ["Ship app update"],
                        },
                        "working_tree_contains": ["README.md"],
                    },
                    required=["git add", "git commit"],
                ),
            ),
            v(
                "stage-file-readme",
                "Ship readme, hold app",
                repo(
                    commits=BASE,
                    working_tree={"README.md": "ready notes", "src/app.py": "debug print"},
                ),
                ["git status", "git add README.md", "git commit -m 'Update setup notes'"],
                ev(
                    {
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["README.md"],
                            "message_contains": ["Update setup notes"],
                        },
                        "working_tree_contains": ["src/app.py"],
                    },
                    required=["git add", "git commit"],
                ),
            ),
        ],
        checks=[
            {
                "label": "The ready file is saved in a new commit.",
                "requirement": {"min_commits_on_branch": {"main": 2}},
            },
        ],
        prerequisites=["inspect-working-diff"],
        workflow=True,
    ),
    q(
        "git-add/dot",
        "stage-visible-folder-work",
        "Save a whole batch of changes together",
        "A small docs update is complete and every visible changed file belongs in one snapshot.",
        "Stage all the visible work at once, then commit it as a single checkpoint.",
        [
            v(
                "stage-dot-docs",
                "Docs batch",
                repo(
                    commits=BASE,
                    working_tree={
                        "README.md": "new intro",
                        "docs/guide.md": {"status": "untracked", "content": "Guide"},
                    },
                ),
                ["git add .", "git commit -m 'Refresh docs'"],
                ev(
                    {
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["README.md", "docs/guide.md"],
                            "message_contains": ["Refresh docs"],
                        },
                        "working_tree_clean": True,
                    },
                    required=["git add", "git commit"],
                ),
            ),
            v(
                "stage-dot-ui",
                "UI batch",
                repo(
                    commits=BASE,
                    working_tree={
                        "src/app.py": "print('ui')\n",
                        "src/theme.css": {"status": "untracked", "content": "body{}"},
                    },
                ),
                ["git add .", "git commit -m 'Add theme styles'"],
                ev(
                    {
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["src/app.py", "src/theme.css"],
                            "message_contains": ["Add theme styles"],
                        },
                        "working_tree_clean": True,
                    },
                    required=["git add", "git commit"],
                ),
            ),
        ],
        checks=[
            {
                "label": "All the visible work is saved together.",
                "requirement": {"working_tree_clean": True},
            },
            {
                "label": "A new snapshot was saved.",
                "requirement": {"min_commits_on_branch": {"main": 2}},
            },
        ],
        prerequisites=["stage-one-file"],
        workflow=True,
    ),
    q(
        "git-add/all",
        "stage-all-changes",
        "Stage every tracked and untracked change",
        "A cleanup commit should include all adds, edits, and removals that are currently visible.",
        "Prepare every working-tree change for the next snapshot.",
        [
            v(
                "stage-all-cleanup",
                "Cleanup batch",
                repo(
                    commits=BASE,
                    working_tree={
                        "src/app.py": "print('clean')\n",
                        "tmp.log": {"status": "untracked", "content": "log"},
                    },
                ),
                ["git add -A"],
                ev(
                    {"staging_contains": ["src/app.py", "tmp.log"], "working_tree_clean": True},
                    required=["git add"],
                ),
            ),
            v(
                "stage-all-assets",
                "Asset batch",
                repo(
                    commits=BASE,
                    working_tree={
                        "README.md": "new",
                        "assets/logo.svg": {"status": "untracked", "content": "svg"},
                    },
                ),
                ["git add --all"],
                ev(
                    {
                        "staging_contains": ["README.md", "assets/logo.svg"],
                        "working_tree_clean": True,
                    },
                    required=["git add"],
                ),
            ),
        ],
        checks=[
            {
                "label": "All working changes are staged.",
                "requirement": {"working_tree_clean": True},
            }
        ],
        prerequisites=["stage-visible-folder-work"],
        workflow=True,
    ),
    q(
        "git-add/patch",
        "stage-selected-hunks",
        "Stage selected hunks only",
        "One file has a useful fix and an unrelated draft hunk. Only the useful hunk belongs in the next snapshot.",
        "Stage the selected hunk while leaving the unrelated hunk in the working tree.",
        [
            v(
                "patch-login-hunk",
                "Login hunk",
                repo(
                    commits=BASE,
                    working_tree={
                        "src/app.py": {
                            "status": "modified",
                            "hunks": ["login validation", "debug draft"],
                        }
                    },
                    partial_hunks={
                        "src/app.py": {
                            "target_hunks": ["login validation"],
                            "leftover_hunks": ["debug draft"],
                        }
                    },
                ),
                ["git add -p src/app.py"],
                ev(
                    {
                        "rules": [
                            {
                                "type": "staging_contains_tokens",
                                "path": "src/app.py",
                                "tokens": ["login validation"],
                            },
                            {
                                "type": "working_tree_contains_tokens",
                                "path": "src/app.py",
                                "tokens": ["debug draft"],
                            },
                        ]
                    },
                    required=["git add -p"],
                ),
            ),
            v(
                "patch-copy-hunk",
                "Copy hunk",
                repo(
                    commits=BASE,
                    working_tree={
                        "README.md": {
                            "status": "modified",
                            "hunks": ["clear install steps", "future roadmap"],
                        }
                    },
                    partial_hunks={
                        "README.md": {
                            "target_hunks": ["clear install steps"],
                            "leftover_hunks": ["future roadmap"],
                        }
                    },
                ),
                ["git add --patch README.md"],
                ev(
                    {
                        "rules": [
                            {
                                "type": "staging_contains_tokens",
                                "path": "README.md",
                                "tokens": ["clear install steps"],
                            },
                            {
                                "type": "working_tree_contains_tokens",
                                "path": "README.md",
                                "tokens": ["future roadmap"],
                            },
                        ]
                    },
                    required=["git add --patch"],
                ),
            ),
        ],
        checks=[
            {
                "label": "Your selected hunk is staged.",
                "requirement": {"staging_not_empty": True},
            }
        ],
        prerequisites=["stage-one-file"],
        workflow=True,
    ),
    q(
        "git-diff/staged",
        "inspect-staged-diff",
        "Verify staged content, then save",
        "A file is already staged for the next snapshot; verify the staged content before sealing it.",
        "Use a staged diff to confirm what will be committed, then commit it.",
        [
            v(
                "diff-staged-app",
                "Staged app",
                repo(commits=BASE, staging={"src/app.py": "print('ready')\n"}),
                ["git diff --staged", "git commit -m 'Save reviewed app change'"],
                ev(
                    {
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["src/app.py"],
                            "message_contains": ["Save reviewed app change"],
                        },
                        "staging_empty": True,
                        "working_tree_clean": True,
                    },
                    required=["git diff --staged", "git commit"],
                ),
            ),
            v(
                "diff-staged-readme",
                "Staged readme",
                repo(commits=BASE, staging={"README.md": "ready notes"}),
                ["git diff --cached", "git commit -m 'Save reviewed notes'"],
                ev(
                    {
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["README.md"],
                            "message_contains": ["Save reviewed notes"],
                        },
                        "staging_empty": True,
                        "working_tree_clean": True,
                    },
                    required=["git diff --cached", "git commit"],
                ),
            ),
        ],
        checks=[
            {
                "label": "The verified content is committed.",
                "requirement": {"min_commits_on_branch": {"main": 2}},
            },
            {
                "label": "The staging area is clear.",
                "requirement": {"staging_empty": True},
            },
        ],
        prerequisites=["stage-one-file"],
        min_counted_commands=1,
        max_counted_commands=4,
        workflow=True,
    ),
    q(
        "git-commit/message",
        "commit-staged-snapshot",
        "Save a change end to end",
        "A tracked file has new work in the working tree and needs to become a clear local checkpoint.",
        "Check what changed, stage the file, then save it with the required message.",
        [
            v(
                "commit-login-copy",
                "Login copy",
                repo(commits=BASE, working_tree={"src/app.py": "print('login copy')\n"}),
                ["git status", "git add src/app.py", "git commit -m 'Update login copy'"],
                ev(
                    {
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["src/app.py"],
                            "message_contains": ["Update login copy"],
                        },
                        "staging_empty": True,
                        "working_tree_clean": True,
                    },
                    required=["git add", "git commit"],
                ),
            ),
            v(
                "commit-readme-setup",
                "Readme setup",
                repo(commits=BASE, working_tree={"README.md": "Install steps"}),
                ["git status", "git add README.md", "git commit -m 'Update setup notes'"],
                ev(
                    {
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["README.md"],
                            "message_contains": ["Update setup notes"],
                        },
                        "staging_empty": True,
                        "working_tree_clean": True,
                    },
                    required=["git add", "git commit"],
                ),
            ),
        ],
        checks=[
            {
                "label": "The change is saved in a new commit.",
                "requirement": {"min_commits_on_branch": {"main": 2}},
            },
            {
                "label": "Nothing is left uncommitted.",
                "requirement": {"working_tree_clean": True},
            },
        ],
        prerequisites=["stage-one-file", "inspect-staged-diff"],
        workflow=True,
    ),
    q(
        "git-commit/all-message",
        "commit-tracked-changes-directly",
        "Commit tracked edits directly",
        "Only tracked files should be saved; a new scratch file must remain untracked.",
        "Save the tracked edits in one checkpoint while leaving scratch work alone.",
        [
            v(
                "commit-all-app",
                "Tracked app edit",
                repo(
                    commits=BASE,
                    working_tree={
                        "src/app.py": "print('tracked')\n",
                        "scratch.txt": {"status": "untracked", "content": "notes"},
                    },
                ),
                ["git commit -a -m 'Update tracked app'"],
                ev(
                    {
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["src/app.py"],
                            "excludes_paths": ["scratch.txt"],
                            "message_contains": ["Update tracked app"],
                        },
                        "working_tree_contains": ["scratch.txt"],
                    },
                    required=["git commit"],
                ),
                details=[{"label": "Commit message", "value": "Update tracked app"}],
            ),
            v(
                "commit-all-readme",
                "Tracked readme edit",
                repo(
                    commits=BASE,
                    working_tree={
                        "README.md": "tracked notes",
                        "idea.md": {"status": "untracked", "content": "later"},
                    },
                ),
                ["git commit -a -m 'Update tracked notes'"],
                ev(
                    {
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["README.md"],
                            "excludes_paths": ["idea.md"],
                            "message_contains": ["Update tracked notes"],
                        },
                        "working_tree_contains": ["idea.md"],
                    },
                    required=["git commit"],
                ),
                details=[{"label": "Commit message", "value": "Update tracked notes"}],
            ),
        ],
        checks=[
            {
                "label": "Your tracked edits are saved in a new commit.",
                "requirement": {"min_commits_on_branch": {"main": 2}},
            }
        ],
        prerequisites=["commit-staged-snapshot"],
        workflow=True,
    ),
    q(
        "git-restore/staged-file",
        "unstage-one-file",
        "Move a staged file back out of staging",
        "A file was staged too early and needs more review before it belongs in the next snapshot.",
        "Remove the requested file from staging while keeping its work in the working tree.",
        [
            v(
                "unstage-app",
                "Unstage app",
                repo(commits=BASE, staging={"src/app.py": "print('draft')\n"}),
                ["git restore --staged src/app.py"],
                ev(
                    {
                        "working_tree_contains": ["src/app.py"],
                        "rules": [{"type": "staging_excludes", "paths": ["src/app.py"]}],
                    },
                    required=["git restore"],
                ),
            ),
            v(
                "unstage-readme",
                "Unstage readme",
                repo(commits=BASE, staging={"README.md": "draft"}),
                ["git restore --staged README.md"],
                ev(
                    {
                        "working_tree_contains": ["README.md"],
                        "rules": [{"type": "staging_excludes", "paths": ["README.md"]}],
                    },
                    required=["git restore"],
                ),
            ),
        ],
        checks=[
            {
                "label": "The file is no longer staged (its work stays in the working tree).",
                "requirement": {"staging_empty": True},
            }
        ],
        prerequisites=["stage-one-file"],
        workflow=True,
    ),
    q(
        "git-restore/working-file",
        "discard-working-file-change",
        "Discard an unwanted working-tree change",
        "A debug edit should be thrown away, not saved or staged.",
        "Restore the requested file back to the committed version.",
        [
            v(
                "restore-app-debug",
                "Discard app debug",
                repo(commits=BASE, working_tree={"src/app.py": "print('debug')\n"}),
                ["git restore src/app.py"],
                ev({"working_tree_clean": True, "staging_empty": True}, required=["git restore"]),
            ),
            v(
                "restore-readme-draft",
                "Discard readme draft",
                repo(commits=BASE, working_tree={"README.md": "bad draft"}),
                ["git restore README.md"],
                ev({"working_tree_clean": True, "staging_empty": True}, required=["git restore"]),
            ),
        ],
        checks=[
            {
                "label": "The unwanted working change is gone.",
                "requirement": {"working_tree_clean": True},
            }
        ],
        prerequisites=["inspect-working-diff"],
        workflow=True,
    ),
    q(
        "git-rm/tracked-file",
        "remove-tracked-file",
        "Remove a tracked file from the next commit",
        "A tracked debug file should disappear from the project history going forward.",
        "Stage the removal of the requested tracked file.",
        [
            v(
                "rm-debug-log",
                "Remove debug log",
                repo(
                    commits=[
                        commit("c0", "Initial project", [], {**BASE_TREE, "debug.log": "trace"})
                    ],
                    branches={"main": "c0"},
                ),
                ["git rm debug.log"],
                ev(
                    {"working_tree_absent": ["debug.log"], "staging_contains": ["debug.log"]},
                    required=["git rm"],
                ),
            ),
            v(
                "rm-old-report",
                "Remove old report",
                repo(
                    commits=[
                        commit("c0", "Initial project", [], {**BASE_TREE, "reports/old.txt": "old"})
                    ],
                    branches={"main": "c0"},
                ),
                ["git rm reports/old.txt"],
                ev(
                    {
                        "working_tree_absent": ["reports/old.txt"],
                        "staging_contains": ["reports/old.txt"],
                    },
                    required=["git rm"],
                ),
            ),
        ],
        checks=[
            {
                "label": "The file's removal is staged for the next commit.",
                "requirement": {"staging_not_empty": True},
            }
        ],
        prerequisites=["commit-staged-snapshot"],
        workflow=True,
    ),
    q(
        "git-rm/cached",
        "stop-tracking-local-file",
        "Stop tracking a file but keep it locally",
        "A local configuration file was accidentally tracked and should stay on disk but leave future commits.",
        "Stage the file for removal from tracking while preserving the local copy.",
        [
            v(
                "rm-cached-env",
                "Keep local env",
                repo(
                    commits=[commit("c0", "Track env", [], {**BASE_TREE, ".env": "SECRET=1"})],
                    branches={"main": "c0"},
                ),
                ["git rm --cached .env"],
                ev(
                    {
                        "staging_contains": [".env"],
                        "working_tree_contains": [".env"],
                        "rules": [meta_equals("last_rm_cached_paths", [".env"])],
                    },
                    required=["git rm --cached"],
                ),
            ),
            v(
                "rm-cached-local",
                "Keep local settings",
                repo(
                    commits=[commit("c0", "Track settings", [], {**BASE_TREE, "local.json": "{}"})],
                    branches={"main": "c0"},
                ),
                ["git rm --cached local.json"],
                ev(
                    {
                        "staging_contains": ["local.json"],
                        "working_tree_contains": ["local.json"],
                        "rules": [meta_equals("last_rm_cached_paths", ["local.json"])],
                    },
                    required=["git rm --cached"],
                ),
            ),
        ],
        checks=[
            {
                "label": "The file's untracking is staged (the local copy is kept).",
                "requirement": {"staging_not_empty": True},
            }
        ],
        prerequisites=["remove-tracked-file"],
        workflow=True,
    ),
]
