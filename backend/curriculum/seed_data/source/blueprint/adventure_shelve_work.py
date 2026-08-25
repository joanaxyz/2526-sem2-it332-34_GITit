"""Blueprint adventure levels for shelve-work."""

from __future__ import annotations

from .helpers import _wave

ADVENTURE_LEVELS = [
        {
            "slug": "shelve-local-work",
            "title": "Shelve Local Work",
            "waves": [
                _wave(
                    "ch6-adv-stash-current-work",
                    "git-stash/push",
                    "Stash current work",
                    ["git stash"],
                    state="stash-dirty",
                    story=(
                        "src/app.py and src/dashboard.py both have unfinished edits, but a different "
                        "task needs your attention right now. Put this work away so the tree is clean, "
                        "without committing anything unfinished."
                    ),
                    evaluation={
                        "working_tree_clean": True,
                        "staging_empty": True,
                        "rules": [{"type": "operation_metadata_equals", "key": "stash_count", "value": 1}],
                    },
                    checks=[
                        {
                            "label": "The unfinished work is shelved; the tree is clean and one stash entry exists.",
                            "requirement": {
                                "working_tree_clean": True,
                                "rules": [{"type": "operation_metadata_equals", "key": "stash_count", "value": 1}],
                            },
                        },
                    ],
                ),
                _wave(
                    "ch6-adv-list-stashes",
                    "git-stash/list",
                    "List stashes",
                    ["git stash list"],
                    state="stashed",
                    story=(
                        "Before restoring anything, confirm exactly what is sitting in the stash stack "
                        "and from which commit it was shelved."
                    ),
                    evaluation={"rules": [{"type": "commit_count_equals", "count": 3}]},
                    checks=[
                        {
                            "label": "The stash stack was listed before touching anything.",
                            "requirement": {"required_commands": ["git stash list"]},
                        },
                    ],
                ),
                _wave(
                    "ch6-adv-stash-before-switch",
                    "git-stash/push",
                    "Stash before switch",
                    ["git status", "git stash", "git switch hotfix/navbar"],
                    required=["git status", "git stash", "git switch"],
                    forms=["git-status/plain", "git-switch/existing"],
                    state="stash-dirty",
                    story=(
                        "hotfix/navbar suddenly needs attention, but the working tree is not clean "
                        "enough to switch safely. Check the status, shelve the local work, and move "
                        "onto the hotfix branch."
                    ),
                    evaluation={
                        "head_branch": "hotfix/navbar",
                        "rules": [{"type": "operation_metadata_equals", "key": "stash_count", "value": 1}],
                    },
                    checks=[
                        {
                            "label": "The dirty tree was checked, then shelved before switching.",
                            "requirement": {
                                "required_commands": ["git status", "git stash"],
                                "rules": [{"type": "operation_metadata_equals", "key": "stash_count", "value": 1}],
                            },
                        },
                        {
                            "label": "HEAD landed cleanly on hotfix/navbar with the local WIP preserved in the stash.",
                            "requirement": {"head_branch": "hotfix/navbar"},
                        },
                    ],
                ),
            ],
        },
        {
            "slug": "restore-stashed-work",
            "title": "Restore Stashed Work",
            "waves": [
                _wave(
                    "ch6-adv-pop-stash",
                    "git-stash/pop",
                    "Pop stash",
                    ["git stash pop"],
                    state="stashed",
                    story=(
                        "The shelved work is needed again, and the stash entry itself has no further "
                        "use once it's back. Restore it and remove the stash entry in the same move."
                    ),
                    evaluation={
                        "rules": [
                            {"type": "working_tree_contains", "path": "src/app.py"},
                            {"type": "operation_metadata_equals", "key": "stash_count", "value": 0},
                        ]
                    },
                    checks=[
                        {
                            "label": "The shelved work is restored, and the stash entry is gone.",
                            "requirement": {
                                "rules": [
                                    {"type": "working_tree_contains", "path": "src/app.py"},
                                    {"type": "operation_metadata_equals", "key": "stash_count", "value": 0},
                                ]
                            },
                        },
                    ],
                ),
                _wave(
                    "ch6-adv-apply-stash",
                    "git-stash/apply",
                    "Apply stash",
                    ["git stash apply"],
                    state="stashed",
                    story=(
                        "This shelved work might still be useful somewhere else, so keep the stash "
                        "entry around even after restoring it here."
                    ),
                    evaluation={
                        "rules": [
                            {"type": "working_tree_contains", "path": "src/app.py"},
                            {"type": "operation_metadata_equals", "key": "stash_count", "value": 1},
                        ]
                    },
                    checks=[
                        {
                            "label": "The shelved work is restored to the working tree, and the stash entry is kept for reuse.",
                            "requirement": {
                                "rules": [{"type": "working_tree_contains", "path": "src/app.py"}]
                            },
                        },
                    ],
                ),
                _wave(
                    "ch6-adv-drop-stash",
                    "git-stash/drop",
                    "Drop stash",
                    ["git stash drop"],
                    state="stashed",
                    story=(
                        "This shelved work turned out to be unnecessary after all. Delete the stash "
                        "entry outright, without restoring it to the working tree."
                    ),
                    evaluation={
                        "working_tree_clean": True,
                        "rules": [{"type": "operation_metadata_equals", "key": "stash_count", "value": 0}],
                    },
                    checks=[
                        {
                            "label": "The stash entry is gone, and nothing was restored to the working tree.",
                            "requirement": {
                                "working_tree_clean": True,
                                "rules": [
                                    {"type": "operation_metadata_equals", "key": "stash_count", "value": 0}
                                ],
                            },
                        },
                    ],
                ),
                _wave(
                    "ch6-adv-stash-restore-commit",
                    "git-stash/push",
                    "Stash restore commit",
                    [
                        "git stash",
                        "git switch hotfix/navbar",
                        "git add README.md",
                        "git commit -m 'Commit urgent fix'",
                        "git switch main",
                        "git stash pop",
                        "git add src/app.py",
                        "git commit -m 'Save restored WIP'",
                    ],
                    required=["git stash", "git switch", "git commit", "git stash pop"],
                    forms=["git-switch/existing", "git-add/file", "git-commit/message", "git-stash/pop"],
                    state="stash-dirty",
                    story=(
                        "Unfinished work across src/app.py and src/dashboard.py can't follow you onto "
                        "hotfix/navbar for an urgent look. Shelve it, handle the interruption, come "
                        "back, and land your own work as a real commit exactly where you left off."
                    ),
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["src/app.py"],
                            "message_contains": ["Save restored WIP"],
                        },
                        "staging_empty": True,
                        "rules": [
                            {"type": "operation_metadata_equals", "key": "last_stash_action", "value": "pop"}
                        ],
                    },
                    checks=[
                        {
                            "label": "The interruption was handled on hotfix/navbar after shelving local work.",
                            "requirement": {"required_commands": ["git stash", "git switch"]},
                        },
                        {
                            "label": "The restored work landed as a real commit back on main.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["src/app.py"],
                                    "message_contains": ["Save restored WIP"],
                                }
                            },
                        },
                    ],
                    workspace_files=[
                        {
                            "after_command_index": 2,
                            "path": "README.md",
                            "content": "base\nUrgent navbar fix\n",
                        }
                    ],
                ),
            ],
        },
        {
            "slug": "manage-the-stash-stack",
            "title": "Manage the Stash Stack",
            "waves": [
                _wave(
                    "ch6-adv-list-then-pop",
                    "git-stash/pop",
                    "Check the shelf, then restore",
                    ["git stash list", "git stash pop"],
                    required=["git stash list", "git stash pop"],
                    forms=["git-stash/list"],
                    state="stashed",
                    story=(
                        "Never restore blind: read the stash stack first to confirm what is "
                        "shelved and where it came from, then restore it and clear the entry in "
                        "one move."
                    ),
                    evaluation={
                        "rules": [
                            {"type": "working_tree_contains", "path": "src/app.py"},
                            {"type": "operation_metadata_equals", "key": "stash_count", "value": 0},
                        ]
                    },
                    checks=[
                        {
                            "label": "The stack was read before restoring.",
                            "requirement": {"required_commands": ["git stash list"]},
                        },
                        {
                            "label": "The work is back and the shelf entry is gone.",
                            "requirement": {
                                "rules": [
                                    {"type": "working_tree_contains", "path": "src/app.py"},
                                    {"type": "operation_metadata_equals", "key": "stash_count", "value": 0},
                                ]
                            },
                        },
                    ],
                ),
                _wave(
                    "ch6-adv-list-then-apply",
                    "git-stash/apply",
                    "Check the shelf, restore a copy",
                    ["git stash list", "git stash apply"],
                    required=["git stash list", "git stash apply"],
                    forms=["git-stash/list"],
                    state="stashed",
                    story=(
                        "This shelved work is needed here and might be needed again elsewhere. "
                        "Read the stack, then restore the work while keeping the shelf entry "
                        "intact for reuse."
                    ),
                    evaluation={
                        "rules": [
                            {"type": "working_tree_contains", "path": "src/app.py"},
                            {"type": "operation_metadata_equals", "key": "stash_count", "value": 1},
                        ]
                    },
                    checks=[
                        {
                            "label": "The stack was read before restoring.",
                            "requirement": {"required_commands": ["git stash list"]},
                        },
                        {
                            "label": "The work is back while the shelf entry survives.",
                            "requirement": {
                                "rules": [{"type": "working_tree_contains", "path": "src/app.py"}]
                            },
                        },
                    ],
                ),
                _wave(
                    "ch6-adv-list-then-drop",
                    "git-stash/drop",
                    "Check the shelf, then clear it",
                    ["git stash list", "git stash drop", "git status"],
                    required=["git stash list", "git stash drop", "git status"],
                    forms=["git-stash/list", "git-status/plain"],
                    state="stashed",
                    story=(
                        "The shelved experiment is officially dead. Read the stack to confirm "
                        "which entry is about to go, delete it without restoring anything, then "
                        "check the state to prove the workspace stayed clean."
                    ),
                    evaluation={
                        "working_tree_clean": True,
                        "rules": [{"type": "operation_metadata_equals", "key": "stash_count", "value": 0}],
                    },
                    checks=[
                        {
                            "label": "The stack was read before deleting.",
                            "requirement": {"required_commands": ["git stash list"]},
                        },
                        {
                            "label": "The entry is gone and nothing leaked into the workspace.",
                            "requirement": {
                                "working_tree_clean": True,
                                "rules": [
                                    {"type": "operation_metadata_equals", "key": "stash_count", "value": 0}
                                ],
                            },
                        },
                    ],
                ),
                _wave(
                    "ch6-adv-apply-then-commit",
                    "git-stash/apply",
                    "Restore a copy, land it",
                    ["git stash apply", "git add src/app.py", "git commit -m 'Land restored work'"],
                    required=["git stash apply", "git add", "git commit"],
                    forms=["git-add/file", "git-commit/message"],
                    state="stashed",
                    story=(
                        "The shelved work is ready to become real history here, but the shelf "
                        "copy should survive as insurance until the commit is reviewed. Restore "
                        "a copy, stage it, and land it."
                    ),
                    details=[{"label": "Commit message", "value": "Land restored work"}],
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["src/app.py"],
                            "message_contains": ["Land restored work"],
                        },
                        "rules": [{"type": "operation_metadata_equals", "key": "stash_count", "value": 1}],
                    },
                    checks=[
                        {
                            "label": "The restored work landed as a real commit.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["src/app.py"],
                                    "message_contains": ["Land restored work"],
                                }
                            },
                        },
                        {
                            "label": "The shelf copy survives as insurance.",
                            "requirement": {
                                "rules": [
                                    {"type": "operation_metadata_equals", "key": "stash_count", "value": 1}
                                ]
                            },
                        },
                    ],
                ),
                _wave(
                    "ch6-adv-apply-then-drop",
                    "git-stash/drop",
                    "Restore, verify, then clear",
                    ["git stash apply", "git stash drop"],
                    required=["git stash apply", "git stash drop"],
                    forms=["git-stash/apply"],
                    state="stashed",
                    story=(
                        "The careful two-step restore: bring the work back while the shelf "
                        "entry still exists, confirm it arrived intact, and only then clear the "
                        "entry manually."
                    ),
                    evaluation={
                        "rules": [
                            {"type": "working_tree_contains", "path": "src/app.py"},
                            {"type": "operation_metadata_equals", "key": "stash_count", "value": 0},
                        ]
                    },
                    checks=[
                        {
                            "label": "The work is back in the working tree.",
                            "requirement": {
                                "rules": [{"type": "working_tree_contains", "path": "src/app.py"}]
                            },
                        },
                        {
                            "label": "The shelf entry was cleared only after the restore.",
                            "requirement": {
                                "rules": [
                                    {"type": "operation_metadata_equals", "key": "stash_count", "value": 0}
                                ]
                            },
                        },
                    ],
                ),
                _wave(
                    "ch6-adv-stash-cycle",
                    "git-stash/push",
                    "One full shelf cycle",
                    ["git stash", "git stash list", "git stash pop"],
                    required=["git stash", "git stash list", "git stash pop"],
                    forms=["git-stash/list", "git-stash/pop"],
                    state="stash-dirty",
                    story=(
                        "Run one complete shelf cycle on purpose: put the unfinished work away, "
                        "read the stack entry it created, and bring it straight back - ending "
                        "exactly where you started, but with the whole mechanism understood."
                    ),
                    evaluation={
                        "working_tree_dirty": True,
                        "rules": [
                            {"type": "operation_metadata_equals", "key": "last_stash_action", "value": "pop"},
                            {"type": "operation_metadata_equals", "key": "stash_count", "value": 0},
                        ],
                    },
                    checks=[
                        {
                            "label": "The full cycle ran: shelve, read, restore.",
                            "requirement": {
                                "required_commands": ["git stash", "git stash list", "git stash pop"]
                            },
                        },
                    ],
                ),
            ],
        },
        {
            "slug": "interruption-drills",
            "title": "Interruption Drills",
            "waves": [
                _wave(
                    "ch6-adv-shelve-fix-return",
                    "git-stash/push",
                    "Interrupt, fix, restore carefully",
                    [
                        "git stash",
                        "git switch hotfix/navbar",
                        "git add README.md",
                        "git commit -m 'Quick navbar patch'",
                        "git switch main",
                        "git stash apply",
                        "git stash drop",
                    ],
                    required=["git stash", "git switch", "git add", "git commit", "git stash apply", "git stash drop"],
                    forms=["git-switch/existing", "git-add/file", "git-commit/message", "git-stash/apply", "git-stash/drop"],
                    state="stash-dirty",
                    story=(
                        "A navbar emergency interrupts unfinished work. Shelve it, patch the "
                        "hotfix branch, come home, and do the cautious restore: bring the work "
                        "back while keeping the shelf entry, then clear it only once everything "
                        "looks right."
                    ),
                    details=[{"label": "Hotfix message", "value": "Quick navbar patch"}],
                    evaluation={
                        "head_branch": "main",
                        "rules": [
                            {"type": "working_tree_contains", "path": "src/app.py"},
                            {"type": "operation_metadata_equals", "key": "stash_count", "value": 0},
                            {"type": "operation_metadata_equals", "key": "last_stash_action", "value": "drop"},
                        ],
                    },
                    checks=[
                        {
                            "label": "The emergency was patched on its own branch after shelving.",
                            "requirement": {
                                "required_commands": ["git stash", "git switch", "git commit"]
                            },
                        },
                        {
                            "label": "The shelved work is back and the shelf is clear.",
                            "requirement": {
                                "rules": [
                                    {"type": "working_tree_contains", "path": "src/app.py"},
                                    {"type": "operation_metadata_equals", "key": "stash_count", "value": 0},
                                ]
                            },
                        },
                    ],
                    workspace_files=[
                        {
                            "after_command_index": 2,
                            "path": "README.md",
                            "content": "base\nQuick navbar patch\n",
                        }
                    ],
                ),
                _wave(
                    "ch6-adv-drop-stale-stash",
                    "git-stash/drop",
                    "Clear the shelf, prove it",
                    ["git stash drop", "git stash list"],
                    required=["git stash drop", "git stash list"],
                    forms=["git-stash/list"],
                    state="stashed",
                    story=(
                        "That shelved experiment has been sitting for weeks and its moment has "
                        "passed. Delete the entry, then read the stack once more to prove the "
                        "shelf is truly empty."
                    ),
                    evaluation={
                        "working_tree_clean": True,
                        "rules": [{"type": "operation_metadata_equals", "key": "stash_count", "value": 0}],
                    },
                    checks=[
                        {
                            "label": "The stale entry is deleted without restoring.",
                            "requirement": {
                                "working_tree_clean": True,
                                "rules": [
                                    {"type": "operation_metadata_equals", "key": "stash_count", "value": 0}
                                ],
                            },
                        },
                        {
                            "label": "The empty shelf was confirmed afterward.",
                            "requirement": {"required_commands": ["git stash list"]},
                        },
                    ],
                ),
                _wave(
                    "ch6-adv-branch-for-restored-work",
                    "git-switch/create",
                    "Restore onto a fresh line",
                    [
                        "git switch -c feature/wip-landing",
                        "git stash pop",
                        "git add src/app.py",
                        "git commit -m 'Land WIP on its own line'",
                    ],
                    required=["git switch -c", "git stash pop", "git add", "git commit"],
                    forms=["git-stash/pop", "git-add/file", "git-commit/message"],
                    state="stashed",
                    story=(
                        "The shelved work deserves better than landing straight on main. "
                        "Create a fresh line for it, restore the work there, and commit it "
                        "where it can be reviewed properly."
                    ),
                    details=[{"label": "New branch", "value": "feature/wip-landing"}],
                    evaluation={
                        "head_branch": "feature/wip-landing",
                        "latest_commit": {
                            "branch": "feature/wip-landing",
                            "contains_paths": ["src/app.py"],
                            "message_contains": ["Land WIP on its own line"],
                        },
                        "rules": [{"type": "operation_metadata_equals", "key": "stash_count", "value": 0}],
                    },
                    checks=[
                        {
                            "label": "The restored work landed on its own fresh line.",
                            "requirement": {
                                "head_branch": "feature/wip-landing",
                                "latest_commit": {
                                    "branch": "feature/wip-landing",
                                    "message_contains": ["Land WIP on its own line"],
                                },
                            },
                        },
                    ],
                ),
                _wave(
                    "ch6-adv-legacy-line-stash",
                    "git-checkout/legacy-create",
                    "Old spelling, careful restore",
                    ["git checkout -b review/stash-check", "git stash apply"],
                    required=["git checkout -b", "git stash apply"],
                    forms=["git-stash/apply"],
                    state="stashed",
                    story=(
                        "A teammate's muscle memory creates the review line the old way before "
                        "restoring the shelved work onto it - keeping the shelf entry until the "
                        "review passes. Follow their exact steps."
                    ),
                    details=[{"label": "New branch", "value": "review/stash-check"}],
                    evaluation={
                        "head_branch": "review/stash-check",
                        "rules": [
                            {"type": "working_tree_contains", "path": "src/app.py"},
                            {"type": "operation_metadata_equals", "key": "stash_count", "value": 1},
                        ],
                    },
                    checks=[
                        {
                            "label": "The review line was created with the legacy spelling.",
                            "requirement": {"head_branch": "review/stash-check"},
                        },
                        {
                            "label": "The work is restored while the shelf entry survives.",
                            "requirement": {
                                "rules": [{"type": "working_tree_contains", "path": "src/app.py"}]
                            },
                        },
                    ],
                ),
                _wave(
                    "ch6-adv-final-drop-audit",
                    "git-stash/drop",
                    "Glance, then clear the shelf",
                    ["git status -s", "git stash drop"],
                    required=["git status -s", "git stash drop"],
                    forms=["git-status/short"],
                    state="stashed",
                    story=(
                        "End-of-sprint housekeeping: confirm with a compact glance that the "
                        "workspace holds nothing unsaved, then clear the obsolete shelf entry "
                        "for good."
                    ),
                    evaluation={
                        "working_tree_clean": True,
                        "rules": [{"type": "operation_metadata_equals", "key": "stash_count", "value": 0}],
                    },
                    checks=[
                        {
                            "label": "The workspace was checked before clearing.",
                            "requirement": {"required_commands": ["git status -s"]},
                        },
                        {
                            "label": "The obsolete entry is gone.",
                            "requirement": {
                                "rules": [
                                    {"type": "operation_metadata_equals", "key": "stash_count", "value": 0}
                                ]
                            },
                        },
                    ],
                ),
            ],
        },
    ]
