"""Repository Foundations levels for cloning."""

from __future__ import annotations

from ..helpers import _wave

LEVELS = [
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
    ]
