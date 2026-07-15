"""Additional legacy challenge scenarios batch 2."""

from __future__ import annotations

from .helpers import *  # noqa: F403

LEGACY_CHALLENGES = [
    challenge(
        "merging-conflicts",
        "finish-conflicted-merge",
        "Finish a Conflicted Merge",
        "Resolve a conflicted integration and leave the repository clean.",
        "These scenarios focus on the middle of a merge, where the learner must read conflict state, stage a resolution, and finish or abort intentionally.",
        [
            level(
                "easy",
                story="A merge is already paused on one conflicted file, and the incoming side is the accepted version.",
                task="Take the incoming side, stage it, and finish the merge.",
                before="main is mid-merge with src/auth.js conflicted.",
                after="main points to a merge commit and no conflict state remains.",
                uses_adventure_levels=[
                    "choose-their-conflict-side",
                    "stage-one-file",
                    "continue-resolved-merge",
                ],
                min_counted_commands=3,
                max_counted_commands=6,
                variants=[
                    variant(
                        "easy-take-theirs-and-continue",
                        "Take theirs and continue",
                        story="The feature version of the auth timeout is the one the team accepted.",
                        task="Use the incoming side and complete the merge.",
                        before="conflict in src/auth.js; merge parent feature/auth-timeout",
                        after="merge commit on main with no conflicts",
                        initial=PRECONFLICT,
                        solution=[
                            "git checkout --theirs src/auth.js",
                            "git add src/auth.js",
                            "git merge --continue",
                        ],
                        evaluation=_contract(
                            {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["src/auth.js"],
                                    "message_contains": ["Merge"],
                                },
                                "conflict_free": True,
                                "staging_empty": True,
                                "rules": [
                                    {"type": "commit_is_merge", "branch": "main"},
                                    {"type": "commit_has_parent", "branch": "main", "parent": "m1"},
                                    {"type": "commit_has_parent", "branch": "main", "parent": "f1"},
                                ],
                            },
                            required=["git checkout --theirs", "git add", "git merge --continue"],
                            graph={
                                "from": "merge paused at conflict",
                                "to": "main has completed merge commit",
                            },
                            concepts=["choose conflict side", "stage resolution", "continue merge"],
                        ),
                    )
                ],
            ),
            level(
                "medium",
                story="A merge will conflict, but the final file should combine the accepted feature behavior.",
                task="Start the merge, write the accepted resolution, stage it, and continue.",
                before="main -> m1 and feature/auth-timeout -> f1 both edit src/auth.js.",
                after="main points to a resolved merge commit.",
                uses_adventure_levels=[
                    "merge-fast-forward-branch",
                    "stage-one-file",
                    "continue-resolved-merge",
                ],
                min_counted_commands=3,
                max_counted_commands=8,
                variants=[
                    variant(
                        "medium-start-resolve-auth-merge",
                        "Start and resolve conflict",
                        story="The merge must be completed, not abandoned, and the final auth config should use strict mode.",
                        task="Resolve the merge conflict manually and finish it.",
                        before="main m1 and feature/auth-timeout f1 diverged",
                        after="main -> merge commit with strict auth config",
                        initial=repo(
                            commits=CONFLICT_HISTORY,
                            branches={"main": "m1", "feature/auth-timeout": "f1"},
                            head="main",
                        ),
                        workspace_files=[
                            {
                                "after_command_index": 1,
                                "path": "src/auth.js",
                                "content": "timeout=2500\nmode='strict'\n",
                            }
                        ],
                        solution=[
                            "git merge feature/auth-timeout",
                            "git add src/auth.js",
                            "git merge --continue",
                        ],
                        evaluation=_contract(
                            {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["src/auth.js"],
                                    "message_contains": ["Merge"],
                                },
                                "conflict_free": True,
                                "staging_empty": True,
                                "rules": [
                                    {"type": "commit_is_merge", "branch": "main"},
                                    {"type": "commit_has_parent", "branch": "main", "parent": "m1"},
                                    {"type": "commit_has_parent", "branch": "main", "parent": "f1"},
                                    {
                                        "type": "commit_tree_contains",
                                        "branch": "main",
                                        "tree": {"src/auth.js": "timeout=2500\nmode='strict'\n"},
                                    },
                                ],
                            },
                            required=["git merge", "git add", "git merge --continue"],
                            graph={
                                "from": "two branch tips conflict",
                                "to": "resolved merge commit joins both tips",
                            },
                            concepts=["start merge", "manual resolution", "merge continuation"],
                        ),
                    )
                ],
            ),
            level(
                "hard",
                story="A merge tool is requested for the paused conflict before the final resolution is staged.",
                task="Open the merge tool, write the accepted file, stage it, and continue the merge.",
                before="main is mid-merge with src/auth.js conflicted.",
                after="main points to a clean merge commit.",
                uses_adventure_levels=[
                    "launch-merge-tool",
                    "stage-one-file",
                    "continue-resolved-merge",
                ],
                min_counted_commands=4,
                max_counted_commands=8,
                variants=[
                    variant(
                        "hard-mergetool-resolve-continue",
                        "Merge tool then continue",
                        story="The team wants you to inspect the conflict in a merge tool before accepting the final content.",
                        task="Use the merge tool path, then finish the merge cleanly.",
                        before="conflicted src/auth.js in an in-progress merge",
                        after="main -> merge commit; no staged or conflicted leftovers",
                        initial=PRECONFLICT,
                        workspace_files=[
                            {
                                "after_command_index": 1,
                                "path": "src/auth.js",
                                "content": "timeout=2500\nmode='strict'\n",
                            }
                        ],
                        solution=[
                            "git mergetool src/auth.js",
                            "git add src/auth.js",
                            "git merge --continue",
                        ],
                        evaluation=_contract(
                            {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["src/auth.js"],
                                    "message_contains": ["Merge"],
                                },
                                "conflict_free": True,
                                "staging_empty": True,
                                "rules": [
                                    {"type": "commit_is_merge", "branch": "main"},
                                    meta_equals("last_mergetool_opened", True),
                                ],
                            },
                            required=["git mergetool", "git add", "git merge --continue"],
                            graph={
                                "from": "merge paused at conflict",
                                "to": "merge completed after tool-assisted inspection",
                            },
                            concepts=["merge tool", "stage resolved file", "continue merge"],
                        ),
                    )
                ],
            ),
        ],
    ),
    challenge(
        "undoing-recovery",
        "undo-the-right-way",
        "Undo the Right Way",
        "Choose restore, amend, reset, or revert based on what kind of mistake happened.",
        "Undo scenarios teach that Git recovery is not one command: the safe move depends on whether the mistake is in the workspace, the local tip, or shared history.",
        [
            level(
                "easy",
                story="A local debug edit was made in the working tree and should not be saved.",
                task="Discard the working-tree edit without creating a commit.",
                before="main -> c0; src/app.py has an unwanted local change.",
                after="main still points to c0 and the workspace is clean.",
                uses_adventure_levels=["discard-working-file-change", "inspect-working-diff"],
                min_counted_commands=1,
                max_counted_commands=4,
                variants=[
                    variant(
                        "easy-restore-debug-edit",
                        "Restore debug edit",
                        story="The debug print was never meant to leave your machine.",
                        task="Throw away the working-tree edit.",
                        before="src/app.py modified with debug text",
                        after="workspace clean at c0",
                        initial=repo(commits=SNAPSHOT_BASE, working_tree={"src/app.py": "debug\n"}),
                        solution=["git restore src/app.py"],
                        evaluation=_contract(
                            {"working_tree_clean": True, "staging_empty": True},
                            required=["git restore"],
                            graph={"from": "main -> c0 plus dirty file", "to": "main -> c0 clean"},
                            concepts=["restore workspace", "discard unsaved edit"],
                        ),
                    )
                ],
            ),
            level(
                "medium",
                story="The latest local commit is good, but one staged fix belongs inside it rather than in a new commit.",
                task="Amend the latest commit without changing its message.",
                before="main -> c1; src/app.py has a staged correction.",
                after="main points to a replacement commit with the same message and the correction included.",
                uses_adventure_levels=["amend-without-editing-message"],
                min_counted_commands=1,
                max_counted_commands=4,
                variants=[
                    variant(
                        "medium-amend-staged-correction",
                        "Amend staged correction",
                        story="The staged typo fix should be folded into the latest local commit.",
                        task="Amend the latest commit and keep its message.",
                        before="main -> c1; staged src/app.py correction",
                        after="main -> replacement c1 with corrected app file",
                        initial=repo(
                            commits=[
                                commit("c0", "Initial portal", [], {"README.md": "Portal\n"}),
                                commit(
                                    "c1",
                                    "Update app shell",
                                    ["c0"],
                                    {"README.md": "Portal\n", "src/app.py": "typo\n"},
                                ),
                            ],
                            branches={"main": "c1"},
                            staging={"src/app.py": "fixed\n"},
                        ),
                        solution=["git commit --amend --no-edit"],
                        evaluation=_contract(
                            {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["src/app.py"],
                                    "message_contains": ["Update app shell"],
                                },
                                "staging_empty": True,
                                "rules": [{"type": "commit_replaced_by_amend", "old": "c1"}],
                            },
                            required=["git commit --amend --no-edit"],
                            graph={
                                "from": "main -> c1 plus staged correction",
                                "to": "main -> replacement commit",
                            },
                            concepts=["amend content", "keep message"],
                        ),
                    )
                ],
            ),
            level(
                "hard",
                story="A bad commit was already shared to origin/main, so rewriting it away would harm teammates.",
                task="Create a new revert commit that undoes the bad change while preserving history.",
                before="main and origin/main both point to c2.",
                after="main points to a revert commit after c2.",
                uses_adventure_levels=["revert-shared-commit", "inspect-graph-history"],
                min_counted_commands=1,
                max_counted_commands=5,
                variants=[
                    variant(
                        "hard-revert-instead-of-reset",
                        "Revert shared commit",
                        story="The wrong login route is public, so the repair must be a forward-moving commit.",
                        task="Undo c2 without moving the branch backward.",
                        before="main/origin-main -> c2",
                        after="main -> revert commit after c2",
                        initial=repo(
                            commits=RECOVERY_HISTORY,
                            branches={"main": "c2"},
                            remote_branches={"origin/main": "c2"},
                            upstream_tracking={"main": "origin/main"},
                            remotes={"origin": "https://example.test/team/app.git"},
                        ),
                        solution=["git revert c2"],
                        evaluation=_contract(
                            {
                                "latest_commit": {"branch": "main", "message_contains": ["Revert"]},
                                "rules": [
                                    {"type": "new_revert_commit_exists"},
                                    {
                                        "type": "revert_preserves_history",
                                        "branch": "main",
                                        "commit": "c2",
                                    },
                                    {
                                        "type": "commit_parent_equals",
                                        "branch": "main",
                                        "parent": "c2",
                                    },
                                ],
                                "working_tree_clean": True,
                            },
                            required=["git revert"],
                            forbidden=["git reset --hard"],
                            graph={
                                "from": "shared bad commit at branch tip",
                                "to": "new revert commit preserves old history",
                            },
                            concepts=["safe shared undo", "revert instead of reset"],
                        ),
                    )
                ],
            ),
        ],
    ),
    challenge(
        "temporary-work-patches",
        "hotfix-interruption",
        "Hotfix Interruption",
        "Pause unfinished work, make an urgent fix elsewhere, then restore the paused work.",
        "This scenario family tests the real interruption loop: local work is not lost, the hotfix lands on the right branch, and the original workspace comes back.",
        [
            level(
                "easy",
                story="Unfinished release notes block a branch switch for an urgent review.",
                task="Stash the notes and switch to the hotfix branch.",
                before="main -> c1 with notes.md modified; hotfix/login exists at c1.",
                after="HEAD is on hotfix/login and the notes are stored in the stash.",
                uses_adventure_levels=["stash-local-work", "switch-existing-branch"],
                min_counted_commands=2,
                max_counted_commands=5,
                variants=[
                    variant(
                        "easy-stash-and-switch-hotfix",
                        "Stash and switch",
                        story="The notes can wait, but the hotfix branch needs attention now.",
                        task="Shelve the notes and move to hotfix/login.",
                        before="HEAD on main with notes.md modified",
                        after="HEAD on hotfix/login; stash contains notes.md",
                        initial=repo(
                            commits=BRANCH_BASE,
                            branches={"main": "c1", "hotfix/login": "c1"},
                            head="main",
                            working_tree={"notes.md": {"status": "modified", "content": "draft\n"}},
                        ),
                        solution=["git stash", "git switch hotfix/login"],
                        evaluation=_contract(
                            {
                                "head_branch": "hotfix/login",
                                "working_tree_clean": True,
                                "rules": [
                                    {"type": "stash_stack_contains_paths", "paths": ["notes.md"]}
                                ],
                            },
                            required=["git stash", "git switch"],
                            graph={
                                "from": "dirty main workspace",
                                "to": "clean hotfix branch with WIP shelved",
                            },
                            concepts=["stash interruption", "switch after cleanup"],
                        ),
                    )
                ],
            ),
            level(
                "medium",
                story="A hotfix file must be committed on the hotfix branch before the paused work returns to main.",
                task="Stash local notes, commit the hotfix on its branch, return to main, and pop the notes.",
                before="main has notes.md modified; hotfix/login points to c1.",
                after="hotfix/login has the fix commit; HEAD is back on main with notes.md restored.",
                uses_adventure_levels=[
                    "stash-local-work",
                    "switch-existing-branch",
                    "stage-one-file",
                    "commit-staged-snapshot",
                    "pop-top-stash",
                ],
                min_counted_commands=6,
                max_counted_commands=10,
                variants=[
                    variant(
                        "medium-hotfix-commit-then-pop",
                        "Commit hotfix then pop",
                        story="The urgent fix belongs on hotfix/login, but your main-branch notes should survive.",
                        task="Complete the interruption loop cleanly.",
                        before="main dirty; hotfix/login clean",
                        after="hotfix/login -> fix commit; main checked out with notes restored",
                        initial=repo(
                            commits=BRANCH_BASE,
                            branches={"main": "c1", "hotfix/login": "c1"},
                            head="main",
                            working_tree={"notes.md": {"status": "modified", "content": "draft\n"}},
                        ),
                        workspace_files=[
                            {
                                "after_command_index": 2,
                                "path": "README.md",
                                "content": "Portal\nHotfix note\n",
                            }
                        ],
                        solution=[
                            "git stash",
                            "git switch hotfix/login",
                            "git add README.md",
                            'git commit -m "Add hotfix note"',
                            "git switch main",
                            "git stash pop",
                        ],
                        evaluation=_contract(
                            {
                                "head_branch": "main",
                                "working_tree_contains": ["notes.md"],
                                "stash_stack_empty": True,
                                "latest_commit": {
                                    "branch": "hotfix/login",
                                    "contains_paths": ["README.md"],
                                    "message_contains": ["hotfix"],
                                },
                            },
                            required=[
                                "git stash",
                                "git switch",
                                "git add",
                                "git commit",
                                "git stash pop",
                            ],
                            graph={
                                "from": "main dirty, hotfix branch clean",
                                "to": "hotfix branch advanced; main work restored",
                            },
                            concepts=["stash pop", "commit on target branch", "return to work"],
                        ),
                    )
                ],
            ),
            level(
                "hard",
                story="An approved hotfix commit exists on another branch while your release branch has unfinished notes.",
                task="Shelve the notes, copy the approved fix onto release, then restore the notes.",
                before="release -> r1 with notes.md modified; bugfix/login -> b1.",
                after="release has a copied login fix and notes.md is restored as local work.",
                uses_adventure_levels=[
                    "stash-local-work",
                    "cherry-pick-one-commit",
                    "pop-top-stash",
                ],
                min_counted_commands=3,
                max_counted_commands=7,
                variants=[
                    variant(
                        "hard-stash-pick-pop-release",
                        "Stash pick pop",
                        story="The release notes are unfinished, but the approved login fix should land now.",
                        task="Protect the notes while transplanting the hotfix.",
                        before="release dirty; bugfix/login has b1",
                        after="release -> copied b1 fix; notes.md restored locally",
                        initial=repo(
                            commits=PATCH_HISTORY[:3],
                            branches={"release": "r1", "bugfix/login": "b1"},
                            head="release",
                            working_tree={"notes.md": {"status": "modified", "content": "draft\n"}},
                        ),
                        solution=["git stash", "git cherry-pick b1", "git stash pop"],
                        evaluation=_contract(
                            {
                                "head_branch": "release",
                                "working_tree_contains": ["notes.md"],
                                "latest_commit": {
                                    "branch": "release",
                                    "contains_paths": ["src/login.py"],
                                    "message_contains": ["login"],
                                },
                                "rules": [
                                    {
                                        "type": "cherry_pick_created_new_commit",
                                        "source": "b1",
                                        "branch": "release",
                                    }
                                ],
                            },
                            required=["git stash", "git cherry-pick", "git stash pop"],
                            graph={
                                "from": "dirty release plus separate hotfix commit",
                                "to": "release gets copied fix and original WIP returns",
                            },
                            concepts=["stash around cherry-pick", "transplant one fix"],
                        ),
                    )
                ],
            ),
        ],
    ),
    challenge(
        "remotes-collaboration",
        "daily-sync",
        "Daily Sync",
        "Fetch, inspect, integrate, and publish the everyday remote loop.",
        "Daily sync scenarios keep local and remote refs honest: fetch before trust, pull when appropriate, and push only after the local story is ready.",
        [
            level(
                "easy",
                story="The remote has moved, and you need a safe look before integrating.",
                task="Fetch the remote update without moving local main.",
                before="main -> c1; local origin/main -> c1; remote origin/main -> r2.",
                after="origin/main -> r2 while main still points to c1.",
                uses_adventure_levels=["fetch-origin-updates", "inspect-graph-history"],
                min_counted_commands=1,
                max_counted_commands=4,
                variants=[
                    variant(
                        "easy-daily-fetch-first",
                        "Fetch first",
                        story="Start the day by refreshing remote-tracking refs.",
                        task="Fetch origin safely.",
                        before="main and origin/main both c1 locally; remote has r2",
                        after="origin/main r2; main c1",
                        initial=repo(
                            commits=REMOTE_BASE,
                            branches={"main": "c1"},
                            remote_branches={"origin/main": "c1"},
                            upstream_tracking={"main": "origin/main"},
                            remotes={"origin": "https://example.test/team/app.git"},
                            remote_updates={"origin/main": "r2"},
                            remote_fixtures=REMOTE_FIXTURE_AHEAD,
                        ),
                        solution=["git fetch origin"],
                        evaluation=_contract(
                            {
                                "branch_points_to": {"main": "c1"},
                                "remote_branch_points_to": {"origin/main": "r2"},
                                "rules": [
                                    {
                                        "type": "fetch_updated_remote_tracking_without_moving_local",
                                        "branch": "main",
                                    }
                                ],
                            },
                            required=["git fetch"],
                            graph={"from": "main == origin/main == c1", "to": "origin/main -> r2"},
                            concepts=["fetch first", "local branch unchanged"],
                        ),
                    )
                ],
            ),
            level(
                "medium",
                story="The fetched upstream update is ready and local main has no extra commits.",
                task="Fast-forward local main to the upstream tip.",
                before="main -> c1; remote has r2.",
                after="main and origin/main both point to r2.",
                uses_adventure_levels=["pull-fast-forward-update", "fetch-origin-updates"],
                min_counted_commands=1,
                max_counted_commands=4,
                variants=[
                    variant(
                        "medium-daily-pull-update",
                        "Pull update",
                        story="The remote update is the next safe step for local main.",
                        task="Bring local main up to date.",
                        before="main behind origin/main",
                        after="main and origin/main at r2",
                        initial=repo(
                            commits=REMOTE_BASE,
                            branches={"main": "c1"},
                            remote_branches={"origin/main": "c1"},
                            upstream_tracking={"main": "origin/main"},
                            remotes={"origin": "https://example.test/team/app.git"},
                            remote_updates={"origin/main": "r2"},
                            remote_fixtures=REMOTE_FIXTURE_AHEAD,
                        ),
                        solution=["git pull"],
                        evaluation=_contract(
                            {
                                "branch_points_to": {"main": "r2"},
                                "remote_branch_points_to": {"origin/main": "r2"},
                                "rules": [
                                    {
                                        "type": "pull_moved_local_to_upstream",
                                        "branch": "main",
                                        "upstream": "origin/main",
                                    }
                                ],
                                "working_tree_clean": True,
                            },
                            required=["git pull"],
                            graph={"from": "main behind upstream", "to": "main catches upstream"},
                            concepts=["pull fast-forward", "upstream tracking"],
                        ),
                    )
                ],
            ),
            level(
                "hard",
                story="Local work and remote work both need to land in the shared branch.",
                task="Fetch, merge the remote-tracking branch, and publish the integrated result.",
                before="main -> l2; origin/main local -> c1; remote origin/main -> r2.",
                after="main and origin/main point to the new merge commit.",
                uses_adventure_levels=[
                    "fetch-origin-updates",
                    "merge-with-merge-commit",
                    "push-current-branch",
                ],
                min_counted_commands=3,
                max_counted_commands=9,
                variants=[
                    variant(
                        "hard-daily-merge-and-publish",
                        "Merge and publish",
                        story="Your release note and the remote review note both belong in the shared branch.",
                        task="Integrate the remote update and publish it.",
                        before="main l2 diverged from remote r2",
                        after="origin/main matches local merge commit",
                        initial=repo(
                            commits=REMOTE_DIVERGED,
                            branches={"main": "l2"},
                            remote_branches={"origin/main": "c1"},
                            upstream_tracking={"main": "origin/main"},
                            remotes={"origin": "https://example.test/team/app.git"},
                            remote_updates={"origin/main": "r2"},
                            remote_fixtures={
                                "branches": {"origin/main": "r2"},
                                "default_branch": "origin/main",
                                "commits": [REMOTE_DIVERGED[-1]],
                            },
                        ),
                        solution=["git fetch origin", "git merge origin/main", "git push"],
                        evaluation=_contract(
                            {
                                "remote_branch_matches_local": {"origin/main": "main"},
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["review.md"],
                                    "message_contains": ["Merge"],
                                },
                                "rules": [
                                    {"type": "commit_is_merge", "branch": "main"},
                                    {
                                        "type": "push_moved_remote_to_local_tip",
                                        "remote_branch": "origin/main",
                                    },
                                ],
                                "working_tree_clean": True,
                            },
                            required=["git fetch", "git merge", "git push"],
                            graph={
                                "from": "local and remote diverged",
                                "to": "published merge joins both histories",
                            },
                            concepts=["daily sync", "merge remote work", "push result"],
                        ),
                    )
                ],
            ),
        ],
    ),
    challenge(
        "remotes-collaboration",
        "publish-new-branch",
        "Publish a New Branch",
        "Create upstream tracking and keep remote branch refs intentional.",
        "Publishing scenarios make remote refs visible: a local branch becomes a shared branch, future pushes know their destination, and obsolete remote branches can be removed.",
        [
            level(
                "easy",
                story="A feature branch is ready for review and has never been pushed.",
                task="Publish it to origin and set upstream tracking.",
                before="feature/report -> c1 exists locally; origin has only main.",
                after="origin/feature/report points to c1 and feature/report tracks it.",
                uses_adventure_levels=["push-and-set-upstream"],
                min_counted_commands=1,
                max_counted_commands=4,
                variants=[
                    variant(
                        "easy-publish-feature-upstream",
                        "Publish feature upstream",
                        story="Future pushes should know where feature/report belongs.",
                        task="Publish the feature branch with upstream tracking.",
                        before="local feature/report has no upstream",
                        after="origin/feature/report matches local feature/report",
                        initial=repo(
                            commits=[
                                commit("c0", "Create portal", [], {"README.md": "Portal\n"}),
                                commit(
                                    "c1",
                                    "Add report",
                                    ["c0"],
                                    {"README.md": "Portal\n", "report.md": "draft\n"},
                                ),
                            ],
                            branches={"main": "c0", "feature/report": "c1"},
                            head="feature/report",
                            remotes={"origin": "https://example.test/team/app.git"},
                            remote_branches={"origin/main": "c0"},
                        ),
                        solution=["git push -u origin feature/report"],
                        evaluation=_contract(
                            {
                                "upstream_tracking": {"feature/report": "origin/feature/report"},
                                "rules": [
                                    {
                                        "type": "push_moved_remote_to_local_tip",
                                        "branch": "feature/report",
                                        "remote_branch": "origin/feature/report",
                                    }
                                ],
                            },
                            required=["git push -u"],
                            graph={
                                "from": "local feature branch only",
                                "to": "matching remote branch plus upstream tracking",
                            },
                            concepts=["publish branch", "set upstream"],
                        ),
                    )
                ],
            ),
            level(
                "medium",
                story="A tracked feature branch has one new local commit and needs to update its remote branch.",
                task="Push the current branch to its upstream.",
                before="feature/report -> c2; origin/feature/report -> c1.",
                after="origin/feature/report also points to c2.",
                uses_adventure_levels=["push-current-branch"],
                min_counted_commands=1,
                max_counted_commands=4,
                variants=[
                    variant(
                        "medium-push-current-feature",
                        "Push current feature",
                        story="Upstream tracking is already set, so the current branch can publish directly.",
                        task="Update the remote branch from the local branch.",
                        before="local feature/report ahead of origin/feature/report",
                        after="origin/feature/report matches local tip c2",
                        initial=repo(
                            commits=[
                                commit("c0", "Create portal", [], {"README.md": "Portal\n"}),
                                commit(
                                    "c1",
                                    "Add report",
                                    ["c0"],
                                    {"README.md": "Portal\n", "report.md": "v1\n"},
                                ),
                                commit(
                                    "c2",
                                    "Polish report",
                                    ["c1"],
                                    {"README.md": "Portal\n", "report.md": "v2\n"},
                                ),
                            ],
                            branches={"main": "c0", "feature/report": "c2"},
                            head="feature/report",
                            remotes={"origin": "https://example.test/team/app.git"},
                            remote_branches={"origin/main": "c0", "origin/feature/report": "c1"},
                            upstream_tracking={"feature/report": "origin/feature/report"},
                        ),
                        solution=["git push"],
                        evaluation=_contract(
                            {
                                "rules": [
                                    {
                                        "type": "push_moved_remote_to_local_tip",
                                        "branch": "feature/report",
                                        "remote_branch": "origin/feature/report",
                                    }
                                ]
                            },
                            required=["git push"],
                            graph={
                                "from": "local branch ahead of upstream",
                                "to": "remote branch catches local branch",
                            },
                            concepts=["push current branch", "upstream destination"],
                        ),
                    )
                ],
            ),
            level(
                "hard",
                story="A review branch was merged and the remote branch should be removed from origin.",
                task="Delete the obsolete remote branch without deleting local main.",
                before="origin/feature/report exists at c1.",
                after="origin/feature/report is absent.",
                uses_adventure_levels=["delete-remote-branch"],
                min_counted_commands=1,
                max_counted_commands=4,
                variants=[
                    variant(
                        "hard-delete-remote-feature",
                        "Delete remote feature",
                        story="The remote review branch is no longer needed after integration.",
                        task="Remove the remote branch from origin.",
                        before="origin/feature/report -> c1",
                        after="origin/feature/report absent",
                        initial=repo(
                            commits=[
                                commit("c0", "Create portal", [], {"README.md": "Portal\n"}),
                                commit(
                                    "c1",
                                    "Add report",
                                    ["c0"],
                                    {"README.md": "Portal\n", "report.md": "v1\n"},
                                ),
                            ],
                            branches={"main": "c1"},
                            remotes={"origin": "https://example.test/team/app.git"},
                            remote_branches={"origin/main": "c1", "origin/feature/report": "c1"},
                        ),
                        solution=["git push origin --delete feature/report"],
                        evaluation=_contract(
                            {
                                "remote_branch_absent": ["origin/feature/report"],
                                "rules": [meta_equals("remote_branch_deleted", "feature/report")],
                            },
                            required=["git push"],
                            graph={
                                "from": "remote feature branch exists",
                                "to": "remote feature branch removed",
                            },
                            concepts=["delete remote branch", "remote ref cleanup"],
                        ),
                    )
                ],
            ),
        ],
    ),
]
