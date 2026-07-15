"""Blueprint adventure levels for repository-foundations."""

from __future__ import annotations

from .helpers import _wave

ADVENTURE_LEVELS = [
        {
            "slug": "start-a-repository",
            "title": "Start a Repository",
            "waves": [
                _wave(
                    "ch1-adv-init-here",
                    "git-init/current-directory",
                    "Create repository metadata",
                    ["git init"],
                    state="uninitialized",
                    story=(
                        "A capstone folder already holds README.md and src/app.py, but nothing about "
                        "it is tracked yet. Give this folder its own repository metadata so history "
                        "can begin; the files themselves stay untouched and unsaved for now."
                    ),
                    evaluation={
                        "repository_initialized": True,
                        "staging_empty": True,
                        "rules": [{"type": "commit_count_equals", "count": 0}],
                    },
                    checks=[
                        {
                            "label": "The current folder is now a Git repository.",
                            "requirement": {"repository_initialized": True},
                        },
                    ],
                ),
                _wave(
                    "ch1-adv-init-named-folder",
                    "git-init/named-directory",
                    "Initialize named folder",
                    ["git init project"],
                    state="uninitialized",
                    story=(
                        "A new exercise must live in its own project folder instead of reusing the "
                        "current workspace. Create repository metadata for the exact folder name shown "
                        "below."
                    ),
                    details=[{"label": "Folder name", "value": "project"}],
                    evaluation={
                        "repository_initialized": True,
                        "rules": [
                            {
                                "type": "operation_metadata_equals",
                                "key": "last_init_directory",
                                "value": "project",
                            }
                        ],
                    },
                    checks=[
                        {
                            "label": "The repository was created in the requested folder.",
                            "requirement": {
                                "rules": [
                                    {
                                        "type": "operation_metadata_equals",
                                        "key": "last_init_directory",
                                        "value": "project",
                                    }
                                ]
                            },
                        }
                    ],
                ),
                _wave(
                    "ch1-adv-init-first-branch",
                    "git-init/initial-branch",
                    "Choose first branch",
                    ["git init -b main"],
                    state="uninitialized",
                    story=(
                        "The team's starter repository has to begin on a specific first branch, before "
                        "any snapshots exist. Initialize the folder so the first branch has the exact "
                        "name shown below."
                    ),
                    details=[{"label": "First branch name", "value": "main"}],
                    evaluation={
                        "repository_initialized": True,
                        "head_branch": "main",
                        "rules": [
                            {
                                "type": "operation_metadata_equals",
                                "key": "last_init_initial_branch",
                                "value": "main",
                            }
                        ],
                    },
                    checks=[
                        {
                            "label": "The folder is now a Git repository.",
                            "requirement": {"repository_initialized": True},
                        },
                        {
                            "label": "The first branch uses the requested name.",
                            "requirement": {"head_branch": "main"},
                        },
                    ],
                ),
            ],
        },
        {
            "slug": "read-the-workspace",
            "title": "Read the Workspace",
            "waves": [
                _wave(
                    "ch1-adv-status-plain",
                    "git-status/plain",
                    "Read plain status",
                    ["git status"],
                    state="dirty",
                    story=(
                        "A teammate wants to know whether last night's README edit is safe to build "
                        "on. Open the repository and read its exact status before you promise anything: "
                        "one tracked file, README.md, carries an unstaged edit. Report what Git sees "
                        "without staging or committing anything yet."
                    ),
                    evaluation={
                        "working_tree_dirty": True,
                        "staging_empty": True,
                        "rules": [{"type": "commit_count_equals", "count": 1}],
                    },
                    checks=[
                        {
                            "label": "The working tree was inspected with status before anything changed.",
                            "requirement": {"required_commands": ["git status"]},
                        },
                    ],
                ),
                _wave(
                    "ch1-adv-diff-working-intro",
                    "git-diff/working",
                    "Read an unstaged change",
                    ["git diff"],
                    state="dirty",
                    story=(
                        "README.md carries an edit nobody has reviewed yet. Read the exact changed "
                        "lines the working tree holds before anyone decides whether to keep them; "
                        "change nothing while you look."
                    ),
                    evaluation={
                        "working_tree_dirty": True,
                        "staging_empty": True,
                        "rules": [{"type": "commit_count_equals", "count": 1}],
                    },
                    checks=[
                        {
                            "label": "The unstaged edit was read line by line.",
                            "requirement": {"required_commands": ["git diff"]},
                        },
                    ],
                ),
                _wave(
                    "ch1-adv-read-before-touching",
                    "git-status/plain",
                    "Read before touching",
                    ["git status", "git diff"],
                    required=["git status", "git diff"],
                    forms=["git-diff/working"],
                    state="mixed",
                    story=(
                        "A handoff note says this workspace has one tracked edit and one loose local "
                        "file. Verify the note: read the overall state first, then the exact changed "
                        "lines, and leave every file exactly as you found it."
                    ),
                    evaluation={
                        "working_tree_dirty": True,
                        "staging_empty": True,
                        "rules": [{"type": "commit_count_equals", "count": 1}],
                    },
                    checks=[
                        {
                            "label": "The overall state was read before the detailed diff.",
                            "requirement": {"required_commands": ["git status", "git diff"]},
                        },
                    ],
                ),
            ],
        },
        {
            "slug": "stage-and-commit",
            "title": "Stage and Commit",
            "waves": [
                _wave(
                    "ch1-adv-stage-one-file",
                    "git-add/file",
                    "Stage one file",
                    ["git add README.md"],
                    state="dirty",
                    story=(
                        "The working tree holds exactly one modified file, README.md. Move that file "
                        "into the staging area so the next snapshot can include it, without creating "
                        "the commit yet."
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
                            "label": "README.md is staged for the next snapshot.",
                            "requirement": {"rules": [{"type": "staging_contains", "path": "README.md"}]},
                        },
                    ],
                ),
                _wave(
                    "ch1-adv-commit-staged-snapshot",
                    "git-commit/message",
                    "Commit staged work",
                    ["git commit -m 'Save staged work'"],
                    state="staged",
                    story=(
                        "README.md already sits in the staging area with a reviewed edit. Turn that "
                        "staged snapshot into the next commit on main."
                    ),
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["README.md"],
                            "message_contains": ["Save staged work"],
                        },
                        "staging_empty": True,
                        "working_tree_clean": True,
                    },
                    checks=[
                        {
                            "label": "The staged README edit became the newest commit on main.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["README.md"],
                                    "message_contains": ["Save staged work"],
                                }
                            },
                        },
                        {
                            "label": "Staging and the working tree are clean afterward.",
                            "requirement": {"staging_empty": True, "working_tree_clean": True},
                        },
                    ],
                ),
                _wave(
                    "ch1-adv-stage-folder-intro",
                    "git-add/dot",
                    "Stage the whole folder",
                    ["git add ."],
                    state="folder",
                    story=(
                        "Two pieces of finished work sit in this folder: a modified src/app.py and a "
                        "brand-new docs/guide.md. Move everything visible below the current folder "
                        "into the staging area in one sweep, without creating the snapshot yet."
                    ),
                    evaluation={
                        "staging_not_empty": True,
                        "working_tree_clean": True,
                        "rules": [
                            {"type": "staging_contains", "path": "src/app.py"},
                            {"type": "staging_contains", "path": "docs/guide.md"},
                            {"type": "commit_count_equals", "count": 1},
                        ],
                    },
                    checks=[
                        {
                            "label": "Both visible files moved into the staging area together.",
                            "requirement": {
                                "rules": [
                                    {"type": "staging_contains", "path": "src/app.py"},
                                    {"type": "staging_contains", "path": "docs/guide.md"},
                                ]
                            },
                        },
                    ],
                ),
                _wave(
                    "ch1-adv-first-save-workflow",
                    "git-status/plain",
                    "First save workflow",
                    ["git status", "git add README.md", "git commit -m 'Save first feature'"],
                    required=["git status", "git add", "git commit"],
                    forms=["git-add/file", "git-commit/message"],
                    state="dirty",
                    story=(
                        "One small feature sits unstaged in README.md. Confirm what changed, then "
                        "carry it all the way from the working tree to a real commit on main."
                    ),
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["README.md"],
                            "message_contains": ["Save first feature"],
                        },
                        "staging_empty": True,
                        "working_tree_clean": True,
                    },
                    checks=[
                        {
                            "label": "The change was inspected with status before saving it.",
                            "requirement": {"required_commands": ["git status"]},
                        },
                        {
                            "label": "The feature became the newest commit on main.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["README.md"],
                                    "message_contains": ["Save first feature"],
                                }
                            },
                        },
                        {
                            "label": "Nothing is left staged or unstaged afterward.",
                            "requirement": {"staging_empty": True, "working_tree_clean": True},
                        },
                    ],
                ),
            ],
        },
        {
            "slug": "the-first-snapshot",
            "title": "The First Snapshot",
            "waves": [
                _wave(
                    "ch1-adv-init-current-folder",
                    "git-init/current-directory",
                    "Initialize current folder",
                    ["git init", "git add .", "git commit -m 'Initial commit'"],
                    required=["git init", "git add", "git commit"],
                    forms=["git-add/dot", "git-commit/message"],
                    state="uninitialized",
                    story=(
                        "A capstone folder already contains README.md and src/app.py, but it has no "
                        "repository metadata yet. Turn this current folder into a repository, save both "
                        "starter files in the first snapshot using the provided message, and leave the "
                        "workspace clean."
                    ),
                    details=[{"label": "Commit message", "value": "Initial commit"}],
                    evaluation={
                        "repository_initialized": True,
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["README.md", "src/app.py"],
                            "message_contains": ["Initial commit"],
                        },
                        "working_tree_clean": True,
                        "staging_empty": True,
                    },
                    checks=[
                        {
                            "label": "The current folder is now a Git repository.",
                            "requirement": {"repository_initialized": True},
                        },
                        {
                            "label": "Both starter files are saved in the first snapshot.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["README.md", "src/app.py"],
                                }
                            },
                        },
                        {
                            "label": "No starter work is left uncommitted.",
                            "requirement": {"working_tree_clean": True, "staging_empty": True},
                        },
                    ],
                ),
                _wave(
                    "ch1-adv-diff-staged-intro",
                    "git-diff/staged",
                    "Read the staged snapshot",
                    ["git diff --staged"],
                    state="staged",
                    story=(
                        "A README.md edit is already sitting in the staging area, one step away from "
                        "becoming permanent history. Read exactly what the staged version will change "
                        "compared to the last snapshot, and stop there."
                    ),
                    evaluation={
                        "staging_not_empty": True,
                        "rules": [
                            {"type": "staging_contains", "path": "README.md"},
                            {"type": "commit_count_equals", "count": 1},
                        ],
                    },
                    checks=[
                        {
                            "label": "The staged change was reviewed against the last snapshot.",
                            "requirement": {"required_commands": ["git diff --staged"]},
                        },
                    ],
                ),
                _wave(
                    "ch1-adv-diff-before-stage",
                    "git-diff/working",
                    "Diff before staging",
                    ["git diff", "git add README.md", "git commit -m 'Save reviewed edit'"],
                    required=["git diff", "git add", "git commit"],
                    forms=["git-add/file", "git-commit/message"],
                    state="dirty",
                    story=(
                        "README.md has an unstaged edit sitting in the working tree. Read exactly what "
                        "changed with diff before you decide to keep it, then stage and commit the "
                        "reviewed edit."
                    ),
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["README.md"],
                            "message_contains": ["Save reviewed edit"],
                        },
                        "staging_empty": True,
                        "working_tree_clean": True,
                    },
                    checks=[
                        {
                            "label": "The unstaged edit was reviewed with diff before staging.",
                            "requirement": {"required_commands": ["git diff"]},
                        },
                        {
                            "label": "The reviewed edit became the newest commit on main.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["README.md"],
                                    "message_contains": ["Save reviewed edit"],
                                }
                            },
                        },
                        {
                            "label": "Staging and the working tree are clean afterward.",
                            "requirement": {"staging_empty": True, "working_tree_clean": True},
                        },
                    ],
                ),
                _wave(
                    "ch1-adv-diff-after-stage",
                    "git-diff/staged",
                    "Diff staged work",
                    ["git diff --staged", "git commit -m 'Save staged edit'"],
                    required=["git diff --staged", "git commit"],
                    forms=["git-commit/message"],
                    state="staged",
                    story=(
                        "README.md is already staged with an edit. Before sealing the snapshot, review "
                        "exactly what the staged version will change relative to the last commit, then "
                        "commit it."
                    ),
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["README.md"],
                            "message_contains": ["Save staged edit"],
                        },
                        "staging_empty": True,
                        "working_tree_clean": True,
                    },
                    checks=[
                        {
                            "label": "The staged snapshot was reviewed with diff --staged before committing.",
                            "requirement": {"required_commands": ["git diff --staged"]},
                        },
                        {
                            "label": "The reviewed staged snapshot became the newest commit on main.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["README.md"],
                                    "message_contains": ["Save staged edit"],
                                }
                            },
                        },
                    ],
                ),
                _wave(
                    "ch1-adv-save-folder-work",
                    "git-add/dot",
                    "Save folder work",
                    ["git add .", "git commit -m 'Save folder work'"],
                    required=["git add", "git commit"],
                    forms=["git-commit/message"],
                    state="folder",
                    story=(
                        "A small folder of visible project files needs saving at once: a modified "
                        "src/app.py and a brand-new docs/guide.md. Stage the whole folder in one move "
                        "and commit both files together."
                    ),
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["src/app.py", "docs/guide.md"],
                            "message_contains": ["Save folder work"],
                        },
                        "staging_empty": True,
                        "working_tree_clean": True,
                    },
                    checks=[
                        {
                            "label": "The commit on main contains every visible project file.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["src/app.py", "docs/guide.md"],
                                    "message_contains": ["Save folder work"],
                                }
                            },
                        },
                    ],
                ),
            ],
        },
        {
            "slug": "practice-fresh-starts",
            "title": "Practice Fresh Starts",
            "waves": [
                _wave(
                    "ch1-adv-fresh-docs-site",
                    "git-init/current-directory",
                    "Found a docs site",
                    ["git init", "git add .", "git commit -m 'Publish docs seed'"],
                    required=["git init", "git add", "git commit"],
                    forms=["git-add/dot", "git-commit/message"],
                    state="uninitialized",
                    story=(
                        "The documentation team wants its site folder under version control today. "
                        "Turn the folder into a repository and land both starter files in one first "
                        "snapshot using the provided message, leaving nothing unsaved."
                    ),
                    details=[{"label": "Commit message", "value": "Publish docs seed"}],
                    evaluation={
                        "repository_initialized": True,
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["README.md", "src/app.py"],
                            "message_contains": ["Publish docs seed"],
                        },
                        "working_tree_clean": True,
                        "staging_empty": True,
                    },
                    checks=[
                        {
                            "label": "The docs folder is now a Git repository.",
                            "requirement": {"repository_initialized": True},
                        },
                        {
                            "label": "Both starter files landed in the first snapshot.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["README.md", "src/app.py"],
                                    "message_contains": ["Publish docs seed"],
                                }
                            },
                        },
                        {
                            "label": "Nothing is left staged or unstaged afterward.",
                            "requirement": {"working_tree_clean": True, "staging_empty": True},
                        },
                    ],
                ),
                _wave(
                    "ch1-adv-named-tool-setup",
                    "git-init/named-directory",
                    "Set up a named tool folder",
                    ["git init tool-kit", "git add .", "git commit -m 'Tool kit start'"],
                    required=["git init", "git add", "git commit"],
                    forms=["git-add/dot", "git-commit/message"],
                    state="uninitialized",
                    story=(
                        "A shared helper tool deserves its own dedicated workspace instead of living "
                        "inside the current folder. Create repository metadata under the exact folder "
                        "name shown below, then save the starter files as its first snapshot."
                    ),
                    details=[
                        {"label": "Folder name", "value": "tool-kit"},
                        {"label": "Commit message", "value": "Tool kit start"},
                    ],
                    evaluation={
                        "repository_initialized": True,
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["README.md", "src/app.py"],
                            "message_contains": ["Tool kit start"],
                        },
                        "working_tree_clean": True,
                        "rules": [
                            {
                                "type": "operation_metadata_equals",
                                "key": "last_init_directory",
                                "value": "tool-kit",
                            }
                        ],
                    },
                    checks=[
                        {
                            "label": "The repository was created under the requested folder name.",
                            "requirement": {
                                "rules": [
                                    {
                                        "type": "operation_metadata_equals",
                                        "key": "last_init_directory",
                                        "value": "tool-kit",
                                    }
                                ]
                            },
                        },
                        {
                            "label": "The starter files are saved in the first snapshot.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["README.md", "src/app.py"],
                                    "message_contains": ["Tool kit start"],
                                }
                            },
                        },
                    ],
                ),
                _wave(
                    "ch1-adv-branch-first-project",
                    "git-init/initial-branch",
                    "Start history on trunk",
                    ["git init -b trunk", "git add .", "git commit -m 'Start on trunk'"],
                    required=["git init", "git add", "git commit"],
                    forms=["git-add/dot", "git-commit/message"],
                    state="uninitialized",
                    story=(
                        "This team names its default line of work trunk, and the new project must "
                        "begin there before any snapshot exists. Initialize the folder so its first "
                        "branch carries the required name, then save the starter files on it."
                    ),
                    details=[
                        {"label": "First branch name", "value": "trunk"},
                        {"label": "Commit message", "value": "Start on trunk"},
                    ],
                    evaluation={
                        "repository_initialized": True,
                        "head_branch": "trunk",
                        "latest_commit": {
                            "branch": "trunk",
                            "contains_paths": ["README.md", "src/app.py"],
                            "message_contains": ["Start on trunk"],
                        },
                        "working_tree_clean": True,
                        "staging_empty": True,
                    },
                    checks=[
                        {
                            "label": "History began on the requested first branch.",
                            "requirement": {"head_branch": "trunk"},
                        },
                        {
                            "label": "The starter files are saved on that branch.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "trunk",
                                    "contains_paths": ["README.md", "src/app.py"],
                                    "message_contains": ["Start on trunk"],
                                }
                            },
                        },
                    ],
                ),
            ],
        },
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
        {
            "slug": "copy-a-project",
            "title": "Copy a Project",
            "waves": [
                _wave(
                    "ch1-adv-clone-intro",
                    "git-clone/default-folder",
                    "Copy a remote project",
                    ["git clone https://example.test/team/app.git"],
                    state="clone",
                    story=(
                        "The team's application lives on a shared server at "
                        "https://example.test/team/app.git and you have nothing local yet. Bring a "
                        "complete copy of it down into its default local folder."
                    ),
                    details=[{"label": "Remote URL", "value": "https://example.test/team/app.git"}],
                    evaluation={
                        "repository_initialized": True,
                        "working_tree_clean": True,
                        "staging_empty": True,
                    },
                    checks=[
                        {
                            "label": "A complete local copy of the remote project exists.",
                            "requirement": {"repository_initialized": True},
                        },
                    ],
                ),
                _wave(
                    "ch1-adv-clone-named-intro",
                    "git-clone/named-folder",
                    "Copy into a chosen folder",
                    ["git clone https://example.test/team/app.git starter-copy"],
                    state="clone",
                    story=(
                        "You need a second copy of the team application, and it must land in a "
                        "folder with the exact name shown below rather than the default. Bring the "
                        "project down into that folder."
                    ),
                    details=[
                        {"label": "Remote URL", "value": "https://example.test/team/app.git"},
                        {"label": "Folder name", "value": "starter-copy"},
                    ],
                    evaluation={
                        "repository_initialized": True,
                        "rules": [
                            {
                                "type": "operation_metadata_equals",
                                "key": "last_clone_destination",
                                "value": "starter-copy",
                            }
                        ],
                    },
                    checks=[
                        {
                            "label": "The copy landed in the requested folder.",
                            "requirement": {
                                "rules": [
                                    {
                                        "type": "operation_metadata_equals",
                                        "key": "last_clone_destination",
                                        "value": "starter-copy",
                                    }
                                ]
                            },
                        }
                    ],
                ),
                _wave(
                    "ch1-adv-clone-branch-intro",
                    "git-clone/branch",
                    "Copy a specific branch",
                    ["git clone -b starter https://example.test/team/app.git"],
                    state="clone",
                    story=(
                        "The exercise material for this week lives on a branch named starter, not on "
                        "the project's default line of work. Copy the project so that branch is the "
                        "one checked out from the very first moment."
                    ),
                    details=[{"label": "Branch to check out", "value": "starter"}],
                    evaluation={
                        "repository_initialized": True,
                        "head_branch": "starter",
                        "working_tree_clean": True,
                    },
                    checks=[
                        {
                            "label": "The copy checked out the requested branch directly.",
                            "requirement": {"head_branch": "starter"},
                        }
                    ],
                ),
                _wave(
                    "ch1-adv-clone-depth-intro",
                    "git-clone/depth",
                    "Copy only recent history",
                    ["git clone --depth 1 https://example.test/team/app.git"],
                    state="clone",
                    story=(
                        "For this quick experiment only the project's current state matters; its "
                        "full past would just waste time and space. Copy the project with exactly "
                        "one snapshot of history."
                    ),
                    details=[{"label": "History depth", "value": "1"}],
                    evaluation={
                        "repository_initialized": True,
                        "rules": [{"type": "commit_count_equals", "count": 1}],
                    },
                    checks=[
                        {
                            "label": "The copy is shallow: exactly one snapshot of history came down.",
                            "requirement": {"rules": [{"type": "commit_count_equals", "count": 1}]},
                        }
                    ],
                ),
            ],
        },
        {
            "slug": "inspect-what-you-cloned",
            "title": "Inspect What You Cloned",
            "waves": [
                _wave(
                    "ch1-adv-clone-default",
                    "git-clone/default-folder",
                    "Clone default folder",
                    ["git clone https://example.test/team/app.git", "git status"],
                    required=["git clone", "git status"],
                    forms=["git-status/plain"],
                    state="clone",
                    story=(
                        "A teammate's repository lives at https://example.test/team/app.git. Clone it "
                        "into its default local folder, then confirm the copy is clean by inspecting "
                        "its status."
                    ),
                    evaluation={
                        "repository_initialized": True,
                        "working_tree_clean": True,
                        "staging_empty": True,
                    },
                    checks=[
                        {
                            "label": "The remote project is cloned locally.",
                            "requirement": {"repository_initialized": True},
                        },
                        {
                            "label": "The fresh clone was confirmed clean with status.",
                            "requirement": {
                                "required_commands": ["git status"],
                                "working_tree_clean": True,
                                "staging_empty": True,
                            },
                        },
                    ],
                ),
                _wave(
                    "ch1-adv-clone-named-folder",
                    "git-clone/named-folder",
                    "Clone named folder",
                    ["git clone https://example.test/team/app.git app-copy", "git log --oneline"],
                    required=["git clone", "git log"],
                    forms=["git-log/oneline"],
                    state="clone",
                    story=(
                        "This exercise needs the clone to land in a specific project folder, app-copy, "
                        "instead of the default name. Clone into that exact folder, then read its "
                        "history to confirm what came down."
                    ),
                    evaluation={
                        "repository_initialized": True,
                        "rules": [
                            {"type": "operation_metadata_equals", "key": "last_clone_destination", "value": "app-copy"},
                        ],
                    },
                    checks=[
                        {
                            "label": "The clone landed in the requested app-copy folder.",
                            "requirement": {
                                "rules": [
                                    {
                                        "type": "operation_metadata_equals",
                                        "key": "last_clone_destination",
                                        "value": "app-copy",
                                    }
                                ]
                            },
                        },
                        {
                            "label": "The cloned history was inspected before moving on.",
                            "requirement": {"required_commands": ["git log"]},
                        },
                    ],
                ),
                _wave(
                    "ch1-adv-clone-specific-branch",
                    "git-clone/branch",
                    "Clone specific branch",
                    ["git clone -b starter https://example.test/team/app.git", "git status"],
                    required=["git clone", "git status"],
                    forms=["git-status/plain"],
                    state="clone",
                    story=(
                        "The exercise's starter content lives on a branch named starter, not the "
                        "default branch. Clone the repository so it checks out starter immediately, "
                        "then confirm you landed on it."
                    ),
                    evaluation={
                        "repository_initialized": True,
                        "head_branch": "starter",
                        "working_tree_clean": True,
                    },
                    checks=[
                        {
                            "label": "The clone checked out the starter branch directly.",
                            "requirement": {"head_branch": "starter"},
                        },
                        {
                            "label": "The branch was confirmed with status after cloning.",
                            "requirement": {"required_commands": ["git status"]},
                        },
                    ],
                ),
                _wave(
                    "ch1-adv-clone-shallow",
                    "git-clone/depth",
                    "Clone shallow history",
                    ["git clone --depth 1 https://example.test/team/app.git", "git log --oneline"],
                    required=["git clone", "git log"],
                    forms=["git-log/oneline"],
                    state="clone",
                    story=(
                        "Only the current state of this remote project matters for this task, not its "
                        "full history. Clone with a depth of one commit, then read the log to confirm "
                        "exactly how much history is visible."
                    ),
                    evaluation={
                        "repository_initialized": True,
                        "rules": [{"type": "commit_count_equals", "count": 1}],
                    },
                    checks=[
                        {
                            "label": "The clone is shallow: exactly one commit of history is visible.",
                            "requirement": {"rules": [{"type": "commit_count_equals", "count": 1}]},
                        },
                        {
                            "label": "The visible history was confirmed with a log after cloning.",
                            "requirement": {"required_commands": ["git log"]},
                        },
                    ],
                ),
            ],
        },
        {
            "slug": "clone-drills",
            "title": "Clone Drills",
            "waves": [
                _wave(
                    "ch1-adv-clone-named-then-status",
                    "git-clone/named-folder",
                    "Copy to a lab folder and verify",
                    ["git clone https://example.test/team/app.git app-lab", "git status"],
                    required=["git clone", "git status"],
                    forms=["git-status/plain"],
                    state="clone",
                    story=(
                        "A testing session needs its own disposable copy of the team app in a folder "
                        "named app-lab. Bring the copy down into that folder, then confirm it starts "
                        "perfectly clean before any experiments begin."
                    ),
                    details=[{"label": "Folder name", "value": "app-lab"}],
                    evaluation={
                        "repository_initialized": True,
                        "working_tree_clean": True,
                        "staging_empty": True,
                        "rules": [
                            {
                                "type": "operation_metadata_equals",
                                "key": "last_clone_destination",
                                "value": "app-lab",
                            }
                        ],
                    },
                    checks=[
                        {
                            "label": "The copy landed in the requested lab folder.",
                            "requirement": {
                                "rules": [
                                    {
                                        "type": "operation_metadata_equals",
                                        "key": "last_clone_destination",
                                        "value": "app-lab",
                                    }
                                ]
                            },
                        },
                        {
                            "label": "The lab copy was confirmed clean before experiments.",
                            "requirement": {"required_commands": ["git status"]},
                        },
                    ],
                ),
                _wave(
                    "ch1-adv-clone-branch-then-graph",
                    "git-clone/branch",
                    "Copy a branch and map it",
                    [
                        "git clone -b starter https://example.test/team/app.git",
                        "git log --oneline --graph --all",
                    ],
                    required=["git clone", "git log"],
                    forms=["git-log/graph-all"],
                    state="clone",
                    story=(
                        "You are joining work that lives on the starter branch and want to see how "
                        "it relates to everything else the project contains. Copy the project onto "
                        "that branch, then draw every ref to map where you landed."
                    ),
                    details=[{"label": "Branch to check out", "value": "starter"}],
                    evaluation={
                        "repository_initialized": True,
                        "head_branch": "starter",
                    },
                    checks=[
                        {
                            "label": "The copy checked out the requested branch.",
                            "requirement": {"head_branch": "starter"},
                        },
                        {
                            "label": "The full ref graph was drawn after arriving.",
                            "requirement": {"required_commands": ["git log"]},
                        },
                    ],
                ),
                _wave(
                    "ch1-adv-clone-depth-then-limit",
                    "git-clone/depth",
                    "Shallow copy, shallow read",
                    [
                        "git clone --depth 1 https://example.test/team/app.git",
                        "git log -n 1",
                    ],
                    required=["git clone", "git log"],
                    forms=["git-log/limit"],
                    state="clone",
                    story=(
                        "A quick demo machine needs the team app with the least possible history. "
                        "Copy it one snapshot deep, then read exactly one history entry to confirm "
                        "how little came down."
                    ),
                    details=[{"label": "History depth", "value": "1"}],
                    evaluation={
                        "repository_initialized": True,
                        "rules": [{"type": "commit_count_equals", "count": 1}],
                    },
                    checks=[
                        {
                            "label": "Exactly one snapshot of history is visible.",
                            "requirement": {"rules": [{"type": "commit_count_equals", "count": 1}]},
                        },
                        {
                            "label": "The visible history was confirmed with a limited read.",
                            "requirement": {"required_commands": ["git log"]},
                        },
                    ],
                ),
                _wave(
                    "ch1-adv-clone-then-show",
                    "git-clone/default-folder",
                    "Copy then open the newest snapshot",
                    ["git clone https://example.test/team/app.git", "git show"],
                    required=["git clone", "git show"],
                    forms=["git-show/head"],
                    state="clone",
                    story=(
                        "Before touching a single line of the team app, you want to know what its "
                        "most recent snapshot actually changed. Copy the project down, then open "
                        "that newest snapshot and read it in full."
                    ),
                    evaluation={
                        "repository_initialized": True,
                        "working_tree_clean": True,
                        "staging_empty": True,
                    },
                    checks=[
                        {
                            "label": "A complete local copy exists.",
                            "requirement": {"repository_initialized": True},
                        },
                        {
                            "label": "The newest snapshot was opened and read after copying.",
                            "requirement": {"required_commands": ["git show"]},
                        },
                    ],
                ),
                _wave(
                    "ch1-adv-new-vs-clone",
                    "git-init/named-directory",
                    "Fresh workspace, not a copy",
                    ["git init scratch-pad", "git status"],
                    required=["git init", "git status"],
                    forms=["git-status/plain"],
                    state="uninitialized",
                    story=(
                        "Copying the team app would drag along history this throwaway experiment "
                        "does not need. Create a brand-new workspace under the exact folder name "
                        "shown below instead, then read its state to see what a fresh start looks "
                        "like."
                    ),
                    details=[{"label": "Folder name", "value": "scratch-pad"}],
                    evaluation={
                        "repository_initialized": True,
                        "staging_empty": True,
                        "rules": [
                            {
                                "type": "operation_metadata_equals",
                                "key": "last_init_directory",
                                "value": "scratch-pad",
                            },
                            {"type": "commit_count_equals", "count": 0},
                        ],
                    },
                    checks=[
                        {
                            "label": "A fresh repository exists under the requested folder name.",
                            "requirement": {
                                "rules": [
                                    {
                                        "type": "operation_metadata_equals",
                                        "key": "last_init_directory",
                                        "value": "scratch-pad",
                                    }
                                ]
                            },
                        },
                        {
                            "label": "The fresh state was read; no snapshot exists yet.",
                            "requirement": {
                                "required_commands": ["git status"],
                                "rules": [{"type": "commit_count_equals", "count": 0}],
                            },
                        },
                    ],
                ),
            ],
        },
        {
            "slug": "configure-identity-and-aliases",
            "title": "Configure Identity and Aliases",
            "waves": [
                _wave(
                    "ch1-adv-set-user-name",
                    "git-config/global-user-name",
                    "Set user name",
                    ["git config --global user.name 'Learner A'"],
                    state="clean",
                    story=(
                        "This machine has never had a Git identity configured. Before anything gets "
                        "authored here, set the global author name so every future commit is "
                        "attributed correctly."
                    ),
                    evaluation={
                        "rules": [
                            {"type": "operation_metadata_equals", "key": "last_config_key", "value": "user.name"},
                            {"type": "operation_metadata_equals", "key": "last_config_scope", "value": "global"},
                        ]
                    },
                    checks=[
                        {
                            "label": "The global author name is saved in your config.",
                            "requirement": {
                                "rules": [
                                    {"type": "operation_metadata_equals", "key": "last_config_key", "value": "user.name"},
                                    {"type": "operation_metadata_equals", "key": "last_config_scope", "value": "global"},
                                ]
                            },
                        }
                    ],
                ),
                _wave(
                    "ch1-adv-set-user-email",
                    "git-config/global-user-email",
                    "Set user email",
                    ["git config --global user.email learner-a@example.test"],
                    state="clean",
                    story=(
                        "Author name is set, but the email half of this machine's identity is still "
                        "missing. Set the global author email to complete it."
                    ),
                    evaluation={
                        "rules": [
                            {"type": "operation_metadata_equals", "key": "last_config_key", "value": "user.email"},
                            {"type": "operation_metadata_equals", "key": "last_config_scope", "value": "global"},
                        ]
                    },
                    checks=[
                        {
                            "label": "The global author email is saved in your config.",
                            "requirement": {
                                "rules": [
                                    {"type": "operation_metadata_equals", "key": "last_config_key", "value": "user.email"},
                                    {"type": "operation_metadata_equals", "key": "last_config_scope", "value": "global"},
                                ]
                            },
                        }
                    ],
                ),
                _wave(
                    "ch1-adv-config-list-intro",
                    "git-config/list",
                    "List effective settings",
                    ["git config --list"],
                    state="clean",
                    story=(
                        "Before this machine authors anything, you want to see every setting Git "
                        "will actually apply here: identity, shortcuts, all of it. Read the full "
                        "effective configuration without changing a single value."
                    ),
                    evaluation={
                        "repository_initialized": True,
                        "staging_empty": True,
                        "rules": [{"type": "commit_count_equals", "count": 1}],
                    },
                    checks=[
                        {
                            "label": "The effective configuration was listed and read.",
                            "requirement": {"required_commands": ["git config --list"]},
                        },
                    ],
                ),
                _wave(
                    "ch1-adv-alias-intro",
                    "git-config/alias",
                    "Create a status shortcut",
                    ["git config --global alias.st status"],
                    state="clean",
                    story=(
                        "You check the workspace state constantly, and the full spelling is slowing "
                        "you down. Record a global shortcut named st that expands to the state-"
                        "reading command."
                    ),
                    details=[
                        {"label": "Alias name", "value": "st"},
                        {"label": "Expands to", "value": "status"},
                    ],
                    evaluation={
                        "rules": [
                            {
                                "type": "operation_metadata_equals",
                                "key": "last_config_key",
                                "value": "alias.st",
                            }
                        ]
                    },
                    checks=[
                        {
                            "label": "A global st shortcut is recorded in your configuration.",
                            "requirement": {
                                "rules": [
                                    {
                                        "type": "operation_metadata_equals",
                                        "key": "last_config_key",
                                        "value": "alias.st",
                                    }
                                ]
                            },
                        }
                    ],
                ),
                _wave(
                    "ch1-adv-list-config",
                    "git-config/list",
                    "List config",
                    ["git config --list", "git add README.md", "git commit -m 'Save verified identity'"],
                    required=["git config --list", "git commit"],
                    forms=["git-add/file", "git-commit/message"],
                    state="dirty",
                    story=(
                        "Before this next commit goes out under your name, verify the effective "
                        "configuration actually has the identity you expect, then save the pending "
                        "README edit."
                    ),
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["README.md"],
                            "message_contains": ["Save verified identity"],
                        },
                        "staging_empty": True,
                        "working_tree_clean": True,
                    },
                    checks=[
                        {
                            "label": "The effective configuration was listed and checked before committing.",
                            "requirement": {"required_commands": ["git config --list"]},
                        },
                        {
                            "label": "The verified change is committed on main.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["README.md"],
                                    "message_contains": ["Save verified identity"],
                                }
                            },
                        },
                    ],
                ),
                _wave(
                    "ch1-adv-create-alias",
                    "git-config/alias",
                    "Create alias",
                    [
                        "git config --global alias.st status",
                        "git config --list",
                        "git add README.md",
                        "git commit -m 'Save alias setup'",
                    ],
                    required=["git config --global alias.st", "git config --list", "git commit"],
                    forms=["git-config/list", "git-add/file", "git-commit/message"],
                    state="dirty",
                    story=(
                        "Typing the full status command all day is getting old. Create a global "
                        "alias.st shortcut for it, confirm it is recorded, and then use the normal "
                        "save loop to commit the pending README edit."
                    ),
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["README.md"],
                            "message_contains": ["Save alias setup"],
                        },
                        "staging_empty": True,
                        "working_tree_clean": True,
                        "rules": [
                            {"type": "operation_metadata_equals", "key": "last_config_key", "value": "alias.st"},
                        ],
                    },
                    checks=[
                        {
                            "label": "A global alias.st shortcut is recorded and verified in config.",
                            "requirement": {
                                "rules": [
                                    {"type": "operation_metadata_equals", "key": "last_config_key", "value": "alias.st"},
                                ]
                            },
                        },
                        {
                            "label": "The repository is clean after the normal save loop runs.",
                            "requirement": {"staging_empty": True, "working_tree_clean": True},
                        },
                    ],
                ),
            ],
        },
        {
            "slug": "ignore-noise",
            "title": "Ignore Noise",
            "waves": [
                _wave(
                    "ch1-adv-status-ignored-intro",
                    "git-status/ignored",
                    "See what Git ignores",
                    ["git status --ignored"],
                    state="ignore",
                    story=(
                        "This workspace holds real source work, a rule file, and a generated log "
                        "that should never enter history. Read the state with ignored entries "
                        "included so you can see exactly what Git is deliberately overlooking."
                    ),
                    evaluation={
                        "staging_empty": True,
                        "rules": [{"type": "ignored_paths_present", "paths": ["build.log"]}],
                    },
                    checks=[
                        {
                            "label": "The state was read with ignored entries included.",
                            "requirement": {"required_commands": ["git status --ignored"]},
                        },
                    ],
                ),
                _wave(
                    "ch1-adv-check-ignore-intro",
                    "git-check-ignore/verbose",
                    "Trace an ignore rule",
                    ["git check-ignore -v build.log"],
                    state="ignore",
                    story=(
                        "A teammate asks why build.log never shows up as trackable work. Trace "
                        "exactly which rule file and pattern claim that path, so you can answer "
                        "with evidence instead of a guess."
                    ),
                    details=[{"label": "Path to trace", "value": "build.log"}],
                    evaluation={
                        "staging_empty": True,
                        "rules": [{"type": "ignored_paths_present", "paths": ["build.log"]}],
                    },
                    checks=[
                        {
                            "label": "The matching rule was traced for the ignored path.",
                            "requirement": {"required_commands": ["git check-ignore"]},
                        },
                    ],
                ),
                _wave(
                    "ch1-adv-write-ignore-rule",
                    "git-status/ignored",
                    "Write ignore rule",
                    ["git status --ignored", "git add .gitignore src/app.py", "git commit -m 'Ignore build output'"],
                    required=["git status --ignored", "git add", "git commit"],
                    forms=["git-add/file", "git-commit/message"],
                    state="ignore",
                    story=(
                        "A generated build.log sits beside a real source edit in src/app.py, and a new "
                        ".gitignore rule already exists to keep build output out. Confirm the ignored "
                        "file with status --ignored, then commit only the ignore rule and the source "
                        "edit."
                    ),
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": [".gitignore", "src/app.py"],
                            "excludes_paths": ["build.log"],
                            "message_contains": ["Ignore build output"],
                        },
                        "staging_empty": True,
                        "working_tree_clean": True,
                        "rules": [{"type": "ignored_paths_present", "paths": ["build.log"]}],
                    },
                    checks=[
                        {
                            "label": "The build output was confirmed as ignored noise, not real work.",
                            "requirement": {"required_commands": ["git status --ignored"]},
                        },
                        {
                            "label": "The ignore rule and the source edit are committed together.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": [".gitignore", "src/app.py"],
                                    "message_contains": ["Ignore build output"],
                                }
                            },
                        },
                    ],
                ),
                _wave(
                    "ch1-adv-explain-ignore-rule",
                    "git-check-ignore/verbose",
                    "Explain ignore rule",
                    ["git check-ignore -v build.log", "git add src/app.py", "git commit -m 'Save source without build log'"],
                    required=["git check-ignore -v", "git commit"],
                    forms=["git-add/file", "git-commit/message"],
                    state="ignore",
                    story=(
                        "A teammate asks exactly which rule is keeping build.log out of history. Trace "
                        "the matching .gitignore pattern with check-ignore -v, then save the real "
                        "source edit without dragging the generated file along."
                    ),
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["src/app.py"],
                            "excludes_paths": ["build.log", ".gitignore"],
                            "message_contains": ["Save source without build log"],
                        },
                        "staging_empty": True,
                    },
                    checks=[
                        {
                            "label": "The matching ignore rule was traced with check-ignore -v.",
                            "requirement": {"required_commands": ["git check-ignore -v"]},
                        },
                        {
                            "label": "Only the source edit is committed; the generated file is not.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["src/app.py"],
                                    "excludes_paths": ["build.log"],
                                    "message_contains": ["Save source without build log"],
                                }
                            },
                        },
                    ],
                ),
            ],
        },
        {
            "slug": "founding-workflows",
            "title": "Founding Workflows",
            "waves": [
                _wave(
                    "ch1-adv-new-project-identity",
                    "git-init/current-directory",
                    "Found a project with identity",
                    [
                        "git init",
                        "git config --global user.name 'Learner A'",
                        "git config --global user.email learner-a@example.test",
                        "git add .",
                        "git commit -m 'Initial commit'",
                    ],
                    required=["git init", "git config", "git add", "git commit"],
                    forms=[
                        "git-config/global-user-name",
                        "git-config/global-user-email",
                        "git-add/dot",
                        "git-commit/message",
                    ],
                    state="uninitialized",
                    story=(
                        "A brand-new machine, a brand-new project: nothing is tracked and no author "
                        "identity exists yet. Stand the repository up, record the author name and "
                        "email shown below, and land every starter file in a first snapshot that is "
                        "attributed correctly."
                    ),
                    details=[
                        {"label": "Author name", "value": "Learner A"},
                        {"label": "Author email", "value": "learner-a@example.test"},
                        {"label": "Commit message", "value": "Initial commit"},
                    ],
                    evaluation={
                        "repository_initialized": True,
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["README.md", "src/app.py"],
                            "message_contains": ["Initial commit"],
                        },
                        "working_tree_clean": True,
                        "staging_empty": True,
                        "rules": [
                            {
                                "type": "operation_metadata_equals",
                                "key": "last_config_key",
                                "value": "user.email",
                            }
                        ],
                    },
                    checks=[
                        {
                            "label": "The folder is a repository with both identity halves recorded.",
                            "requirement": {
                                "repository_initialized": True,
                                "rules": [
                                    {
                                        "type": "operation_metadata_equals",
                                        "key": "last_config_key",
                                        "value": "user.email",
                                    }
                                ],
                            },
                        },
                        {
                            "label": "Every starter file landed in the first snapshot.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["README.md", "src/app.py"],
                                    "message_contains": ["Initial commit"],
                                }
                            },
                        },
                        {
                            "label": "Nothing is left staged or unstaged afterward.",
                            "requirement": {"working_tree_clean": True, "staging_empty": True},
                        },
                    ],
                ),
                _wave(
                    "ch1-adv-init-status-save",
                    "git-init/current-directory",
                    "Initialize, inspect, save, verify",
                    [
                        "git init",
                        "git status",
                        "git add .",
                        "git commit -m 'First snapshot'",
                        "git log --oneline",
                    ],
                    required=["git init", "git status", "git add", "git commit", "git log"],
                    forms=["git-status/plain", "git-add/dot", "git-commit/message", "git-log/oneline"],
                    state="uninitialized",
                    story=(
                        "This starter folder is about to become the project of record, and you want "
                        "the full founding routine done properly: create the repository, read what "
                        "it sees, save everything as the first snapshot, and verify it in history."
                    ),
                    details=[{"label": "Commit message", "value": "First snapshot"}],
                    evaluation={
                        "repository_initialized": True,
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["README.md", "src/app.py"],
                            "message_contains": ["First snapshot"],
                        },
                        "working_tree_clean": True,
                        "staging_empty": True,
                        "rules": [{"type": "commit_count_equals", "count": 1}],
                    },
                    checks=[
                        {
                            "label": "The fresh repository state was read before saving.",
                            "requirement": {"required_commands": ["git status"]},
                        },
                        {
                            "label": "Every starter file landed in the first snapshot.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["README.md", "src/app.py"],
                                    "message_contains": ["First snapshot"],
                                }
                            },
                        },
                        {
                            "label": "The snapshot was verified against history afterward.",
                            "requirement": {"required_commands": ["git log"]},
                        },
                    ],
                ),
                _wave(
                    "ch1-adv-named-project-save",
                    "git-init/named-directory",
                    "Found a studio workspace",
                    [
                        "git init studio",
                        "git status",
                        "git add .",
                        "git commit -m 'Studio setup'",
                    ],
                    required=["git init", "git status", "git add", "git commit"],
                    forms=["git-status/plain", "git-add/dot", "git-commit/message"],
                    state="uninitialized",
                    story=(
                        "The design team's new workspace must live under the exact folder name "
                        "shown below. Create it, read what the fresh repository sees, and save the "
                        "starter files as its first snapshot."
                    ),
                    details=[
                        {"label": "Folder name", "value": "studio"},
                        {"label": "Commit message", "value": "Studio setup"},
                    ],
                    evaluation={
                        "repository_initialized": True,
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["README.md", "src/app.py"],
                            "message_contains": ["Studio setup"],
                        },
                        "working_tree_clean": True,
                        "rules": [
                            {
                                "type": "operation_metadata_equals",
                                "key": "last_init_directory",
                                "value": "studio",
                            }
                        ],
                    },
                    checks=[
                        {
                            "label": "The workspace was created under the requested folder name.",
                            "requirement": {
                                "rules": [
                                    {
                                        "type": "operation_metadata_equals",
                                        "key": "last_init_directory",
                                        "value": "studio",
                                    }
                                ]
                            },
                        },
                        {
                            "label": "The starter files are saved in the first snapshot.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["README.md", "src/app.py"],
                                    "message_contains": ["Studio setup"],
                                }
                            },
                        },
                    ],
                ),
                _wave(
                    "ch1-adv-review-then-save",
                    "git-diff/working",
                    "Review every angle, then save",
                    [
                        "git status",
                        "git diff",
                        "git add README.md",
                        "git diff --staged",
                        "git commit -m 'Save reviewed work'",
                    ],
                    required=["git status", "git diff", "git add", "git diff --staged", "git commit"],
                    forms=["git-status/plain", "git-add/file", "git-diff/staged", "git-commit/message"],
                    state="mixed",
                    story=(
                        "One tracked edit is ready to ship while a loose scratch file must stay "
                        "local. Read the overall state, review the unstaged lines, stage only the "
                        "real work, re-check what is about to be saved, and then seal the snapshot."
                    ),
                    details=[{"label": "Commit message", "value": "Save reviewed work"}],
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["README.md"],
                            "excludes_paths": ["scratch.txt"],
                            "message_contains": ["Save reviewed work"],
                        },
                        "staging_empty": True,
                        "rules": [{"type": "commit_count_equals", "count": 2}],
                    },
                    checks=[
                        {
                            "label": "The work was reviewed before and after staging.",
                            "requirement": {"required_commands": ["git diff", "git diff --staged"]},
                        },
                        {
                            "label": "Only the real edit was committed; the scratch file stayed local.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["README.md"],
                                    "excludes_paths": ["scratch.txt"],
                                    "message_contains": ["Save reviewed work"],
                                }
                            },
                        },
                    ],
                ),
                _wave(
                    "ch1-adv-two-snapshots",
                    "git-add/file",
                    "Build history in two snapshots",
                    [
                        "git init",
                        "git add README.md",
                        "git commit -m 'Add readme'",
                        "git add .",
                        "git commit -m 'Add source'",
                        "git log --oneline",
                    ],
                    required=["git init", "git add", "git commit", "git log"],
                    forms=[
                        "git-init/current-directory",
                        "git-commit/message",
                        "git-add/dot",
                        "git-log/oneline",
                    ],
                    state="uninitialized",
                    story=(
                        "This new project's history should tell a story: first the introduction, "
                        "then the source. Stand the repository up, save the readme by itself, save "
                        "the remaining work as a second snapshot, and read the history you built."
                    ),
                    details=[
                        {"label": "First message", "value": "Add readme"},
                        {"label": "Second message", "value": "Add source"},
                    ],
                    evaluation={
                        "repository_initialized": True,
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["src/app.py"],
                            "message_contains": ["Add source"],
                        },
                        "working_tree_clean": True,
                        "staging_empty": True,
                        "rules": [{"type": "commit_count_equals", "count": 2}],
                    },
                    checks=[
                        {
                            "label": "History holds exactly two snapshots, in story order.",
                            "requirement": {"rules": [{"type": "commit_count_equals", "count": 2}]},
                        },
                        {
                            "label": "The second snapshot carries the source work.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["src/app.py"],
                                    "message_contains": ["Add source"],
                                }
                            },
                        },
                        {
                            "label": "The built history was read back afterward.",
                            "requirement": {"required_commands": ["git log"]},
                        },
                    ],
                ),
                _wave(
                    "ch1-adv-ignore-from-scratch",
                    "git-status/ignored",
                    "Adopt ignore rules end to end",
                    [
                        "git status --ignored",
                        "git check-ignore -v build.log",
                        "git add .gitignore src/app.py",
                        "git commit -m 'Adopt ignore rules'",
                    ],
                    required=["git status --ignored", "git check-ignore", "git add", "git commit"],
                    forms=["git-check-ignore/verbose", "git-add/file", "git-commit/message"],
                    state="ignore",
                    story=(
                        "Generated output keeps photobombing this workspace next to real source "
                        "work. Confirm what is being overlooked and why, then commit the rule file "
                        "and the source edit together while the generated file stays out of history."
                    ),
                    details=[{"label": "Commit message", "value": "Adopt ignore rules"}],
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": [".gitignore", "src/app.py"],
                            "excludes_paths": ["build.log"],
                            "message_contains": ["Adopt ignore rules"],
                        },
                        "staging_empty": True,
                        "rules": [{"type": "ignored_paths_present", "paths": ["build.log"]}],
                    },
                    checks=[
                        {
                            "label": "The ignored path and its matching rule were both confirmed.",
                            "requirement": {
                                "required_commands": ["git status --ignored", "git check-ignore"]
                            },
                        },
                        {
                            "label": "The rule and the source edit are committed; the noise is not.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": [".gitignore", "src/app.py"],
                                    "excludes_paths": ["build.log"],
                                    "message_contains": ["Adopt ignore rules"],
                                }
                            },
                        },
                    ],
                ),
            ],
        },
        {
            "slug": "fresh-start-drills",
            "title": "Fresh Start Drills",
            "waves": [
                _wave(
                    "ch1-adv-init-named-archive",
                    "git-init/named-directory",
                    "Create an archive workspace",
                    ["git init archive-lab", "git status -s"],
                    required=["git init", "git status"],
                    forms=["git-status/short"],
                    state="uninitialized",
                    story=(
                        "Last quarter's experiment files need a home of their own before cleanup "
                        "week. Create a repository under the exact folder name shown below, then "
                        "take a compact glance at what the fresh workspace sees."
                    ),
                    details=[{"label": "Folder name", "value": "archive-lab"}],
                    evaluation={
                        "repository_initialized": True,
                        "staging_empty": True,
                        "rules": [
                            {
                                "type": "operation_metadata_equals",
                                "key": "last_init_directory",
                                "value": "archive-lab",
                            },
                            {"type": "commit_count_equals", "count": 0},
                        ],
                    },
                    checks=[
                        {
                            "label": "The archive repository exists under the requested name.",
                            "requirement": {
                                "rules": [
                                    {
                                        "type": "operation_metadata_equals",
                                        "key": "last_init_directory",
                                        "value": "archive-lab",
                                    }
                                ]
                            },
                        },
                        {
                            "label": "The fresh state was read; nothing is saved yet.",
                            "requirement": {
                                "required_commands": ["git status -s"],
                                "rules": [{"type": "commit_count_equals", "count": 0}],
                            },
                        },
                    ],
                ),
                _wave(
                    "ch1-adv-init-named-notes",
                    "git-init/named-directory",
                    "Found a field-notes workspace",
                    ["git init field-notes", "git add .", "git commit -m 'Field notes start'"],
                    required=["git init", "git add", "git commit"],
                    forms=["git-add/dot", "git-commit/message"],
                    state="uninitialized",
                    story=(
                        "A research trip starts tomorrow and its notes deserve a dedicated, named "
                        "workspace with the starter material already saved. Create the folder shown "
                        "below as a repository and land everything in its first snapshot."
                    ),
                    details=[
                        {"label": "Folder name", "value": "field-notes"},
                        {"label": "Commit message", "value": "Field notes start"},
                    ],
                    evaluation={
                        "repository_initialized": True,
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["README.md", "src/app.py"],
                            "message_contains": ["Field notes start"],
                        },
                        "working_tree_clean": True,
                        "rules": [
                            {
                                "type": "operation_metadata_equals",
                                "key": "last_init_directory",
                                "value": "field-notes",
                            }
                        ],
                    },
                    checks=[
                        {
                            "label": "The notes repository exists under the requested name.",
                            "requirement": {
                                "rules": [
                                    {
                                        "type": "operation_metadata_equals",
                                        "key": "last_init_directory",
                                        "value": "field-notes",
                                    }
                                ]
                            },
                        },
                        {
                            "label": "The starter material is saved in the first snapshot.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["README.md", "src/app.py"],
                                    "message_contains": ["Field notes start"],
                                }
                            },
                        },
                    ],
                ),
                _wave(
                    "ch1-adv-init-release-branch",
                    "git-init/initial-branch",
                    "Begin on the release line",
                    ["git init -b release", "git status"],
                    required=["git init", "git status"],
                    forms=["git-status/plain"],
                    state="uninitialized",
                    story=(
                        "This deployment project tracks everything on a line named release from day "
                        "one. Initialize the folder so its first branch carries that exact name, "
                        "then read the fresh state to confirm where you stand."
                    ),
                    details=[{"label": "First branch name", "value": "release"}],
                    evaluation={
                        "repository_initialized": True,
                        "head_branch": "release",
                        "rules": [
                            {
                                "type": "operation_metadata_equals",
                                "key": "last_init_initial_branch",
                                "value": "release",
                            }
                        ],
                    },
                    checks=[
                        {
                            "label": "The first branch carries the requested name.",
                            "requirement": {"head_branch": "release"},
                        },
                        {
                            "label": "The fresh state was read after initializing.",
                            "requirement": {"required_commands": ["git status"]},
                        },
                    ],
                ),
                _wave(
                    "ch1-adv-init-docs-main",
                    "git-init/initial-branch",
                    "Docs history on its own line",
                    ["git init -b docs-main", "git add .", "git commit -m 'Docs baseline'"],
                    required=["git init", "git add", "git commit"],
                    forms=["git-add/dot", "git-commit/message"],
                    state="uninitialized",
                    story=(
                        "The documentation archive keeps its history on a line named docs-main, "
                        "separate from application code conventions. Start the repository on that "
                        "exact line and save the starter files as its baseline snapshot."
                    ),
                    details=[
                        {"label": "First branch name", "value": "docs-main"},
                        {"label": "Commit message", "value": "Docs baseline"},
                    ],
                    evaluation={
                        "repository_initialized": True,
                        "head_branch": "docs-main",
                        "latest_commit": {
                            "branch": "docs-main",
                            "contains_paths": ["README.md", "src/app.py"],
                            "message_contains": ["Docs baseline"],
                        },
                        "working_tree_clean": True,
                        "staging_empty": True,
                    },
                    checks=[
                        {
                            "label": "History began on the requested docs line.",
                            "requirement": {"head_branch": "docs-main"},
                        },
                        {
                            "label": "The baseline snapshot landed on that line.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "docs-main",
                                    "contains_paths": ["README.md", "src/app.py"],
                                    "message_contains": ["Docs baseline"],
                                }
                            },
                        },
                    ],
                ),
                _wave(
                    "ch1-adv-clone-branch-refresh",
                    "git-clone/branch",
                    "Branch copy, compact check",
                    [
                        "git clone -b starter https://example.test/team/app.git",
                        "git status -s",
                    ],
                    required=["git clone", "git status"],
                    forms=["git-status/short"],
                    state="clone",
                    story=(
                        "A fresh session on the training material: bring the project down already "
                        "checked out on its starter branch, then take one compact glance to confirm "
                        "the copy is clean."
                    ),
                    details=[{"label": "Branch to check out", "value": "starter"}],
                    evaluation={
                        "repository_initialized": True,
                        "head_branch": "starter",
                        "working_tree_clean": True,
                        "staging_empty": True,
                    },
                    checks=[
                        {
                            "label": "The copy checked out the requested branch.",
                            "requirement": {"head_branch": "starter"},
                        },
                        {
                            "label": "The copy was confirmed clean with a compact glance.",
                            "requirement": {"required_commands": ["git status -s"]},
                        },
                    ],
                ),
                _wave(
                    "ch1-adv-clone-depth-refresh",
                    "git-clone/depth",
                    "Shallow copy, open the tip",
                    [
                        "git clone --depth 1 https://example.test/team/app.git",
                        "git show",
                    ],
                    required=["git clone", "git show"],
                    forms=["git-show/head"],
                    state="clone",
                    story=(
                        "A workshop laptop needs the team app with only its current snapshot. Copy "
                        "it one snapshot deep, then open that lone snapshot to see exactly what "
                        "state the workshop starts from."
                    ),
                    details=[{"label": "History depth", "value": "1"}],
                    evaluation={
                        "repository_initialized": True,
                        "rules": [{"type": "commit_count_equals", "count": 1}],
                    },
                    checks=[
                        {
                            "label": "Exactly one snapshot of history came down.",
                            "requirement": {"rules": [{"type": "commit_count_equals", "count": 1}]},
                        },
                        {
                            "label": "The lone snapshot was opened and read.",
                            "requirement": {"required_commands": ["git show"]},
                        },
                    ],
                ),
            ],
        },
        {
            "slug": "inspection-drills",
            "title": "Inspection Drills",
            "waves": [
                _wave(
                    "ch1-adv-porcelain-staged",
                    "git-status/porcelain",
                    "Script check mid-snapshot",
                    ["git status --porcelain"],
                    state="staged",
                    story=(
                        "A release script runs while a README.md change is already staged and "
                        "waiting. Read the workspace in the stable script-friendly form to see how "
                        "a half-built snapshot reports itself, and touch nothing."
                    ),
                    evaluation={
                        "staging_not_empty": True,
                        "rules": [
                            {"type": "staging_contains", "path": "README.md"},
                            {"type": "commit_count_equals", "count": 1},
                        ],
                    },
                    checks=[
                        {
                            "label": "The half-built snapshot was read in script-stable form.",
                            "requirement": {"required_commands": ["git status --porcelain"]},
                        },
                    ],
                ),
                _wave(
                    "ch1-adv-identity-fresh-machine",
                    "git-config/global-user-name",
                    "Set up a fresh machine",
                    [
                        "git config --global user.name 'Learner C'",
                        "git config --global user.email learner-c@example.test",
                        "git config --list",
                    ],
                    required=["git config --global user.name", "git config --global user.email", "git config --list"],
                    forms=["git-config/global-user-email", "git-config/list"],
                    state="clean",
                    story=(
                        "A loaner laptop has no idea who you are, and nothing should be authored "
                        "from it until it does. Record both halves of the identity shown below, "
                        "then list the effective settings to confirm the machine is ready."
                    ),
                    details=[
                        {"label": "Author name", "value": "Learner C"},
                        {"label": "Author email", "value": "learner-c@example.test"},
                    ],
                    evaluation={
                        "rules": [
                            {
                                "type": "operation_metadata_equals",
                                "key": "last_config_key",
                                "value": "user.email",
                            },
                            {
                                "type": "operation_metadata_equals",
                                "key": "last_config_scope",
                                "value": "global",
                            },
                        ]
                    },
                    checks=[
                        {
                            "label": "Both halves of the identity are recorded globally.",
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
                            "label": "The effective settings were listed to confirm readiness.",
                            "requirement": {"required_commands": ["git config --list"]},
                        },
                    ],
                ),
                _wave(
                    "ch1-adv-alias-shortlog",
                    "git-config/alias",
                    "Create a history shortcut",
                    ["git config --global alias.lg log", "git config --list"],
                    required=["git config --global alias.lg", "git config --list"],
                    forms=["git-config/list"],
                    state="clean",
                    story=(
                        "You read project history more than any other output, so it deserves its "
                        "own shortcut. Record a global shortcut named lg for the history command, "
                        "then list the settings to confirm it stuck."
                    ),
                    details=[
                        {"label": "Alias name", "value": "lg"},
                        {"label": "Expands to", "value": "log"},
                    ],
                    evaluation={
                        "rules": [
                            {
                                "type": "operation_metadata_equals",
                                "key": "last_config_key",
                                "value": "alias.lg",
                            }
                        ]
                    },
                    checks=[
                        {
                            "label": "A global lg shortcut is recorded in your configuration.",
                            "requirement": {
                                "rules": [
                                    {
                                        "type": "operation_metadata_equals",
                                        "key": "last_config_key",
                                        "value": "alias.lg",
                                    }
                                ]
                            },
                        },
                        {
                            "label": "The recorded shortcut was confirmed in the listed settings.",
                            "requirement": {"required_commands": ["git config --list"]},
                        },
                    ],
                ),
                _wave(
                    "ch1-adv-show-second-commit",
                    "git-show/commit",
                    "Describe the latest change",
                    ["git show c1", "git add CHANGELOG.md", "git commit -m 'Describe latest change'"],
                    required=["git show", "git add", "git commit"],
                    forms=["git-add/file", "git-commit/message"],
                    state="show-note",
                    story=(
                        "The changelog draft needs an accurate description of the most recent "
                        "snapshot, referenced by its exact name. Open that named snapshot, read "
                        "what it changed, then save the finished changelog entry."
                    ),
                    details=[
                        {"label": "Commit to inspect", "value": "c1"},
                        {"label": "Commit message", "value": "Describe latest change"},
                    ],
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["CHANGELOG.md"],
                            "message_contains": ["Describe latest change"],
                        },
                        "staging_empty": True,
                        "working_tree_clean": True,
                        "rules": [{"type": "commit_count_equals", "count": 3}],
                    },
                    checks=[
                        {
                            "label": "The named snapshot was opened and read first.",
                            "requirement": {"required_commands": ["git show"]},
                        },
                        {
                            "label": "The changelog entry is committed on main.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["CHANGELOG.md"],
                                    "message_contains": ["Describe latest change"],
                                }
                            },
                        },
                    ],
                ),
                _wave(
                    "ch1-adv-patch-review-note",
                    "git-log/patch",
                    "Patch review, then a note",
                    ["git log -p", "git add REVIEW.md", "git commit -m 'Record patch review'"],
                    required=["git log -p", "git add", "git commit"],
                    forms=["git-add/file", "git-commit/message"],
                    state="history-note",
                    story=(
                        "A review note, REVIEW.md, should summarize every line this project's "
                        "history has changed so far. Walk the history with full patch text to "
                        "gather the facts, then save the finished note as the next snapshot."
                    ),
                    details=[{"label": "Commit message", "value": "Record patch review"}],
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["REVIEW.md"],
                            "message_contains": ["Record patch review"],
                        },
                        "staging_empty": True,
                        "working_tree_clean": True,
                        "rules": [{"type": "commit_count_equals", "count": 3}],
                    },
                    checks=[
                        {
                            "label": "History was walked with full patch detail first.",
                            "requirement": {"required_commands": ["git log -p"]},
                        },
                        {
                            "label": "The review note is committed on main.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["REVIEW.md"],
                                    "message_contains": ["Record patch review"],
                                }
                            },
                        },
                    ],
                ),
                _wave(
                    "ch1-adv-name-only-audit",
                    "git-show/name-only",
                    "Path audit, then a note",
                    [
                        "git show --name-only c0",
                        "git add AUDIT.md",
                        "git commit -m 'List first commit paths'",
                    ],
                    required=["git show --name-only", "git add", "git commit"],
                    forms=["git-add/file", "git-commit/message"],
                    state="audit-note",
                    story=(
                        "The audit sheet's last blank is the list of paths the project's very first "
                        "snapshot touched. Read exactly that list from the named snapshot, complete "
                        "AUDIT.md, and save it."
                    ),
                    details=[
                        {"label": "Commit to inspect", "value": "c0"},
                        {"label": "Commit message", "value": "List first commit paths"},
                    ],
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["AUDIT.md"],
                            "message_contains": ["List first commit paths"],
                        },
                        "staging_empty": True,
                        "working_tree_clean": True,
                        "rules": [{"type": "commit_count_equals", "count": 4}],
                    },
                    checks=[
                        {
                            "label": "Only the touched paths were read from the named snapshot.",
                            "requirement": {"required_commands": ["git show --name-only"]},
                        },
                        {
                            "label": "The completed audit note is committed on main.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["AUDIT.md"],
                                    "message_contains": ["List first commit paths"],
                                }
                            },
                        },
                    ],
                ),
            ],
        },
    ]
