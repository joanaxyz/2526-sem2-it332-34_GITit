"""Repository Foundations levels for fresh start drills."""

from __future__ import annotations

from ..helpers import _wave

LEVELS = [
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
    ]
