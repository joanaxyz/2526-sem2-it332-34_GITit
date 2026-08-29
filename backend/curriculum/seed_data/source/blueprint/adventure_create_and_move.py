"""Blueprint adventure levels for create-and-move."""

from __future__ import annotations

from .helpers import _wave

ADVENTURE_LEVELS = [
        {
            "slug": "create-and-inspect-branches",
            "title": "Create and Inspect Branches",
            "waves": [
                _wave(
                    "ch3-adv-list-branches",
                    "git-branch/list",
                    "List branches",
                    ["git branch"],
                    state="branch",
                    story=(
                        "Before touching anything, find out exactly which branches already exist in "
                        "this small graph of main, feature/ui, old, and scratch. List them without "
                        "creating, moving, or deleting a single pointer."
                    ),
                    evaluation={"rules": [{"type": "commit_count_equals", "count": 3}]},
                    checks=[
                        {
                            "label": "The branch list was read without changing anything.",
                            "requirement": {"required_commands": ["git branch"]},
                        },
                    ],
                ),
                _wave(
                    "ch3-adv-create-branch",
                    "git-branch/create",
                    "Create branch",
                    ["git branch release"],
                    state="branch",
                    story=(
                        "A new line of work needs its own name, but nobody should switch onto it yet. "
                        "Create a release branch pointer at the current commit without moving HEAD off "
                        "main."
                    ),
                    evaluation={"head_branch": "main", "rules": [{"type": "branch_exists", "branch": "release"}]},
                    checks=[
                        {
                            "label": "The new branch exists, pointing at the current commit, and HEAD never left main.",
                            "requirement": {
                                "head_branch": "main",
                                "rules": [{"type": "branch_exists", "branch": "release"}],
                            },
                        },
                    ],
                ),
                _wave(
                    "ch3-adv-create-branch-at-start",
                    "git-branch/create-at-start",
                    "Create branch at start",
                    ["git branch hotfix c0"],
                    state="branch",
                    story=(
                        "A hotfix needs to branch from the old release commit c0, not from wherever "
                        "main currently sits. Create the hotfix branch pointing exactly at that earlier "
                        "commit."
                    ),
                    evaluation={"rules": [{"type": "branch_points_to", "branch": "hotfix", "commit": "c0"}]},
                    checks=[
                        {
                            "label": "The hotfix branch points at the requested start commit, not the current tip.",
                            "requirement": {
                                "rules": [{"type": "branch_points_to", "branch": "hotfix", "commit": "c0"}]
                            },
                        },
                    ],
                ),
                _wave(
                    "ch3-adv-verbose-branches",
                    "git-branch/verbose",
                    "Verbose branches",
                    ["git branch -v"],
                    state="branch",
                    story=(
                        "Before deciding where to work next, compare every branch tip at a glance - not "
                        "just the names. Read the verbose branch listing to see each tip commit."
                    ),
                    evaluation={"rules": [{"type": "commit_count_equals", "count": 3}]},
                    checks=[
                        {
                            "label": "Every branch tip was compared with the verbose listing.",
                            "requirement": {"required_commands": ["git branch -v"]},
                        },
                    ],
                ),
                _wave(
                    "ch3-adv-list-then-create",
                    "git-branch/create",
                    "Survey, then add a pointer",
                    ["git branch", "git branch feature/audit"],
                    required=["git branch"],
                    forms=["git-branch/list"],
                    state="branch",
                    story=(
                        "Before adding yet another line of work, survey the pointers that already "
                        "exist. Then create feature/audit at the current commit, leaving HEAD "
                        "exactly where it is."
                    ),
                    details=[{"label": "New branch", "value": "feature/audit"}],
                    evaluation={
                        "head_branch": "main",
                        "rules": [{"type": "branch_exists", "branch": "feature/audit"}],
                    },
                    checks=[
                        {
                            "label": "The new pointer exists and HEAD never moved.",
                            "requirement": {
                                "head_branch": "main",
                                "rules": [{"type": "branch_exists", "branch": "feature/audit"}],
                            },
                        },
                    ],
                ),
                _wave(
                    "ch3-adv-verbose-then-pin",
                    "git-branch/create-at-start",
                    "Compare tips, pin the archive",
                    ["git branch -v", "git branch archive c1"],
                    required=["git branch -v", "git branch"],
                    forms=["git-branch/verbose"],
                    state="branch",
                    story=(
                        "An archive pointer must mark the older commit c1 permanently. Compare "
                        "every branch tip first so you pin the right spot, then create the archive "
                        "branch exactly there."
                    ),
                    details=[{"label": "Archive target", "value": "c1"}],
                    evaluation={
                        "rules": [{"type": "branch_points_to", "branch": "archive", "commit": "c1"}],
                    },
                    checks=[
                        {
                            "label": "Branch tips were compared before pinning.",
                            "requirement": {"required_commands": ["git branch -v"]},
                        },
                        {
                            "label": "The archive pointer marks the requested commit.",
                            "requirement": {
                                "rules": [{"type": "branch_points_to", "branch": "archive", "commit": "c1"}]
                            },
                        },
                    ],
                ),
            ],
        },
        {
            "slug": "move-head",
            "title": "Move HEAD",
            "waves": [
                _wave(
                    "ch3-adv-switch-existing-intro",
                    "git-switch/existing",
                    "Step onto another branch",
                    ["git switch feature/ui"],
                    state="branch",
                    story=(
                        "The next task lives on the existing feature/ui line, not on main. Move "
                        "HEAD onto that branch and nothing more - no commits, no new pointers."
                    ),
                    evaluation={"head_branch": "feature/ui"},
                    checks=[
                        {
                            "label": "HEAD now points at the existing feature branch.",
                            "requirement": {"head_branch": "feature/ui"},
                        },
                    ],
                ),
                _wave(
                    "ch3-adv-switch-create-intro",
                    "git-switch/create",
                    "Create and step on in one move",
                    ["git switch -c feature/new"],
                    state="branch",
                    story=(
                        "A brand-new piece of work deserves a brand-new line. Create feature/new "
                        "and move onto it in a single step, leaving every existing pointer where "
                        "it was."
                    ),
                    details=[{"label": "New branch", "value": "feature/new"}],
                    evaluation={
                        "head_branch": "feature/new",
                        "rules": [{"type": "branch_exists", "branch": "feature/new"}],
                    },
                    checks=[
                        {
                            "label": "The new branch exists and HEAD stepped onto it.",
                            "requirement": {
                                "head_branch": "feature/new",
                                "rules": [{"type": "branch_exists", "branch": "feature/new"}],
                            },
                        },
                    ],
                ),
                _wave(
                    "ch3-adv-checkout-legacy-intro",
                    "git-checkout/legacy-create",
                    "The older create-and-switch spelling",
                    ["git checkout -b legacy/feature"],
                    required=["git checkout -b"],
                    state="branch",
                    story=(
                        "Half the tutorials online still teach the older spelling for creating "
                        "and stepping onto a branch at once. Use it once yourself so it never "
                        "confuses you: create legacy/feature the old way."
                    ),
                    details=[{"label": "New branch", "value": "legacy/feature"}],
                    evaluation={
                        "head_branch": "legacy/feature",
                        "rules": [{"type": "branch_exists", "branch": "legacy/feature"}],
                    },
                    checks=[
                        {
                            "label": "The branch was created and checked out with the legacy spelling.",
                            "requirement": {"head_branch": "legacy/feature"},
                        },
                    ],
                ),
                _wave(
                    "ch3-adv-inspect-detached",
                    "git-switch/detach",
                    "Inspect detached",
                    ["git switch --detach c0"],
                    state="branch",
                    story=(
                        "Before trusting a rumor about what the old commit c0 contained, look at it "
                        "directly. Move HEAD there without moving any branch pointer."
                    ),
                    evaluation={"rules": [{"type": "head_detached_at", "commit": "c0"}]},
                    checks=[
                        {
                            "label": "HEAD is detached directly at the old commit; no branch pointer moved.",
                            "requirement": {"rules": [{"type": "head_detached_at", "commit": "c0"}]},
                        },
                    ],
                ),
            ],
        },
        {
            "slug": "move-head-safely",
            "title": "Move HEAD Safely",
            "waves": [
                _wave(
                    "ch3-adv-switch-existing",
                    "git-switch/existing",
                    "Switch existing",
                    ["git switch feature/ui", "git add README.md", "git commit -m 'Work on feature'"],
                    required=["git switch", "git commit"],
                    forms=["git-add/file", "git-commit/message"],
                    state="branch-dirty",
                    story=(
                        "feature/ui already exists, and a pending README edit belongs there, not on "
                        "main. Move onto the existing branch, then commit the edit on it."
                    ),
                    evaluation={
                        "head_branch": "feature/ui",
                        "latest_commit": {
                            "branch": "feature/ui",
                            "contains_paths": ["README.md"],
                            "message_contains": ["Work on feature"],
                        },
                        "rules": [{"type": "branch_points_to", "branch": "main", "commit": "c2"}],
                    },
                    checks=[
                        {
                            "label": "HEAD moved onto the existing feature/ui branch.",
                            "requirement": {"head_branch": "feature/ui"},
                        },
                        {
                            "label": "The edit advanced feature/ui by one commit, leaving main untouched.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "feature/ui",
                                    "contains_paths": ["README.md"],
                                    "message_contains": ["Work on feature"],
                                },
                                "rules": [{"type": "branch_points_to", "branch": "main", "commit": "c2"}],
                            },
                        },
                    ],
                ),
                _wave(
                    "ch3-adv-switch-create",
                    "git-switch/create",
                    "Switch create",
                    ["git switch -c feature/new", "git add README.md", "git commit -m 'Start new feature'"],
                    required=["git switch -c", "git commit"],
                    forms=["git-add/file", "git-commit/message"],
                    state="dirty",
                    story=(
                        "A brand-new feature needs its own branch from scratch. Create and switch onto "
                        "feature/new in one move, then commit the isolated work there instead of on "
                        "main."
                    ),
                    evaluation={
                        "head_branch": "feature/new",
                        "latest_commit": {
                            "branch": "feature/new",
                            "contains_paths": ["README.md"],
                            "message_contains": ["Start new feature"],
                        },
                        "rules": [{"type": "branch_points_to", "branch": "main", "commit": "c0"}],
                    },
                    checks=[
                        {
                            "label": "A brand-new feature/new branch was created and switched onto.",
                            "requirement": {"head_branch": "feature/new"},
                        },
                        {
                            "label": "The isolated work advanced feature/new; main stayed at its original tip.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "feature/new",
                                    "contains_paths": ["README.md"],
                                    "message_contains": ["Start new feature"],
                                },
                                "rules": [{"type": "branch_points_to", "branch": "main", "commit": "c0"}],
                            },
                        },
                    ],
                ),
                _wave(
                    "ch3-adv-checkout-legacy-create",
                    "git-checkout/legacy-create",
                    "Checkout legacy create",
                    ["git checkout -b legacy/feature", "git add README.md", "git commit -m 'Start legacy branch'"],
                    required=["git checkout -b", "git commit"],
                    forms=["git-add/file", "git-commit/message"],
                    state="dirty",
                    story=(
                        "A teammate still uses the older create-and-switch spelling out of habit. Use "
                        "checkout -b to create legacy/feature and move onto it, then commit the pending "
                        "work there."
                    ),
                    evaluation={
                        "head_branch": "legacy/feature",
                        "latest_commit": {
                            "branch": "legacy/feature",
                            "contains_paths": ["README.md"],
                            "message_contains": ["Start legacy branch"],
                        },
                    },
                    checks=[
                        {
                            "label": "legacy/feature was created and checked out with the legacy spelling.",
                            "requirement": {"head_branch": "legacy/feature"},
                        },
                        {
                            "label": "The pending work is committed on the new branch.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "legacy/feature",
                                    "contains_paths": ["README.md"],
                                    "message_contains": ["Start legacy branch"],
                                }
                            },
                        },
                    ],
                ),
                _wave(
                    "ch3-adv-graph-before-switch",
                    "git-log/graph-all",
                    "Map the graph, then move",
                    ["git log --oneline --graph --all", "git branch", "git switch feature/ui"],
                    required=["git log", "git branch", "git switch"],
                    forms=["git-branch/list", "git-switch/existing"],
                    state="branch",
                    story=(
                        "Never move blind: draw the whole ref graph, read the branch list, and "
                        "only then step onto the feature line where today's work belongs."
                    ),
                    evaluation={"head_branch": "feature/ui"},
                    checks=[
                        {
                            "label": "The graph and branch list were read before moving.",
                            "requirement": {"required_commands": ["git log", "git branch"]},
                        },
                        {
                            "label": "HEAD landed on the feature line.",
                            "requirement": {"head_branch": "feature/ui"},
                        },
                    ],
                ),
                _wave(
                    "ch3-adv-detach-inspect-note",
                    "git-switch/detach",
                    "Inspect detached, report on main",
                    [
                        "git switch --detach c1",
                        "git show",
                        "git switch main",
                        "git add README.md",
                        "git commit -m 'Record inspection'",
                    ],
                    required=["git switch --detach", "git show", "git switch", "git add", "git commit"],
                    forms=["git-show/head", "git-switch/existing", "git-add/file", "git-commit/message"],
                    state="branch-dirty",
                    story=(
                        "A question about the older commit c1 needs a first-hand answer. Visit it "
                        "detached, read the snapshot where you stand, then return to main and "
                        "commit the pending note recording what you found."
                    ),
                    details=[{"label": "Commit message", "value": "Record inspection"}],
                    evaluation={
                        "head_branch": "main",
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["README.md"],
                            "message_contains": ["Record inspection"],
                        },
                    },
                    checks=[
                        {
                            "label": "The old commit was visited detached and read in place.",
                            "requirement": {"required_commands": ["git switch --detach", "git show"]},
                        },
                        {
                            "label": "The findings are committed back on main.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["README.md"],
                                    "message_contains": ["Record inspection"],
                                }
                            },
                        },
                    ],
                ),
            ],
        },
        {
            "slug": "start-lines-deliberately",
            "title": "Start Lines Deliberately",
            "waves": [
                _wave(
                    "ch3-adv-init-trunk-branch",
                    "git-init/initial-branch",
                    "New project on the trunk line",
                    ["git init -b trunk", "git add .", "git commit -m 'Trunk baseline'", "git branch"],
                    required=["git init", "git add", "git commit", "git branch"],
                    forms=["git-add/dot", "git-commit/message", "git-branch/list"],
                    state="uninitialized",
                    story=(
                        "This team's convention names its default line trunk, and a new project "
                        "must honor it from the very first snapshot. Start the repository on that "
                        "line, save the baseline, then read the branch list to confirm the shape."
                    ),
                    details=[
                        {"label": "First branch name", "value": "trunk"},
                        {"label": "Commit message", "value": "Trunk baseline"},
                    ],
                    evaluation={
                        "repository_initialized": True,
                        "head_branch": "trunk",
                        "latest_commit": {
                            "branch": "trunk",
                            "contains_paths": ["README.md", "src/app.py"],
                            "message_contains": ["Trunk baseline"],
                        },
                        "working_tree_clean": True,
                    },
                    checks=[
                        {
                            "label": "History began on the trunk line with the baseline saved.",
                            "requirement": {
                                "head_branch": "trunk",
                                "latest_commit": {
                                    "branch": "trunk",
                                    "message_contains": ["Trunk baseline"],
                                },
                            },
                        },
                        {
                            "label": "The branch shape was confirmed from the list.",
                            "requirement": {"required_commands": ["git branch"]},
                        },
                    ],
                ),
                _wave(
                    "ch3-adv-init-line-then-branch",
                    "git-init/initial-branch",
                    "Baseline, then a kickoff line",
                    [
                        "git init -b main",
                        "git add .",
                        "git commit -m 'Product baseline'",
                        "git branch feature/kickoff",
                    ],
                    required=["git init", "git add", "git commit", "git branch"],
                    forms=["git-add/dot", "git-commit/message", "git-branch/create"],
                    state="uninitialized",
                    story=(
                        "A new product starts today: the repository must begin explicitly on main, "
                        "hold a baseline snapshot, and already offer a feature/kickoff pointer for "
                        "the first sprint - without HEAD leaving main."
                    ),
                    details=[
                        {"label": "First branch name", "value": "main"},
                        {"label": "Commit message", "value": "Product baseline"},
                        {"label": "Kickoff branch", "value": "feature/kickoff"},
                    ],
                    evaluation={
                        "repository_initialized": True,
                        "head_branch": "main",
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["README.md", "src/app.py"],
                            "message_contains": ["Product baseline"],
                        },
                        "rules": [{"type": "branch_exists", "branch": "feature/kickoff"}],
                    },
                    checks=[
                        {
                            "label": "The baseline snapshot landed on an explicit main line.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "message_contains": ["Product baseline"],
                                }
                            },
                        },
                        {
                            "label": "The kickoff pointer exists while HEAD stayed on main.",
                            "requirement": {
                                "head_branch": "main",
                                "rules": [{"type": "branch_exists", "branch": "feature/kickoff"}],
                            },
                        },
                    ],
                ),
                _wave(
                    "ch3-adv-alias-switch",
                    "git-config/alias",
                    "A shortcut for moving around",
                    ["git config --global alias.sw switch", "git config --list", "git switch feature/ui"],
                    required=["git config --global alias.sw", "git config --list", "git switch"],
                    forms=["git-config/list", "git-switch/existing"],
                    state="branch",
                    story=(
                        "You move between lines of work a dozen times a day now. Record a global "
                        "shortcut named sw for the branch-moving command, confirm it in the "
                        "settings, then use the full spelling once more to reach the feature line."
                    ),
                    details=[
                        {"label": "Alias name", "value": "sw"},
                        {"label": "Expands to", "value": "switch"},
                    ],
                    evaluation={
                        "head_branch": "feature/ui",
                        "rules": [
                            {
                                "type": "operation_metadata_equals",
                                "key": "last_config_key",
                                "value": "alias.sw",
                            }
                        ],
                    },
                    checks=[
                        {
                            "label": "The sw shortcut is recorded and confirmed.",
                            "requirement": {
                                "rules": [
                                    {
                                        "type": "operation_metadata_equals",
                                        "key": "last_config_key",
                                        "value": "alias.sw",
                                    }
                                ],
                                "required_commands": ["git config --list"],
                            },
                        },
                        {
                            "label": "HEAD finished on the feature line.",
                            "requirement": {"head_branch": "feature/ui"},
                        },
                    ],
                ),
            ],
        },
    ]
