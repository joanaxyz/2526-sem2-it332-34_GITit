"""Blueprint adventure levels for integrate-branches."""

from __future__ import annotations

from .helpers import _wave

ADVENTURE_LEVELS = [
        {
            "slug": "understand-merge-shape",
            "title": "Understand Merge Shape",
            "waves": [
                _wave(
                    "ch4-adv-find-merge-base",
                    "git-merge-base/two-refs",
                    "Find merge base",
                    ["git merge-base main feature/profile"],
                    state="merge",
                    story=(
                        "main and feature/profile diverged from a shared commit some time ago. Before "
                        "merging them, find exactly where they split - their common ancestor."
                    ),
                    evaluation={"rules": [{"type": "operation_metadata_equals", "key": "last_merge_base", "value": "c0"}]},
                    checks=[
                        {
                            "label": "The common ancestor of both branches was identified before merging.",
                            "requirement": {
                                "rules": [
                                    {"type": "operation_metadata_equals", "key": "last_merge_base", "value": "c0"}
                                ]
                            },
                        },
                    ],
                ),
                _wave(
                    "ch4-adv-merge-fast-forward",
                    "git-merge/branch",
                    "Merge fast-forward",
                    ["git merge feature/profile"],
                    state="merge-ff",
                    story=(
                        "main has not moved since feature/profile branched off, so feature/profile is "
                        "directly ahead. Bring main forward to meet it - no merge commit is needed."
                    ),
                    evaluation={
                        "rules": [
                            {"type": "branch_points_to", "branch": "main", "commit": "c2"},
                            {"type": "operation_metadata_equals", "key": "last_merge_fast_forward", "value": True},
                        ]
                    },
                    checks=[
                        {
                            "label": "main advanced directly to the feature tip with a fast-forward, not a new commit.",
                            "requirement": {
                                "rules": [
                                    {"type": "branch_points_to", "branch": "main", "commit": "c2"},
                                    {
                                        "type": "operation_metadata_equals",
                                        "key": "last_merge_fast_forward",
                                        "value": True,
                                    },
                                ]
                            },
                        },
                    ],
                ),
                _wave(
                    "ch4-adv-merge-no-ff",
                    "git-merge/no-ff",
                    "Merge no fast-forward",
                    ["git merge --no-ff feature/profile"],
                    state="merge-ff",
                    story=(
                        "feature/profile is directly ahead again, but this time the team wants the "
                        "branch's history preserved and visible, not silently folded in. Force a real "
                        "merge commit even though a fast-forward is possible."
                    ),
                    evaluation={
                        "latest_commit": {"branch": "main"},
                        "rules": [{"type": "commit_parent_count_equals", "count": 2}],
                    },
                    checks=[
                        {
                            "label": "A real merge commit with two parents was created, preserving both histories.",
                            "requirement": {
                                "latest_commit": {"branch": "main"},
                                "rules": [{"type": "commit_parent_count_equals", "count": 2}],
                            },
                        },
                    ],
                ),
                _wave(
                    "ch4-adv-squash-intro",
                    "git-merge/squash",
                    "Stage a branch as one snapshot",
                    ["git merge --squash feature/profile"],
                    required=["git merge --squash"],
                    state="merge",
                    story=(
                        "feature/profile's finished result matters, but its individual commits do "
                        "not. Stage the branch's combined work as one pending snapshot - and stop "
                        "there, before any commit is made."
                    ),
                    evaluation={
                        "staging_not_empty": True,
                        "head_branch": "main",
                        "rules": [{"type": "staging_contains", "path": "src/profile.py"}],
                    },
                    checks=[
                        {
                            "label": "The branch's combined work waits in staging as one snapshot.",
                            "requirement": {
                                "rules": [{"type": "staging_contains", "path": "src/profile.py"}]
                            },
                        },
                    ],
                ),
                _wave(
                    "ch4-adv-merge-squash",
                    "git-merge/squash",
                    "Merge squash",
                    ["git merge --squash feature/profile", "git commit -m 'Squash profile feature'"],
                    required=["git merge --squash", "git commit"],
                    forms=["git-commit/message"],
                    state="merge",
                    story=(
                        "feature/profile's individual commits are not worth keeping in main's history - "
                        "only the finished result matters. Stage its combined work as one clean snapshot "
                        "and commit it as a single, ordinary commit."
                    ),
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["src/profile.py"],
                            "message_contains": ["Squash profile feature"],
                        },
                        "staging_empty": True,
                        "rules": [{"type": "commit_is_not_merge"}],
                    },
                    checks=[
                        {
                            "label": "The squashed feature work landed as one ordinary commit, not a merge commit.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["src/profile.py"],
                                    "message_contains": ["Squash profile feature"],
                                },
                                "rules": [{"type": "commit_is_not_merge"}],
                            },
                        },
                    ],
                ),
            ],
        },
        {
            "slug": "merge-histories",
            "title": "Merge Real Histories",
            "waves": [
                _wave(
                    "ch4-adv-base-then-merge",
                    "git-merge-base/two-refs",
                    "Find the base, then integrate",
                    ["git merge-base main feature/profile", "git merge feature/profile"],
                    required=["git merge-base", "git merge"],
                    forms=["git-merge/branch"],
                    state="merge",
                    story=(
                        "Two diverged lines are ready to combine. Locate their common ancestor "
                        "first so you know exactly what the merge will span, then integrate the "
                        "feature into main."
                    ),
                    evaluation={
                        "latest_commit": {"branch": "main"},
                        "rules": [
                            {"type": "commit_parent_count_equals", "count": 2},
                            {"type": "operation_metadata_equals", "key": "last_merge_base", "value": "c0"},
                        ],
                    },
                    checks=[
                        {
                            "label": "The common ancestor was located before merging.",
                            "requirement": {
                                "rules": [
                                    {"type": "operation_metadata_equals", "key": "last_merge_base", "value": "c0"}
                                ]
                            },
                        },
                        {
                            "label": "The diverged lines combined into a real merge commit.",
                            "requirement": {
                                "latest_commit": {"branch": "main"},
                                "rules": [{"type": "commit_parent_count_equals", "count": 2}],
                            },
                        },
                    ],
                ),
                _wave(
                    "ch4-adv-graph-then-merge",
                    "git-log/graph-all",
                    "Map, measure, merge visibly",
                    [
                        "git log --oneline --graph --all",
                        "git merge-base main feature/profile",
                        "git merge --no-ff feature/profile",
                    ],
                    required=["git log", "git merge-base", "git merge --no-ff"],
                    forms=["git-merge-base/two-refs", "git-merge/no-ff"],
                    state="merge",
                    story=(
                        "Before this integration, build the full picture: draw the graph, locate "
                        "the split point, and then merge so the feature's history stays visible as "
                        "its own line in the record."
                    ),
                    evaluation={
                        "latest_commit": {"branch": "main"},
                        "rules": [{"type": "commit_parent_count_equals", "count": 2}],
                    },
                    checks=[
                        {
                            "label": "The graph and split point were read before merging.",
                            "requirement": {"required_commands": ["git log", "git merge-base"]},
                        },
                        {
                            "label": "The merge preserved both histories in a two-parent commit.",
                            "requirement": {
                                "latest_commit": {"branch": "main"},
                                "rules": [{"type": "commit_parent_count_equals", "count": 2}],
                            },
                        },
                    ],
                ),
                _wave(
                    "ch4-adv-branch-then-merge-back",
                    "git-switch/create",
                    "Branch out, merge back",
                    [
                        "git switch -c feature/notes",
                        "git add README.md",
                        "git commit -m 'Notes update'",
                        "git switch main",
                        "git merge feature/notes",
                    ],
                    required=["git switch -c", "git add", "git commit", "git switch", "git merge"],
                    forms=["git-add/file", "git-commit/message", "git-switch/existing", "git-merge/branch"],
                    state="dirty",
                    story=(
                        "Run the full loop every feature follows: isolate the pending edit on its "
                        "own new line, commit it there, return to main, and bring the finished "
                        "work home with a merge."
                    ),
                    details=[{"label": "Commit message", "value": "Notes update"}],
                    evaluation={
                        "head_branch": "main",
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["README.md"],
                            "message_contains": ["Notes update"],
                        },
                        "rules": [{"type": "branch_exists", "branch": "feature/notes"}],
                    },
                    checks=[
                        {
                            "label": "The edit was isolated and committed on its own line.",
                            "requirement": {"rules": [{"type": "branch_exists", "branch": "feature/notes"}]},
                        },
                        {
                            "label": "The finished work came home to main via the merge.",
                            "requirement": {
                                "head_branch": "main",
                                "latest_commit": {
                                    "branch": "main",
                                    "message_contains": ["Notes update"],
                                },
                            },
                        },
                    ],
                ),
                _wave(
                    "ch4-adv-no-ff-policy",
                    "git-merge/no-ff",
                    "Policy: keep the branch visible",
                    ["git merge --no-ff feature/profile", "git log --oneline --graph --all"],
                    required=["git merge --no-ff", "git log"],
                    forms=["git-log/graph-all"],
                    state="merge-ff",
                    story=(
                        "House policy says every feature keeps its own visible bump in history, "
                        "even when a silent fast-forward is possible. Merge accordingly, then draw "
                        "the graph to see the preserved shape."
                    ),
                    evaluation={
                        "latest_commit": {"branch": "main"},
                        "rules": [{"type": "commit_parent_count_equals", "count": 2}],
                    },
                    checks=[
                        {
                            "label": "A two-parent merge commit preserved the branch shape.",
                            "requirement": {
                                "latest_commit": {"branch": "main"},
                                "rules": [{"type": "commit_parent_count_equals", "count": 2}],
                            },
                        },
                        {
                            "label": "The preserved shape was drawn afterward.",
                            "requirement": {"required_commands": ["git log"]},
                        },
                    ],
                ),
                _wave(
                    "ch4-adv-ff-check-first",
                    "git-merge/branch",
                    "Verify the fast-forward, then take it",
                    [
                        "git branch -v",
                        "git merge-base main feature/profile",
                        "git merge feature/profile",
                    ],
                    required=["git branch -v", "git merge-base", "git merge"],
                    forms=["git-branch/verbose", "git-merge-base/two-refs"],
                    state="merge-ff",
                    story=(
                        "It looks like main never moved since the feature split - which would "
                        "make this a simple fast-forward. Verify that with the tips and the split "
                        "point, then take the fast-forward."
                    ),
                    evaluation={
                        "rules": [
                            {"type": "branch_points_to", "branch": "main", "commit": "c2"},
                            {"type": "operation_metadata_equals", "key": "last_merge_fast_forward", "value": True},
                        ]
                    },
                    checks=[
                        {
                            "label": "The tips and split point were verified first.",
                            "requirement": {"required_commands": ["git branch -v", "git merge-base"]},
                        },
                        {
                            "label": "main advanced by fast-forward, with no new commit.",
                            "requirement": {
                                "rules": [
                                    {"type": "branch_points_to", "branch": "main", "commit": "c2"},
                                    {
                                        "type": "operation_metadata_equals",
                                        "key": "last_merge_fast_forward",
                                        "value": True,
                                    },
                                ]
                            },
                        },
                    ],
                ),
            ],
        },
        {
            "slug": "abort-and-retry",
            "title": "Abort and Retry",
            "waves": [
                _wave(
                    "ch4-adv-abort-conflicted-merge",
                    "git-merge/abort",
                    "Abort conflicted merge",
                    ["git merge --abort"],
                    state="conflict",
                    story=(
                        "A merge with feature/auth-timeout was started by mistake and is now stuck mid-"
                        "conflict. Back all the way out to the clean pre-merge state on main."
                    ),
                    evaluation={"conflict_free": True, "working_tree_clean": True, "staging_empty": True},
                    checks=[
                        {
                            "label": "The conflicted merge is fully backed out; the tree is clean again.",
                            "requirement": {
                                "conflict_free": True,
                                "working_tree_clean": True,
                                "staging_empty": True,
                            },
                        },
                    ],
                ),
                _wave(
                    "ch4-adv-retry-correct-merge",
                    "git-merge/abort",
                    "Retry correct merge",
                    ["git merge --abort", "git switch main", "git merge feature/profile"],
                    required=["git merge --abort", "git switch", "git merge"],
                    forms=["git-switch/existing", "git-merge/branch"],
                    state="conflict-with-feature",
                    story=(
                        "The wrong branch, feature/auth-timeout, was merged into a conflict by mistake. "
                        "Abort it, make sure you are back on main, and merge the branch that was "
                        "actually intended: feature/profile."
                    ),
                    evaluation={
                        "rules": [
                            {"type": "operation_metadata_equals", "key": "last_merge_branch", "value": "feature/profile"}
                        ]
                    },
                    checks=[
                        {
                            "label": "The wrong merge was aborted and the intended branch, feature/profile, is now the one being merged.",
                            "requirement": {
                                "rules": [
                                    {
                                        "type": "operation_metadata_equals",
                                        "key": "last_merge_branch",
                                        "value": "feature/profile",
                                    }
                                ]
                            },
                        },
                    ],
                ),
                _wave(
                    "ch4-adv-abort-then-inspect",
                    "git-merge/abort",
                    "Read, back out, confirm",
                    ["git log --oneline --graph --all", "git merge --abort", "git status"],
                    required=["git log", "git merge --abort", "git status"],
                    forms=["git-log/graph-all", "git-status/plain"],
                    state="conflict",
                    story=(
                        "Before abandoning this stuck merge, draw the whole graph so the next "
                        "attempt starts informed. Then back all the way out and confirm the "
                        "workspace is clean again."
                    ),
                    evaluation={
                        "conflict_free": True,
                        "working_tree_clean": True,
                        "staging_empty": True,
                    },
                    checks=[
                        {
                            "label": "The battlefield was mapped before backing out.",
                            "requirement": {"required_commands": ["git log"]},
                        },
                        {
                            "label": "The merge is fully backed out and the tree confirmed clean.",
                            "requirement": {
                                "conflict_free": True,
                                "working_tree_clean": True,
                                "staging_empty": True,
                            },
                        },
                    ],
                ),
                _wave(
                    "ch4-adv-abort-verify-drill",
                    "git-merge/abort",
                    "Script-check the damage, then retreat",
                    ["git status --porcelain", "git merge --abort", "git status"],
                    required=["git status --porcelain", "git merge --abort", "git status"],
                    forms=["git-status/porcelain", "git-status/plain"],
                    state="conflict",
                    story=(
                        "A merge attempt went sideways minutes before a demo. Capture the "
                        "script-stable state for the incident note, back the merge out entirely, "
                        "and confirm nothing half-merged remains."
                    ),
                    evaluation={
                        "conflict_free": True,
                        "working_tree_clean": True,
                        "staging_empty": True,
                    },
                    checks=[
                        {
                            "label": "The damaged state was captured before retreating.",
                            "requirement": {"required_commands": ["git status --porcelain"]},
                        },
                        {
                            "label": "The workspace is clean, with no half-merged leftovers.",
                            "requirement": {
                                "conflict_free": True,
                                "working_tree_clean": True,
                                "staging_empty": True,
                            },
                        },
                    ],
                ),
            ],
        },
    ]
