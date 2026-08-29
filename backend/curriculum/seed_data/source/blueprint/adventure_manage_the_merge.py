"""Blueprint adventure levels for manage-the-merge."""

from __future__ import annotations

from .helpers import _wave

ADVENTURE_LEVELS = [
        {
            "slug": "merge-drills",
            "title": "Merge Drills",
            "waves": [
                _wave(
                    "ch4-adv-squash-then-verify",
                    "git-merge/squash",
                    "Squash, seal, read the story",
                    [
                        "git merge --squash feature/profile",
                        "git commit -m 'Fold profile work'",
                        "git log --oneline",
                    ],
                    required=["git merge --squash", "git commit", "git log"],
                    forms=["git-commit/message", "git-log/oneline"],
                    state="merge",
                    story=(
                        "Fold the feature branch's combined work into one ordinary snapshot on "
                        "main, seal it under the provided message, then read the compact history "
                        "to see a single tidy entry where a whole branch used to be."
                    ),
                    details=[{"label": "Commit message", "value": "Fold profile work"}],
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["src/profile.py"],
                            "message_contains": ["Fold profile work"],
                        },
                        "staging_empty": True,
                        "rules": [{"type": "commit_is_not_merge"}],
                    },
                    checks=[
                        {
                            "label": "The folded work landed as one ordinary commit.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["src/profile.py"],
                                    "message_contains": ["Fold profile work"],
                                },
                                "rules": [{"type": "commit_is_not_merge"}],
                            },
                        },
                        {
                            "label": "The tidy history was read afterward.",
                            "requirement": {"required_commands": ["git log"]},
                        },
                    ],
                ),
                _wave(
                    "ch4-adv-squash-inspect",
                    "git-merge/squash",
                    "Squash, inspect, then seal",
                    [
                        "git merge --squash feature/profile",
                        "git diff --staged",
                        "git commit -m 'Land squashed feature'",
                    ],
                    required=["git merge --squash", "git diff --staged", "git commit"],
                    forms=["git-diff/staged", "git-commit/message"],
                    state="merge",
                    story=(
                        "Stage the feature's combined work as one snapshot, but read exactly what "
                        "is about to enter history before sealing it - squashes deserve review "
                        "just like any other snapshot."
                    ),
                    details=[{"label": "Commit message", "value": "Land squashed feature"}],
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["src/profile.py"],
                            "message_contains": ["Land squashed feature"],
                        },
                        "staging_empty": True,
                        "rules": [{"type": "commit_is_not_merge"}],
                    },
                    checks=[
                        {
                            "label": "The staged squash was reviewed before sealing.",
                            "requirement": {"required_commands": ["git diff --staged"]},
                        },
                        {
                            "label": "The reviewed work landed as one ordinary commit.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "message_contains": ["Land squashed feature"],
                                },
                                "rules": [{"type": "commit_is_not_merge"}],
                            },
                        },
                    ],
                ),
                _wave(
                    "ch4-adv-squash-status",
                    "git-merge/squash",
                    "Squash with a state check",
                    [
                        "git merge --squash feature/profile",
                        "git status",
                        "git commit -m 'Squash with checks'",
                    ],
                    required=["git merge --squash", "git status", "git commit"],
                    forms=["git-status/plain", "git-commit/message"],
                    state="merge",
                    story=(
                        "Squash the feature's work into staging, read the workspace state to "
                        "understand what a pending squash looks like from the outside, then seal "
                        "it as one ordinary commit."
                    ),
                    details=[{"label": "Commit message", "value": "Squash with checks"}],
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["src/profile.py"],
                            "message_contains": ["Squash with checks"],
                        },
                        "staging_empty": True,
                        "rules": [{"type": "commit_is_not_merge"}],
                    },
                    checks=[
                        {
                            "label": "The pending squash was inspected before sealing.",
                            "requirement": {"required_commands": ["git status"]},
                        },
                        {
                            "label": "The squash landed as one ordinary commit.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "message_contains": ["Squash with checks"],
                                },
                                "rules": [{"type": "commit_is_not_merge"}],
                            },
                        },
                    ],
                ),
                _wave(
                    "ch4-adv-base-audit",
                    "git-merge-base/two-refs",
                    "Find the split, open it",
                    ["git merge-base main feature/profile", "git show c0"],
                    required=["git merge-base", "git show"],
                    forms=["git-show/commit"],
                    state="merge",
                    story=(
                        "A review question needs precision: where exactly did these two lines "
                        "part ways, and what did the project look like at that moment? Locate the "
                        "split point, then open that exact snapshot."
                    ),
                    evaluation={
                        "rules": [
                            {"type": "operation_metadata_equals", "key": "last_merge_base", "value": "c0"}
                        ]
                    },
                    checks=[
                        {
                            "label": "The split point was located precisely.",
                            "requirement": {
                                "rules": [
                                    {"type": "operation_metadata_equals", "key": "last_merge_base", "value": "c0"}
                                ]
                            },
                        },
                        {
                            "label": "The split-point snapshot was opened and read.",
                            "requirement": {"required_commands": ["git show"]},
                        },
                    ],
                ),
                _wave(
                    "ch4-adv-ff-vs-real",
                    "git-merge/no-ff",
                    "Refuse the silent fast-forward",
                    [
                        "git merge-base main feature/profile",
                        "git merge --no-ff feature/profile",
                        "git log --oneline --graph --all",
                    ],
                    required=["git merge-base", "git merge --no-ff", "git log"],
                    forms=["git-merge-base/two-refs", "git-log/graph-all"],
                    state="merge-ff",
                    story=(
                        "The split point confirms a fast-forward is possible - and that is "
                        "exactly why this release merge should refuse it. Force a real merge "
                        "commit, then draw the graph to compare the shape you kept."
                    ),
                    evaluation={
                        "latest_commit": {"branch": "main"},
                        "rules": [{"type": "commit_parent_count_equals", "count": 2}],
                    },
                    checks=[
                        {
                            "label": "The split point was checked before deciding.",
                            "requirement": {"required_commands": ["git merge-base"]},
                        },
                        {
                            "label": "A real two-parent merge commit was created deliberately.",
                            "requirement": {
                                "latest_commit": {"branch": "main"},
                                "rules": [{"type": "commit_parent_count_equals", "count": 2}],
                            },
                        },
                    ],
                ),
                _wave(
                    "ch4-adv-abort-drill",
                    "git-merge/abort",
                    "Scope it, then abandon it",
                    ["git ls-files -u", "git merge --abort"],
                    required=["git ls-files -u", "git merge --abort"],
                    forms=["git-ls-files/unmerged"],
                    state="conflict",
                    story=(
                        "An experimental merge hit conflicts and the experiment is over. List "
                        "the unmerged entries once for the record, then abandon the merge "
                        "completely."
                    ),
                    evaluation={
                        "conflict_free": True,
                        "working_tree_clean": True,
                        "staging_empty": True,
                    },
                    checks=[
                        {
                            "label": "The unmerged entries were recorded before abandoning.",
                            "requirement": {"required_commands": ["git ls-files -u"]},
                        },
                        {
                            "label": "The merge is fully abandoned; the workspace is clean.",
                            "requirement": {"conflict_free": True, "working_tree_clean": True},
                        },
                    ],
                ),
                _wave(
                    "ch4-adv-mergetool-drill",
                    "git-mergetool/launch",
                    "Base first, then the tool",
                    ["git diff --base src/auth.js", "git mergetool"],
                    required=["git diff --base", "git mergetool"],
                    forms=["git-diff-conflict/base"],
                    state="conflict",
                    story=(
                        "Give the merge tool the context it deserves: read what the conflicted "
                        "file looked like at the split point first, then launch the tool to work "
                        "the conflict."
                    ),
                    evaluation={
                        "rules": [
                            {"type": "operation_metadata_equals", "key": "last_mergetool_opened", "value": True}
                        ]
                    },
                    checks=[
                        {
                            "label": "The base version was read before launching the tool.",
                            "requirement": {"required_commands": ["git diff --base"]},
                        },
                        {
                            "label": "The merge tool was launched on the conflict.",
                            "requirement": {
                                "rules": [
                                    {
                                        "type": "operation_metadata_equals",
                                        "key": "last_mergetool_opened",
                                        "value": True,
                                    }
                                ]
                            },
                        },
                    ],
                ),
                _wave(
                    "ch4-adv-mergetool-after-reading",
                    "git-mergetool/launch",
                    "Read every version, then the tool",
                    [
                        "git diff --base src/auth.js",
                        "git diff --ours src/auth.js",
                        "git diff --theirs src/auth.js",
                        "git mergetool",
                    ],
                    required=["git diff --base", "git diff --ours", "git diff --theirs", "git mergetool"],
                    forms=["git-diff-conflict/base", "git-diff-conflict/ours", "git-diff-conflict/theirs"],
                    state="conflict",
                    story=(
                        "Neither side of this conflict is obviously right, which is exactly when "
                        "the tool helps most. Read both competing versions yourself first, then "
                        "launch the merge tool to work through them."
                    ),
                    evaluation={
                        "rules": [
                            {"type": "operation_metadata_equals", "key": "last_mergetool_opened", "value": True}
                        ]
                    },
                    checks=[
                        {
                            "label": "Both sides were read before the tool took over.",
                            "requirement": {"required_commands": ["git diff --ours", "git diff --theirs"]},
                        },
                        {
                            "label": "The merge tool was launched on the conflict.",
                            "requirement": {
                                "rules": [
                                    {
                                        "type": "operation_metadata_equals",
                                        "key": "last_mergetool_opened",
                                        "value": True,
                                    }
                                ]
                            },
                        },
                    ],
                ),
            ],
        },
        {
            "slug": "resolution-gauntlet",
            "title": "Resolution Gauntlet",
            "waves": [
                _wave(
                    "ch4-adv-resolve-and-map",
                    "git-checkout-conflict/ours",
                    "Resolve, finish, map the join",
                    [
                        "git checkout --ours src/auth.js",
                        "git add src/auth.js",
                        "git merge --continue",
                        "git log --oneline --graph --all",
                    ],
                    required=["git checkout --ours", "git add", "git merge --continue", "git log"],
                    forms=["git-add/file", "git-merge/continue", "git-log/graph-all"],
                    state="conflict",
                    story=(
                        "Keep your branch's side of the conflict, stage the resolution, complete "
                        "the merge, and then draw the graph - see with your own eyes how the two "
                        "lines joined into one."
                    ),
                    evaluation={
                        "conflict_free": True,
                        "latest_commit": {"branch": "main", "contains_paths": ["src/auth.js"]},
                        "rules": [
                            {"type": "commit_parent_count_equals", "count": 2},
                            {"type": "operation_metadata_equals", "key": "last_checkout_conflict_side", "value": "ours"},
                        ],
                    },
                    checks=[
                        {
                            "label": "Our side won and the merge finished cleanly.",
                            "requirement": {
                                "conflict_free": True,
                                "rules": [{"type": "commit_parent_count_equals", "count": 2}],
                            },
                        },
                        {
                            "label": "The joined history was mapped afterward.",
                            "requirement": {"required_commands": ["git log"]},
                        },
                    ],
                ),
                _wave(
                    "ch4-adv-ours-quick-drill",
                    "git-checkout-conflict/ours",
                    "Verify, keep ours, finish",
                    [
                        "git diff --ours src/auth.js",
                        "git checkout --ours src/auth.js",
                        "git add src/auth.js",
                        "git merge --continue",
                    ],
                    required=["git diff --ours", "git checkout --ours", "git add", "git merge --continue"],
                    forms=["git-diff-conflict/ours", "git-add/file", "git-merge/continue"],
                    state="conflict",
                    story=(
                        "Trust, but verify: read our side's version one more time, keep it, "
                        "stage the resolution, and complete the merge in one steady pass."
                    ),
                    evaluation={
                        "conflict_free": True,
                        "latest_commit": {"branch": "main", "contains_paths": ["src/auth.js"]},
                        "rules": [
                            {"type": "commit_parent_count_equals", "count": 2},
                            {"type": "operation_metadata_equals", "key": "last_checkout_conflict_side", "value": "ours"},
                        ],
                    },
                    checks=[
                        {
                            "label": "Our side was verified before keeping it.",
                            "requirement": {"required_commands": ["git diff --ours"]},
                        },
                        {
                            "label": "The merge finished cleanly with our side kept.",
                            "requirement": {
                                "conflict_free": True,
                                "rules": [{"type": "commit_parent_count_equals", "count": 2}],
                            },
                        },
                    ],
                ),
                _wave(
                    "ch4-adv-theirs-quick-drill",
                    "git-checkout-conflict/theirs",
                    "Verify, take theirs, finish",
                    [
                        "git diff --theirs src/auth.js",
                        "git checkout --theirs src/auth.js",
                        "git add src/auth.js",
                        "git merge --continue",
                    ],
                    required=["git diff --theirs", "git checkout --theirs", "git add", "git merge --continue"],
                    forms=["git-diff-conflict/theirs", "git-add/file", "git-merge/continue"],
                    state="conflict",
                    story=(
                        "The incoming change was written with newer information. Read their "
                        "version once more, take it, stage the resolution, and complete the "
                        "merge."
                    ),
                    evaluation={
                        "conflict_free": True,
                        "latest_commit": {"branch": "main", "contains_paths": ["src/auth.js"]},
                        "rules": [
                            {"type": "commit_parent_count_equals", "count": 2},
                            {"type": "operation_metadata_equals", "key": "last_checkout_conflict_side", "value": "theirs"},
                        ],
                    },
                    checks=[
                        {
                            "label": "Their side was verified before taking it.",
                            "requirement": {"required_commands": ["git diff --theirs"]},
                        },
                        {
                            "label": "The merge finished cleanly with the incoming side kept.",
                            "requirement": {
                                "conflict_free": True,
                                "rules": [{"type": "commit_parent_count_equals", "count": 2}],
                            },
                        },
                    ],
                ),
                _wave(
                    "ch4-adv-mergetool-finish-drill",
                    "git-mergetool/launch",
                    "Tool, stage, finish, confirm",
                    [
                        "git mergetool",
                        "git add src/auth.js",
                        "git merge --continue",
                        "git status",
                    ],
                    required=["git mergetool", "git add", "git merge --continue", "git status"],
                    forms=["git-add/file", "git-merge/continue", "git-status/plain"],
                    state="conflict",
                    story=(
                        "Run the tool-assisted path end to end: launch the merge tool, stage its "
                        "resolution, complete the merge, and read the state to confirm nothing "
                        "conflicted remains."
                    ),
                    evaluation={
                        "conflict_free": True,
                        "latest_commit": {"branch": "main", "contains_paths": ["src/auth.js"]},
                        "rules": [
                            {"type": "commit_parent_count_equals", "count": 2},
                            {"type": "operation_metadata_equals", "key": "last_mergetool_opened", "value": True},
                        ],
                    },
                    checks=[
                        {
                            "label": "The tool-assisted resolution finished the merge.",
                            "requirement": {
                                "conflict_free": True,
                                "rules": [{"type": "commit_parent_count_equals", "count": 2}],
                            },
                        },
                        {
                            "label": "The clean end state was confirmed.",
                            "requirement": {"required_commands": ["git status"]},
                        },
                    ],
                ),
                _wave(
                    "ch4-adv-tool-assisted-final",
                    "git-mergetool/launch",
                    "Scope, tool, finish, map",
                    [
                        "git ls-files -u",
                        "git mergetool",
                        "git add src/auth.js",
                        "git merge --continue",
                        "git log --oneline --graph --all",
                    ],
                    required=["git ls-files -u", "git mergetool", "git add", "git merge --continue", "git log"],
                    forms=["git-ls-files/unmerged", "git-add/file", "git-merge/continue", "git-log/graph-all"],
                    state="conflict",
                    story=(
                        "The full professional pass: scope the conflict from the index, work it "
                        "with the merge tool, stage and complete the merge, then map the joined "
                        "history."
                    ),
                    evaluation={
                        "conflict_free": True,
                        "latest_commit": {"branch": "main", "contains_paths": ["src/auth.js"]},
                        "rules": [
                            {"type": "commit_parent_count_equals", "count": 2},
                            {"type": "operation_metadata_equals", "key": "last_mergetool_opened", "value": True},
                        ],
                    },
                    checks=[
                        {
                            "label": "The conflict was scoped and worked with the tool.",
                            "requirement": {"required_commands": ["git ls-files -u", "git mergetool"]},
                        },
                        {
                            "label": "The merge completed and the joined shape was mapped.",
                            "requirement": {
                                "conflict_free": True,
                                "rules": [{"type": "commit_parent_count_equals", "count": 2}],
                                "required_commands": ["git log"],
                            },
                        },
                    ],
                ),
                _wave(
                    "ch4-adv-abort-final",
                    "git-merge/abort",
                    "Abandon, then survey the field",
                    [
                        "git ls-files -u",
                        "git diff --base src/auth.js",
                        "git merge --abort",
                        "git log --oneline --graph --all",
                    ],
                    required=["git ls-files -u", "git diff --base", "git merge --abort", "git log"],
                    forms=["git-ls-files/unmerged", "git-diff-conflict/base", "git-log/graph-all"],
                    state="conflict",
                    story=(
                        "This integration needs rethinking, not resolving. Record the unmerged "
                        "entries and the base version for the postmortem, abandon the merge "
                        "entirely, then draw the untouched graph to plan a better approach."
                    ),
                    evaluation={
                        "conflict_free": True,
                        "working_tree_clean": True,
                        "staging_empty": True,
                    },
                    checks=[
                        {
                            "label": "The conflicted merge is fully abandoned.",
                            "requirement": {
                                "conflict_free": True,
                                "working_tree_clean": True,
                                "staging_empty": True,
                            },
                        },
                        {
                            "label": "The untouched graph was surveyed afterward.",
                            "requirement": {"required_commands": ["git log"]},
                        },
                    ],
                ),
            ],
        },
        {
            "slug": "integration-capstones",
            "title": "Integration Capstones",
            "waves": [
                _wave(
                    "ch4-adv-full-integration",
                    "git-switch/create",
                    "Isolate, finish, integrate visibly",
                    [
                        "git switch -c feature/banner",
                        "git add README.md",
                        "git commit -m 'Banner work'",
                        "git switch main",
                        "git merge --no-ff feature/banner",
                    ],
                    required=["git switch -c", "git add", "git commit", "git switch", "git merge --no-ff"],
                    forms=["git-add/file", "git-commit/message", "git-switch/existing", "git-merge/no-ff"],
                    state="dirty",
                    story=(
                        "The pending banner edit gets the full treatment: isolate it on its own "
                        "line, commit it there, return to main, and integrate it with a merge "
                        "that keeps the feature visible in history forever."
                    ),
                    details=[{"label": "Commit message", "value": "Banner work"}],
                    evaluation={
                        "head_branch": "main",
                        "latest_commit": {"branch": "main"},
                        "rules": [
                            {"type": "commit_parent_count_equals", "count": 2},
                            {"type": "branch_exists", "branch": "feature/banner"},
                        ],
                    },
                    checks=[
                        {
                            "label": "The edit was isolated and committed on its own line.",
                            "requirement": {"rules": [{"type": "branch_exists", "branch": "feature/banner"}]},
                        },
                        {
                            "label": "The integration kept the feature visible as a merge commit.",
                            "requirement": {
                                "head_branch": "main",
                                "rules": [{"type": "commit_parent_count_equals", "count": 2}],
                            },
                        },
                    ],
                ),
                _wave(
                    "ch4-adv-merge-two-features",
                    "git-merge/branch",
                    "Insurance first, then integrate",
                    [
                        "git merge-base main feature/profile",
                        "git branch backup/main",
                        "git merge feature/profile",
                        "git log --oneline",
                    ],
                    required=["git merge-base", "git branch", "git merge", "git log"],
                    forms=["git-merge-base/two-refs", "git-branch/create", "git-log/oneline"],
                    state="merge",
                    story=(
                        "Integrate like a professional under pressure: check the split point, "
                        "leave an insurance pointer on main's current tip, merge the feature, "
                        "and read the compact history to confirm the landing."
                    ),
                    evaluation={
                        "latest_commit": {"branch": "main"},
                        "rules": [
                            {"type": "commit_parent_count_equals", "count": 2},
                            {"type": "branch_exists", "branch": "backup/main"},
                        ],
                    },
                    checks=[
                        {
                            "label": "An insurance pointer marks the pre-merge tip.",
                            "requirement": {"rules": [{"type": "branch_exists", "branch": "backup/main"}]},
                        },
                        {
                            "label": "The feature merged into a two-parent commit.",
                            "requirement": {
                                "latest_commit": {"branch": "main"},
                                "rules": [{"type": "commit_parent_count_equals", "count": 2}],
                            },
                        },
                    ],
                ),
                _wave(
                    "ch4-adv-squash-drill",
                    "git-merge/squash",
                    "Compact landing",
                    ["git merge --squash feature/profile", "git commit -m 'Compact the feature'"],
                    required=["git merge --squash", "git commit"],
                    forms=["git-commit/message"],
                    state="merge",
                    story=(
                        "This feature's history is noise; its result is signal. Land the "
                        "branch's combined work as exactly one ordinary commit under the "
                        "provided message."
                    ),
                    details=[{"label": "Commit message", "value": "Compact the feature"}],
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["src/profile.py"],
                            "message_contains": ["Compact the feature"],
                        },
                        "staging_empty": True,
                        "rules": [{"type": "commit_is_not_merge"}],
                    },
                    checks=[
                        {
                            "label": "The feature landed as one compact, ordinary commit.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "message_contains": ["Compact the feature"],
                                },
                                "rules": [{"type": "commit_is_not_merge"}],
                            },
                        },
                    ],
                ),
                _wave(
                    "ch4-adv-merge-map-final",
                    "git-merge/no-ff",
                    "Integrate, map, tidy up",
                    [
                        "git merge --no-ff feature/profile",
                        "git log --oneline --graph --all",
                        "git branch -d feature/profile",
                    ],
                    required=["git merge --no-ff", "git log", "git branch -d"],
                    forms=["git-log/graph-all", "git-branch/delete"],
                    state="merge-ff",
                    story=(
                        "Close out the feature properly: integrate it with its history "
                        "preserved, map the joined graph, and retire the branch pointer now that "
                        "its work lives on main."
                    ),
                    evaluation={
                        "latest_commit": {"branch": "main"},
                        "rules": [
                            {"type": "commit_parent_count_equals", "count": 2},
                            {"type": "branch_absent", "branch": "feature/profile"},
                        ],
                    },
                    checks=[
                        {
                            "label": "The integration preserved the feature's history.",
                            "requirement": {
                                "latest_commit": {"branch": "main"},
                                "rules": [{"type": "commit_parent_count_equals", "count": 2}],
                            },
                        },
                        {
                            "label": "The finished branch pointer is retired.",
                            "requirement": {
                                "rules": [{"type": "branch_absent", "branch": "feature/profile"}]
                            },
                        },
                    ],
                ),
                _wave(
                    "ch4-adv-second-service-merge",
                    "git-merge/branch",
                    "Another service lands",
                    ["git merge feature/profile", "git log --oneline --graph --all"],
                    required=["git merge", "git log"],
                    forms=["git-log/graph-all"],
                    state="merge",
                    story=(
                        "The profile service is signed off and main has moved since it "
                        "branched. Integrate the diverged feature - a real merge this time by "
                        "necessity - and map the result."
                    ),
                    evaluation={
                        "latest_commit": {"branch": "main"},
                        "rules": [{"type": "commit_parent_count_equals", "count": 2}],
                    },
                    checks=[
                        {
                            "label": "The diverged feature merged into a two-parent commit.",
                            "requirement": {
                                "latest_commit": {"branch": "main"},
                                "rules": [{"type": "commit_parent_count_equals", "count": 2}],
                            },
                        },
                        {
                            "label": "The joined result was mapped afterward.",
                            "requirement": {"required_commands": ["git log"]},
                        },
                    ],
                ),
            ],
        },
    ]
