"""Blueprint adventure levels for detach-and-clean."""

from __future__ import annotations

from .helpers import _wave

ADVENTURE_LEVELS = [
        {
            "slug": "branch-workflows-with-clean-snapshots",
            "title": "Branch Workflows with Clean Snapshots",
            "waves": [
                _wave(
                    "ch3-adv-branch-for-feature",
                    "git-switch/create",
                    "Branch for feature",
                    ["git status", "git switch -c feature/report", "git add -p src/app.py", "git commit -m 'Add report feature'"],
                    required=["git status", "git switch -c", "git add -p", "git commit"],
                    forms=["git-status/plain", "git-add/patch", "git-commit/message"],
                    state="partial",
                    story=(
                        "src/app.py mixes a real report feature with a leftover debug hunk, still on "
                        "main. Check the status, then start a feature/report branch and commit only the "
                        "feature hunk there - main must stay untouched."
                    ),
                    evaluation={
                        "head_branch": "feature/report",
                        "latest_commit": {
                            "branch": "feature/report",
                            "contains_paths": ["src/app.py"],
                            "message_contains": ["Add report feature"],
                        },
                        "rules": [{"type": "branch_points_to", "branch": "main", "commit": "c0"}],
                    },
                    checks=[
                        {
                            "label": "The mixed file was inspected with status before branching.",
                            "requirement": {"required_commands": ["git status"]},
                        },
                        {
                            "label": "The feature hunk landed on a new feature/report branch, ahead of main.",
                            "requirement": {
                                "head_branch": "feature/report",
                                "latest_commit": {
                                    "branch": "feature/report",
                                    "contains_paths": ["src/app.py"],
                                    "message_contains": ["Add report feature"],
                                },
                                "rules": [{"type": "branch_points_to", "branch": "main", "commit": "c0"}],
                            },
                        },
                    ],
                ),
                _wave(
                    "ch3-adv-branch-from-release",
                    "git-branch/create-at-start",
                    "Branch from release",
                    ["git branch hotfix c0", "git switch hotfix", "git add README.md", "git commit -m 'Patch release note'"],
                    required=["git branch", "git switch", "git commit"],
                    forms=["git-switch/existing", "git-add/file", "git-commit/message"],
                    state="branch-dirty",
                    story=(
                        "A hotfix must build on the old release commit c0, not on main's current tip. "
                        "Point a hotfix branch at c0, move onto it, and commit the release note there."
                    ),
                    evaluation={
                        "head_branch": "hotfix",
                        "latest_commit": {
                            "branch": "hotfix",
                            "contains_paths": ["README.md"],
                            "message_contains": ["Patch release note"],
                        },
                        "rules": [{"type": "branch_points_to", "branch": "main", "commit": "c2"}],
                    },
                    checks=[
                        {
                            "label": "The hotfix branch was pointed at the old release commit, then switched onto.",
                            "requirement": {"head_branch": "hotfix"},
                        },
                        {
                            "label": "The release note advanced hotfix; main stayed exactly where it was.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "hotfix",
                                    "contains_paths": ["README.md"],
                                    "message_contains": ["Patch release note"],
                                },
                                "rules": [{"type": "branch_points_to", "branch": "main", "commit": "c2"}],
                            },
                        },
                    ],
                ),
                _wave(
                    "ch3-adv-recover-detached-work",
                    "git-switch/detach",
                    "Recover detached work",
                    [
                        "git switch --detach c0",
                        "git add README.md",
                        "git commit -m 'Detached useful work'",
                        "git branch rescue HEAD",
                        "git switch rescue",
                    ],
                    required=["git switch --detach", "git commit", "git branch", "git switch"],
                    forms=["git-branch/create-at-start", "git-switch/existing", "git-add/file", "git-commit/message"],
                    state="dirty",
                    story=(
                        "Detached inspection turned into real, useful work: a commit worth keeping. "
                        "Anchor that detached commit onto a real branch named rescue before it becomes "
                        "unreachable, then land on that branch."
                    ),
                    evaluation={
                        "head_branch": "rescue",
                        "latest_commit": {
                            "branch": "rescue",
                            "contains_paths": ["README.md"],
                            "message_contains": ["Detached useful work"],
                        },
                        "rules": [{"type": "branch_points_to", "branch": "main", "commit": "c0"}],
                    },
                    checks=[
                        {
                            "label": "The detached commit is anchored onto a real rescue branch.",
                            "requirement": {"head_branch": "rescue"},
                        },
                        {
                            "label": "The rescued work is exactly the detached commit; main is unaffected.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "rescue",
                                    "contains_paths": ["README.md"],
                                    "message_contains": ["Detached useful work"],
                                },
                                "rules": [{"type": "branch_points_to", "branch": "main", "commit": "c0"}],
                            },
                        },
                    ],
                ),
                _wave(
                    "ch3-adv-feature-then-inspect",
                    "git-switch/create",
                    "New line, then map the result",
                    [
                        "git switch -c feature/notes",
                        "git add README.md",
                        "git commit -m 'Draft notes'",
                        "git log --oneline --graph --all",
                    ],
                    required=["git switch -c", "git add", "git commit", "git log"],
                    forms=["git-add/file", "git-commit/message", "git-log/graph-all"],
                    state="branch-dirty",
                    story=(
                        "The pending README draft belongs on its own new line. Create "
                        "feature/notes and step onto it in one move, commit the draft there, then "
                        "draw the full graph to see the new tip sitting ahead of main."
                    ),
                    details=[{"label": "Commit message", "value": "Draft notes"}],
                    evaluation={
                        "head_branch": "feature/notes",
                        "latest_commit": {
                            "branch": "feature/notes",
                            "contains_paths": ["README.md"],
                            "message_contains": ["Draft notes"],
                        },
                    },
                    checks=[
                        {
                            "label": "The draft landed on the brand-new line.",
                            "requirement": {
                                "head_branch": "feature/notes",
                                "latest_commit": {
                                    "branch": "feature/notes",
                                    "message_contains": ["Draft notes"],
                                },
                            },
                        },
                        {
                            "label": "The new shape was mapped on the full graph.",
                            "requirement": {"required_commands": ["git log"]},
                        },
                    ],
                ),
                _wave(
                    "ch3-adv-legacy-hotfix",
                    "git-checkout/legacy-create",
                    "Hotfix the legacy way",
                    [
                        "git checkout -b hotfix/legacy",
                        "git add README.md",
                        "git commit -m 'Legacy hotfix'",
                        "git branch -v",
                    ],
                    required=["git checkout -b", "git add", "git commit", "git branch -v"],
                    forms=["git-add/file", "git-commit/message", "git-branch/verbose"],
                    state="branch-dirty",
                    story=(
                        "Pairing with a teammate who lives in the older spelling: create the "
                        "hotfix line their way, commit the pending patch on it, then compare "
                        "every tip in the verbose listing to confirm where the fix sits."
                    ),
                    details=[{"label": "Commit message", "value": "Legacy hotfix"}],
                    evaluation={
                        "head_branch": "hotfix/legacy",
                        "latest_commit": {
                            "branch": "hotfix/legacy",
                            "contains_paths": ["README.md"],
                            "message_contains": ["Legacy hotfix"],
                        },
                    },
                    checks=[
                        {
                            "label": "The patch landed on a line created the legacy way.",
                            "requirement": {
                                "head_branch": "hotfix/legacy",
                                "latest_commit": {
                                    "branch": "hotfix/legacy",
                                    "message_contains": ["Legacy hotfix"],
                                },
                            },
                        },
                        {
                            "label": "Every tip was compared in the verbose listing.",
                            "requirement": {"required_commands": ["git branch -v"]},
                        },
                    ],
                ),
            ],
        },
        {
            "slug": "delete-branch-pointers-deliberately",
            "title": "Delete Branch Pointers Deliberately",
            "waves": [
                _wave(
                    "ch3-adv-delete-merged-branch",
                    "git-branch/delete",
                    "Delete merged branch",
                    ["git branch -d old"],
                    state="branch-delete",
                    story=(
                        "The old branch's work has already been folded into main - keeping the pointer "
                        "around is just clutter now. Remove old with the safe delete, which refuses "
                        "unmerged work."
                    ),
                    evaluation={"rules": [{"type": "branch_absent", "branch": "old"}]},
                    checks=[
                        {
                            "label": "The already-merged old branch pointer is gone.",
                            "requirement": {"rules": [{"type": "branch_absent", "branch": "old"}]},
                        },
                    ],
                ),
                _wave(
                    "ch3-adv-force-delete-scratch-branch",
                    "git-branch/delete-force",
                    "Force delete scratch branch",
                    ["git branch -D scratch"],
                    state="branch-delete",
                    story=(
                        "scratch was an experiment that never merged anywhere and never will. Confirm "
                        "it is disposable, then force-remove it even though its commit is not reachable "
                        "from main."
                    ),
                    evaluation={"rules": [{"type": "branch_absent", "branch": "scratch"}]},
                    checks=[
                        {
                            "label": "The disposable scratch pointer is removed, even though it was unmerged.",
                            "requirement": {"rules": [{"type": "branch_absent", "branch": "scratch"}]},
                        },
                    ],
                ),
                _wave(
                    "ch3-adv-branch-cleanup-workflow",
                    "git-log/graph-all",
                    "Branch cleanup workflow",
                    ["git log --oneline --graph --all", "git branch -v", "git branch -d old", "git branch -D scratch"],
                    required=["git log", "git branch -v", "git branch -d", "git branch -D"],
                    forms=["git-branch/verbose", "git-branch/delete", "git-branch/delete-force"],
                    state="branch-delete",
                    story=(
                        "Both old and scratch are cluttering the branch list, but for different "
                        "reasons: one is merged, one never will be. Verify reachability with the full "
                        "graph and verbose listing, then remove exactly the two disposable pointers."
                    ),
                    evaluation={
                        "rules": [
                            {"type": "branch_absent", "branch": "old"},
                            {"type": "branch_absent", "branch": "scratch"},
                        ]
                    },
                    checks=[
                        {
                            "label": "Reachability was verified with the graphed log and verbose branch listing.",
                            "requirement": {"required_commands": ["git log", "git branch -v"]},
                        },
                        {
                            "label": "Both disposable branch pointers are gone after cleanup.",
                            "requirement": {
                                "rules": [
                                    {"type": "branch_absent", "branch": "old"},
                                    {"type": "branch_absent", "branch": "scratch"},
                                ]
                            },
                        },
                    ],
                ),
                _wave(
                    "ch3-adv-list-before-delete",
                    "git-branch/delete",
                    "Survey, then retire a pointer",
                    ["git branch", "git branch -d old"],
                    required=["git branch", "git branch -d"],
                    forms=["git-branch/list"],
                    state="branch-delete",
                    story=(
                        "Cleanup starts with a survey: read the branch list, spot the pointer "
                        "whose work already merged, and retire it with the safe delete that "
                        "refuses anything unmerged."
                    ),
                    evaluation={"rules": [{"type": "branch_absent", "branch": "old"}]},
                    checks=[
                        {
                            "label": "The pointers were surveyed before deleting.",
                            "requirement": {"required_commands": ["git branch"]},
                        },
                        {
                            "label": "The merged pointer is retired.",
                            "requirement": {"rules": [{"type": "branch_absent", "branch": "old"}]},
                        },
                    ],
                ),
                _wave(
                    "ch3-adv-verbose-before-force",
                    "git-branch/delete-force",
                    "Compare tips, then force-remove",
                    ["git branch -v", "git branch -D scratch"],
                    required=["git branch -v", "git branch -D"],
                    forms=["git-branch/verbose"],
                    state="branch-delete",
                    story=(
                        "The scratch experiment never merged and never will. Compare every tip in "
                        "the verbose listing to be certain nothing else depends on it, then "
                        "force-remove the disposable pointer."
                    ),
                    evaluation={"rules": [{"type": "branch_absent", "branch": "scratch"}]},
                    checks=[
                        {
                            "label": "Tips were compared before forcing anything.",
                            "requirement": {"required_commands": ["git branch -v"]},
                        },
                        {
                            "label": "The disposable pointer is force-removed.",
                            "requirement": {"rules": [{"type": "branch_absent", "branch": "scratch"}]},
                        },
                    ],
                ),
            ],
        },
        {
            "slug": "branch-drills",
            "title": "Branch Drills",
            "waves": [
                _wave(
                    "ch3-adv-create-pair",
                    "git-branch/create",
                    "Stage two environments",
                    ["git branch staging", "git branch qa", "git branch", "git branch -v"],
                    required=["git branch"],
                    forms=["git-branch/list", "git-branch/verbose"],
                    state="branch",
                    story=(
                        "The deploy pipeline needs two environment pointers at the current "
                        "commit: staging and qa. Create both without moving HEAD, then read the "
                        "plain and verbose listings to confirm the pair."
                    ),
                    details=[
                        {"label": "First branch", "value": "staging"},
                        {"label": "Second branch", "value": "qa"},
                    ],
                    evaluation={
                        "head_branch": "main",
                        "rules": [
                            {"type": "branch_exists", "branch": "staging"},
                            {"type": "branch_exists", "branch": "qa"},
                        ],
                    },
                    checks=[
                        {
                            "label": "Both environment pointers exist while HEAD never left main.",
                            "requirement": {
                                "head_branch": "main",
                                "rules": [
                                    {"type": "branch_exists", "branch": "staging"},
                                    {"type": "branch_exists", "branch": "qa"},
                                ]
                            },
                        },
                    ],
                ),
                _wave(
                    "ch3-adv-branch-per-task",
                    "git-branch/create",
                    "One pointer per task",
                    [
                        "git branch task/login",
                        "git branch task/search",
                        "git branch task/profile",
                        "git branch",
                    ],
                    required=["git branch"],
                    forms=["git-branch/list"],
                    state="branch",
                    story=(
                        "Sprint planning split the work three ways, and each task gets its own "
                        "line starting from the current commit. Create all three pointers, then "
                        "read the list to confirm the sprint board matches the repository."
                    ),
                    evaluation={
                        "head_branch": "main",
                        "rules": [
                            {"type": "branch_exists", "branch": "task/login"},
                            {"type": "branch_exists", "branch": "task/search"},
                            {"type": "branch_exists", "branch": "task/profile"},
                        ],
                    },
                    checks=[
                        {
                            "label": "All three task pointers exist while HEAD stayed on main.",
                            "requirement": {
                                "head_branch": "main",
                                "rules": [
                                    {"type": "branch_exists", "branch": "task/login"},
                                    {"type": "branch_exists", "branch": "task/search"},
                                    {"type": "branch_exists", "branch": "task/profile"},
                                ]
                            },
                        },
                    ],
                ),
                _wave(
                    "ch3-adv-switch-tour",
                    "git-switch/existing",
                    "Tour the lines, land on old",
                    ["git branch", "git switch feature/ui", "git switch old"],
                    required=["git branch", "git switch"],
                    forms=["git-branch/list"],
                    state="branch",
                    story=(
                        "An archaeology request: something on the old line needs eyes today. "
                        "Read the list, pass through the feature line to grab context, and end "
                        "stationed on old."
                    ),
                    evaluation={"head_branch": "old"},
                    checks=[
                        {
                            "label": "The lines were surveyed before moving.",
                            "requirement": {"required_commands": ["git branch"]},
                        },
                        {
                            "label": "HEAD finished stationed on the old line.",
                            "requirement": {"head_branch": "old"},
                        },
                    ],
                ),
                _wave(
                    "ch3-adv-legacy-drill",
                    "git-checkout/legacy-create",
                    "Legacy spelling, quick fix line",
                    ["git checkout -b fix/typo", "git branch -v"],
                    required=["git checkout -b", "git branch -v"],
                    forms=["git-branch/verbose"],
                    state="branch",
                    story=(
                        "A one-character typo fix needs its own line, and muscle memory from an "
                        "old guide kicks in. Create fix/typo with the legacy spelling, then "
                        "compare tips to see the new line sharing the current commit."
                    ),
                    details=[{"label": "New branch", "value": "fix/typo"}],
                    evaluation={
                        "head_branch": "fix/typo",
                        "rules": [{"type": "branch_exists", "branch": "fix/typo"}],
                    },
                    checks=[
                        {
                            "label": "The fix line exists and HEAD stepped onto it.",
                            "requirement": {"head_branch": "fix/typo"},
                        },
                        {
                            "label": "The tips were compared after creating it.",
                            "requirement": {"required_commands": ["git branch -v"]},
                        },
                    ],
                ),
                _wave(
                    "ch3-adv-detach-audit",
                    "git-switch/detach",
                    "Detached audit of an old tip",
                    ["git switch --detach c1", "git show"],
                    required=["git switch --detach", "git show"],
                    forms=["git-show/head"],
                    state="branch",
                    story=(
                        "An audit asks exactly what commit c1 contained - not what any branch "
                        "says about it. Move HEAD there directly without touching a single "
                        "pointer, then read the snapshot where you stand."
                    ),
                    details=[{"label": "Commit to visit", "value": "c1"}],
                    evaluation={"rules": [{"type": "head_detached_at", "commit": "c1"}]},
                    checks=[
                        {
                            "label": "HEAD is detached exactly at the audited commit.",
                            "requirement": {"rules": [{"type": "head_detached_at", "commit": "c1"}]},
                        },
                        {
                            "label": "The snapshot was read where HEAD stands.",
                            "requirement": {"required_commands": ["git show"]},
                        },
                    ],
                ),
                _wave(
                    "ch3-adv-pin-release-lines",
                    "git-branch/create-at-start",
                    "Pin the release history",
                    [
                        "git branch release/v1 c0",
                        "git branch release/v2 c1",
                        "git branch integration",
                        "git branch",
                    ],
                    required=["git branch"],
                    forms=["git-branch/create", "git-branch/list"],
                    state="branch",
                    story=(
                        "Release archaeology: v1 shipped from the first commit and v2 from the "
                        "second, but nobody ever labeled them. Pin both release pointers at their "
                        "exact commits, add an integration pointer at the current tip, and read "
                        "the final list."
                    ),
                    details=[
                        {"label": "release/v1 target", "value": "c0"},
                        {"label": "release/v2 target", "value": "c1"},
                    ],
                    evaluation={
                        "head_branch": "main",
                        "rules": [
                            {"type": "branch_points_to", "branch": "release/v1", "commit": "c0"},
                            {"type": "branch_points_to", "branch": "release/v2", "commit": "c1"},
                            {"type": "branch_exists", "branch": "integration"},
                        ],
                    },
                    checks=[
                        {
                            "label": "Both release pointers pin their exact commits.",
                            "requirement": {
                                "rules": [
                                    {"type": "branch_points_to", "branch": "release/v1", "commit": "c0"},
                                    {"type": "branch_points_to", "branch": "release/v2", "commit": "c1"},
                                ]
                            },
                        },
                        {
                            "label": "The integration pointer exists at the current tip.",
                            "requirement": {"rules": [{"type": "branch_exists", "branch": "integration"}]},
                        },
                    ],
                ),
            ],
        },
        {
            "slug": "cleanup-gauntlet",
            "title": "Cleanup Gauntlet",
            "waves": [
                _wave(
                    "ch3-adv-full-cleanup",
                    "git-branch/delete",
                    "Retire both kinds of clutter",
                    ["git branch", "git branch -d old", "git branch -D scratch"],
                    required=["git branch", "git branch -d", "git branch -D"],
                    forms=["git-branch/list", "git-branch/delete-force"],
                    state="branch-delete",
                    story=(
                        "Two pointers clutter the list for opposite reasons: one merged long "
                        "ago, one never will. Survey the list, retire the merged one safely, and "
                        "force-remove the disposable one."
                    ),
                    evaluation={
                        "rules": [
                            {"type": "branch_absent", "branch": "old"},
                            {"type": "branch_absent", "branch": "scratch"},
                        ]
                    },
                    checks=[
                        {
                            "label": "The list was surveyed before any deletion.",
                            "requirement": {"required_commands": ["git branch"]},
                        },
                        {
                            "label": "Both clutter pointers are gone.",
                            "requirement": {
                                "rules": [
                                    {"type": "branch_absent", "branch": "old"},
                                    {"type": "branch_absent", "branch": "scratch"},
                                ]
                            },
                        },
                    ],
                ),
                _wave(
                    "ch3-adv-delete-then-verify",
                    "git-branch/delete",
                    "Retire, then verify the list",
                    ["git branch -d old", "git branch -v"],
                    required=["git branch -d", "git branch -v"],
                    forms=["git-branch/verbose"],
                    state="branch-delete",
                    story=(
                        "The merged pointer goes first. Retire it with the safe delete, then "
                        "read the verbose listing to verify only live lines remain."
                    ),
                    evaluation={"rules": [{"type": "branch_absent", "branch": "old"}]},
                    checks=[
                        {
                            "label": "The merged pointer is retired.",
                            "requirement": {"rules": [{"type": "branch_absent", "branch": "old"}]},
                        },
                        {
                            "label": "The remaining tips were verified afterward.",
                            "requirement": {"required_commands": ["git branch -v"]},
                        },
                    ],
                ),
                _wave(
                    "ch3-adv-force-then-graph",
                    "git-branch/delete-force",
                    "Force-remove, then redraw",
                    ["git branch -D scratch", "git log --oneline --graph --all"],
                    required=["git branch -D", "git log"],
                    forms=["git-log/graph-all"],
                    state="branch-delete",
                    story=(
                        "The dead experiment goes today. Force-remove its pointer, then redraw "
                        "the whole graph to see how much cleaner the picture reads without it."
                    ),
                    evaluation={"rules": [{"type": "branch_absent", "branch": "scratch"}]},
                    checks=[
                        {
                            "label": "The experiment's pointer is force-removed.",
                            "requirement": {"rules": [{"type": "branch_absent", "branch": "scratch"}]},
                        },
                        {
                            "label": "The cleaned graph was redrawn afterward.",
                            "requirement": {"required_commands": ["git log"]},
                        },
                    ],
                ),
                _wave(
                    "ch3-adv-prune-and-pin",
                    "git-branch/delete",
                    "Prune one, pin one",
                    ["git branch -d old", "git branch keep c1", "git branch"],
                    required=["git branch -d", "git branch"],
                    forms=["git-branch/create-at-start", "git-branch/list"],
                    state="branch-delete",
                    story=(
                        "Housekeeping with a twist: the merged pointer retires, but the commit "
                        "it pointed at still matters - pin a keep branch on that exact commit "
                        "before reading the final list."
                    ),
                    details=[{"label": "Pin target", "value": "c1"}],
                    evaluation={
                        "rules": [
                            {"type": "branch_absent", "branch": "old"},
                            {"type": "branch_points_to", "branch": "keep", "commit": "c1"},
                        ]
                    },
                    checks=[
                        {
                            "label": "The merged pointer is pruned.",
                            "requirement": {"rules": [{"type": "branch_absent", "branch": "old"}]},
                        },
                        {
                            "label": "The keep pointer pins the surviving commit.",
                            "requirement": {
                                "rules": [{"type": "branch_points_to", "branch": "keep", "commit": "c1"}]
                            },
                        },
                    ],
                ),
                _wave(
                    "ch3-adv-force-cleanup-note",
                    "git-branch/delete-force",
                    "Force-remove, read the story",
                    ["git branch -D scratch", "git log --oneline"],
                    required=["git branch -D", "git log"],
                    forms=["git-log/oneline"],
                    state="branch-delete",
                    story=(
                        "With the dead experiment's pointer force-removed, the compact history "
                        "should read as one clean story again. Remove it, then read that story "
                        "top to bottom."
                    ),
                    evaluation={"rules": [{"type": "branch_absent", "branch": "scratch"}]},
                    checks=[
                        {
                            "label": "The experiment's pointer is gone.",
                            "requirement": {"rules": [{"type": "branch_absent", "branch": "scratch"}]},
                        },
                        {
                            "label": "The compact story was read afterward.",
                            "requirement": {"required_commands": ["git log"]},
                        },
                    ],
                ),
            ],
        },
    ]
