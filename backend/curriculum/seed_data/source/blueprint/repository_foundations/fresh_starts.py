"""Repository Foundations levels for fresh starts."""

from __future__ import annotations

from ..helpers import _wave

LEVELS = [
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
    ]
