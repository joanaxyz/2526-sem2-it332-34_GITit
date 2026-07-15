"""Blueprint adventure levels for step-back-safely."""

from __future__ import annotations

from .helpers import _wave

ADVENTURE_LEVELS = [
        {
            "slug": "read-recovery-clues",
            "title": "Read Recovery Clues",
            "waves": [
                _wave(
                    "ch5-adv-read-reflog",
                    "git-reflog/head",
                    "Read reflog",
                    ["git reflog"],
                    state="recovery",
                    story=(
                        "main just gained a commit that turned out to be broken. Before deciding how "
                        "to undo it, read the reflog to see exactly how HEAD has moved recently."
                    ),
                    evaluation={"rules": [{"type": "commit_count_equals", "count": 3}]},
                    checks=[
                        {
                            "label": "Recent HEAD movements were inspected before any recovery move.",
                            "requirement": {"required_commands": ["git reflog"]},
                        },
                    ],
                ),
                _wave(
                    "ch5-adv-reflog-then-log",
                    "git-reflog/head",
                    "Two views of recent history",
                    ["git reflog", "git log --oneline"],
                    required=["git reflog", "git log"],
                    forms=["git-log/oneline"],
                    state="recovery",
                    story=(
                        "Before undoing anything, compare Git's two memories: the reflog's "
                        "record of every HEAD movement, and the branch's own compact history. "
                        "Read both, touch nothing."
                    ),
                    evaluation={
                        "staging_empty": True,
                        "rules": [{"type": "commit_count_equals", "count": 3}],
                    },
                    checks=[
                        {
                            "label": "Both the reflog and the branch history were read.",
                            "requirement": {"required_commands": ["git reflog", "git log"]},
                        },
                    ],
                ),
                _wave(
                    "ch5-adv-inspect-suspect",
                    "git-show/commit",
                    "Interrogate the suspect commit",
                    ["git log -n 2", "git show c2"],
                    required=["git log", "git show"],
                    forms=["git-log/limit"],
                    state="recovery",
                    story=(
                        "The bug report points at the newest work. Read just the last two "
                        "history entries to frame the timeline, then open the suspect commit "
                        "itself and read everything it changed."
                    ),
                    details=[{"label": "Commit to inspect", "value": "c2"}],
                    evaluation={
                        "staging_empty": True,
                        "rules": [{"type": "commit_count_equals", "count": 3}],
                    },
                    checks=[
                        {
                            "label": "The timeline was framed and the suspect opened directly.",
                            "requirement": {"required_commands": ["git log", "git show"]},
                        },
                    ],
                ),
                _wave(
                    "ch5-adv-patch-the-evidence",
                    "git-log/patch",
                    "Full patches, then the path list",
                    ["git log -p", "git show --name-only c2"],
                    required=["git log -p", "git show --name-only"],
                    forms=["git-show/name-only"],
                    state="recovery",
                    story=(
                        "The postmortem needs receipts: walk the whole history with its full "
                        "patch text, then pull just the list of paths the suspect commit "
                        "touched. Gather the evidence without changing a thing."
                    ),
                    details=[{"label": "Commit to inspect", "value": "c2"}],
                    evaluation={
                        "staging_empty": True,
                        "rules": [{"type": "commit_count_equals", "count": 3}],
                    },
                    checks=[
                        {
                            "label": "The patches and the suspect's path list were both read.",
                            "requirement": {"required_commands": ["git log -p", "git show --name-only"]},
                        },
                    ],
                ),
                _wave(
                    "ch5-adv-detach-the-suspect",
                    "git-switch/detach",
                    "Stand inside the suspect commit",
                    ["git switch --detach c2", "git show"],
                    required=["git switch --detach", "git show"],
                    forms=["git-show/head"],
                    state="recovery",
                    story=(
                        "Reports disagree about what the suspect commit actually contains. End "
                        "the debate: move HEAD there directly without touching any branch, and "
                        "read the snapshot from the inside."
                    ),
                    details=[{"label": "Commit to visit", "value": "c2"}],
                    evaluation={"rules": [{"type": "head_detached_at", "commit": "c2"}]},
                    checks=[
                        {
                            "label": "HEAD is detached at the suspect commit.",
                            "requirement": {"rules": [{"type": "head_detached_at", "commit": "c2"}]},
                        },
                        {
                            "label": "The snapshot was read from the inside.",
                            "requirement": {"required_commands": ["git show"]},
                        },
                    ],
                ),
            ],
        },
        {
            "slug": "move-private-history-back",
            "title": "Move Private History Back",
            "waves": [
                _wave(
                    "ch5-adv-reset-hard-to-commit",
                    "git-reset/hard",
                    "Reset hard to commit",
                    ["git reset --hard c1"],
                    state="recovery",
                    story=(
                        "The latest commit on this private branch, c2, turned out to be broken and has "
                        "never been shared. Discard it completely and return to the last known-good "
                        "commit, c1."
                    ),
                    evaluation={"working_tree_clean": True, "rules": [{"type": "branch_points_to", "branch": "main", "commit": "c1"}]},
                    checks=[
                        {
                            "label": "main points back at the known-good commit, and the tree matches it exactly.",
                            "requirement": {
                                "working_tree_clean": True,
                                "rules": [{"type": "branch_points_to", "branch": "main", "commit": "c1"}],
                            },
                        },
                    ],
                ),
                _wave(
                    "ch5-adv-reset-hard-parent",
                    "git-reset/hard-head",
                    "Reset hard parent",
                    ["git reset --hard HEAD~1"],
                    state="recovery",
                    story=(
                        "Only the single latest private commit is bad. Drop exactly one commit from "
                        "the tip using a relative reference, without naming it directly."
                    ),
                    evaluation={"working_tree_clean": True, "rules": [{"type": "branch_points_to", "branch": "main", "commit": "c1"}]},
                    checks=[
                        {
                            "label": "The branch moved back exactly one commit from its starting tip.",
                            "requirement": {
                                "working_tree_clean": True,
                                "rules": [{"type": "branch_points_to", "branch": "main", "commit": "c1"}],
                            },
                        },
                    ],
                ),
                _wave(
                    "ch5-adv-branch-before-reset",
                    "git-branch/create-at-start",
                    "Branch before reset",
                    ["git branch backup HEAD", "git reset --hard HEAD~1"],
                    required=["git branch", "git reset --hard"],
                    forms=["git-reset/hard-head"],
                    state="recovery",
                    story=(
                        "Before rewriting this private branch's history, keep a safety net. Anchor the "
                        "current tip on a backup branch first, then move main back one commit."
                    ),
                    evaluation={
                        "rules": [
                            {"type": "branch_points_to", "branch": "backup", "commit": "c2"},
                            {"type": "branch_points_to", "branch": "main", "commit": "c1"},
                        ]
                    },
                    checks=[
                        {
                            "label": "The old tip is preserved on a backup branch before rewriting.",
                            "requirement": {
                                "rules": [{"type": "branch_points_to", "branch": "backup", "commit": "c2"}]
                            },
                        },
                        {
                            "label": "main itself moved back one commit.",
                            "requirement": {
                                "rules": [{"type": "branch_points_to", "branch": "main", "commit": "c1"}]
                            },
                        },
                    ],
                ),
                _wave(
                    "ch5-adv-reset-after-inspect",
                    "git-reset/hard",
                    "Confirm the target, then step back",
                    ["git show c2", "git reset --hard c1"],
                    required=["git show", "git reset --hard"],
                    forms=["git-show/commit"],
                    state="recovery",
                    story=(
                        "One last check before rewriting private history: open the commit you "
                        "are about to discard and confirm nothing in it is worth saving. Then "
                        "move the branch back to the known-good commit."
                    ),
                    details=[{"label": "Known-good commit", "value": "c1"}],
                    evaluation={
                        "working_tree_clean": True,
                        "rules": [{"type": "branch_points_to", "branch": "main", "commit": "c1"}],
                    },
                    checks=[
                        {
                            "label": "The doomed commit was inspected before the rewrite.",
                            "requirement": {"required_commands": ["git show"]},
                        },
                        {
                            "label": "The branch stepped back to the known-good commit.",
                            "requirement": {
                                "working_tree_clean": True,
                                "rules": [{"type": "branch_points_to", "branch": "main", "commit": "c1"}],
                            },
                        },
                    ],
                ),
                _wave(
                    "ch5-adv-detach-preview-reset",
                    "git-switch/detach",
                    "Preview the past, then adopt it",
                    ["git switch --detach c1", "git switch main", "git reset --hard HEAD~1"],
                    required=["git switch --detach", "git switch", "git reset --hard HEAD~1"],
                    forms=["git-switch/existing", "git-reset/hard-head"],
                    state="recovery",
                    story=(
                        "Would rolling back actually fix things? Find out safely: visit the "
                        "older commit detached and look around, return to the branch, and only "
                        "then drop the broken tip for real."
                    ),
                    evaluation={
                        "head_branch": "main",
                        "working_tree_clean": True,
                        "rules": [{"type": "branch_points_to", "branch": "main", "commit": "c1"}],
                    },
                    checks=[
                        {
                            "label": "The rollback target was previewed detached first.",
                            "requirement": {"required_commands": ["git switch --detach"]},
                        },
                        {
                            "label": "The branch then stepped back one commit for real.",
                            "requirement": {
                                "rules": [{"type": "branch_points_to", "branch": "main", "commit": "c1"}]
                            },
                        },
                    ],
                ),
                _wave(
                    "ch5-adv-backup-then-clean-reset",
                    "git-branch/create",
                    "Safety net, then the rewrite",
                    ["git branch safety-net", "git reset --hard c1"],
                    required=["git branch", "git reset --hard"],
                    forms=["git-reset/hard"],
                    state="recovery",
                    story=(
                        "Rewriting history without a safety net is how work gets lost. Leave a "
                        "plain pointer on the current tip first, then move the branch back to "
                        "the known-good commit knowing nothing is truly gone."
                    ),
                    details=[
                        {"label": "Safety branch", "value": "safety-net"},
                        {"label": "Known-good commit", "value": "c1"},
                    ],
                    evaluation={
                        "working_tree_clean": True,
                        "rules": [
                            {"type": "branch_points_to", "branch": "safety-net", "commit": "c2"},
                            {"type": "branch_points_to", "branch": "main", "commit": "c1"},
                        ],
                    },
                    checks=[
                        {
                            "label": "The old tip survives on the safety-net pointer.",
                            "requirement": {
                                "rules": [{"type": "branch_points_to", "branch": "safety-net", "commit": "c2"}]
                            },
                        },
                        {
                            "label": "The branch itself stepped back to the known-good commit.",
                            "requirement": {
                                "rules": [{"type": "branch_points_to", "branch": "main", "commit": "c1"}]
                            },
                        },
                    ],
                ),
                _wave(
                    "ch5-adv-amend-vs-reset",
                    "git-commit/amend",
                    "The smallest undo that works",
                    ["git log -n 1", "git commit --amend -m 'Correct the release note'"],
                    required=["git log", "git commit --amend"],
                    forms=["git-log/limit"],
                    state="amend",
                    story=(
                        "Not every mistake needs history surgery. The only problem here is the "
                        "newest commit's sloppy message - confirm that with a single history "
                        "entry, then fix it in place with the smallest undo available."
                    ),
                    details=[{"label": "New message", "value": "Correct the release note"}],
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "message_contains": ["Correct the release note"],
                        },
                        "rules": [{"type": "branch_tip_replaces_commit", "branch": "main", "old": "c1"}],
                    },
                    checks=[
                        {
                            "label": "The scope was confirmed as a single sloppy entry.",
                            "requirement": {"required_commands": ["git log"]},
                        },
                        {
                            "label": "The commit was corrected in place, with no reset needed.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "message_contains": ["Correct the release note"],
                                }
                            },
                        },
                    ],
                ),
                _wave(
                    "ch5-adv-fold-fix-not-reset",
                    "git-commit/no-edit",
                    "Fold the fix, keep the history",
                    ["git status -s", "git add README.md", "git commit --amend --no-edit"],
                    required=["git status -s", "git add", "git commit --amend --no-edit"],
                    forms=["git-status/short", "git-add/file"],
                    state="amend-dirty",
                    story=(
                        "The \"mistake\" is just one edit that missed the last local commit. "
                        "Glance at the state, sweep the edit in, and fold it into the existing "
                        "commit - no resets, no lost history, message untouched."
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
                            "label": "The missing edit was folded into the existing commit.",
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
                    ],
                ),
            ],
        },
        {
            "slug": "private-history-drills",
            "title": "Private History Drills",
            "waves": [
                _wave(
                    "ch5-adv-reset-drill-named",
                    "git-reset/hard",
                    "Read, then step back by name",
                    ["git log --oneline", "git reset --hard c1"],
                    required=["git log", "git reset --hard"],
                    forms=["git-log/oneline"],
                    state="recovery",
                    story=(
                        "Routine private cleanup: read the compact history to pick the "
                        "known-good commit by name, then move the branch back to it exactly."
                    ),
                    details=[{"label": "Known-good commit", "value": "c1"}],
                    evaluation={
                        "working_tree_clean": True,
                        "rules": [{"type": "branch_points_to", "branch": "main", "commit": "c1"}],
                    },
                    checks=[
                        {
                            "label": "The target was picked from the compact history.",
                            "requirement": {"required_commands": ["git log"]},
                        },
                        {
                            "label": "The branch stepped back to the named commit.",
                            "requirement": {
                                "rules": [{"type": "branch_points_to", "branch": "main", "commit": "c1"}]
                            },
                        },
                    ],
                ),
                _wave(
                    "ch5-adv-reset-drill-relative",
                    "git-reset/hard-head",
                    "Check, then step back one",
                    ["git status", "git reset --hard HEAD~1"],
                    required=["git status", "git reset --hard HEAD~1"],
                    forms=["git-status/plain"],
                    state="recovery",
                    story=(
                        "One bad private commit sits on the tip and the workspace should be "
                        "clean. Confirm there is nothing unsaved to protect, then drop exactly "
                        "one commit using the relative spelling."
                    ),
                    evaluation={
                        "working_tree_clean": True,
                        "rules": [{"type": "branch_points_to", "branch": "main", "commit": "c1"}],
                    },
                    checks=[
                        {
                            "label": "The workspace was checked before the rewrite.",
                            "requirement": {"required_commands": ["git status"]},
                        },
                        {
                            "label": "The branch moved back exactly one commit.",
                            "requirement": {
                                "rules": [{"type": "branch_points_to", "branch": "main", "commit": "c1"}]
                            },
                        },
                    ],
                ),
                _wave(
                    "ch5-adv-reset-reflog-drill",
                    "git-reset/hard-head",
                    "Record the before, then step back",
                    ["git reflog", "git reset --hard HEAD~1"],
                    required=["git reflog", "git reset --hard HEAD~1"],
                    forms=["git-reflog/head"],
                    state="recovery",
                    story=(
                        "Discipline drill: before any hard step back, read the reflog so you "
                        "know the entry that will bring you home if this turns out wrong. Then "
                        "drop the broken tip."
                    ),
                    evaluation={
                        "working_tree_clean": True,
                        "rules": [{"type": "branch_points_to", "branch": "main", "commit": "c1"}],
                    },
                    checks=[
                        {
                            "label": "The reflog was read before the rewrite.",
                            "requirement": {"required_commands": ["git reflog"]},
                        },
                        {
                            "label": "The broken tip is dropped; the branch sits one back.",
                            "requirement": {
                                "rules": [{"type": "branch_points_to", "branch": "main", "commit": "c1"}]
                            },
                        },
                    ],
                ),
                _wave(
                    "ch5-adv-remove-then-reset",
                    "git-rm/tracked-file",
                    "A removal, regretted entirely",
                    ["git rm old.txt", "git commit -m 'Retire junk note'", "git reset --hard HEAD~1"],
                    required=["git rm", "git commit", "git reset --hard HEAD~1"],
                    forms=["git-commit/message", "git-reset/hard-head"],
                    state="tracked-junk",
                    story=(
                        "You remove the old note, commit it - and the teammate who wrote it "
                        "asks for it back thirty seconds later. Practice the full private undo: "
                        "the removal commit, then the step back that resurrects the file."
                    ),
                    details=[{"label": "Commit message", "value": "Retire junk note"}],
                    evaluation={
                        "rules": [{"type": "branch_points_to", "branch": "main", "commit": "c0"}],
                    },
                    checks=[
                        {
                            "label": "The removal was committed, then undone with a step back.",
                            "requirement": {
                                "required_commands": ["git rm", "git commit", "git reset --hard HEAD~1"]
                            },
                        },
                    ],
                ),
                _wave(
                    "ch5-adv-alias-undo",
                    "git-config/alias",
                    "A shortcut for stepping back",
                    ["git config --global alias.undo reset", "git config --list"],
                    required=["git config --global alias.undo", "git config --list"],
                    forms=["git-config/list"],
                    state="recovery",
                    story=(
                        "Recovery work keeps reaching for the same command. Record a global "
                        "shortcut named undo for the branch-moving command, then list the "
                        "settings to confirm it stuck."
                    ),
                    details=[
                        {"label": "Alias name", "value": "undo"},
                        {"label": "Expands to", "value": "reset"},
                    ],
                    evaluation={
                        "rules": [
                            {
                                "type": "operation_metadata_equals",
                                "key": "last_config_key",
                                "value": "alias.undo",
                            }
                        ]
                    },
                    checks=[
                        {
                            "label": "The undo shortcut is recorded and confirmed.",
                            "requirement": {
                                "rules": [
                                    {
                                        "type": "operation_metadata_equals",
                                        "key": "last_config_key",
                                        "value": "alias.undo",
                                    }
                                ],
                                "required_commands": ["git config --list"],
                            },
                        },
                    ],
                ),
            ],
        },
    ]
