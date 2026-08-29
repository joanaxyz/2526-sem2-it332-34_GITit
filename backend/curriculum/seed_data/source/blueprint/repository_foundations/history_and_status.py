"""Repository Foundations levels for history and status."""

from __future__ import annotations

from ..helpers import _wave

LEVELS = [
        {
            "slug": "read-history",
            "title": "Read History",
            "waves": [
                _wave(
                    "ch1-adv-log-oneline-intro",
                    "git-log/oneline",
                    "Read compact history",
                    ["git log --oneline"],
                    state="history-note",
                    story=(
                        "Two snapshots already exist in this project and a teammate asks which one is "
                        "newest. Read the history in its compact one-line form to answer, and change "
                        "nothing while you look."
                    ),
                    evaluation={
                        "staging_empty": True,
                        "rules": [{"type": "commit_count_equals", "count": 2}],
                    },
                    checks=[
                        {
                            "label": "The history was read in its compact one-line form.",
                            "requirement": {"required_commands": ["git log"]},
                        },
                    ],
                ),
                _wave(
                    "ch1-adv-log-graph-intro",
                    "git-log/graph-all",
                    "Graph every ref",
                    ["git log --oneline --graph --all"],
                    state="branch-note",
                    story=(
                        "This project has more than one line of work: main and feature/ui both point "
                        "somewhere on a small graph. Draw every ref at once to see how the two tips "
                        "relate, without moving anything."
                    ),
                    evaluation={
                        "staging_empty": True,
                        "head_branch": "main",
                    },
                    checks=[
                        {
                            "label": "Every ref was inspected on one drawn graph.",
                            "requirement": {"required_commands": ["git log"]},
                        },
                    ],
                ),
                _wave(
                    "ch1-adv-log-limit-intro",
                    "git-log/limit",
                    "Limit history output",
                    ["git log -n 2"],
                    state="audit-note",
                    story=(
                        "This history is three snapshots deep, but the review meeting only cares "
                        "about the most recent two. Read exactly that many entries and no more, "
                        "leaving the repository untouched."
                    ),
                    details=[{"label": "Entries to read", "value": "2"}],
                    evaluation={
                        "staging_empty": True,
                        "rules": [{"type": "commit_count_equals", "count": 3}],
                    },
                    checks=[
                        {
                            "label": "History was read with a limited entry count.",
                            "requirement": {"required_commands": ["git log"]},
                        },
                    ],
                ),
                _wave(
                    "ch1-adv-compact-history",
                    "git-log/oneline",
                    "Compact history",
                    ["git log --oneline", "git add REVIEW.md", "git commit -m 'Add review note'"],
                    required=["git log", "git commit"],
                    forms=["git-add/file", "git-commit/message"],
                    state="history-note",
                    story=(
                        "The project already has two commits. Find the latest one with a compact "
                        "one-line history, then add REVIEW.md recording what you found and commit it."
                    ),
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["REVIEW.md"],
                            "message_contains": ["Add review note"],
                        },
                        "staging_empty": True,
                        "working_tree_clean": True,
                        "rules": [{"type": "commit_count_equals", "count": 3}],
                    },
                    checks=[
                        {
                            "label": "The history was inspected with a compact one-line log.",
                            "requirement": {"required_commands": ["git log"]},
                        },
                        {
                            "label": "The review note is committed as the newest commit on main.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["REVIEW.md"],
                                    "message_contains": ["Add review note"],
                                }
                            },
                        },
                    ],
                ),
                _wave(
                    "ch1-adv-graph-history",
                    "git-log/graph-all",
                    "Graph history",
                    ["git log --oneline --graph --all", "git add GRAPH.md", "git commit -m 'Document branch tip'"],
                    required=["git log", "git commit"],
                    forms=["git-add/file", "git-commit/message"],
                    state="branch-note",
                    story=(
                        "main and feature/ui both exist on a small graph. Inspect every ref at once "
                        "with a graphed log to see which tip is current, then document that in "
                        "GRAPH.md and commit it on main."
                    ),
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["GRAPH.md"],
                            "message_contains": ["Document branch tip"],
                        },
                        "staging_empty": True,
                        "working_tree_clean": True,
                    },
                    checks=[
                        {
                            "label": "All refs were inspected at once with a graphed log.",
                            "requirement": {"required_commands": ["git log"]},
                        },
                        {
                            "label": "The branch-tip note is committed on main.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["GRAPH.md"],
                                    "message_contains": ["Document branch tip"],
                                }
                            },
                        },
                    ],
                ),
            ],
        },
        {
            "slug": "inspect-commits",
            "title": "Inspect Commits",
            "waves": [
                _wave(
                    "ch1-adv-show-head-intro",
                    "git-show/head",
                    "Inspect the newest snapshot",
                    ["git show"],
                    state="show-note",
                    story=(
                        "Before building on this project you want to know exactly what its newest "
                        "snapshot changed. Open that snapshot directly and read its full contents, "
                        "without naming any particular commit."
                    ),
                    evaluation={
                        "staging_empty": True,
                        "rules": [{"type": "commit_count_equals", "count": 2}],
                    },
                    checks=[
                        {
                            "label": "The newest snapshot was opened and read directly.",
                            "requirement": {"required_commands": ["git show"]},
                        },
                    ],
                ),
                _wave(
                    "ch1-adv-show-commit-intro",
                    "git-show/commit",
                    "Inspect a named snapshot",
                    ["git show c0"],
                    state="show-note",
                    story=(
                        "A changelog question points at the very first snapshot of this project, not "
                        "the newest one. Open that exact snapshot by name and read what it "
                        "introduced, changing nothing."
                    ),
                    details=[{"label": "Commit to inspect", "value": "c0"}],
                    evaluation={
                        "staging_empty": True,
                        "rules": [{"type": "commit_count_equals", "count": 2}],
                    },
                    checks=[
                        {
                            "label": "The named snapshot was opened and read directly.",
                            "requirement": {"required_commands": ["git show"]},
                        },
                    ],
                ),
                _wave(
                    "ch1-adv-show-name-only-intro",
                    "git-show/name-only",
                    "List a snapshot's paths",
                    ["git show --name-only c0"],
                    state="audit-note",
                    story=(
                        "An audit sheet needs the bare list of file paths the first snapshot touched, "
                        "with none of the patch text. Read exactly that list for the named snapshot "
                        "and nothing more."
                    ),
                    details=[{"label": "Commit to inspect", "value": "c0"}],
                    evaluation={
                        "staging_empty": True,
                        "rules": [{"type": "commit_count_equals", "count": 3}],
                    },
                    checks=[
                        {
                            "label": "Only the touched paths were listed for the named snapshot.",
                            "requirement": {"required_commands": ["git show --name-only"]},
                        },
                    ],
                ),
                _wave(
                    "ch1-adv-show-commit",
                    "git-show/commit",
                    "Show a commit",
                    ["git show c0", "git add CHANGELOG.md", "git commit -m 'Add changelog note'"],
                    required=["git show", "git commit"],
                    forms=["git-add/file", "git-commit/message"],
                    state="show-note",
                    story=(
                        "A changelog draft, CHANGELOG.md, needs one fact confirmed: exactly what the "
                        "very first commit introduced. Inspect that commit directly, then commit the "
                        "changelog note referencing what you found."
                    ),
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["CHANGELOG.md"],
                            "message_contains": ["Add changelog note"],
                        },
                        "staging_empty": True,
                        "working_tree_clean": True,
                    },
                    checks=[
                        {
                            "label": "The referenced commit was inspected directly with show.",
                            "requirement": {"required_commands": ["git show"]},
                        },
                        {
                            "label": "The changelog note is committed on main.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["CHANGELOG.md"],
                                    "message_contains": ["Add changelog note"],
                                }
                            },
                        },
                    ],
                ),
            ],
        },
        {
            "slug": "history-details",
            "title": "History Details",
            "waves": [
                _wave(
                    "ch1-adv-log-patch-intro",
                    "git-log/patch",
                    "Read history as patches",
                    ["git log -p"],
                    state="history-note",
                    story=(
                        "A reviewer wants to see not just which snapshots exist but the full line-by-"
                        "line changes each one made. Walk the history with its complete patch text "
                        "attached, and leave everything as it is."
                    ),
                    evaluation={
                        "staging_empty": True,
                        "rules": [{"type": "commit_count_equals", "count": 2}],
                    },
                    checks=[
                        {
                            "label": "History was read with full patch detail.",
                            "requirement": {"required_commands": ["git log -p"]},
                        },
                    ],
                ),
                _wave(
                    "ch1-adv-log-stat-intro",
                    "git-log/stat",
                    "Read history change summaries",
                    ["git log --stat"],
                    state="audit-note",
                    story=(
                        "The audit meeting needs a quick sense of how big each of the three snapshots "
                        "was: which files changed and by roughly how much. Read the history with its "
                        "per-snapshot change summary, nothing more."
                    ),
                    evaluation={
                        "staging_empty": True,
                        "rules": [{"type": "commit_count_equals", "count": 3}],
                    },
                    checks=[
                        {
                            "label": "History was read with per-snapshot change summaries.",
                            "requirement": {"required_commands": ["git log --stat"]},
                        },
                    ],
                ),
                _wave(
                    "ch1-adv-history-detail-forms",
                    "git-log/limit",
                    "Detailed history audit",
                    [
                        "git log -n 1",
                        "git log -p",
                        "git log --stat",
                        "git show --name-only c0",
                        "git add AUDIT.md",
                        "git commit -m 'Add audit note'",
                    ],
                    required=["git log", "git show", "git commit"],
                    forms=["git-log/patch", "git-log/stat", "git-show/name-only", "git-add/file", "git-commit/message"],
                    state="audit-note",
                    story=(
                        "A commit audit needs every level of detail: the single latest entry, the full "
                        "patch text, the per-commit file stats, and the bare list of paths the first "
                        "commit touched. Gather all four readings, then commit AUDIT.md recording the "
                        "audit."
                    ),
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["AUDIT.md"],
                            "message_contains": ["Add audit note"],
                        },
                        "staging_empty": True,
                        "working_tree_clean": True,
                    },
                    checks=[
                        {
                            "label": "The history was audited at every level of detail: limited log, patch, stat, and name-only show.",
                            "requirement": {"required_commands": ["git log", "git show"]},
                        },
                        {
                            "label": "The audit note is committed on main and nothing else is left over.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["AUDIT.md"],
                                    "message_contains": ["Add audit note"],
                                }
                            },
                        },
                    ],
                ),
                _wave(
                    "ch1-adv-audit-then-save",
                    "git-log/stat",
                    "Audit then record findings",
                    [
                        "git log --stat",
                        "git show",
                        "git add AUDIT.md",
                        "git commit -m 'Record audit findings'",
                    ],
                    required=["git log --stat", "git show", "git add", "git commit"],
                    forms=["git-show/head", "git-add/file", "git-commit/message"],
                    state="audit-note",
                    story=(
                        "An audit draft, AUDIT.md, is waiting for two facts: how large each past "
                        "snapshot was, and what the newest one actually contains. Gather both "
                        "readings, then save the completed audit note as the next snapshot."
                    ),
                    details=[{"label": "Commit message", "value": "Record audit findings"}],
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["AUDIT.md"],
                            "message_contains": ["Record audit findings"],
                        },
                        "staging_empty": True,
                        "working_tree_clean": True,
                        "rules": [{"type": "commit_count_equals", "count": 4}],
                    },
                    checks=[
                        {
                            "label": "Change summaries and the newest snapshot were both read first.",
                            "requirement": {"required_commands": ["git log --stat", "git show"]},
                        },
                        {
                            "label": "The audit note is committed on main.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["AUDIT.md"],
                                    "message_contains": ["Record audit findings"],
                                }
                            },
                        },
                    ],
                ),
            ],
        },
        {
            "slug": "status-at-a-glance",
            "title": "Status at a Glance",
            "waves": [
                _wave(
                    "ch1-adv-status-short-intro",
                    "git-status/short",
                    "Read compact status",
                    ["git status -s"],
                    state="mixed",
                    story=(
                        "This workspace holds one tracked edit and one loose local file, and you "
                        "check it a dozen times a day. Read the state in its two-column compact form "
                        "instead of the full report, touching nothing."
                    ),
                    evaluation={
                        "working_tree_dirty": True,
                        "staging_empty": True,
                        "rules": [{"type": "commit_count_equals", "count": 1}],
                    },
                    checks=[
                        {
                            "label": "The workspace was read in compact two-column form.",
                            "requirement": {"required_commands": ["git status -s"]},
                        },
                    ],
                ),
                _wave(
                    "ch1-adv-status-porcelain-intro",
                    "git-status/porcelain",
                    "Read script-stable status",
                    ["git status --porcelain"],
                    state="mixed",
                    story=(
                        "A build script needs to parse this workspace's state, so the output format "
                        "must never change between versions. Read the state in its stable, script-"
                        "friendly form and leave the files alone."
                    ),
                    evaluation={
                        "working_tree_dirty": True,
                        "staging_empty": True,
                        "rules": [{"type": "commit_count_equals", "count": 1}],
                    },
                    checks=[
                        {
                            "label": "The workspace was read in script-stable form.",
                            "requirement": {"required_commands": ["git status --porcelain"]},
                        },
                    ],
                ),
                _wave(
                    "ch1-adv-compact-and-script-status",
                    "git-status/short",
                    "Compact script status",
                    ["git status -s", "git status --porcelain", "git add README.md", "git commit -m 'Save compact status work'"],
                    required=["git status -s", "git status --porcelain", "git commit"],
                    forms=["git-status/porcelain", "git-add/file", "git-commit/message"],
                    state="dirty",
                    story=(
                        "Reading the full status output is slower than it needs to be. Use the "
                        "compact -s form, then the stable script-friendly --porcelain form, to confirm "
                        "the one real change before committing it."
                    ),
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["README.md"],
                            "message_contains": ["Save compact status work"],
                        },
                        "staging_empty": True,
                        "working_tree_clean": True,
                    },
                    checks=[
                        {
                            "label": "The change was confirmed with both the compact and porcelain status forms.",
                            "requirement": {"required_commands": ["git status -s", "git status --porcelain"]},
                        },
                        {
                            "label": "Only the intended file is committed.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["README.md"],
                                    "message_contains": ["Save compact status work"],
                                }
                            },
                        },
                    ],
                ),
                _wave(
                    "ch1-adv-short-status-save",
                    "git-status/short",
                    "Glance then save everything",
                    [
                        "git status -s",
                        "git add .",
                        "git commit -m 'Save inspected work'",
                        "git log --oneline",
                    ],
                    required=["git status -s", "git add", "git commit", "git log"],
                    forms=["git-add/dot", "git-commit/message", "git-log/oneline"],
                    state="folder",
                    story=(
                        "A folder of finished work is ready to go: one modified source file and one "
                        "new guide. Confirm the pieces with a compact glance, save everything below "
                        "the folder in one snapshot, then read the history to verify it landed."
                    ),
                    details=[{"label": "Commit message", "value": "Save inspected work"}],
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["src/app.py", "docs/guide.md"],
                            "message_contains": ["Save inspected work"],
                        },
                        "staging_empty": True,
                        "working_tree_clean": True,
                        "rules": [{"type": "commit_count_equals", "count": 2}],
                    },
                    checks=[
                        {
                            "label": "The pieces were confirmed with a compact glance first.",
                            "requirement": {"required_commands": ["git status -s"]},
                        },
                        {
                            "label": "Every visible file landed in one snapshot on main.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["src/app.py", "docs/guide.md"],
                                    "message_contains": ["Save inspected work"],
                                }
                            },
                        },
                        {
                            "label": "The landing was verified against history afterward.",
                            "requirement": {"required_commands": ["git log"]},
                        },
                    ],
                ),
            ],
        },
    ]
