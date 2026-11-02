"""Blueprint adventure levels for reverse-and-recover."""

from __future__ import annotations

from .helpers import _wave

ADVENTURE_LEVELS = [
        {
            "slug": "undo-shared-work-safely",
            "title": "Undo Shared Work Safely",
            "waves": [
                _wave(
                    "ch5-adv-revert-one-commit",
                    "git-revert/one-commit",
                    "Revert one commit",
                    ["git revert c2"],
                    state="recovery",
                    story=(
                        "c2 already shipped to everyone else on main - rewriting history now would "
                        "break their clones. Undo its effect with a brand-new commit instead, keeping "
                        "the mistake visible in history."
                    ),
                    evaluation={
                        "rules": [
                            {"type": "new_revert_commit_exists"},
                            {"type": "revert_preserves_history", "commit": "c2", "branch": "main"},
                        ]
                    },
                    checks=[
                        {
                            "label": "A new revert commit undoes the change, and the original mistake stays in history.",
                            "requirement": {
                                "rules": [
                                    {"type": "new_revert_commit_exists"},
                                    {"type": "revert_preserves_history", "commit": "c2", "branch": "main"},
                                ]
                            },
                        },
                    ],
                ),
                _wave(
                    "ch5-adv-revert-no-edit",
                    "git-revert/no-edit",
                    "Revert no edit",
                    ["git revert --no-edit c2"],
                    state="recovery",
                    story=(
                        "The same public mistake needs undoing, quickly this time - the automatic "
                        "revert message is good enough. Undo c2 without stopping to edit the message."
                    ),
                    evaluation={
                        "rules": [
                            {"type": "new_revert_commit_exists"},
                            {"type": "revert_preserves_history", "commit": "c2", "branch": "main"},
                            {"type": "operation_metadata_equals", "key": "last_revert_no_edit", "value": True},
                        ]
                    },
                    checks=[
                        {
                            "label": "The revert used the generated message directly, with no edit step.",
                            "requirement": {
                                "rules": [
                                    {
                                        "type": "operation_metadata_equals",
                                        "key": "last_revert_no_edit",
                                        "value": True,
                                    }
                                ]
                            },
                        },
                        {
                            "label": "The original mistake still remains visible in history.",
                            "requirement": {
                                "rules": [
                                    {"type": "new_revert_commit_exists"},
                                    {"type": "revert_preserves_history", "commit": "c2", "branch": "main"},
                                ]
                            },
                        },
                    ],
                ),
                _wave(
                    "ch5-adv-revert-then-fix",
                    "git-revert/one-commit",
                    "Revert then fix",
                    ["git revert c2", "git add README.md", "git commit -m 'Add safer replacement'"],
                    required=["git revert", "git commit"],
                    forms=["git-add/file", "git-commit/message"],
                    state="recovery-dirty",
                    story=(
                        "The bad public commit needs undoing, and a safer replacement is already drafted "
                        "and waiting. Back out the mistake first, then commit the safer version as a "
                        "second, separate commit."
                    ),
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["README.md"],
                            "message_contains": ["Add safer replacement"],
                        },
                        "staging_empty": True,
                        "working_tree_clean": True,
                        "rules": [{"type": "revert_preserves_history", "commit": "c2", "branch": "main"}],
                    },
                    checks=[
                        {
                            "label": "The bad commit was reverted before anything else happened.",
                            "requirement": {
                                "rules": [
                                    {"type": "new_revert_commit_exists"},
                                    {"type": "revert_preserves_history", "commit": "c2", "branch": "main"},
                                ]
                            },
                        },
                        {
                            "label": "The safer replacement landed as its own commit on main.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["README.md"],
                                    "message_contains": ["Add safer replacement"],
                                }
                            },
                        },
                    ],
                ),
                _wave(
                    "ch5-adv-revert-quick-drill",
                    "git-revert/no-edit",
                    "Fast reversal, quick read",
                    ["git revert --no-edit c2", "git log --oneline"],
                    required=["git revert --no-edit", "git log"],
                    forms=["git-log/oneline"],
                    state="recovery",
                    story=(
                        "The shared mistake is burning users right now; the generated message "
                        "is fine. Reverse it without stopping to edit, then read the compact "
                        "history to confirm the reversal sits on top."
                    ),
                    evaluation={
                        "rules": [
                            {"type": "new_revert_commit_exists"},
                            {"type": "revert_preserves_history", "commit": "c2", "branch": "main"},
                        ]
                    },
                    checks=[
                        {
                            "label": "The mistake was reversed with the generated message.",
                            "requirement": {
                                "rules": [
                                    {"type": "new_revert_commit_exists"},
                                    {"type": "revert_preserves_history", "commit": "c2", "branch": "main"},
                                ]
                            },
                        },
                        {
                            "label": "The reversal was confirmed at the top of history.",
                            "requirement": {"required_commands": ["git log"]},
                        },
                    ],
                ),
                _wave(
                    "ch5-adv-revert-verify",
                    "git-revert/no-edit",
                    "Reverse, then open the result",
                    ["git revert --no-edit c2", "git show"],
                    required=["git revert --no-edit", "git show"],
                    forms=["git-show/head"],
                    state="recovery",
                    story=(
                        "Reverse the shared mistake without editing the message, then open the "
                        "brand-new reversal commit itself and read exactly what it changed - "
                        "trust is good, reading is better."
                    ),
                    evaluation={
                        "rules": [
                            {"type": "new_revert_commit_exists"},
                            {"type": "revert_preserves_history", "commit": "c2", "branch": "main"},
                        ]
                    },
                    checks=[
                        {
                            "label": "The mistake was reversed cleanly.",
                            "requirement": {"rules": [{"type": "new_revert_commit_exists"}]},
                        },
                        {
                            "label": "The reversal commit was opened and read.",
                            "requirement": {"required_commands": ["git show"]},
                        },
                    ],
                ),
                _wave(
                    "ch5-adv-revert-stat",
                    "git-revert/no-edit",
                    "Reverse, then size the damage",
                    ["git revert --no-edit c2", "git log --stat"],
                    required=["git revert --no-edit", "git log --stat"],
                    forms=["git-log/stat"],
                    state="recovery",
                    story=(
                        "After reversing the shared mistake, the incident report needs one more "
                        "fact: how big the mistake and its reversal actually were. Read the "
                        "history with change summaries to size both."
                    ),
                    evaluation={
                        "rules": [
                            {"type": "new_revert_commit_exists"},
                            {"type": "revert_preserves_history", "commit": "c2", "branch": "main"},
                        ]
                    },
                    checks=[
                        {
                            "label": "The mistake was reversed cleanly.",
                            "requirement": {"rules": [{"type": "new_revert_commit_exists"}]},
                        },
                        {
                            "label": "The sizes were read for the incident report.",
                            "requirement": {"required_commands": ["git log --stat"]},
                        },
                    ],
                ),
                _wave(
                    "ch5-adv-graph-then-revert",
                    "git-revert/one-commit",
                    "Map the shared line, then reverse",
                    ["git log --oneline --graph --all", "git revert c2"],
                    required=["git log", "git revert"],
                    forms=["git-log/graph-all"],
                    state="recovery",
                    story=(
                        "Draw the graph first and let it make the argument: this line is "
                        "shared, so its history must not be rewritten. Then reverse the bad "
                        "commit the safe way."
                    ),
                    evaluation={
                        "rules": [
                            {"type": "new_revert_commit_exists"},
                            {"type": "revert_preserves_history", "commit": "c2", "branch": "main"},
                        ]
                    },
                    checks=[
                        {
                            "label": "The shared shape was mapped before deciding.",
                            "requirement": {"required_commands": ["git log"]},
                        },
                        {
                            "label": "The mistake was reversed, not rewritten away.",
                            "requirement": {
                                "rules": [
                                    {"type": "new_revert_commit_exists"},
                                    {"type": "revert_preserves_history", "commit": "c2", "branch": "main"},
                                ]
                            },
                        },
                    ],
                ),
            ],
        },
        {
            "slug": "recover-after-a-mistake",
            "title": "Recover After a Mistake",
            "waves": [
                _wave(
                    "ch5-adv-recover-lost-tip",
                    "git-reflog/head",
                    "Recover lost tip",
                    ["git reflog", "git branch recovered c2", "git switch recovered"],
                    required=["git reflog", "git branch", "git switch"],
                    forms=["git-branch/create-at-start", "git-switch/existing"],
                    state="reflog-lost",
                    story=(
                        "An accidental reset moved main back to c1, leaving a genuinely useful commit, "
                        "c2, unreachable by name. Find it in the reflog, anchor it on a new recovered "
                        "branch, and switch onto it."
                    ),
                    evaluation={
                        "head_branch": "recovered",
                        "rules": [
                            {"type": "branch_points_to", "branch": "recovered", "commit": "c2"},
                            {"type": "branch_points_to", "branch": "main", "commit": "c1"},
                        ],
                    },
                    checks=[
                        {
                            "label": "The lost commit was found in the reflog before anything else.",
                            "requirement": {"required_commands": ["git reflog"]},
                        },
                        {
                            "label": "The lost commit now has a real, reachable name: recovered.",
                            "requirement": {
                                "head_branch": "recovered",
                                "rules": [{"type": "branch_points_to", "branch": "recovered", "commit": "c2"}],
                            },
                        },
                    ],
                ),
                _wave(
                    "ch5-adv-restore-main-from-reflog",
                    "git-reflog/head",
                    "Restore main from reflog",
                    ["git reflog", "git reset --hard HEAD@{0}"],
                    required=["git reflog", "git reset --hard"],
                    forms=["git-reset/hard"],
                    state="reflog-lost",
                    story=(
                        "main was reset back to c1 by mistake, and the desired tip only still exists in "
                        "the reflog now. Find that entry, then move main straight back to it."
                    ),
                    evaluation={"rules": [{"type": "branch_points_to", "branch": "main", "commit": "c2"}]},
                    checks=[
                        {
                            "label": "The desired previous tip was located in the reflog.",
                            "requirement": {"required_commands": ["git reflog"]},
                        },
                        {
                            "label": "main is restored to exactly that previous tip.",
                            "requirement": {
                                "rules": [{"type": "branch_points_to", "branch": "main", "commit": "c2"}]
                            },
                        },
                    ],
                ),
                _wave(
                    "ch5-adv-choose-reset-or-revert",
                    "git-log/graph-all",
                    "Choose reset or revert",
                    ["git log --oneline --graph --all", "git show c2", "git revert c2"],
                    required=["git log", "git show", "git revert"],
                    forms=["git-show/commit", "git-revert/one-commit"],
                    state="recovery",
                    story=(
                        "c2 is already on main, which is shared with the team - it is not a private "
                        "branch you can safely rewrite. Confirm that with the history and the commit "
                        "itself, then apply the undo strategy that fits shared history: revert, not "
                        "reset."
                    ),
                    evaluation={
                        "rules": [
                            {"type": "new_revert_commit_exists"},
                            {"type": "revert_preserves_history", "commit": "c2", "branch": "main"},
                        ]
                    },
                    checks=[
                        {
                            "label": "The history and the commit itself were checked before choosing an undo strategy.",
                            "requirement": {"required_commands": ["git log", "git show"]},
                        },
                        {
                            "label": "Because the mistake is shared, it was undone with a revert, not a history rewrite.",
                            "requirement": {
                                "rules": [
                                    {"type": "new_revert_commit_exists"},
                                    {"type": "revert_preserves_history", "commit": "c2", "branch": "main"},
                                ]
                            },
                        },
                    ],
                ),
                _wave(
                    "ch5-adv-reflog-audit-note",
                    "git-reflog/head",
                    "What the log forgot",
                    ["git reflog", "git log --oneline"],
                    required=["git reflog", "git log"],
                    forms=["git-log/oneline"],
                    state="reflog-lost",
                    story=(
                        "After the accidental step back, the branch history looks innocently "
                        "short - but the reflog remembers what the log no longer shows. Read "
                        "both and note the difference before planning the rescue."
                    ),
                    evaluation={
                        "staging_empty": True,
                        "rules": [{"type": "commit_count_equals", "count": 3}],
                    },
                    checks=[
                        {
                            "label": "Both memories were read and compared.",
                            "requirement": {"required_commands": ["git reflog", "git log"]},
                        },
                    ],
                ),
                _wave(
                    "ch5-adv-restore-and-mark",
                    "git-reset/hard",
                    "Restore the tip, mark it safe",
                    ["git reflog", "git reset --hard HEAD@{0}", "git branch confirmed"],
                    required=["git reflog", "git reset --hard", "git branch"],
                    forms=["git-reflog/head", "git-branch/create"],
                    state="reflog-lost",
                    story=(
                        "The reflog still remembers the tip that the accidental step back "
                        "abandoned. Find the entry, move the branch straight back onto it, and "
                        "leave a confirmed pointer there so this never has to be rescued twice."
                    ),
                    details=[{"label": "Marker branch", "value": "confirmed"}],
                    evaluation={
                        "rules": [
                            {"type": "branch_points_to", "branch": "main", "commit": "c2"},
                            {"type": "branch_points_to", "branch": "confirmed", "commit": "c2"},
                        ]
                    },
                    checks=[
                        {
                            "label": "The lost tip was found and the branch restored to it.",
                            "requirement": {
                                "rules": [{"type": "branch_points_to", "branch": "main", "commit": "c2"}]
                            },
                        },
                        {
                            "label": "A confirmed pointer marks the restored tip.",
                            "requirement": {
                                "rules": [{"type": "branch_points_to", "branch": "confirmed", "commit": "c2"}]
                            },
                        },
                    ],
                ),
                _wave(
                    "ch5-adv-revert-no-edit-final",
                    "git-revert/no-edit",
                    "Reverse, then read the room",
                    ["git revert --no-edit c2", "git status"],
                    required=["git revert --no-edit", "git status"],
                    forms=["git-status/plain"],
                    state="recovery",
                    story=(
                        "Reverse the shared mistake with the generated message, then read the "
                        "workspace state to confirm the reversal left everything clean and "
                        "settled behind it."
                    ),
                    evaluation={
                        "working_tree_clean": True,
                        "staging_empty": True,
                        "rules": [
                            {"type": "new_revert_commit_exists"},
                            {"type": "revert_preserves_history", "commit": "c2", "branch": "main"},
                        ],
                    },
                    checks=[
                        {
                            "label": "The mistake was reversed with the generated message.",
                            "requirement": {"rules": [{"type": "new_revert_commit_exists"}]},
                        },
                        {
                            "label": "The workspace reads clean after the reversal.",
                            "requirement": {"required_commands": ["git status"]},
                        },
                    ],
                ),
                _wave(
                    "ch5-adv-quick-reverts",
                    "git-revert/no-edit",
                    "Reflog first, reverse fast",
                    ["git reflog", "git revert --no-edit c2"],
                    required=["git reflog", "git revert --no-edit"],
                    forms=["git-reflog/head"],
                    state="recovery",
                    story=(
                        "Incident habit: before any undo, capture what the reflog shows so the "
                        "report has a before-picture. Then reverse the shared mistake without "
                        "stopping to edit the message."
                    ),
                    evaluation={
                        "rules": [
                            {"type": "new_revert_commit_exists"},
                            {"type": "revert_preserves_history", "commit": "c2", "branch": "main"},
                        ]
                    },
                    checks=[
                        {
                            "label": "The before-picture was captured from the reflog.",
                            "requirement": {"required_commands": ["git reflog"]},
                        },
                        {
                            "label": "The mistake was reversed the safe way.",
                            "requirement": {"rules": [{"type": "new_revert_commit_exists"}]},
                        },
                    ],
                ),
                _wave(
                    "ch5-adv-isolate-fix-line",
                    "git-switch/create",
                    "Reverse on a dedicated line",
                    ["git switch -c fix/rollback", "git revert c2"],
                    required=["git switch -c", "git revert"],
                    forms=["git-revert/one-commit"],
                    state="recovery",
                    story=(
                        "Policy on this team: even reversals go through review. Create a "
                        "dedicated rollback line, then reverse the bad commit there so the "
                        "reversal itself can be reviewed before it reaches main."
                    ),
                    details=[{"label": "Rollback branch", "value": "fix/rollback"}],
                    evaluation={
                        "head_branch": "fix/rollback",
                        "rules": [
                            {"type": "new_revert_commit_exists"},
                            {"type": "revert_preserves_history", "commit": "c2", "branch": "fix/rollback"},
                        ],
                    },
                    checks=[
                        {
                            "label": "The rollback got its own dedicated line.",
                            "requirement": {"head_branch": "fix/rollback"},
                        },
                        {
                            "label": "The reversal commit sits on that line for review.",
                            "requirement": {"rules": [{"type": "new_revert_commit_exists"}]},
                        },
                    ],
                ),
                _wave(
                    "ch5-adv-revert-map-final",
                    "git-revert/one-commit",
                    "Reverse, then map the record",
                    ["git revert c2", "git log --oneline --graph --all"],
                    required=["git revert", "git log"],
                    forms=["git-log/graph-all"],
                    state="recovery",
                    story=(
                        "Finish the recovery chapter the honest way: reverse the shared "
                        "mistake, then draw the graph and see both the mistake and its "
                        "correction standing in the permanent record."
                    ),
                    evaluation={
                        "rules": [
                            {"type": "new_revert_commit_exists"},
                            {"type": "revert_preserves_history", "commit": "c2", "branch": "main"},
                        ]
                    },
                    checks=[
                        {
                            "label": "The mistake was reversed with history preserved.",
                            "requirement": {
                                "rules": [
                                    {"type": "new_revert_commit_exists"},
                                    {"type": "revert_preserves_history", "commit": "c2", "branch": "main"},
                                ]
                            },
                        },
                        {
                            "label": "The full record was mapped afterward.",
                            "requirement": {"required_commands": ["git log"]},
                        },
                    ],
                ),
            ],
        },
    ]
