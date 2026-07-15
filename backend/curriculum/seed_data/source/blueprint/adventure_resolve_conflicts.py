"""Blueprint adventure levels for resolve-conflicts."""

from __future__ import annotations

from .helpers import _wave

ADVENTURE_LEVELS = [
        {
            "slug": "read-the-conflict",
            "title": "Read the Conflict",
            "waves": [
                _wave(
                    "ch4-adv-diff-ours-intro",
                    "git-diff-conflict/ours",
                    "Read our side of the conflict",
                    ["git diff --ours src/auth.js"],
                    required=["git diff --ours"],
                    state="conflict",
                    story=(
                        "A merge has paused mid-conflict on src/auth.js. Start the investigation "
                        "with one question: how does the conflicted file differ from the version "
                        "your own branch brought in? Read only that."
                    ),
                    evaluation={"rules": [{"type": "conflicts_contain_paths", "paths": ["src/auth.js"]}]},
                    checks=[
                        {
                            "label": "Our side of the conflict was read on its own.",
                            "requirement": {"required_commands": ["git diff --ours"]},
                        },
                    ],
                ),
                _wave(
                    "ch4-adv-diff-theirs-intro",
                    "git-diff-conflict/theirs",
                    "Read their side of the conflict",
                    ["git diff --theirs src/auth.js"],
                    required=["git diff --theirs"],
                    state="conflict",
                    story=(
                        "Same paused merge, opposite question: how does the conflicted file "
                        "differ from the version the incoming branch wants? Read exactly that "
                        "comparison and nothing else."
                    ),
                    evaluation={"rules": [{"type": "conflicts_contain_paths", "paths": ["src/auth.js"]}]},
                    checks=[
                        {
                            "label": "Their side of the conflict was read on its own.",
                            "requirement": {"required_commands": ["git diff --theirs"]},
                        },
                    ],
                ),
                _wave(
                    "ch4-adv-list-unmerged-files",
                    "git-ls-files/unmerged",
                    "List unmerged files",
                    ["git ls-files -u"],
                    state="conflict",
                    story=(
                        "A merge with feature/auth-timeout has paused mid-conflict. Before touching "
                        "anything, list exactly which index entries are unmerged."
                    ),
                    evaluation={"rules": [{"type": "conflicts_contain_paths", "paths": ["src/auth.js"]}]},
                    checks=[
                        {
                            "label": "The unmerged index entries were listed before acting.",
                            "requirement": {"required_commands": ["git ls-files -u"]},
                        },
                    ],
                ),
                _wave(
                    "ch4-adv-diff-conflict-base",
                    "git-diff-conflict/base",
                    "Diff conflict base",
                    ["git diff --base src/auth.js"],
                    state="conflict",
                    story=(
                        "Before choosing a side of this conflict, see what src/auth.js looked like "
                        "before either branch touched it. Compare the conflicted file against the "
                        "common base."
                    ),
                    evaluation={"rules": [{"type": "conflicts_contain_paths", "paths": ["src/auth.js"]}]},
                    checks=[
                        {
                            "label": "The conflicted file was compared against the common base.",
                            "requirement": {"required_commands": ["git diff --base"]},
                        },
                    ],
                ),
                _wave(
                    "ch4-adv-diff-conflict-ours-theirs",
                    "git-diff-conflict/ours",
                    "Diff conflict sides",
                    ["git diff --ours src/auth.js", "git diff --theirs src/auth.js"],
                    required=["git diff --ours", "git diff --theirs"],
                    forms=["git-diff-conflict/theirs"],
                    state="conflict",
                    story=(
                        "Two candidate timeouts are in conflict in src/auth.js. Compare both sides - "
                        "the current branch's version and the incoming branch's version - before "
                        "deciding which one to keep."
                    ),
                    evaluation={"rules": [{"type": "conflicts_contain_paths", "paths": ["src/auth.js"]}]},
                    checks=[
                        {
                            "label": "Both conflict sides were compared before any resolution was chosen.",
                            "requirement": {"required_commands": ["git diff --ours", "git diff --theirs"]},
                        },
                    ],
                ),
                _wave(
                    "ch4-adv-base-vs-sides",
                    "git-diff-conflict/base",
                    "Base, ours, theirs: full picture",
                    [
                        "git diff --base src/auth.js",
                        "git diff --ours src/auth.js",
                        "git diff --theirs src/auth.js",
                    ],
                    required=["git diff --base", "git diff --ours", "git diff --theirs"],
                    forms=["git-diff-conflict/ours", "git-diff-conflict/theirs"],
                    state="conflict",
                    story=(
                        "Before anyone argues about this conflict in standup, gather all three "
                        "readings: what the file was at the split, what your branch made of it, "
                        "and what the incoming branch wants. Change nothing."
                    ),
                    evaluation={"rules": [{"type": "conflicts_contain_paths", "paths": ["src/auth.js"]}]},
                    checks=[
                        {
                            "label": "The conflict was read against the base and both sides.",
                            "requirement": {
                                "required_commands": ["git diff --base", "git diff --ours", "git diff --theirs"]
                            },
                        },
                    ],
                ),
                _wave(
                    "ch4-adv-launch-mergetool",
                    "git-mergetool/launch",
                    "Launch mergetool",
                    ["git mergetool"],
                    state="conflict",
                    story=(
                        "Reading raw conflict markers is error-prone for this one. Launch the "
                        "configured merge tool on the conflicted file instead of resolving it by hand."
                    ),
                    evaluation={
                        "rules": [
                            {"type": "operation_metadata_equals", "key": "last_mergetool_opened", "value": True}
                        ]
                    },
                    checks=[
                        {
                            "label": "The merge tool was launched on the conflicted file.",
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
            "slug": "choose-a-side",
            "title": "Choose a Side",
            "waves": [
                _wave(
                    "ch4-adv-take-ours-intro",
                    "git-checkout-conflict/ours",
                    "Keep our version",
                    ["git checkout --ours src/auth.js"],
                    required=["git checkout --ours"],
                    state="conflict",
                    story=(
                        "The decision is made: your branch's version of the conflicted file "
                        "wins. Replace the conflict markers with our side's content - just the "
                        "file choice, nothing staged or finished yet."
                    ),
                    evaluation={
                        "rules": [
                            {
                                "type": "operation_metadata_equals",
                                "key": "last_checkout_conflict_side",
                                "value": "ours",
                            }
                        ]
                    },
                    checks=[
                        {
                            "label": "Our side's content now fills the conflicted file.",
                            "requirement": {
                                "rules": [
                                    {
                                        "type": "operation_metadata_equals",
                                        "key": "last_checkout_conflict_side",
                                        "value": "ours",
                                    }
                                ]
                            },
                        },
                    ],
                ),
                _wave(
                    "ch4-adv-take-theirs-intro",
                    "git-checkout-conflict/theirs",
                    "Take the incoming version",
                    ["git checkout --theirs src/auth.js"],
                    required=["git checkout --theirs"],
                    state="conflict",
                    story=(
                        "This time the incoming branch clearly knows better. Replace the "
                        "conflicted file's markers with their side's content - only the file "
                        "choice for now, nothing staged or finished."
                    ),
                    evaluation={
                        "rules": [
                            {
                                "type": "operation_metadata_equals",
                                "key": "last_checkout_conflict_side",
                                "value": "theirs",
                            }
                        ]
                    },
                    checks=[
                        {
                            "label": "Their side's content now fills the conflicted file.",
                            "requirement": {
                                "rules": [
                                    {
                                        "type": "operation_metadata_equals",
                                        "key": "last_checkout_conflict_side",
                                        "value": "theirs",
                                    }
                                ]
                            },
                        },
                    ],
                ),
                _wave(
                    "ch4-adv-merge-continue-intro",
                    "git-merge/continue",
                    "Finish a resolved merge",
                    ["git merge --continue"],
                    required=["git merge --continue"],
                    state="conflict-resolved",
                    story=(
                        "The hard part is already done: the conflicted file is resolved and "
                        "staged, and the merge is waiting for one final instruction. Give it - "
                        "complete the paused merge."
                    ),
                    evaluation={
                        "staging_empty": True,
                        "latest_commit": {"branch": "main"},
                        "rules": [{"type": "commit_parent_count_equals", "count": 2}],
                    },
                    checks=[
                        {
                            "label": "The paused merge completed as a two-parent merge commit.",
                            "requirement": {
                                "staging_empty": True,
                                "rules": [{"type": "commit_parent_count_equals", "count": 2}],
                            },
                        },
                    ],
                ),
            ],
        },
        {
            "slug": "resolve-conflicts-and-finish",
            "title": "Resolve Conflicts and Finish",
            "waves": [
                _wave(
                    "ch4-adv-take-ours",
                    "git-checkout-conflict/ours",
                    "Take ours",
                    ["git checkout --ours src/auth.js", "git add src/auth.js", "git merge --continue"],
                    required=["git checkout --ours", "git add", "git merge --continue"],
                    forms=["git-add/file", "git-merge/continue"],
                    state="conflict",
                    story=(
                        "main's own timeout value is the one that should win this conflict. Take the "
                        "current branch's side for src/auth.js, stage it, and finish the merge."
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
                            "label": "The current branch's side was kept for the conflicted file.",
                            "requirement": {
                                "rules": [
                                    {
                                        "type": "operation_metadata_equals",
                                        "key": "last_checkout_conflict_side",
                                        "value": "ours",
                                    }
                                ]
                            },
                        },
                        {
                            "label": "The merge finished cleanly as a real merge commit.",
                            "requirement": {
                                "conflict_free": True,
                                "latest_commit": {"branch": "main", "contains_paths": ["src/auth.js"]},
                                "rules": [{"type": "commit_parent_count_equals", "count": 2}],
                            },
                        },
                    ],
                ),
                _wave(
                    "ch4-adv-take-theirs",
                    "git-checkout-conflict/theirs",
                    "Take theirs",
                    ["git checkout --theirs src/auth.js", "git add src/auth.js", "git merge --continue"],
                    required=["git checkout --theirs", "git add", "git merge --continue"],
                    forms=["git-add/file", "git-merge/continue"],
                    state="conflict",
                    story=(
                        "The incoming feature branch's timeout tuning is the one that should win this "
                        "conflict. Take the incoming side for src/auth.js, stage it, and finish the "
                        "merge."
                    ),
                    evaluation={
                        "conflict_free": True,
                        "latest_commit": {"branch": "main", "contains_paths": ["src/auth.js"]},
                        "rules": [
                            {"type": "commit_parent_count_equals", "count": 2},
                            {
                                "type": "operation_metadata_equals",
                                "key": "last_checkout_conflict_side",
                                "value": "theirs",
                            },
                        ],
                    },
                    checks=[
                        {
                            "label": "The incoming branch's side was kept for the conflicted file.",
                            "requirement": {
                                "rules": [
                                    {
                                        "type": "operation_metadata_equals",
                                        "key": "last_checkout_conflict_side",
                                        "value": "theirs",
                                    }
                                ]
                            },
                        },
                        {
                            "label": "The merge finished cleanly as a real merge commit.",
                            "requirement": {
                                "conflict_free": True,
                                "latest_commit": {"branch": "main", "contains_paths": ["src/auth.js"]},
                                "rules": [{"type": "commit_parent_count_equals", "count": 2}],
                            },
                        },
                    ],
                ),
                _wave(
                    "ch4-adv-manual-mixed-resolution",
                    "git-ls-files/unmerged",
                    "Manual mixed resolution",
                    [
                        "git ls-files -u",
                        "git diff --ours src/auth.js",
                        "git diff --theirs src/auth.js",
                        "git checkout --theirs src/auth.js",
                        "git add src/auth.js",
                        "git merge --continue",
                    ],
                    required=["git ls-files -u", "git diff --ours", "git diff --theirs", "git add", "git merge --continue"],
                    forms=["git-diff-conflict/ours", "git-diff-conflict/theirs", "git-checkout-conflict/theirs", "git-add/file", "git-merge/continue"],
                    state="conflict",
                    story=(
                        "This conflict deserves real evidence, not a coin flip. List the unmerged entry, "
                        "compare both timeout values side by side, and only then choose the incoming "
                        "branch's value before finishing the merge."
                    ),
                    evaluation={
                        "conflict_free": True,
                        "latest_commit": {"branch": "main", "contains_paths": ["src/auth.js"]},
                        "rules": [{"type": "commit_parent_count_equals", "count": 2}],
                    },
                    checks=[
                        {
                            "label": "The conflict was inspected from every angle before a side was chosen.",
                            "requirement": {
                                "required_commands": ["git ls-files -u", "git diff --ours", "git diff --theirs"]
                            },
                        },
                        {
                            "label": "The merge finished cleanly with the evidence-based resolution in place.",
                            "requirement": {
                                "conflict_free": True,
                                "latest_commit": {"branch": "main", "contains_paths": ["src/auth.js"]},
                                "rules": [{"type": "commit_parent_count_equals", "count": 2}],
                            },
                        },
                    ],
                ),
                _wave(
                    "ch4-adv-two-file-conflict-workflow",
                    "git-checkout-conflict/ours",
                    "Two-file conflict workflow",
                    ["git checkout --ours src/auth.js", "git add src/auth.js", "git merge --continue"],
                    required=["git checkout --ours", "git add", "git merge --continue"],
                    forms=["git-add/file", "git-merge/continue"],
                    state="conflict",
                    story=(
                        "A realistic handoff: the conflicted src/auth.js needs a deliberate decision, "
                        "not a default. Confirm main's timeout should win, resolve it explicitly, and "
                        "complete the merge with an exact, conflict-free result."
                    ),
                    evaluation={
                        "conflict_free": True,
                        "working_tree_clean": True,
                        "latest_commit": {"branch": "main", "contains_paths": ["src/auth.js"]},
                        "rules": [{"type": "commit_parent_count_equals", "count": 2}],
                    },
                    checks=[
                        {
                            "label": "The conflict resolved exactly as intended, with a clean tree afterward.",
                            "requirement": {
                                "conflict_free": True,
                                "working_tree_clean": True,
                                "latest_commit": {"branch": "main", "contains_paths": ["src/auth.js"]},
                                "rules": [{"type": "commit_parent_count_equals", "count": 2}],
                            },
                        },
                    ],
                ),
            ],
        },
        {
            "slug": "evidence-first-resolutions",
            "title": "Evidence-First Resolutions",
            "waves": [
                _wave(
                    "ch4-adv-evidence-take-ours",
                    "git-diff-conflict/ours",
                    "Compare both, keep ours",
                    [
                        "git diff --ours src/auth.js",
                        "git diff --theirs src/auth.js",
                        "git checkout --ours src/auth.js",
                        "git add src/auth.js",
                        "git merge --continue",
                    ],
                    required=["git diff --ours", "git diff --theirs", "git checkout --ours", "git add", "git merge --continue"],
                    forms=["git-diff-conflict/theirs", "git-checkout-conflict/ours", "git-add/file", "git-merge/continue"],
                    state="conflict",
                    story=(
                        "Settle this conflict like an engineer: read both candidate versions "
                        "side by side, conclude that your branch's value is correct, keep it, "
                        "stage the resolution, and finish the merge."
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
                            "label": "Both sides were compared before choosing.",
                            "requirement": {"required_commands": ["git diff --ours", "git diff --theirs"]},
                        },
                        {
                            "label": "Our side won and the merge finished cleanly.",
                            "requirement": {
                                "conflict_free": True,
                                "rules": [
                                    {"type": "commit_parent_count_equals", "count": 2},
                                    {
                                        "type": "operation_metadata_equals",
                                        "key": "last_checkout_conflict_side",
                                        "value": "ours",
                                    },
                                ],
                            },
                        },
                    ],
                ),
                _wave(
                    "ch4-adv-base-informed-resolution",
                    "git-diff-conflict/base",
                    "Full evidence, incoming wins",
                    [
                        "git diff --base src/auth.js",
                        "git diff --ours src/auth.js",
                        "git diff --theirs src/auth.js",
                        "git checkout --theirs src/auth.js",
                        "git add src/auth.js",
                        "git merge --continue",
                    ],
                    required=["git diff --base", "git diff --ours", "git diff --theirs", "git checkout --theirs", "git add", "git merge --continue"],
                    forms=["git-diff-conflict/ours", "git-diff-conflict/theirs", "git-checkout-conflict/theirs", "git-add/file", "git-merge/continue"],
                    state="conflict",
                    story=(
                        "The full investigation: read the file at the split point, then both "
                        "competing versions. The incoming branch's tuning wins on the evidence - "
                        "take it, stage it, and complete the merge."
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
                            "label": "The base and both sides were all read first.",
                            "requirement": {
                                "required_commands": ["git diff --base", "git diff --ours", "git diff --theirs"]
                            },
                        },
                        {
                            "label": "The incoming side won and the merge finished cleanly.",
                            "requirement": {
                                "conflict_free": True,
                                "rules": [
                                    {"type": "commit_parent_count_equals", "count": 2},
                                    {
                                        "type": "operation_metadata_equals",
                                        "key": "last_checkout_conflict_side",
                                        "value": "theirs",
                                    },
                                ],
                            },
                        },
                    ],
                ),
                _wave(
                    "ch4-adv-mergetool-then-finish",
                    "git-mergetool/launch",
                    "Tool-assisted resolution",
                    ["git mergetool", "git add src/auth.js", "git merge --continue"],
                    required=["git mergetool", "git add", "git merge --continue"],
                    forms=["git-add/file", "git-merge/continue"],
                    state="conflict",
                    story=(
                        "This conflict is exactly what the configured merge tool is for. Launch "
                        "it on the conflicted file, accept the tool-assisted resolution, stage "
                        "it, and complete the merge."
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
                            "label": "The merge tool handled the conflicted file.",
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
                        {
                            "label": "The tool-assisted resolution finished the merge cleanly.",
                            "requirement": {
                                "conflict_free": True,
                                "rules": [{"type": "commit_parent_count_equals", "count": 2}],
                            },
                        },
                    ],
                ),
                _wave(
                    "ch4-adv-finish-staged-resolution",
                    "git-merge/continue",
                    "Inherited resolution, finish it",
                    ["git status", "git merge --continue", "git log --oneline --graph --all"],
                    required=["git status", "git merge --continue", "git log"],
                    forms=["git-status/plain", "git-log/graph-all"],
                    state="conflict-resolved",
                    story=(
                        "A teammate resolved and staged this conflict before stepping away. Read "
                        "the state to confirm exactly where they left off, complete the paused "
                        "merge, then draw the graph to see the joined histories."
                    ),
                    evaluation={
                        "staging_empty": True,
                        "latest_commit": {"branch": "main"},
                        "rules": [{"type": "commit_parent_count_equals", "count": 2}],
                    },
                    checks=[
                        {
                            "label": "The inherited state was read before finishing.",
                            "requirement": {"required_commands": ["git status"]},
                        },
                        {
                            "label": "The merge completed and the joined shape was drawn.",
                            "requirement": {
                                "staging_empty": True,
                                "rules": [{"type": "commit_parent_count_equals", "count": 2}],
                                "required_commands": ["git log"],
                            },
                        },
                    ],
                ),
                _wave(
                    "ch4-adv-ls-then-take-theirs",
                    "git-ls-files/unmerged",
                    "List, choose incoming, finish",
                    [
                        "git ls-files -u",
                        "git checkout --theirs src/auth.js",
                        "git add src/auth.js",
                        "git merge --continue",
                    ],
                    required=["git ls-files -u", "git checkout --theirs", "git add", "git merge --continue"],
                    forms=["git-checkout-conflict/theirs", "git-add/file", "git-merge/continue"],
                    state="conflict",
                    story=(
                        "Start from the index's own report: list the unmerged entries to scope "
                        "the problem, take the incoming side for the conflicted file, stage the "
                        "resolution, and complete the merge."
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
                            "label": "The unmerged entries were listed before acting.",
                            "requirement": {"required_commands": ["git ls-files -u"]},
                        },
                        {
                            "label": "The incoming side won and the merge finished cleanly.",
                            "requirement": {
                                "conflict_free": True,
                                "rules": [{"type": "commit_parent_count_equals", "count": 2}],
                            },
                        },
                    ],
                ),
            ],
        },
    ]
