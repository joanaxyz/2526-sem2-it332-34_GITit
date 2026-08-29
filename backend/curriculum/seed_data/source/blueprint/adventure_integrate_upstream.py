"""Blueprint adventure levels for integrate-upstream."""

from __future__ import annotations

from .helpers import _wave

ADVENTURE_LEVELS = [
        {
            "slug": "pull-and-integrate",
            "title": "Pull and Integrate",
            "waves": [
                _wave(
                    "ch7-adv-pull-default",
                    "git-pull/default",
                    "Pull default",
                    ["git pull"],
                    state="remote",
                    story=(
                        "The local main branch is clean and directly behind origin's latest work. "
                        "Bring that upstream change into main."
                    ),
                    evaluation={"rules": [{"type": "branch_points_to", "branch": "main", "commit": "r2"}]},
                    checks=[
                        {
                            "label": "The clean local branch integrated the upstream change.",
                            "requirement": {
                                "rules": [{"type": "branch_points_to", "branch": "main", "commit": "r2"}]
                            },
                        },
                    ],
                ),
                _wave(
                    "ch7-adv-pull-rebase",
                    "git-pull/rebase",
                    "Pull rebase",
                    ["git pull --rebase"],
                    state="remote-diverged",
                    story=(
                        "A local-only commit and origin's tip have both moved past their shared "
                        "starting point. Replay the local commit cleanly on top of the updated "
                        "upstream instead of merging."
                    ),
                    evaluation={
                        "latest_commit": {"branch": "main", "contains_paths": ["notes.md"], "message_contains": ["Local note"]},
                        "rules": [
                            {"type": "commit_parent_equals", "branch": "main", "parent_equals": "c1"},
                            {"type": "operation_metadata_equals", "key": "pull_strategy", "value": "rebase"},
                        ],
                    },
                    checks=[
                        {
                            "label": "The local commit's content survived and now sits on top of the updated upstream tip.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["notes.md"],
                                    "message_contains": ["Local note"],
                                },
                                "rules": [{"type": "commit_parent_equals", "branch": "main", "parent_equals": "c1"}],
                            },
                        },
                    ],
                ),
                _wave(
                    "ch7-adv-pull-with-local-work-safe",
                    "git-stash/push",
                    "Pull with local work safe",
                    ["git stash", "git pull --rebase", "git stash pop"],
                    required=["git stash", "git pull --rebase", "git stash pop"],
                    forms=["git-pull/rebase", "git-stash/pop"],
                    state="remote-dirty",
                    story=(
                        "Local WIP is sitting dirty in the working tree, and origin has moved on. "
                        "Protect the WIP before synchronizing, then bring it back afterward."
                    ),
                    evaluation={
                        "rules": [
                            {"type": "branch_points_to", "branch": "main", "commit": "r2"},
                            {"type": "operation_metadata_equals", "key": "last_stash_action", "value": "pop"},
                            {"type": "working_tree_dirty"},
                        ]
                    },
                    checks=[
                        {
                            "label": "Local work was shelved before syncing with origin.",
                            "requirement": {"required_commands": ["git stash"]},
                        },
                        {
                            "label": "main is synchronized with origin, and the local work is back afterward.",
                            "requirement": {
                                "rules": [
                                    {"type": "branch_points_to", "branch": "main", "commit": "r2"},
                                    {
                                        "type": "operation_metadata_equals",
                                        "key": "last_stash_action",
                                        "value": "pop",
                                    },
                                    {"type": "working_tree_dirty"},
                                ]
                            },
                        },
                    ],
                ),
                _wave(
                    "ch7-adv-pull-then-log",
                    "git-pull/default",
                    "Sync, then read what arrived",
                    ["git pull", "git log --oneline"],
                    required=["git pull", "git log"],
                    forms=["git-log/oneline"],
                    state="remote",
                    story=(
                        "Origin moved ahead overnight. Bring the upstream work into the clean "
                        "local branch, then read the compact history to see exactly what the "
                        "team shipped while you slept."
                    ),
                    evaluation={
                        "rules": [{"type": "branch_points_to", "branch": "main", "commit": "r2"}]
                    },
                    checks=[
                        {
                            "label": "The upstream work is integrated into main.",
                            "requirement": {
                                "rules": [{"type": "branch_points_to", "branch": "main", "commit": "r2"}]
                            },
                        },
                        {
                            "label": "The arrivals were read afterward.",
                            "requirement": {"required_commands": ["git log"]},
                        },
                    ],
                ),
                _wave(
                    "ch7-adv-status-then-pull",
                    "git-pull/default",
                    "Confirm clean, then sync",
                    ["git status", "git pull"],
                    required=["git status", "git pull"],
                    forms=["git-status/plain"],
                    state="remote",
                    story=(
                        "The golden rule of syncing: know your own state first. Confirm the "
                        "working tree is clean, then bring the upstream work in without "
                        "surprises."
                    ),
                    evaluation={
                        "rules": [{"type": "branch_points_to", "branch": "main", "commit": "r2"}]
                    },
                    checks=[
                        {
                            "label": "The local state was confirmed before syncing.",
                            "requirement": {"required_commands": ["git status"]},
                        },
                        {
                            "label": "The upstream work is integrated into main.",
                            "requirement": {
                                "rules": [{"type": "branch_points_to", "branch": "main", "commit": "r2"}]
                            },
                        },
                    ],
                ),
                _wave(
                    "ch7-adv-fetch-inspect-pull",
                    "git-pull/default",
                    "Look before you integrate",
                    ["git fetch origin", "git log --oneline --graph --all", "git pull"],
                    required=["git fetch", "git log", "git pull"],
                    forms=["git-fetch/origin", "git-log/graph-all"],
                    state="remote",
                    story=(
                        "The cautious sync: refresh what you know about origin without moving "
                        "anything, draw the graph to inspect what is incoming, and only then "
                        "integrate it into the local branch."
                    ),
                    evaluation={
                        "rules": [{"type": "branch_points_to", "branch": "main", "commit": "r2"}]
                    },
                    checks=[
                        {
                            "label": "The incoming work was inspected before integrating.",
                            "requirement": {"required_commands": ["git fetch", "git log"]},
                        },
                        {
                            "label": "The upstream work is integrated into main.",
                            "requirement": {
                                "rules": [{"type": "branch_points_to", "branch": "main", "commit": "r2"}]
                            },
                        },
                    ],
                ),
                _wave(
                    "ch7-adv-pull-rebase-verify",
                    "git-pull/rebase",
                    "Replay, then read the new order",
                    ["git pull --rebase", "git log --oneline"],
                    required=["git pull --rebase", "git log"],
                    forms=["git-log/oneline"],
                    state="remote-diverged",
                    story=(
                        "Local work and upstream work both moved past their shared start. "
                        "Replay the local commit on top of the teammate's, then read the "
                        "compact history to see the clean, linear result."
                    ),
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["notes.md"],
                            "message_contains": ["Local note"],
                        },
                        "rules": [
                            {"type": "commit_parent_equals", "branch": "main", "parent_equals": "c1"},
                            {"type": "operation_metadata_equals", "key": "pull_strategy", "value": "rebase"},
                        ],
                    },
                    checks=[
                        {
                            "label": "The local commit now sits on top of the upstream tip.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "message_contains": ["Local note"],
                                },
                                "rules": [
                                    {"type": "commit_parent_equals", "branch": "main", "parent_equals": "c1"}
                                ],
                            },
                        },
                        {
                            "label": "The linear result was read afterward.",
                            "requirement": {"required_commands": ["git log"]},
                        },
                    ],
                ),
                _wave(
                    "ch7-adv-remote-check-pull",
                    "git-pull/default",
                    "Verify the source, then sync",
                    ["git remote -v", "git pull"],
                    required=["git remote -v", "git pull"],
                    forms=["git-remote/verbose"],
                    state="remote",
                    story=(
                        "On a borrowed machine, never sync blind: verify which server this "
                        "checkout actually pulls from, then bring the upstream work in."
                    ),
                    evaluation={
                        "rules": [{"type": "branch_points_to", "branch": "main", "commit": "r2"}]
                    },
                    checks=[
                        {
                            "label": "The sync source was verified first.",
                            "requirement": {"required_commands": ["git remote -v"]},
                        },
                        {
                            "label": "The upstream work is integrated into main.",
                            "requirement": {
                                "rules": [{"type": "branch_points_to", "branch": "main", "commit": "r2"}]
                            },
                        },
                    ],
                ),
            ],
        },
        {
            "slug": "upstream-drills",
            "title": "Upstream Drills",
            "waves": [
                _wave(
                    "ch7-adv-pull-drill-morning",
                    "git-pull/default",
                    "The morning sync",
                    ["git status -s", "git pull"],
                    required=["git status -s", "git pull"],
                    forms=["git-status/short"],
                    state="remote",
                    story=(
                        "First coffee, first command: a compact glance to confirm nothing "
                        "local is at risk, then the morning sync that starts every workday."
                    ),
                    evaluation={
                        "rules": [{"type": "branch_points_to", "branch": "main", "commit": "r2"}]
                    },
                    checks=[
                        {
                            "label": "The glance came before the sync.",
                            "requirement": {"required_commands": ["git status -s"]},
                        },
                        {
                            "label": "The morning sync landed the upstream work.",
                            "requirement": {
                                "rules": [{"type": "branch_points_to", "branch": "main", "commit": "r2"}]
                            },
                        },
                    ],
                ),
                _wave(
                    "ch7-adv-pull-then-show",
                    "git-pull/default",
                    "Sync, then open the newest work",
                    ["git pull", "git show"],
                    required=["git pull", "git show"],
                    forms=["git-show/head"],
                    state="remote",
                    story=(
                        "Bring the upstream work in, then open the newest snapshot and read "
                        "the teammate's change in full - syncing is not the same as knowing "
                        "what arrived."
                    ),
                    evaluation={
                        "rules": [{"type": "branch_points_to", "branch": "main", "commit": "r2"}]
                    },
                    checks=[
                        {
                            "label": "The upstream work is integrated.",
                            "requirement": {
                                "rules": [{"type": "branch_points_to", "branch": "main", "commit": "r2"}]
                            },
                        },
                        {
                            "label": "The arriving change was opened and read.",
                            "requirement": {"required_commands": ["git show"]},
                        },
                    ],
                ),
                _wave(
                    "ch7-adv-rebase-flow-check",
                    "git-pull/rebase",
                    "Replay, then check the top two",
                    ["git pull --rebase", "git log -n 2"],
                    required=["git pull --rebase", "git log"],
                    forms=["git-log/limit"],
                    state="remote-diverged",
                    story=(
                        "After replaying local work on top of the upstream tip, the top two "
                        "history entries should read: your commit, then the teammate's. Replay "
                        "and confirm exactly that."
                    ),
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["notes.md"],
                            "message_contains": ["Local note"],
                        },
                        "rules": [
                            {"type": "operation_metadata_equals", "key": "pull_strategy", "value": "rebase"},
                        ],
                    },
                    checks=[
                        {
                            "label": "The local work was replayed with the rebase strategy.",
                            "requirement": {
                                "rules": [
                                    {
                                        "type": "operation_metadata_equals",
                                        "key": "pull_strategy",
                                        "value": "rebase",
                                    }
                                ]
                            },
                        },
                        {
                            "label": "The new order was confirmed from the top entries.",
                            "requirement": {"required_commands": ["git log"]},
                        },
                    ],
                ),
                _wave(
                    "ch7-adv-rebase-final",
                    "git-pull/rebase",
                    "Replay, then confirm calm",
                    ["git pull --rebase", "git status"],
                    required=["git pull --rebase", "git status"],
                    forms=["git-status/plain"],
                    state="remote-diverged",
                    story=(
                        "Replay the local commit onto the updated upstream, then read the "
                        "state to confirm the rebase left nothing half-done: clean tree, "
                        "nothing staged, one tidy linear history."
                    ),
                    evaluation={
                        "working_tree_clean": True,
                        "staging_empty": True,
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["notes.md"],
                            "message_contains": ["Local note"],
                        },
                        "rules": [
                            {"type": "operation_metadata_equals", "key": "pull_strategy", "value": "rebase"},
                        ],
                    },
                    checks=[
                        {
                            "label": "The local work was replayed onto the upstream tip.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "message_contains": ["Local note"],
                                },
                                "rules": [
                                    {"type": "commit_parent_equals", "branch": "main", "parent_equals": "c1"}
                                ],
                            },
                        },
                        {
                            "label": "The calm end state was confirmed.",
                            "requirement": {"required_commands": ["git status"]},
                        },
                    ],
                ),
                _wave(
                    "ch7-adv-land-before-publish",
                    "git-merge/branch",
                    "Land the feature before sharing",
                    ["git merge feature/profile", "git log --oneline"],
                    required=["git merge", "git log"],
                    forms=["git-log/oneline"],
                    state="merge",
                    story=(
                        "Before anything gets published this afternoon, the finished profile "
                        "feature must land in main. Integrate the diverged branch, then read "
                        "the compact history to confirm the landing."
                    ),
                    evaluation={
                        "latest_commit": {"branch": "main"},
                        "rules": [{"type": "commit_parent_count_equals", "count": 2}],
                    },
                    checks=[
                        {
                            "label": "The feature landed as a two-parent merge commit.",
                            "requirement": {
                                "latest_commit": {"branch": "main"},
                                "rules": [{"type": "commit_parent_count_equals", "count": 2}],
                            },
                        },
                        {
                            "label": "The landing was confirmed in the history.",
                            "requirement": {"required_commands": ["git log"]},
                        },
                    ],
                ),
                _wave(
                    "ch7-adv-land-second-feature",
                    "git-merge/branch",
                    "State check, then integrate",
                    ["git status", "git merge feature/profile"],
                    required=["git status", "git merge"],
                    forms=["git-status/plain"],
                    state="merge",
                    story=(
                        "One more feature is signed off for this release train. Confirm the "
                        "workspace is calm, then integrate the diverged feature branch into "
                        "main before the publish window opens."
                    ),
                    evaluation={
                        "latest_commit": {"branch": "main"},
                        "rules": [{"type": "commit_parent_count_equals", "count": 2}],
                    },
                    checks=[
                        {
                            "label": "The workspace was checked before integrating.",
                            "requirement": {"required_commands": ["git status"]},
                        },
                        {
                            "label": "The feature landed as a merge commit.",
                            "requirement": {
                                "latest_commit": {"branch": "main"},
                                "rules": [{"type": "commit_parent_count_equals", "count": 2}],
                            },
                        },
                    ],
                ),
                _wave(
                    "ch7-adv-insurance-then-land",
                    "git-merge/branch",
                    "Insurance pointer, then integrate",
                    ["git branch pre-merge-backup", "git merge feature/profile"],
                    required=["git branch", "git merge"],
                    forms=["git-branch/create"],
                    state="merge",
                    story=(
                        "Big integration, careful habits: leave a plain pointer on main's "
                        "current tip first, then merge the feature knowing the pre-merge state "
                        "keeps a name either way."
                    ),
                    details=[{"label": "Insurance branch", "value": "pre-merge-backup"}],
                    evaluation={
                        "latest_commit": {"branch": "main"},
                        "rules": [
                            {"type": "commit_parent_count_equals", "count": 2},
                            {"type": "branch_exists", "branch": "pre-merge-backup"},
                        ],
                    },
                    checks=[
                        {
                            "label": "The insurance pointer marks the pre-merge tip.",
                            "requirement": {
                                "rules": [{"type": "branch_exists", "branch": "pre-merge-backup"}]
                            },
                        },
                        {
                            "label": "The feature landed as a merge commit.",
                            "requirement": {
                                "latest_commit": {"branch": "main"},
                                "rules": [{"type": "commit_parent_count_equals", "count": 2}],
                            },
                        },
                    ],
                ),
            ],
        },
    ]
