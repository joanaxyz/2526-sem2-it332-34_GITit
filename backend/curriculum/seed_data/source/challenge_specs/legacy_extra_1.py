"""Additional legacy challenge scenarios batch 1."""

from __future__ import annotations

from .helpers import *  # noqa: F403

LEGACY_CHALLENGES = [
    challenge(
        "tracking-changes-snapshots",
        "craft-clean-snapshot",
        "Craft a Clean Snapshot",
        "Separate ready work from noise before committing.",
        "These scenarios test whether the learner can shape the index as a deliberate draft instead of sweeping the whole workspace into history.",
        [
            level(
                "easy",
                story="Only the app edit is ready for the next snapshot.",
                task="Commit the source change and leave the README draft outside the commit.",
                before="main -> c0; src/app.py and README.md are modified.",
                after="main advances with src/app.py only; README.md remains local work.",
                uses_adventure_levels=["stage-one-file", "commit-staged-snapshot"],
                min_counted_commands=2,
                max_counted_commands=5,
                variants=[
                    variant(
                        "easy-commit-app-not-readme",
                        "Commit app only",
                        story="The app change is done; the README note is still a draft.",
                        task="Create a focused app commit.",
                        before="main -> c0; app and README modified",
                        after="main -> app commit; README still modified locally",
                        initial=repo(
                            commits=SNAPSHOT_BASE,
                            working_tree={
                                "src/app.py": "print('ready')\n",
                                "README.md": "Portal\nDraft note\n",
                            },
                        ),
                        solution=["git add src/app.py", 'git commit -m "Update app setup"'],
                        evaluation=_contract(
                            {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["src/app.py"],
                                    "excludes_paths": ["README.md"],
                                    "message_contains": ["app"],
                                },
                                "working_tree_contains": ["README.md"],
                                "staging_empty": True,
                            },
                            required=["git add", "git commit"],
                            forbidden=["git add .", "git add -A"],
                            graph={"from": "main -> c0", "to": "main -> focused app commit"},
                            concepts=["selective staging", "focused commit"],
                        ),
                    )
                ],
            ),
            level(
                "medium",
                story="A broad stage caught one file that does not belong in the snapshot.",
                task="Back the README out of staging, then commit only the source file.",
                before="main -> c0; app and README are both changed.",
                after="main advances with the app change; README remains unstaged local work.",
                uses_adventure_levels=[
                    "stage-visible-folder-work",
                    "unstage-one-file",
                    "commit-staged-snapshot",
                ],
                min_counted_commands=3,
                max_counted_commands=7,
                variants=[
                    variant(
                        "medium-unstage-readme-before-commit",
                        "Unstage draft before commit",
                        story="You staged too much while preparing the snapshot; the README draft needs another pass.",
                        task="Keep only src/app.py staged for the commit.",
                        before="main -> c0; app and README modified",
                        after="main -> app commit; README remains local work",
                        initial=repo(
                            commits=SNAPSHOT_BASE,
                            working_tree={
                                "src/app.py": "print('clean')\n",
                                "README.md": "Portal\nNeeds review\n",
                            },
                        ),
                        solution=[
                            "git add .",
                            "git restore --staged README.md",
                            'git commit -m "Update app flow"',
                        ],
                        evaluation=_contract(
                            {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["src/app.py"],
                                    "excludes_paths": ["README.md"],
                                    "message_contains": ["app"],
                                },
                                "working_tree_contains": ["README.md"],
                                "staging_empty": True,
                            },
                            required=["git add", "git restore", "git commit"],
                            graph={
                                "from": "two changed files in the workspace",
                                "to": "one committed source change and one local draft",
                            },
                            concepts=["unstage mistake", "commit remaining index"],
                        ),
                    )
                ],
            ),
            level(
                "hard",
                story="One file contains a finished validation hunk and a noisy debug hunk.",
                task="Commit only the finished hunk and leave the debug hunk in the working tree.",
                before="main -> c0; src/app.py has two unrelated hunks.",
                after="main advances with the validation hunk; the debug hunk remains local.",
                uses_adventure_levels=["stage-selected-hunks", "commit-staged-snapshot"],
                min_counted_commands=2,
                max_counted_commands=6,
                variants=[
                    variant(
                        "hard-patch-stage-one-hunk",
                        "Patch-stage one hunk",
                        story="The validation change is ready, but the debug draft is not.",
                        task="Create a commit from the selected hunk only.",
                        before="src/app.py has validation and debug hunks",
                        after="validation committed; debug draft remains unstaged",
                        initial=repo(
                            commits=SNAPSHOT_BASE,
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
                        solution=[
                            "git add -p src/app.py",
                            'git commit -m "Add login validation"',
                        ],
                        evaluation=_contract(
                            {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["src/app.py"],
                                    "message_contains": ["validation"],
                                },
                                "working_tree_contains": ["src/app.py"],
                                "rules": [
                                    {
                                        "type": "working_tree_contains_tokens",
                                        "path": "src/app.py",
                                        "tokens": ["debug draft"],
                                    }
                                ],
                            },
                            required=["git add -p", "git commit"],
                            graph={
                                "from": "main -> c0 with two hunks",
                                "to": "main -> validation commit; debug remains local",
                            },
                            concepts=["patch staging", "atomic commit"],
                        ),
                    )
                ],
            ),
        ],
    ),
    challenge(
        "tracking-changes-snapshots",
        "stop-tracking-secret",
        "Stop Tracking a Secret",
        "Remove sensitive or generated files from history going forward without deleting useful local copies.",
        "These scenarios test the index-level difference between deleting a file and stopping Git from tracking it.",
        [
            level(
                "easy",
                story="A local environment file was committed by mistake but is still needed on disk.",
                task="Stop tracking the env file and commit the cleanup.",
                before="main -> c0 contains .env.",
                after="main advances with .env removed from the tree; local .env remains ignored or untracked.",
                uses_adventure_levels=["stop-tracking-local-file", "commit-staged-snapshot"],
                min_counted_commands=2,
                max_counted_commands=5,
                variants=[
                    variant(
                        "easy-untrack-env-secret",
                        "Untrack env secret",
                        story="The secret cannot stay in future snapshots, but the app still needs the local file.",
                        task="Create a commit that stops tracking .env.",
                        before="main -> c0 includes .env",
                        after="main -> cleanup commit; local .env remains",
                        initial=repo(
                            commits=SNAPSHOT_WITH_SECRET,
                            working_tree={".gitignore": {"status": "untracked", "content": ""}},
                        ),
                        solution=[
                            "git rm --cached .env",
                            'git commit -m "Stop tracking local env"',
                        ],
                        evaluation=_contract(
                            {
                                "latest_commit": {
                                    "branch": "main",
                                    "message_contains": ["env"],
                                },
                                "rules": [
                                    {
                                        "type": "tracked_path_removed_from_commit_tree",
                                        "path": ".env",
                                    },
                                    {"type": "ignored_paths_present", "paths": [".env"]},
                                ],
                                "staging_empty": True,
                            },
                            required=["git rm --cached", "git commit"],
                            graph={
                                "from": "main tree contains .env",
                                "to": "main tree no longer tracks .env",
                            },
                            concepts=["remove from index", "preserve local copy"],
                        ),
                    )
                ],
            ),
            level(
                "medium",
                story="Build output was committed as a directory, but developers still need the local files.",
                task="Stop tracking the generated directory and commit the cleanup.",
                before="main -> c0 contains dist/app.js and dist/app.css.",
                after="main advances without the dist files; the local copies remain outside tracking.",
                uses_adventure_levels=["stop-tracking-directory", "commit-staged-snapshot"],
                min_counted_commands=2,
                max_counted_commands=5,
                variants=[
                    variant(
                        "medium-untrack-dist-directory",
                        "Untrack dist directory",
                        story="The generated bundle should stay on disk but leave future snapshots.",
                        task="Create a cleanup commit that stops tracking dist.",
                        before="main -> c0 includes dist files",
                        after="main -> cleanup commit; local dist files remain",
                        initial=repo(
                            commits=[
                                commit(
                                    "c0",
                                    "Track build output",
                                    [],
                                    {
                                        **SNAPSHOT_BASE[0]["tree"],
                                        "dist/app.js": "bundle\n",
                                        "dist/app.css": "css\n",
                                    },
                                )
                            ]
                        ),
                        solution=[
                            "git rm -r --cached dist",
                            'git commit -m "Stop tracking build output"',
                        ],
                        evaluation=_contract(
                            {
                                "latest_commit": {
                                    "branch": "main",
                                    "message_contains": ["build"],
                                },
                                "working_tree_contains": ["dist/app.js", "dist/app.css"],
                                "rules": [
                                    {
                                        "type": "tracked_path_removed_from_commit_tree",
                                        "path": "dist/app.js",
                                    },
                                    {
                                        "type": "tracked_path_removed_from_commit_tree",
                                        "path": "dist/app.css",
                                    },
                                ],
                                "staging_empty": True,
                            },
                            required=["git rm -r --cached", "git commit"],
                            graph={
                                "from": "main tree includes generated dist directory",
                                "to": "main tree excludes dist while local files remain",
                            },
                            concepts=["recursive cached removal", "generated files"],
                        ),
                    )
                ],
            ),
            level(
                "hard",
                story="A secret cleanup should also add the ignore rule that prevents the mistake from recurring.",
                task="Stop tracking the secret and commit the ignore rule with the cleanup.",
                before="main -> c0 contains .env and has no ignore rule.",
                after="main advances without .env and with .gitignore protecting it.",
                uses_adventure_levels=[
                    "stop-tracking-local-file",
                    "stage-one-file",
                    "commit-staged-snapshot",
                    "inspect-ignored-status",
                ],
                min_counted_commands=3,
                max_counted_commands=7,
                variants=[
                    variant(
                        "hard-untrack-env-and-ignore",
                        "Untrack and ignore env",
                        story="The fix should remove the tracked secret and teach Git to ignore the local copy.",
                        task="Commit both the untracking change and the ignore rule.",
                        before="main -> c0 includes .env",
                        after="main -> cleanup commit includes .gitignore and excludes .env",
                        initial=repo(commits=SNAPSHOT_WITH_SECRET),
                        workspace_files=[
                            {
                                "action": "create",
                                "after_command_index": 0,
                                "path": ".gitignore",
                                "content": ".env\n",
                            }
                        ],
                        solution=[
                            "git rm --cached .env",
                            "git add .gitignore",
                            'git commit -m "Ignore local env"',
                        ],
                        evaluation=_contract(
                            {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": [".gitignore"],
                                    "message_contains": ["env"],
                                },
                                "rules": [
                                    {
                                        "type": "tracked_path_removed_from_commit_tree",
                                        "path": ".env",
                                    },
                                    {"type": "ignored_paths_present", "paths": [".env"]},
                                ],
                                "staging_empty": True,
                            },
                            required=["git rm --cached", "git add", "git commit"],
                            graph={
                                "from": "tracked secret in main",
                                "to": "secret removed from tree and ignore rule committed",
                            },
                            concepts=["index cleanup", "ignore future secrets"],
                        ),
                    )
                ],
            ),
        ],
    ),
    challenge(
        "branching-switching",
        "branch-cleanup",
        "Branch Cleanup",
        "Remove branch pointers deliberately after reading whether they are safe to delete.",
        "Cleanup scenarios make branch refs visible as disposable labels, while commits remain in the object graph.",
        [
            level(
                "easy",
                story="A merged review branch is behind main and can be removed safely.",
                task="Delete the stale local branch while staying on main.",
                before="main -> c2; review/menu -> c1.",
                after="review/menu is absent; main still points to c2.",
                uses_adventure_levels=["delete-merged-branch", "list-local-branches"],
                min_counted_commands=1,
                max_counted_commands=4,
                variants=[
                    variant(
                        "easy-delete-safe-review-branch",
                        "Delete safe branch",
                        story="The branch's work is already reachable from main.",
                        task="Remove the stale branch pointer.",
                        before="main -> c2; review/menu -> c1",
                        after="main -> c2; review/menu absent",
                        initial=repo(
                            commits=BRANCH_LONG,
                            branches={"main": "c2", "review/menu": "c1"},
                            head="main",
                        ),
                        solution=["git branch -d review/menu"],
                        evaluation=_contract(
                            {
                                "branch_points_to": {"main": "c2"},
                                "branch_absent": ["review/menu"],
                                "head_branch": "main",
                            },
                            required=["git branch -d"],
                            graph={"from": "stale branch ref visible", "to": "stale ref removed"},
                            concepts=["safe branch deletion", "branch ref cleanup"],
                        ),
                    )
                ],
            ),
            level(
                "medium",
                story="An abandoned experiment branch is not merged, but the team has decided it should be discarded.",
                task="Force-delete the throwaway branch while keeping main untouched.",
                before="main -> c2; throwaway -> e1 from c0.",
                after="throwaway is absent; main still points to c2.",
                uses_adventure_levels=["force-delete-branch-pointer", "inspect-graph-history"],
                min_counted_commands=1,
                max_counted_commands=4,
                variants=[
                    variant(
                        "medium-force-delete-throwaway",
                        "Force-delete throwaway",
                        story="The experiment branch is not merged and should be intentionally discarded.",
                        task="Remove the throwaway branch pointer.",
                        before="main -> c2; throwaway -> e1",
                        after="main -> c2; throwaway absent",
                        initial=repo(
                            commits=[
                                *BRANCH_LONG,
                                commit("e1", "Throwaway experiment", ["c0"], {"README.md": "x\n"}),
                            ],
                            branches={"main": "c2", "throwaway": "e1"},
                            head="main",
                        ),
                        solution=["git branch -D throwaway"],
                        evaluation=_contract(
                            {
                                "branch_points_to": {"main": "c2"},
                                "branch_absent": ["throwaway"],
                                "head_branch": "main",
                            },
                            required=["git branch -D"],
                            graph={
                                "from": "unmerged throwaway branch exists",
                                "to": "throwaway ref intentionally removed",
                            },
                            concepts=["force branch deletion", "discard abandoned branch"],
                        ),
                    )
                ],
            ),
            level(
                "hard",
                story="You inspected an old commit detached, then need to return to main and clean up an abandoned branch.",
                task="Detach for inspection, return to main, and delete the throwaway branch.",
                before="main -> c2; throwaway -> e1.",
                after="HEAD is back on main, throwaway is gone, and main did not move.",
                uses_adventure_levels=[
                    "inspect-detached-commit",
                    "switch-existing-branch",
                    "force-delete-branch-pointer",
                ],
                min_counted_commands=3,
                max_counted_commands=6,
                variants=[
                    variant(
                        "hard-detach-return-and-delete",
                        "Detach return and delete",
                        story="Detached inspection should not strand HEAD or leave clutter behind.",
                        task="Inspect c1 detached, return to main, then remove throwaway.",
                        before="main -> c2; throwaway -> e1",
                        after="HEAD on main -> c2; throwaway absent",
                        initial=repo(
                            commits=[
                                *BRANCH_LONG,
                                commit("e1", "Throwaway experiment", ["c0"], {"README.md": "x\n"}),
                            ],
                            branches={"main": "c2", "throwaway": "e1"},
                            head="main",
                        ),
                        solution=[
                            "git switch --detach c1",
                            "git switch main",
                            "git branch -D throwaway",
                        ],
                        evaluation=_contract(
                            {
                                "head_branch": "main",
                                "branch_points_to": {"main": "c2"},
                                "branch_absent": ["throwaway"],
                            },
                            required=["git switch --detach", "git switch", "git branch -D"],
                            graph={
                                "from": "main plus abandoned branch",
                                "to": "main restored as HEAD and abandoned ref gone",
                            },
                            concepts=["detached inspection", "return to branch", "cleanup"],
                        ),
                    )
                ],
            ),
        ],
    ),
]
