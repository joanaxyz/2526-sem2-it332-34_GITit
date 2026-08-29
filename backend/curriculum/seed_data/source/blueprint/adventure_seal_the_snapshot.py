"""Blueprint adventure levels for seal-the-snapshot."""

from __future__ import annotations

from .helpers import _wave

ADVENTURE_LEVELS = [
        {
            "slug": "commit-tracked-work",
            "title": "Commit Tracked Work Directly",
            "waves": [
                _wave(
                    "ch2-adv-commit-tracked-directly",
                    "git-commit/all-message",
                    "Commit tracked directly",
                    ["git commit -a -m 'Save tracked edits'"],
                    state="dirty",
                    story=(
                        "README.md is already a tracked file with a pending edit, and nothing new needs "
                        "adding. Save the tracked change directly, without a separate staging step."
                    ),
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["README.md"],
                            "message_contains": ["Save tracked edits"],
                        },
                        "staging_empty": True,
                        "working_tree_clean": True,
                    },
                    checks=[
                        {
                            "label": "The tracked edit is committed directly on main.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["README.md"],
                                    "message_contains": ["Save tracked edits"],
                                }
                            },
                        },
                    ],
                ),
                _wave(
                    "ch2-adv-tracked-commit-verify",
                    "git-commit/all-message",
                    "Direct commit, verified landing",
                    ["git status -s", "git commit -a -m 'Ship tracked fix'", "git log --oneline"],
                    required=["git status -s", "git commit -a", "git log"],
                    forms=["git-status/short", "git-log/oneline"],
                    state="dirty",
                    story=(
                        "One tracked fix is pending and nothing new needs adding. Glance at the "
                        "state, save the tracked work in a single direct step, then read history "
                        "to confirm the fix landed."
                    ),
                    details=[{"label": "Commit message", "value": "Ship tracked fix"}],
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["README.md"],
                            "message_contains": ["Ship tracked fix"],
                        },
                        "staging_empty": True,
                        "working_tree_clean": True,
                        "rules": [{"type": "commit_count_equals", "count": 2}],
                    },
                    checks=[
                        {
                            "label": "The tracked fix was committed in one direct step.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["README.md"],
                                    "message_contains": ["Ship tracked fix"],
                                }
                            },
                        },
                        {
                            "label": "The landing was verified against history.",
                            "requirement": {"required_commands": ["git log"]},
                        },
                    ],
                ),
                _wave(
                    "ch2-adv-tracked-commit-audit",
                    "git-commit/all-message",
                    "Direct commit, sized audit",
                    ["git commit -a -m 'Record tracked update'", "git log --stat"],
                    required=["git commit -a", "git log --stat"],
                    forms=["git-log/stat"],
                    state="dirty",
                    story=(
                        "Save the pending tracked edit directly, then read the history with its "
                        "change summaries to see exactly how large the new snapshot is compared to "
                        "the ones before it."
                    ),
                    details=[{"label": "Commit message", "value": "Record tracked update"}],
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["README.md"],
                            "message_contains": ["Record tracked update"],
                        },
                        "staging_empty": True,
                        "working_tree_clean": True,
                        "rules": [{"type": "commit_count_equals", "count": 2}],
                    },
                    checks=[
                        {
                            "label": "The tracked edit was committed directly.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["README.md"],
                                    "message_contains": ["Record tracked update"],
                                }
                            },
                        },
                        {
                            "label": "The snapshot sizes were audited afterward.",
                            "requirement": {"required_commands": ["git log --stat"]},
                        },
                    ],
                ),
            ],
        },
        {
            "slug": "amend-local-history",
            "title": "Amend Local History",
            "waves": [
                _wave(
                    "ch2-adv-amend-message-or-content",
                    "git-commit/amend",
                    "Amend message or content",
                    ["git commit --amend -m 'Clarify local commit'"],
                    state="amend",
                    story=(
                        "The latest local commit is still just \"wip\" and has not been shared with "
                        "anyone yet. Rewrite it in place with a clear, real message before it goes "
                        "anywhere."
                    ),
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "message_contains": ["Clarify local commit"],
                        },
                        "rules": [{"type": "branch_tip_replaces_commit", "branch": "main", "old": "c1"}],
                    },
                    checks=[
                        {
                            "label": "The old \"wip\" commit is replaced in place, not followed by a new one.",
                            "requirement": {
                                "rules": [{"type": "branch_tip_replaces_commit", "branch": "main", "old": "c1"}]
                            },
                        },
                        {
                            "label": "The amended commit carries the clear message.",
                            "requirement": {
                                "latest_commit": {"branch": "main", "message_contains": ["Clarify local commit"]}
                            },
                        },
                    ],
                ),
                _wave(
                    "ch2-adv-amend-staged-intro",
                    "git-commit/no-edit",
                    "Fold staged work into the last commit",
                    ["git commit --amend --no-edit"],
                    state="amend-staged",
                    story=(
                        "A follow-up edit is already staged, and it belongs inside the latest "
                        "local commit rather than in a new one. The message is already right. Fold "
                        "the staged work in while keeping the message exactly as it is."
                    ),
                    evaluation={
                        "staging_empty": True,
                        "working_tree_clean": True,
                        "rules": [
                            {"type": "branch_tip_replaces_commit", "branch": "main", "old": "c1"},
                        ],
                    },
                    checks=[
                        {
                            "label": "The staged work is folded into the existing commit, not a new one.",
                            "requirement": {
                                "staging_empty": True,
                                "rules": [
                                    {"type": "branch_tip_replaces_commit", "branch": "main", "old": "c1"}
                                ],
                            },
                        },
                    ],
                ),
                _wave(
                    "ch2-adv-amend-without-message-change",
                    "git-commit/no-edit",
                    "Amend without message change",
                    ["git add README.md", "git commit --amend --no-edit"],
                    required=["git add", "git commit --amend --no-edit"],
                    forms=["git-add/file"],
                    state="amend-dirty",
                    story=(
                        "The latest local commit's message is already correct, but README.md has one "
                        "more forgotten edit that belongs in it. Fold that edit into the same commit "
                        "without touching the message."
                    ),
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["README.md"],
                            "message_contains": ["Update app shell"],
                        },
                        "staging_empty": True,
                        "working_tree_clean": True,
                        "rules": [{"type": "branch_tip_replaces_commit", "branch": "main", "old": "c1"}],
                    },
                    checks=[
                        {
                            "label": "The forgotten edit is folded into the existing commit, not a new one.",
                            "requirement": {
                                "rules": [{"type": "branch_tip_replaces_commit", "branch": "main", "old": "c1"}]
                            },
                        },
                        {
                            "label": "The commit message is unchanged, and the tree now includes the edit.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["README.md"],
                                    "message_contains": ["Update app shell"],
                                }
                            },
                        },
                    ],
                ),
                _wave(
                    "ch2-adv-inspect-before-amend",
                    "git-commit/amend",
                    "Inspect, then rewrite in place",
                    ["git show", "git log -n 1", "git commit --amend -m 'Describe the shell update'"],
                    required=["git show", "git log", "git commit --amend"],
                    forms=["git-show/head", "git-log/limit"],
                    state="amend",
                    story=(
                        "Before rewriting the latest local commit, gather the evidence: open the "
                        "snapshot itself, confirm it is the only entry that would be affected, and "
                        "then replace its placeholder message with the provided one."
                    ),
                    details=[{"label": "New message", "value": "Describe the shell update"}],
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "message_contains": ["Describe the shell update"],
                        },
                        "rules": [{"type": "branch_tip_replaces_commit", "branch": "main", "old": "c1"}],
                    },
                    checks=[
                        {
                            "label": "The snapshot was inspected before rewriting.",
                            "requirement": {"required_commands": ["git show", "git log"]},
                        },
                        {
                            "label": "The commit was replaced in place with the clear message.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "message_contains": ["Describe the shell update"],
                                },
                                "rules": [
                                    {"type": "branch_tip_replaces_commit", "branch": "main", "old": "c1"}
                                ],
                            },
                        },
                    ],
                ),
                _wave(
                    "ch2-adv-identity-then-amend",
                    "git-commit/no-edit",
                    "Fix identity, restamp the commit",
                    [
                        "git config --global user.name 'Learner E'",
                        "git config --global user.email learner-e@example.test",
                        "git commit --amend --no-edit",
                    ],
                    required=["git config --global user.name", "git config --global user.email", "git commit --amend --no-edit"],
                    forms=["git-config/global-user-name", "git-config/global-user-email"],
                    state="amend-staged",
                    story=(
                        "The staged follow-up work is fine, but this machine's author identity was "
                        "never set properly before the last commit went in. Record the correct "
                        "identity shown below, then fold the staged work into the commit so it "
                        "carries the right attribution."
                    ),
                    details=[
                        {"label": "Author name", "value": "Learner E"},
                        {"label": "Author email", "value": "learner-e@example.test"},
                    ],
                    evaluation={
                        "staging_empty": True,
                        "working_tree_clean": True,
                        "rules": [
                            {
                                "type": "operation_metadata_equals",
                                "key": "last_config_key",
                                "value": "user.email",
                            },
                            {"type": "branch_tip_replaces_commit", "branch": "main", "old": "c1"},
                        ],
                    },
                    checks=[
                        {
                            "label": "Both halves of the identity are recorded before the rewrite.",
                            "requirement": {
                                "rules": [
                                    {
                                        "type": "operation_metadata_equals",
                                        "key": "last_config_key",
                                        "value": "user.email",
                                    }
                                ]
                            },
                        },
                        {
                            "label": "The staged work is folded into the existing commit.",
                            "requirement": {
                                "staging_empty": True,
                                "rules": [
                                    {"type": "branch_tip_replaces_commit", "branch": "main", "old": "c1"}
                                ],
                            },
                        },
                    ],
                ),
                _wave(
                    "ch2-adv-amend-then-verify",
                    "git-commit/no-edit",
                    "Amend, then audit the rewrite",
                    ["git add README.md", "git commit --amend --no-edit", "git show", "git log -p"],
                    required=["git add", "git commit --amend --no-edit", "git show", "git log -p"],
                    forms=["git-add/file", "git-show/head", "git-log/patch"],
                    state="amend-dirty",
                    story=(
                        "One forgotten README.md edit belongs in the latest local commit. Fold it "
                        "in without touching the message, then audit the result two ways: open the "
                        "rewritten snapshot, and walk the history with full patch text."
                    ),
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["README.md"],
                            "message_contains": ["Update app shell"],
                        },
                        "staging_empty": True,
                        "working_tree_clean": True,
                        "rules": [{"type": "branch_tip_replaces_commit", "branch": "main", "old": "c1"}],
                    },
                    checks=[
                        {
                            "label": "The forgotten edit is folded into the existing commit.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["README.md"],
                                    "message_contains": ["Update app shell"],
                                },
                                "rules": [
                                    {"type": "branch_tip_replaces_commit", "branch": "main", "old": "c1"}
                                ],
                            },
                        },
                        {
                            "label": "The rewrite was audited with a snapshot read and a patch walk.",
                            "requirement": {"required_commands": ["git show", "git log -p"]},
                        },
                    ],
                ),
            ],
        },
        {
            "slug": "sealing-drills",
            "title": "Sealing Drills",
            "waves": [
                _wave(
                    "ch2-adv-full-save-drill",
                    "git-commit/all-message",
                    "Review, script-check, seal",
                    ["git diff", "git status --porcelain", "git commit -a -m 'Save the reviewed pass'"],
                    required=["git diff", "git status --porcelain", "git commit -a"],
                    forms=["git-diff/working", "git-status/porcelain"],
                    state="dirty",
                    story=(
                        "One tracked edit stands between you and a clean workspace. Read the "
                        "changed lines, confirm the state in script-stable form, then seal the "
                        "tracked work directly under the provided message."
                    ),
                    details=[{"label": "Commit message", "value": "Save the reviewed pass"}],
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["README.md"],
                            "message_contains": ["Save the reviewed pass"],
                        },
                        "staging_empty": True,
                        "working_tree_clean": True,
                        "rules": [{"type": "commit_count_equals", "count": 2}],
                    },
                    checks=[
                        {
                            "label": "The edit was reviewed and script-checked before sealing.",
                            "requirement": {"required_commands": ["git diff", "git status --porcelain"]},
                        },
                        {
                            "label": "The tracked work is sealed under the provided message.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["README.md"],
                                    "message_contains": ["Save the reviewed pass"],
                                }
                            },
                        },
                    ],
                ),
                _wave(
                    "ch2-adv-amend-message-drill",
                    "git-commit/amend",
                    "Rename the snapshot, prove it",
                    ["git commit --amend -m 'Name the feature properly'", "git show"],
                    required=["git commit --amend", "git show"],
                    forms=["git-show/head"],
                    state="amend",
                    story=(
                        "The latest local commit still wears its placeholder name. Rewrite the "
                        "message in place with the provided one, then open the rewritten snapshot "
                        "to prove the change took."
                    ),
                    details=[{"label": "New message", "value": "Name the feature properly"}],
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "message_contains": ["Name the feature properly"],
                        },
                        "rules": [{"type": "branch_tip_replaces_commit", "branch": "main", "old": "c1"}],
                    },
                    checks=[
                        {
                            "label": "The commit was replaced in place with the proper name.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "message_contains": ["Name the feature properly"],
                                },
                                "rules": [
                                    {"type": "branch_tip_replaces_commit", "branch": "main", "old": "c1"}
                                ],
                            },
                        },
                        {
                            "label": "The rewritten snapshot was opened to confirm it.",
                            "requirement": {"required_commands": ["git show"]},
                        },
                    ],
                ),
                _wave(
                    "ch2-adv-stat-audit-note",
                    "git-log/stat",
                    "Audit sizes, then seal the note",
                    [
                        "git log --stat",
                        "git log -p",
                        "git show --name-only c0",
                        "git commit -a -m 'Record audit pass'",
                    ],
                    required=["git log --stat", "git log -p", "git show --name-only", "git commit -a"],
                    forms=["git-log/patch", "git-show/name-only", "git-commit/all-message"],
                    state="dirty",
                    story=(
                        "A tracked note about this repository's history is nearly finished. Gather "
                        "the last facts three ways - change summaries, full patches, and the bare "
                        "path list of the first snapshot - then seal the note directly."
                    ),
                    details=[{"label": "Commit message", "value": "Record audit pass"}],
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["README.md"],
                            "message_contains": ["Record audit pass"],
                        },
                        "staging_empty": True,
                        "working_tree_clean": True,
                        "rules": [{"type": "commit_count_equals", "count": 2}],
                    },
                    checks=[
                        {
                            "label": "History was audited at all three levels of detail.",
                            "requirement": {
                                "required_commands": [
                                    "git log --stat",
                                    "git log -p",
                                    "git show --name-only",
                                ]
                            },
                        },
                        {
                            "label": "The audit note is sealed on main.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["README.md"],
                                    "message_contains": ["Record audit pass"],
                                }
                            },
                        },
                    ],
                ),
                _wave(
                    "ch2-adv-quick-tracked-note",
                    "git-commit/all-message",
                    "Quick save, quick look",
                    ["git commit -a -m 'Note the tweak'", "git show"],
                    required=["git commit -a", "git show"],
                    forms=["git-show/head"],
                    state="dirty",
                    story=(
                        "A one-line tracked tweak needs saving before the next meeting. Seal it "
                        "directly, then open the fresh snapshot to double-check exactly what went "
                        "in."
                    ),
                    details=[{"label": "Commit message", "value": "Note the tweak"}],
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["README.md"],
                            "message_contains": ["Note the tweak"],
                        },
                        "staging_empty": True,
                        "working_tree_clean": True,
                        "rules": [{"type": "commit_count_equals", "count": 2}],
                    },
                    checks=[
                        {
                            "label": "The tweak is sealed directly on main.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["README.md"],
                                    "message_contains": ["Note the tweak"],
                                }
                            },
                        },
                        {
                            "label": "The fresh snapshot was opened to double-check it.",
                            "requirement": {"required_commands": ["git show"]},
                        },
                    ],
                ),
                _wave(
                    "ch2-adv-rewrite-wip",
                    "git-commit/amend",
                    "Confirm scope, then rewrite",
                    ["git log -n 1", "git commit --amend -m 'Describe the auth work'"],
                    required=["git log", "git commit --amend"],
                    forms=["git-log/limit"],
                    state="amend",
                    story=(
                        "Only the newest entry of this local history is a placeholder. Confirm "
                        "that by reading exactly one history entry, then rewrite that commit in "
                        "place with the provided description."
                    ),
                    details=[{"label": "New message", "value": "Describe the auth work"}],
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "message_contains": ["Describe the auth work"],
                        },
                        "rules": [{"type": "branch_tip_replaces_commit", "branch": "main", "old": "c1"}],
                    },
                    checks=[
                        {
                            "label": "The rewrite scope was confirmed with a limited read.",
                            "requirement": {"required_commands": ["git log"]},
                        },
                        {
                            "label": "The placeholder commit now carries the real description.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "message_contains": ["Describe the auth work"],
                                }
                            },
                        },
                    ],
                ),
                _wave(
                    "ch2-adv-fold-final-edit",
                    "git-commit/no-edit",
                    "Sweep, fold, audit",
                    ["git add -u", "git commit --amend --no-edit", "git log --stat"],
                    required=["git add -u", "git commit --amend --no-edit", "git log --stat"],
                    forms=["git-add/update", "git-log/stat"],
                    state="amend-dirty",
                    story=(
                        "The final tracked touch-up belongs inside the latest local commit, and "
                        "its message is already right. Sweep the tracked edit in, fold it into the "
                        "commit, then audit the sizes to see the snapshot grow."
                    ),
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["README.md"],
                            "message_contains": ["Update app shell"],
                        },
                        "staging_empty": True,
                        "working_tree_clean": True,
                        "rules": [{"type": "branch_tip_replaces_commit", "branch": "main", "old": "c1"}],
                    },
                    checks=[
                        {
                            "label": "The touch-up is folded into the existing commit.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["README.md"],
                                    "message_contains": ["Update app shell"],
                                },
                                "rules": [
                                    {"type": "branch_tip_replaces_commit", "branch": "main", "old": "c1"}
                                ],
                            },
                        },
                        {
                            "label": "The grown snapshot was audited afterward.",
                            "requirement": {"required_commands": ["git log --stat"]},
                        },
                    ],
                ),
            ],
        },
    ]
