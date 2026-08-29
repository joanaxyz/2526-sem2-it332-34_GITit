"""Catalog completeness adventure levels."""

from __future__ import annotations

from .chapter_3_branching import BRANCH_BASE
from .chapter_4_merging import MERGE_BASE, PRECONFLICT
from .chapter_6_patches import CHERRY_REPO
from .common import *  # noqa: F403

LEVELS = [
    # Catalog completeness pass - supported forms not covered by the original seed.
    q(
        "git-clone/default-folder",
        "clone-default-folder",
        "Clone into the default folder",
        "The remote project name is already the right local folder name.",
        "Clone the remote repository without specifying a custom destination.",
        [
            v(
                "clone-default-starter",
                "Default clone",
                uninitialized({}, remote_fixtures=REMOTE_FIXTURE_MAIN),
                [
                    "git clone https://example.test/cit/starter.git",
                    "git status",
                    "git log --oneline",
                ],
                ev(
                    {
                        "repository_initialized": True,
                        "remote_exists": ["origin"],
                        "upstream_tracking_set": ["main"],
                    },
                    required=["git clone"],
                ),
                details=[{"label": "Repository URL", "value": "https://example.test/cit/starter.git"}],
            ),
        ],
        checks=[
            {
                "label": "The project is cloned into the default folder.",
                "requirement": {"repository_initialized": True},
            },
            {
                "label": "Origin remote is configured.",
                "requirement": {"remote_exists": ["origin"]},
            },
        ],
        prerequisites=["init-current-folder"],
        workflow=True,
    ),
    q(
        "git-status/short",
        "inspect-short-status",
        "Use compact status to finish a save",
        "One file is already staged and another is still modified; a quick compact readout shows both.",
        "Read compact status, stage the remaining file, then commit everything together.",
        [
            v(
                "status-short-app",
                "Finish the save",
                repo(
                    commits=BASE,
                    working_tree={"README.md": "changed"},
                    staging={"src/app.py": "print('staged')\n"},
                ),
                ["git status -s", "git add README.md", "git commit -m 'Save app and notes'"],
                ev(
                    {
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["src/app.py", "README.md"],
                            "message_contains": ["Save app and notes"],
                        },
                        "working_tree_clean": True,
                    },
                    required=["git status -s", "git commit"],
                ),
            ),
        ],
        checks=[
            {
                "label": "Both changes are saved together.",
                "requirement": {"working_tree_clean": True},
            },
            {
                "label": "A new snapshot was saved.",
                "requirement": {"min_commits_on_branch": {"main": 2}},
            },
        ],
        prerequisites=["inspect-status"],
        min_counted_commands=1,
        max_counted_commands=4,
        workflow=True,
    ),
    q(
        "git-status/porcelain",
        "inspect-porcelain-status",
        "Use script-stable status, then save",
        "You want the stable, machine-readable status shape before committing a change.",
        "Read porcelain status, then stage and commit the change it reveals.",
        [
            v(
                "status-porcelain-app",
                "Save the revealed change",
                repo(commits=BASE, working_tree={"README.md": "changed"}),
                [
                    "git status --porcelain",
                    "git add README.md",
                    "git commit -m 'Apply readme change'",
                ],
                ev(
                    {
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["README.md"],
                            "message_contains": ["Apply readme change"],
                        },
                        "working_tree_clean": True,
                    },
                    required=["git status --porcelain", "git commit"],
                ),
            ),
        ],
        checks=[
            {
                "label": "The revealed change is saved.",
                "requirement": {"working_tree_clean": True},
            },
            {
                "label": "A new snapshot was saved.",
                "requirement": {"min_commits_on_branch": {"main": 2}},
            },
        ],
        prerequisites=["inspect-short-status"],
        min_counted_commands=1,
        max_counted_commands=4,
        workflow=True,
    ),
    q(
        "git-config/global-user-name",
        "set-global-user-name",
        "Set your author name, then confirm it",
        "Commits need an author identity. Set your global name, then confirm it landed in your config.",
        "Set the global user.name, then list your config to confirm it is registered.",
        [
            v(
                "config-name-learner-a",
                "Learner A",
                repo(commits=BASE),
                ["git config --global user.name 'Learner A'", "git config --list"],
                ev(
                    {
                        "rules": [
                            meta_equals("last_config_scope", "global"),
                            meta_equals("last_config_key", "user.name"),
                            meta_equals("last_config_value", "Learner A"),
                        ]
                    },
                    required=["git config --global user.name", "git config --list"],
                ),
                details=[{"label": "Name to set", "value": "Learner A"}],
            ),
            v(
                "config-name-learner-b",
                "Learner B",
                repo(commits=BASE),
                ["git config --global user.name 'Learner B'", "git config --list"],
                ev(
                    {
                        "rules": [
                            meta_equals("last_config_scope", "global"),
                            meta_equals("last_config_key", "user.name"),
                            meta_equals("last_config_value", "Learner B"),
                        ]
                    },
                    required=["git config --global user.name", "git config --list"],
                ),
                details=[{"label": "Name to set", "value": "Learner B"}],
            ),
        ],
        checks=[
            {
                "label": "Your author name is saved in global config.",
                "requirement": {"rules": [meta_equals("last_config_key", "user.name")]},
            }
        ],
        prerequisites=["init-current-folder"],
        workflow=True,
    ),
    q(
        "git-config/global-user-email",
        "set-global-user-email",
        "Set your author email, then confirm it",
        "Your commits also need an email identity. Set it globally, then confirm it is registered.",
        "Set the global user.email, then list your config to confirm it is registered.",
        [
            v(
                "config-email-learner-a",
                "Learner A's email",
                repo(commits=BASE),
                ["git config --global user.email learner-a@example.test", "git config --list"],
                ev(
                    {
                        "rules": [
                            meta_equals("last_config_scope", "global"),
                            meta_equals("last_config_key", "user.email"),
                            meta_equals("last_config_value", "learner-a@example.test"),
                        ]
                    },
                    required=["git config --global user.email", "git config --list"],
                ),
                details=[{"label": "Email to set", "value": "learner-a@example.test"}],
            ),
            v(
                "config-email-learner-b",
                "Learner B's email",
                repo(commits=BASE),
                ["git config --global user.email learner-b@example.test", "git config --list"],
                ev(
                    {
                        "rules": [
                            meta_equals("last_config_scope", "global"),
                            meta_equals("last_config_key", "user.email"),
                            meta_equals("last_config_value", "learner-b@example.test"),
                        ]
                    },
                    required=["git config --global user.email", "git config --list"],
                ),
                details=[{"label": "Email to set", "value": "learner-b@example.test"}],
            ),
        ],
        checks=[
            {
                "label": "Your author email is saved in global config.",
                "requirement": {"rules": [meta_equals("last_config_key", "user.email")]},
            }
        ],
        prerequisites=["set-global-user-name"],
        workflow=True,
    ),
    q(
        "git-diff/name-only",
        "inspect-changed-paths",
        "List changed paths",
        "You only need to know which files changed before deciding what to stage.",
        "List changed paths without showing the full diff.",
        [
            v(
                "diff-name-only-readme",
                "Changed path list",
                repo(commits=BASE, working_tree={"README.md": "changed"}),
                ["git diff --name-only"],
                ev({"repository_state_unchanged": True}, required=["git diff --name-only"]),
            ),
        ],
        checks=[
            {
                "label": "Changed paths were listed without mutation.",
                "requirement": {"repository_state_unchanged": True},
            }
        ],
        prerequisites=["inspect-working-diff"],
        min_counted_commands=0,
        max_counted_commands=2,
    ),
    q(
        "git-add/update",
        "stage-tracked-updates",
        "Stage tracked updates only",
        "Tracked edits are ready, but a new scratch file must stay outside the snapshot.",
        "Stage modifications to tracked files without staging untracked files.",
        [
            v(
                "add-update-readme",
                "Stage tracked update",
                repo(
                    commits=BASE,
                    working_tree={
                        "README.md": "changed",
                        "scratch.txt": {"status": "untracked", "content": "notes"},
                    },
                ),
                ["git add -u"],
                ev(
                    {"staging_contains": ["README.md"], "working_tree_contains": ["scratch.txt"]},
                    required=["git add -u"],
                ),
            ),
        ],
        checks=[
            {
                "label": "Tracked changes are staged and untracked scratch remains local.",
                "requirement": {
                    "staging_contains": ["README.md"],
                    "working_tree_contains": ["scratch.txt"],
                },
            }
        ],
        prerequisites=["stage-one-file"],
        workflow=True,
    ),
    q(
        "git-commit/no-edit",
        "amend-without-editing-message",
        "Amend without editing the message",
        "The latest commit message is good, but one staged fix belongs inside that same commit.",
        "Amend the latest commit while keeping its message.",
        [
            v(
                "amend-no-edit-app",
                "Amend content only",
                repo(
                    commits=[
                        commit("c0", "Initial project", [], BASE_TREE),
                        commit("c1", "Update app shell", ["c0"], BASE_TREE),
                    ],
                    branches={"main": "c1"},
                    staging={"src/app.py": "print('patched')\n"},
                ),
                ["git commit --amend --no-edit"],
                ev(
                    {
                        "rules": [
                            {"type": "commit_replaced_by_amend"},
                            {
                                "type": "latest_commit_message_contains",
                                "branch": "main",
                                "text": "Update app shell",
                            },
                        ],
                        "staging_empty": True,
                    },
                    required=["git commit --amend --no-edit"],
                ),
            ),
        ],
        checks=[
            {
                "label": "The commit was amended and the staging area is empty.",
                "requirement": {
                    "staging_empty": True,
                    "rules": [{"type": "commit_replaced_by_amend"}],
                },
            }
        ],
        prerequisites=["amend-latest-commit-message"],
        workflow=True,
    ),
    q(
        "git-rm/recursive-cached",
        "stop-tracking-directory",
        "Stop tracking a generated directory",
        "A generated directory was accidentally committed and should stay locally ignored.",
        "Remove the tracked directory from the index while preserving local files.",
        [
            v(
                "rm-cached-dist",
                "Untrack dist",
                repo(
                    commits=[
                        commit(
                            "c0",
                            "Track build output",
                            [],
                            {**BASE_TREE, "dist/app.js": "bundle", "dist/app.css": "css"},
                        )
                    ],
                    branches={"main": "c0"},
                ),
                ["git rm -r --cached dist"],
                ev(
                    {
                        "staging_contains": ["dist/app.js", "dist/app.css"],
                        "working_tree_contains": ["dist/app.js", "dist/app.css"],
                        "rules": [
                            meta_equals("last_rm_cached_paths", ["dist/app.css", "dist/app.js"])
                        ],
                    },
                    required=["git rm -r --cached"],
                ),
            ),
        ],
        checks=[
            {
                "label": "The directory's untracking is staged (the local files are kept).",
                "requirement": {"staging_not_empty": True},
            }
        ],
        prerequisites=["stop-tracking-local-file"],
        workflow=True,
    ),
    q(
        "git-check-ignore/verbose",
        "explain-ignore-rule",
        "Find the ignore rule, then save the real work",
        "A build artifact is hidden from status. Confirm which rule ignores it, then commit only the real change.",
        "Ask Git which ignore rule matches the artifact, then stage and commit the real file - leaving the artifact ignored.",
        [
            v(
                "ignore-build-log",
                "Build log ignored",
                repo(
                    commits=BASE,
                    working_tree={
                        "build.log": {"status": "ignored", "content": "log"},
                        "CHANGELOG.md": {"status": "untracked", "content": "v1 notes\n"},
                    },
                ),
                [
                    "git check-ignore -v build.log",
                    "git add CHANGELOG.md",
                    "git commit -m 'Add changelog'",
                ],
                ev(
                    {
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["CHANGELOG.md"],
                            "excludes_paths": ["build.log"],
                            "message_contains": ["changelog"],
                        },
                        "working_tree_contains": ["build.log"],
                    },
                    required=["git check-ignore -v", "git commit"],
                ),
            ),
            v(
                "ignore-coverage",
                "Coverage report ignored",
                repo(
                    commits=BASE,
                    working_tree={
                        "coverage.xml": {"status": "ignored", "content": "<coverage/>"},
                        "src/api.py": {"status": "untracked", "content": "def ping(): return 'ok'\n"},
                    },
                ),
                [
                    "git check-ignore -v coverage.xml",
                    "git add src/api.py",
                    "git commit -m 'Add api endpoint'",
                ],
                ev(
                    {
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["src/api.py"],
                            "excludes_paths": ["coverage.xml"],
                            "message_contains": ["api"],
                        },
                        "working_tree_contains": ["coverage.xml"],
                    },
                    required=["git check-ignore -v", "git commit"],
                ),
            ),
        ],
        checks=[
            {
                "label": "Your real change is saved in a new commit.",
                "requirement": {"min_commits_on_branch": {"main": 2}},
            },
        ],
        prerequisites=["inspect-ignored-status"],
        workflow=True,
    ),
    q(
        "git-branch/verbose",
        "inspect-branch-tips",
        "Inspect branch tip commits",
        "Several branches exist and you need to see the commit each name points to.",
        "List branches with their tip commits.",
        [
            v(
                "branch-verbose",
                "Branch tip list",
                repo(commits=BRANCH_BASE, branches={"main": "c2", "docs": "c1"}),
                ["git branch -v"],
                ev({"repository_state_unchanged": True}, required=["git branch -v"]),
            ),
        ],
        checks=[
            {
                "label": "Branch tips were inspected without mutation.",
                "requirement": {"repository_state_unchanged": True},
            }
        ],
        prerequisites=["create-branch-pointer"],
        min_counted_commands=0,
        max_counted_commands=2,
    ),
    q(
        "git-branch/delete-force",
        "force-delete-branch-pointer",
        "Force-delete an unmerged branch",
        "A throwaway branch should be removed even though it is not merged.",
        "Delete the requested branch pointer with force.",
        [
            v(
                "branch-force-delete",
                "Delete throwaway branch",
                repo(
                    commits=[
                        *BRANCH_BASE,
                        commit("c3", "Experiment", ["c0"], {"README.md": "experiment"}),
                    ],
                    branches={"main": "c2", "throwaway": "c3"},
                ),
                ["git branch -D throwaway"],
                ev(
                    {"branch_absent": ["throwaway"], "head_branch": "main"},
                    required=["git branch -D"],
                ),
                details=[{"label": "Branch to delete", "value": "throwaway"}],
            ),
        ],
        checks=[
            {
                "label": "The throwaway branch pointer was removed.",
                "requirement": {"local_branches_at_most": 1},
            }
        ],
        prerequisites=["delete-merged-branch"],
        workflow=True,
    ),
    q(
        "git-merge/squash",
        "squash-merge-branch",
        "Stage a branch as one snapshot",
        "A feature branch should become one clean commit instead of preserving every branch commit.",
        "Squash-merge the feature branch into the index without committing yet.",
        [
            v(
                "merge-squash-feature",
                "Squash feature branch",
                repo(
                    commits=MERGE_BASE,
                    branches={"main": "c1", "feature/profile": "c2"},
                    head="main",
                ),
                ["git merge --squash feature/profile"],
                ev(
                    {
                        "staging_contains": ["src/app.py", "src/profile.py"],
                        "rules": [meta_equals("squash_merge_staged", True)],
                    },
                    required=["git merge --squash"],
                ),
                details=[{"label": "Branch to squash", "value": "feature/profile"}],
            ),
        ],
        checks=[
            {
                "label": "Feature changes are staged as a squash merge.",
                "requirement": {"rules": [meta_equals("squash_merge_staged", True)]},
            }
        ],
        prerequisites=["merge-with-merge-commit"],
        workflow=True,
    ),
    q(
        "git-merge-base/two-refs",
        "find-merge-base",
        "Find a common ancestor",
        "Before merging, identify where two branches diverged.",
        "Print the best common ancestor for the two refs.",
        [
            v(
                "merge-base-main-feature",
                "Find branch base",
                repo(
                    commits=MERGE_BASE,
                    branches={"main": "c1", "feature/profile": "c2"},
                    head="main",
                ),
                ["git merge-base main feature/profile"],
                ev({"rules": [meta_equals("last_merge_base", "c0")]}, required=["git merge-base"]),
            ),
        ],
        checks=[
            {
                "label": "The common ancestor was inspected.",
                "requirement": {"rules": [meta_equals("last_merge_base", "c0")]},
            }
        ],
        prerequisites=["merge-fast-forward-branch"],
        min_counted_commands=0,
        max_counted_commands=2,
        workflow=True,
    ),
    q(
        "git-diff-conflict/ours",
        "inspect-our-conflict-side",
        "Inspect our conflict side",
        "A conflicted file needs comparison before choosing a resolution.",
        "Inspect the current branch side of the conflict.",
        [
            v(
                "diff-ours-auth",
                "Diff ours",
                PRECONFLICT,
                ["git diff --ours src/auth.js"],
                ev({"repository_state_unchanged": True}, required=["git diff --ours"]),
            ),
        ],
        checks=[
            {
                "label": "Our conflict side was inspected without mutation.",
                "requirement": {"repository_state_unchanged": True},
            }
        ],
        prerequisites=["choose-our-conflict-side"],
        min_counted_commands=0,
        max_counted_commands=2,
    ),
    q(
        "git-diff-conflict/theirs",
        "inspect-their-conflict-side",
        "Inspect their conflict side",
        "A conflicted file needs comparison before choosing a resolution.",
        "Inspect the incoming branch side of the conflict.",
        [
            v(
                "diff-theirs-auth",
                "Diff theirs",
                PRECONFLICT,
                ["git diff --theirs src/auth.js"],
                ev({"repository_state_unchanged": True}, required=["git diff --theirs"]),
            ),
        ],
        checks=[
            {
                "label": "Their conflict side was inspected without mutation.",
                "requirement": {"repository_state_unchanged": True},
            }
        ],
        prerequisites=["choose-their-conflict-side"],
        min_counted_commands=0,
        max_counted_commands=2,
    ),
    q(
        "git-diff-conflict/base",
        "inspect-base-conflict-side",
        "Inspect the conflict base",
        "You need to see the original version before deciding how to resolve both sides.",
        "Inspect the base side of the conflict.",
        [
            v(
                "diff-base-auth",
                "Diff base",
                PRECONFLICT,
                ["git diff --base src/auth.js"],
                ev({"repository_state_unchanged": True}, required=["git diff --base"]),
            ),
        ],
        checks=[
            {
                "label": "The conflict base was inspected without mutation.",
                "requirement": {"repository_state_unchanged": True},
            }
        ],
        prerequisites=["inspect-our-conflict-side", "inspect-their-conflict-side"],
        min_counted_commands=0,
        max_counted_commands=2,
    ),
    q(
        "git-ls-files/unmerged",
        "list-unmerged-index-entries",
        "List unmerged index entries",
        "A merge conflict exists and you need to see which paths are unmerged.",
        "List unmerged index entries without changing repository state.",
        [
            v(
                "ls-files-unmerged-auth",
                "List unmerged auth",
                PRECONFLICT,
                ["git ls-files -u"],
                ev({"repository_state_unchanged": True}, required=["git ls-files -u"]),
            ),
        ],
        checks=[
            {
                "label": "Unmerged entries were inspected without mutation.",
                "requirement": {"repository_state_unchanged": True},
            }
        ],
        prerequisites=["inspect-base-conflict-side"],
        min_counted_commands=0,
        max_counted_commands=2,
    ),
    q(
        "git-mergetool/launch",
        "launch-merge-tool",
        "Launch a merge tool",
        "The conflicted file needs an external merge view before you edit it.",
        "Open the configured merge tool for the conflict.",
        [
            v(
                "mergetool-auth",
                "Open merge tool",
                PRECONFLICT,
                ["git mergetool"],
                ev(
                    {
                        "conflicts_contain_paths": ["src/auth.js"],
                        "rules": [meta_equals("last_mergetool_opened", True)],
                    },
                    required=["git mergetool"],
                ),
            ),
        ],
        checks=[
            {
                "label": "A merge tool was opened for the conflict.",
                "requirement": {"rules": [meta_equals("last_mergetool_opened", True)]},
            }
        ],
        prerequisites=["list-unmerged-index-entries"],
        workflow=True,
    ),
    q(
        "git-cherry-pick/abort",
        "abort-cherry-pick",
        "Abort an in-progress cherry-pick",
        "A no-commit cherry-pick introduced the wrong patch and should be backed out cleanly.",
        "Abort the in-progress cherry-pick and return to the original branch state.",
        [
            v(
                "cherry-pick-abort",
                "Abort picked patch",
                {
                    **copy.deepcopy(CHERRY_REPO),
                    "staging": {"src/auth.py": {"status": "added", "content": "guard=True"}},
                    "cherry_pick_in_progress": True,
                    "cherry_pick_original_head": "c1",
                },
                ["git cherry-pick --abort"],
                ev(
                    {
                        "branch_points_to": {"main": "c1"},
                        "working_tree_clean": True,
                        "staging_empty": True,
                        "rules": [meta_equals("last_cherry_pick_aborted", True)],
                    },
                    required=["git cherry-pick --abort"],
                ),
            ),
        ],
        checks=[
            {
                "label": "The cherry-pick is gone and the branch returned to its original tip.",
                "requirement": {"staging_empty": True, "working_tree_clean": True},
            }
        ],
        prerequisites=["cherry-pick-without-commit"],
        workflow=True,
    ),
    q(
        "git-remote/list",
        "list-remote-names",
        "List remote names",
        "Before inspecting URLs, identify which remotes exist.",
        "List configured remote names without changing repository state.",
        [
            v(
                "remote-list-origin",
                "List origin",
                repo(commits=BASE, remotes={"origin": "https://example.test/team/app.git"}),
                ["git remote"],
                ev({"repository_state_unchanged": True}, required=["git remote"]),
            ),
        ],
        checks=[
            {
                "label": "Remote names were inspected without mutation.",
                "requirement": {"repository_state_unchanged": True},
            }
        ],
        min_counted_commands=0,
        max_counted_commands=2,
    ),
    # --- Chapter 1 reauthor: new "Read the Graph" + "Identity & Ignores" moves ---
    q(
        "git-config/alias",
        "set-global-alias",
        "Create a shortcut alias, then confirm it",
        "Typing the same long command repeatedly is slow. Create a short alias, then confirm it is registered.",
        "Create a global alias so a short name runs a longer Git command, then list your config to confirm it.",
        [
            v(
                "alias-co-checkout",
                "Alias co for checkout",
                repo(commits=BASE),
                ["git config --global alias.co checkout", "git config --list"],
                ev(
                    {
                        "rules": [
                            meta_equals("last_config_scope", "global"),
                            meta_equals("last_config_key", "alias.co"),
                            meta_equals("last_config_value", "checkout"),
                        ]
                    },
                    required=["git config --global alias.co", "git config --list"],
                ),
                details=[
                    {"label": "Alias name", "value": "co"},
                    {"label": "Shortcut runs", "value": "checkout"},
                ],
            ),
            v(
                "alias-st-status",
                "Alias st for status",
                repo(commits=BASE),
                ["git config --global alias.st status", "git config --list"],
                ev(
                    {
                        "rules": [
                            meta_equals("last_config_scope", "global"),
                            meta_equals("last_config_key", "alias.st"),
                            meta_equals("last_config_value", "status"),
                        ]
                    },
                    required=["git config --global alias.st", "git config --list"],
                ),
                details=[
                    {"label": "Alias name", "value": "st"},
                    {"label": "Shortcut runs", "value": "status"},
                ],
            ),
        ],
        checks=[
            {
                "label": "A global alias is saved in your config.",
                "requirement": {"rules": [meta_equals("last_config_scope", "global")]},
            }
        ],
        prerequisites=["set-global-user-name"],
        workflow=True,
    ),
]
