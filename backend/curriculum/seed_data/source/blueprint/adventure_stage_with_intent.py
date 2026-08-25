"""Blueprint adventure levels for stage-with-intent."""

from __future__ import annotations

from .helpers import _wave

ADVENTURE_LEVELS = [
        {
            "slug": "see-what-changed",
            "title": "See What Changed",
            "waves": [
                _wave(
                    "ch2-adv-name-only-intro",
                    "git-diff/name-only",
                    "List changed paths only",
                    ["git diff --name-only"],
                    state="mixed",
                    story=(
                        "A quick triage question: which files actually changed here? Skip the patch "
                        "text entirely and read just the list of changed paths, leaving the "
                        "workspace untouched."
                    ),
                    evaluation={
                        "working_tree_dirty": True,
                        "staging_empty": True,
                        "rules": [{"type": "commit_count_equals", "count": 1}],
                    },
                    checks=[
                        {
                            "label": "Only the changed paths were listed, without patch text.",
                            "requirement": {"required_commands": ["git diff --name-only"]},
                        },
                    ],
                ),
                _wave(
                    "ch2-adv-review-both-sides",
                    "git-diff/working",
                    "Review both sides of the index",
                    ["git diff", "git add README.md", "git diff --staged"],
                    required=["git diff", "git add", "git diff --staged"],
                    forms=["git-add/file", "git-diff/staged"],
                    state="dirty",
                    story=(
                        "One README.md edit is heading for the next snapshot, and you want eyes on "
                        "it at every step. Read it while it is unstaged, move it across the index "
                        "boundary, then read it again as the exact content that would be committed."
                    ),
                    evaluation={
                        "staging_not_empty": True,
                        "working_tree_clean": True,
                        "rules": [
                            {"type": "staging_contains", "path": "README.md"},
                            {"type": "commit_count_equals", "count": 1},
                        ],
                    },
                    checks=[
                        {
                            "label": "The edit was reviewed on both sides of the index.",
                            "requirement": {"required_commands": ["git diff", "git diff --staged"]},
                        },
                        {
                            "label": "The reviewed edit now waits in the staging area.",
                            "requirement": {
                                "rules": [{"type": "staging_contains", "path": "README.md"}]
                            },
                        },
                    ],
                ),
                _wave(
                    "ch2-adv-paths-then-details",
                    "git-diff/name-only",
                    "Triage from paths to patches",
                    ["git status -s", "git diff --name-only", "git diff"],
                    required=["git status -s", "git diff --name-only", "git diff"],
                    forms=["git-status/short", "git-diff/working"],
                    state="mixed",
                    story=(
                        "Triage this workspace in three passes of increasing detail: a compact "
                        "glance at everything, the bare list of changed paths, and finally the full "
                        "changed lines. Touch nothing while you read."
                    ),
                    evaluation={
                        "working_tree_dirty": True,
                        "staging_empty": True,
                        "rules": [
                            {"type": "commit_count_equals", "count": 1},
                            {
                                "type": "required_command_sequence",
                                "commands": [
                                    "git status -s",
                                    "git diff --name-only",
                                    "git diff",
                                ],
                            },
                        ],
                    },
                    checks=[
                        {
                            "label": "The workspace was read at all three levels of detail.",
                            "requirement": {
                                "required_commands": [
                                    "git status -s",
                                    "git diff --name-only",
                                    "git diff",
                                ],
                                "rules": [
                                    {
                                        "type": "required_command_sequence",
                                        "commands": [
                                            "git status -s",
                                            "git diff --name-only",
                                            "git diff",
                                        ],
                                    }
                                ],
                            },
                        },
                    ],
                ),
            ],
        },
        {
            "slug": "choose-what-enters-the-snapshot",
            "title": "Choose What Enters the Snapshot",
            "waves": [
                _wave(
                    "ch2-adv-stage-all-changes",
                    "git-add/all",
                    "Stage all changes",
                    ["git add -A"],
                    state="mixed",
                    story=(
                        "The working tree has a modified README.md and a brand-new scratch.txt sitting "
                        "side by side. Stage every kind of change at once - modified and untracked - in "
                        "a single move."
                    ),
                    evaluation={
                        "working_tree_clean": True,
                        "rules": [
                            {"type": "staging_contains", "path": "README.md"},
                            {"type": "staging_contains", "path": "scratch.txt"},
                        ],
                    },
                    checks=[
                        {
                            "label": "Every changed and new file is staged for the next snapshot.",
                            "requirement": {
                                "working_tree_clean": True,
                                "rules": [
                                    {"type": "staging_contains", "path": "README.md"},
                                    {"type": "staging_contains", "path": "scratch.txt"},
                                ],
                            },
                        },
                    ],
                ),
                _wave(
                    "ch2-adv-stage-tracked-only",
                    "git-add/update",
                    "Stage tracked only",
                    ["git add -u"],
                    state="mixed",
                    story=(
                        "The same modified README.md and new scratch.txt are both sitting in the "
                        "working tree. This time, stage only the tracked edit and leave the brand-new "
                        "file untouched and untracked."
                    ),
                    evaluation={
                        "rules": [
                            {"type": "staging_contains", "path": "README.md"},
                            {"type": "working_tree_contains", "path": "scratch.txt"},
                            {"type": "staging_excludes", "path": "scratch.txt"},
                        ]
                    },
                    checks=[
                        {
                            "label": "The tracked README edit is staged, and the new file stays untracked.",
                            "requirement": {
                                "rules": [
                                    {"type": "staging_contains", "path": "README.md"},
                                    {"type": "working_tree_contains", "path": "scratch.txt"},
                                    {"type": "staging_excludes", "path": "scratch.txt"},
                                ]
                            },
                        },
                    ],
                ),
                _wave(
                    "ch2-adv-stage-selected-hunks",
                    "git-add/patch",
                    "Stage selected hunks",
                    ["git add -p src/app.py"],
                    state="partial",
                    story=(
                        "src/app.py has two mixed edits in the same file: a real fix and a leftover "
                        "debug line. Stage only the fix hunk interactively and leave the debug hunk "
                        "behind in the working tree."
                    ),
                    evaluation={
                        "staging_not_empty": True,
                        "working_tree_dirty": True,
                        "rules": [
                            {"type": "staging_contains", "path": "src/app.py"},
                            {"type": "working_tree_contains", "path": "src/app.py"},
                        ],
                    },
                    checks=[
                        {
                            "label": "Only the intended hunk from src/app.py is staged; the rest stays unstaged.",
                            "requirement": {
                                "staging_not_empty": True,
                                "rules": [
                                    {"type": "staging_contains", "path": "src/app.py"},
                                    {"type": "working_tree_contains", "path": "src/app.py"},
                                ],
                            },
                        },
                    ],
                ),
                _wave(
                    "ch2-adv-changed-paths-only",
                    "git-diff/name-only",
                    "Changed paths only",
                    ["git diff --name-only", "git add README.md", "git commit -m 'Save selected path'"],
                    required=["git diff --name-only", "git commit"],
                    forms=["git-add/file", "git-commit/message"],
                    state="mixed",
                    story=(
                        "Before deciding what to stage, list only the changed paths - not the full diff "
                        "text. README.md is the one real edit; scratch.txt is a local file that should "
                        "stay out of history for now."
                    ),
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["README.md"],
                            "excludes_paths": ["scratch.txt"],
                            "message_contains": ["Save selected path"],
                        },
                        "staging_empty": True,
                    },
                    checks=[
                        {
                            "label": "The changed paths were listed before choosing what to stage.",
                            "requirement": {"required_commands": ["git diff --name-only"]},
                        },
                        {
                            "label": "Only the intended path is committed; the scratch file is left out.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["README.md"],
                                    "excludes_paths": ["scratch.txt"],
                                    "message_contains": ["Save selected path"],
                                }
                            },
                        },
                    ],
                ),
            ],
        },
        {
            "slug": "precision-staging-drills",
            "title": "Precision Staging Drills",
            "waves": [
                _wave(
                    "ch2-adv-update-then-commit",
                    "git-add/update",
                    "Sweep tracked edits into a commit",
                    ["git status --porcelain", "git add -u", "git commit -m 'Save tracked work'"],
                    required=["git status --porcelain", "git add -u", "git commit"],
                    forms=["git-status/porcelain", "git-commit/message"],
                    state="mixed",
                    story=(
                        "A script-stable reading confirms it: one tracked edit, one loose local "
                        "file. Stage only what is already tracked and commit it, so the local "
                        "scratch file never enters history."
                    ),
                    details=[{"label": "Commit message", "value": "Save tracked work"}],
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["README.md"],
                            "excludes_paths": ["scratch.txt"],
                            "message_contains": ["Save tracked work"],
                        },
                        "staging_empty": True,
                        "rules": [{"type": "commit_count_equals", "count": 2}],
                    },
                    checks=[
                        {
                            "label": "The state was confirmed in script-stable form first.",
                            "requirement": {"required_commands": ["git status --porcelain"]},
                        },
                        {
                            "label": "Only the tracked edit is committed; the scratch file stayed out.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["README.md"],
                                    "excludes_paths": ["scratch.txt"],
                                    "message_contains": ["Save tracked work"],
                                }
                            },
                        },
                    ],
                ),
                _wave(
                    "ch2-adv-all-then-verify",
                    "git-add/all",
                    "Stage everything, verify the landing",
                    [
                        "git status -s",
                        "git add -A",
                        "git commit -m 'Save everything'",
                        "git log --oneline",
                    ],
                    required=["git status -s", "git add -A", "git commit", "git log"],
                    forms=["git-status/short", "git-commit/message", "git-log/oneline"],
                    state="mixed",
                    story=(
                        "This time both pieces belong in history: the tracked edit and the new "
                        "local file. Glance at the state, stage every kind of change at once, "
                        "commit the batch, and read the history to confirm it landed."
                    ),
                    details=[{"label": "Commit message", "value": "Save everything"}],
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["README.md", "scratch.txt"],
                            "message_contains": ["Save everything"],
                        },
                        "staging_empty": True,
                        "working_tree_clean": True,
                        "rules": [{"type": "commit_count_equals", "count": 2}],
                    },
                    checks=[
                        {
                            "label": "Both the edit and the new file landed in one commit.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["README.md", "scratch.txt"],
                                    "message_contains": ["Save everything"],
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
                    "ch2-adv-patch-only-fix",
                    "git-add/patch",
                    "Ship only the fix hunk",
                    [
                        "git add -p src/app.py",
                        "git diff --staged",
                        "git commit -m 'Ship only the fix'",
                    ],
                    required=["git add -p", "git diff --staged", "git commit"],
                    forms=["git-diff/staged", "git-commit/message"],
                    state="partial",
                    story=(
                        "src/app.py mixes a real fix with a leftover debug line. Stage just the fix "
                        "hunk, read the staged content to prove the debug line is not in it, then "
                        "commit exactly that."
                    ),
                    details=[{"label": "Commit message", "value": "Ship only the fix"}],
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["src/app.py"],
                            "message_contains": ["Ship only the fix"],
                        },
                        "working_tree_dirty": True,
                        "staging_empty": True,
                        "rules": [{"type": "commit_count_equals", "count": 2}],
                    },
                    checks=[
                        {
                            "label": "The staged content was verified before committing.",
                            "requirement": {"required_commands": ["git diff --staged"]},
                        },
                        {
                            "label": "The fix is committed while the debug hunk stays unstaged.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["src/app.py"],
                                    "message_contains": ["Ship only the fix"],
                                },
                                "working_tree_dirty": True,
                            },
                        },
                    ],
                ),
                _wave(
                    "ch2-adv-tracked-updates-only",
                    "git-add/update",
                    "Stage tracked, prove the rest stayed",
                    ["git status --porcelain", "git add -u"],
                    required=["git status --porcelain", "git add -u"],
                    forms=["git-status/porcelain"],
                    state="mixed",
                    story=(
                        "A release script will handle the commit; your job is only the staging "
                        "decision. Confirm the state in script-stable form, then stage tracked "
                        "changes only, leaving the new local file exactly where it is."
                    ),
                    evaluation={
                        "rules": [
                            {"type": "staging_contains", "path": "README.md"},
                            {"type": "staging_excludes", "path": "scratch.txt"},
                            {"type": "working_tree_contains", "path": "scratch.txt"},
                        ]
                    },
                    checks=[
                        {
                            "label": "The tracked edit is staged and the new file is untouched.",
                            "requirement": {
                                "rules": [
                                    {"type": "staging_contains", "path": "README.md"},
                                    {"type": "staging_excludes", "path": "scratch.txt"},
                                ]
                            },
                        },
                    ],
                ),
                _wave(
                    "ch2-adv-batch-stage-check",
                    "git-add/all",
                    "Batch stage, script check",
                    ["git add -A", "git status --porcelain"],
                    required=["git add -A", "git status --porcelain"],
                    forms=["git-status/porcelain"],
                    state="folder",
                    story=(
                        "A folder of finished work needs to be fully staged before an automated "
                        "release check runs. Stage every visible change in one sweep, then read "
                        "the script-stable state the automation will see."
                    ),
                    evaluation={
                        "staging_not_empty": True,
                        "working_tree_clean": True,
                        "rules": [
                            {"type": "staging_contains", "path": "src/app.py"},
                            {"type": "staging_contains", "path": "docs/guide.md"},
                        ],
                    },
                    checks=[
                        {
                            "label": "Every visible change is staged for the release.",
                            "requirement": {
                                "rules": [
                                    {"type": "staging_contains", "path": "src/app.py"},
                                    {"type": "staging_contains", "path": "docs/guide.md"},
                                ]
                            },
                        },
                        {
                            "label": "The staged state was read in script-stable form.",
                            "requirement": {"required_commands": ["git status --porcelain"]},
                        },
                    ],
                ),
                _wave(
                    "ch2-adv-paths-quick-check",
                    "git-diff/name-only",
                    "Paths first, then sweep",
                    ["git diff --name-only", "git add -u", "git commit -m 'Save listed paths'"],
                    required=["git diff --name-only", "git add -u", "git commit"],
                    forms=["git-add/update", "git-commit/message"],
                    state="dirty",
                    story=(
                        "Before sweeping tracked edits into a snapshot, list exactly which paths "
                        "will be involved. Then stage the tracked work and commit it under the "
                        "provided message."
                    ),
                    details=[{"label": "Commit message", "value": "Save listed paths"}],
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["README.md"],
                            "message_contains": ["Save listed paths"],
                        },
                        "staging_empty": True,
                        "working_tree_clean": True,
                        "rules": [{"type": "commit_count_equals", "count": 2}],
                    },
                    checks=[
                        {
                            "label": "The involved paths were listed before staging.",
                            "requirement": {"required_commands": ["git diff --name-only"]},
                        },
                        {
                            "label": "The tracked edit is committed under the provided message.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["README.md"],
                                    "message_contains": ["Save listed paths"],
                                }
                            },
                        },
                    ],
                ),
            ],
        },
        {
            "slug": "shape-two-snapshots",
            "title": "Shape Two Snapshots",
            "waves": [
                _wave(
                    "ch2-adv-shape-two-snapshots",
                    "git-add/patch",
                    "Split messy work",
                    [
                        "git add -p src/app.py",
                        "git commit -m 'Save app fix'",
                        "git add -A",
                        "git commit -m 'Save remaining cleanup'",
                    ],
                    required=["git add -p", "git commit", "git add -A"],
                    forms=["git-add/all", "git-commit/message"],
                    state="partial-plus",
                    story=(
                        "The working tree is genuinely messy: a real fix and a leftover debug hunk both "
                        "live in src/app.py, and docs/notes.md is a brand-new untracked file. Split this "
                        "into exactly two intentional commits: the fix alone first, then everything that "
                        "is left over."
                    ),
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["docs/notes.md"],
                            "message_contains": ["Save remaining cleanup"],
                        },
                        "staging_empty": True,
                        "working_tree_clean": True,
                        "rules": [
                            {"type": "commit_count_equals", "count": 3},
                            {"type": "commit_tree_excludes", "commit": "c1", "paths": ["docs/notes.md"]},
                        ],
                    },
                    checks=[
                        {
                            "label": "The fix landed in its own commit, separate from the leftover cleanup.",
                            "requirement": {
                                "rules": [
                                    {"type": "commit_count_equals", "count": 3},
                                    {"type": "commit_tree_excludes", "commit": "c1", "paths": ["docs/notes.md"]},
                                ]
                            },
                        },
                        {
                            "label": "The remaining cleanup became the newest commit on main.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["docs/notes.md"],
                                    "message_contains": ["Save remaining cleanup"],
                                }
                            },
                        },
                    ],
                ),
                _wave(
                    "ch2-adv-split-with-name-only",
                    "git-diff/name-only",
                    "Split a batch by path list",
                    [
                        "git diff --name-only",
                        "git add README.md",
                        "git commit -m 'Save the real edit'",
                        "git add -A",
                        "git commit -m 'Save the rest'",
                    ],
                    required=["git diff --name-only", "git add", "git commit", "git add -A"],
                    forms=["git-add/file", "git-commit/message", "git-add/all"],
                    state="mixed",
                    story=(
                        "The path list says two things changed: a tracked edit and a new local "
                        "file. They belong in separate snapshots - the real edit first, the "
                        "leftover batch second. Build both commits in that order."
                    ),
                    details=[
                        {"label": "First message", "value": "Save the real edit"},
                        {"label": "Second message", "value": "Save the rest"},
                    ],
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["scratch.txt"],
                            "message_contains": ["Save the rest"],
                        },
                        "staging_empty": True,
                        "working_tree_clean": True,
                        "rules": [
                            {"type": "commit_count_equals", "count": 3},
                            {"type": "commit_tree_excludes", "commit": "c1", "paths": ["scratch.txt"]},
                        ],
                    },
                    checks=[
                        {
                            "label": "The changed paths were listed before splitting.",
                            "requirement": {"required_commands": ["git diff --name-only"]},
                        },
                        {
                            "label": "The edit and the leftover batch landed as separate commits.",
                            "requirement": {
                                "rules": [
                                    {"type": "commit_count_equals", "count": 3},
                                    {"type": "commit_tree_excludes", "commit": "c1", "paths": ["scratch.txt"]},
                                ]
                            },
                        },
                    ],
                ),
                _wave(
                    "ch2-adv-tracked-sweep",
                    "git-add/update",
                    "Sweep tracked edits deliberately",
                    [
                        "git status -s",
                        "git diff --name-only",
                        "git add -u",
                        "git diff --staged",
                        "git commit -m 'Sweep tracked edits'",
                    ],
                    required=["git status -s", "git diff --name-only", "git add -u", "git diff --staged", "git commit"],
                    forms=["git-status/short", "git-diff/name-only", "git-diff/staged", "git-commit/message"],
                    state="mixed",
                    story=(
                        "Run the full precision loop: glance at the state, list the changed paths, "
                        "stage only tracked work, verify the staged content, then seal it. The "
                        "loose local file must survive untouched."
                    ),
                    details=[{"label": "Commit message", "value": "Sweep tracked edits"}],
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["README.md"],
                            "excludes_paths": ["scratch.txt"],
                            "message_contains": ["Sweep tracked edits"],
                        },
                        "staging_empty": True,
                        "rules": [{"type": "commit_count_equals", "count": 2}],
                    },
                    checks=[
                        {
                            "label": "The staged content was verified before sealing.",
                            "requirement": {"required_commands": ["git diff --staged"]},
                        },
                        {
                            "label": "Only tracked work is committed; the local file survived.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["README.md"],
                                    "excludes_paths": ["scratch.txt"],
                                    "message_contains": ["Sweep tracked edits"],
                                }
                            },
                        },
                    ],
                ),
                _wave(
                    "ch2-adv-fresh-batch",
                    "git-add/all",
                    "Stage a folder, prove it, seal it",
                    ["git add -A", "git diff --staged", "git commit -m 'Save the whole batch'"],
                    required=["git add -A", "git diff --staged", "git commit"],
                    forms=["git-diff/staged", "git-commit/message"],
                    state="folder",
                    story=(
                        "Everything in this folder is finished work: a source edit and a new "
                        "guide. Stage the whole batch, read the staged content as one final "
                        "review, then seal it in a single snapshot."
                    ),
                    details=[{"label": "Commit message", "value": "Save the whole batch"}],
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["src/app.py", "docs/guide.md"],
                            "message_contains": ["Save the whole batch"],
                        },
                        "staging_empty": True,
                        "working_tree_clean": True,
                        "rules": [{"type": "commit_count_equals", "count": 2}],
                    },
                    checks=[
                        {
                            "label": "The full batch was reviewed in staged form before sealing.",
                            "requirement": {"required_commands": ["git diff --staged"]},
                        },
                        {
                            "label": "Both files landed together in one snapshot.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["src/app.py", "docs/guide.md"],
                                    "message_contains": ["Save the whole batch"],
                                }
                            },
                        },
                    ],
                ),
            ],
        },
    ]
