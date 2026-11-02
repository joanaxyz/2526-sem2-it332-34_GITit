"""Blueprint adventure levels for connect-and-inspect."""

from __future__ import annotations

from .helpers import _wave

ADVENTURE_LEVELS = [
        {
            "slug": "inspect-remote-setup",
            "title": "Inspect Remote Setup",
            "waves": [
                _wave(
                    "ch7-adv-list-remotes",
                    "git-remote/list",
                    "List remotes",
                    ["git remote"],
                    state="remote",
                    story=(
                        "Before sharing any work, confirm which remote names are already configured "
                        "for this local repository."
                    ),
                    evaluation={"rules": [{"type": "commit_count_equals", "count": 3}]},
                    checks=[
                        {
                            "label": "The configured remote names were listed without changing anything.",
                            "requirement": {"required_commands": ["git remote"]},
                        },
                    ],
                ),
                _wave(
                    "ch7-adv-list-remote-urls",
                    "git-remote/verbose",
                    "List remote URLs",
                    ["git remote -v"],
                    state="remote",
                    story=(
                        "A remote name alone does not confirm where it actually points. Verify the "
                        "fetch and push URLs before trusting this remote for anything."
                    ),
                    evaluation={"rules": [{"type": "commit_count_equals", "count": 3}]},
                    checks=[
                        {
                            "label": "The fetch/push URLs were verified before relying on this remote.",
                            "requirement": {"required_commands": ["git remote -v"]},
                        },
                    ],
                ),
                _wave(
                    "ch7-adv-remote-inspection-workflow",
                    "git-remote/verbose",
                    "Remote inspection workflow",
                    ["git remote -v", "git log --oneline --graph --all", "git status"],
                    required=["git remote -v", "git log", "git status"],
                    forms=["git-log/graph-all", "git-status/plain"],
                    state="remote",
                    story=(
                        "Before deciding whether to fetch, pull, or push, get a full picture: the "
                        "remote's URL, the graph of local and remote-tracking refs, and the current "
                        "working tree status."
                    ),
                    evaluation={"rules": [{"type": "commit_count_equals", "count": 3}]},
                    checks=[
                        {
                            "label": "The remote, the ref graph, and the working tree were all read before acting.",
                            "requirement": {
                                "required_commands": ["git remote -v", "git log", "git status"]
                            },
                        },
                    ],
                ),
                _wave(
                    "ch7-adv-remote-list-drill",
                    "git-remote/list",
                    "Names first, state second",
                    ["git remote", "git status"],
                    required=["git remote", "git status"],
                    forms=["git-status/plain"],
                    state="remote",
                    story=(
                        "New machine, inherited checkout: before anything syncs, read which "
                        "remote names exist and what state the working tree is in. Two reads, "
                        "zero changes."
                    ),
                    evaluation={
                        "staging_empty": True,
                        "rules": [{"type": "commit_count_equals", "count": 3}],
                    },
                    checks=[
                        {
                            "label": "The remote names and the workspace state were both read.",
                            "requirement": {"required_commands": ["git remote", "git status"]},
                        },
                    ],
                ),
                _wave(
                    "ch7-adv-identity-on-shared-machine",
                    "git-config/global-user-name",
                    "Identity before collaboration",
                    [
                        "git config --global user.name 'Learner B'",
                        "git config --global user.email learner-b@example.test",
                        "git config --list",
                        "git remote -v",
                    ],
                    required=["git config --global user.name", "git config --global user.email", "git config --list", "git remote -v"],
                    forms=["git-config/global-user-email", "git-config/list", "git-remote/verbose"],
                    state="remote",
                    story=(
                        "Nothing gets pushed from an anonymous machine. Record both halves of "
                        "the identity shown below, confirm the effective settings, then verify "
                        "exactly which remote this repository would publish to."
                    ),
                    details=[
                        {"label": "Author name", "value": "Learner B"},
                        {"label": "Author email", "value": "learner-b@example.test"},
                    ],
                    evaluation={
                        "rules": [
                            {
                                "type": "operation_metadata_equals",
                                "key": "last_config_key",
                                "value": "user.email",
                            }
                        ]
                    },
                    checks=[
                        {
                            "label": "Both identity halves are recorded and confirmed.",
                            "requirement": {
                                "rules": [
                                    {
                                        "type": "operation_metadata_equals",
                                        "key": "last_config_key",
                                        "value": "user.email",
                                    }
                                ],
                                "required_commands": ["git config --list"],
                            },
                        },
                        {
                            "label": "The publish target's URLs were verified.",
                            "requirement": {"required_commands": ["git remote -v"]},
                        },
                    ],
                ),
                _wave(
                    "ch7-adv-alias-remote-check",
                    "git-config/alias",
                    "A shortcut for remote checks",
                    ["git config --global alias.rv remote", "git remote -v"],
                    required=["git config --global alias.rv", "git remote -v"],
                    forms=["git-remote/verbose"],
                    state="remote",
                    story=(
                        "You verify remotes before every sync, so give the habit a shortcut: "
                        "record a global alias named rv for the remote command, then run the "
                        "full verification once more the long way."
                    ),
                    details=[
                        {"label": "Alias name", "value": "rv"},
                        {"label": "Expands to", "value": "remote"},
                    ],
                    evaluation={
                        "rules": [
                            {
                                "type": "operation_metadata_equals",
                                "key": "last_config_key",
                                "value": "alias.rv",
                            }
                        ]
                    },
                    checks=[
                        {
                            "label": "The rv shortcut is recorded.",
                            "requirement": {
                                "rules": [
                                    {
                                        "type": "operation_metadata_equals",
                                        "key": "last_config_key",
                                        "value": "alias.rv",
                                    }
                                ]
                            },
                        },
                        {
                            "label": "The remote URLs were verified afterward.",
                            "requirement": {"required_commands": ["git remote -v"]},
                        },
                    ],
                ),
            ],
        },
        {
            "slug": "fresh-machine",
            "title": "Fresh Machine",
            "waves": [
                _wave(
                    "ch7-adv-clone-then-remotes",
                    "git-clone/default-folder",
                    "Copy down, check the wiring",
                    ["git clone https://example.test/team/app.git", "git remote"],
                    required=["git clone", "git remote"],
                    forms=["git-remote/list"],
                    state="clone",
                    story=(
                        "Day one on a new laptop: bring the team project down into its default "
                        "folder, then read which remote names the fresh copy was wired with."
                    ),
                    evaluation={
                        "repository_initialized": True,
                        "working_tree_clean": True,
                    },
                    checks=[
                        {
                            "label": "A complete local copy exists.",
                            "requirement": {"repository_initialized": True},
                        },
                        {
                            "label": "The fresh copy's remote wiring was read.",
                            "requirement": {"required_commands": ["git remote"]},
                        },
                    ],
                ),
                _wave(
                    "ch7-adv-clone-check-urls",
                    "git-clone/named-folder",
                    "Named copy, verified URLs",
                    ["git clone https://example.test/team/app.git team-app", "git remote -v"],
                    required=["git clone", "git remote -v"],
                    forms=["git-remote/verbose"],
                    state="clone",
                    story=(
                        "This machine hosts several projects, so the copy must land under the "
                        "exact folder name shown below. Bring it down there, then verify the "
                        "fetch and push URLs it inherited."
                    ),
                    details=[{"label": "Folder name", "value": "team-app"}],
                    evaluation={
                        "repository_initialized": True,
                        "rules": [
                            {
                                "type": "operation_metadata_equals",
                                "key": "last_clone_destination",
                                "value": "team-app",
                            }
                        ],
                    },
                    checks=[
                        {
                            "label": "The copy landed under the requested name.",
                            "requirement": {
                                "rules": [
                                    {
                                        "type": "operation_metadata_equals",
                                        "key": "last_clone_destination",
                                        "value": "team-app",
                                    }
                                ]
                            },
                        },
                        {
                            "label": "The inherited URLs were verified.",
                            "requirement": {"required_commands": ["git remote -v"]},
                        },
                    ],
                ),
                _wave(
                    "ch7-adv-clone-branch-remotes",
                    "git-clone/branch",
                    "Branch copy, wired and checked",
                    ["git clone -b starter https://example.test/team/app.git", "git remote"],
                    required=["git clone", "git remote"],
                    forms=["git-remote/list"],
                    state="clone",
                    story=(
                        "Training week: copy the project down already stationed on its starter "
                        "branch, then read the remote names to confirm the copy stayed wired to "
                        "the team server."
                    ),
                    details=[{"label": "Branch to check out", "value": "starter"}],
                    evaluation={
                        "repository_initialized": True,
                        "head_branch": "starter",
                    },
                    checks=[
                        {
                            "label": "The copy is stationed on the starter branch.",
                            "requirement": {"head_branch": "starter"},
                        },
                        {
                            "label": "The remote wiring was confirmed.",
                            "requirement": {"required_commands": ["git remote"]},
                        },
                    ],
                ),
                _wave(
                    "ch7-adv-clone-depth-urls",
                    "git-clone/depth",
                    "Shallow copy, full wiring",
                    ["git clone --depth 1 https://example.test/team/app.git", "git remote -v"],
                    required=["git clone", "git remote -v"],
                    forms=["git-remote/verbose"],
                    state="clone",
                    story=(
                        "A build agent needs the project's current state with minimal history - "
                        "but its remote wiring must still be complete for later fetches. Copy "
                        "one snapshot deep, then verify the URLs."
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
                            "label": "The wiring was verified for later syncs.",
                            "requirement": {"required_commands": ["git remote -v"]},
                        },
                    ],
                ),
                _wave(
                    "ch7-adv-legacy-start-from-clone",
                    "git-checkout/legacy-create",
                    "Copy, then branch the old way",
                    ["git clone https://example.test/team/app.git", "git checkout -b feature/onboarding"],
                    required=["git clone", "git checkout -b"],
                    forms=["git-clone/default-folder"],
                    state="clone",
                    story=(
                        "Fresh copy, first task - and the onboarding guide you were handed "
                        "still teaches the older branch spelling. Follow it: copy the project "
                        "down, then create your working line the legacy way."
                    ),
                    details=[{"label": "New branch", "value": "feature/onboarding"}],
                    evaluation={
                        "repository_initialized": True,
                        "head_branch": "feature/onboarding",
                    },
                    checks=[
                        {
                            "label": "A complete local copy exists.",
                            "requirement": {"repository_initialized": True},
                        },
                        {
                            "label": "The working line was created with the legacy spelling.",
                            "requirement": {"head_branch": "feature/onboarding"},
                        },
                    ],
                ),
                _wave(
                    "ch7-adv-clone-named-fresh-line",
                    "git-clone/named-folder",
                    "Sandbox copy, sandbox line",
                    ["git clone https://example.test/team/app.git sandbox", "git switch -c experiment/sandbox"],
                    required=["git clone", "git switch -c"],
                    forms=["git-switch/create"],
                    state="clone",
                    story=(
                        "Risky experiment ahead: give it a disposable copy in a folder named "
                        "sandbox, and a disposable line of its own on top. Nothing this "
                        "experiment does should ever touch main."
                    ),
                    details=[
                        {"label": "Folder name", "value": "sandbox"},
                        {"label": "New branch", "value": "experiment/sandbox"},
                    ],
                    evaluation={
                        "repository_initialized": True,
                        "head_branch": "experiment/sandbox",
                        "rules": [
                            {
                                "type": "operation_metadata_equals",
                                "key": "last_clone_destination",
                                "value": "sandbox",
                            }
                        ],
                    },
                    checks=[
                        {
                            "label": "The disposable copy landed in the sandbox folder.",
                            "requirement": {
                                "rules": [
                                    {
                                        "type": "operation_metadata_equals",
                                        "key": "last_clone_destination",
                                        "value": "sandbox",
                                    }
                                ]
                            },
                        },
                        {
                            "label": "The experiment got its own disposable line.",
                            "requirement": {"head_branch": "experiment/sandbox"},
                        },
                    ],
                ),
                _wave(
                    "ch7-adv-clone-fresh-daily",
                    "git-clone/default-folder",
                    "Copy, check, read the story",
                    ["git clone https://example.test/team/app.git", "git status", "git log --oneline"],
                    required=["git clone", "git status", "git log"],
                    forms=["git-status/plain", "git-log/oneline"],
                    state="clone",
                    story=(
                        "The workshop routine you could do in your sleep by now: copy the "
                        "project, confirm the copy is clean, and read its compact history to "
                        "know where the team left off."
                    ),
                    evaluation={
                        "repository_initialized": True,
                        "working_tree_clean": True,
                        "staging_empty": True,
                    },
                    checks=[
                        {
                            "label": "The fresh copy was confirmed clean.",
                            "requirement": {"required_commands": ["git status"]},
                        },
                        {
                            "label": "The team's story so far was read.",
                            "requirement": {"required_commands": ["git log"]},
                        },
                    ],
                ),
                _wave(
                    "ch7-adv-clone-review-copy",
                    "git-clone/named-folder",
                    "Review copy, recent entries",
                    ["git clone https://example.test/team/app.git review-copy", "git log -n 2"],
                    required=["git clone", "git log"],
                    forms=["git-log/limit"],
                    state="clone",
                    story=(
                        "A code review deserves its own untouched copy. Bring the project down "
                        "into review-copy, then read exactly the two most recent history "
                        "entries the review will focus on."
                    ),
                    details=[{"label": "Folder name", "value": "review-copy"}],
                    evaluation={
                        "repository_initialized": True,
                        "rules": [
                            {
                                "type": "operation_metadata_equals",
                                "key": "last_clone_destination",
                                "value": "review-copy",
                            }
                        ],
                    },
                    checks=[
                        {
                            "label": "The review copy landed in its own folder.",
                            "requirement": {
                                "rules": [
                                    {
                                        "type": "operation_metadata_equals",
                                        "key": "last_clone_destination",
                                        "value": "review-copy",
                                    }
                                ]
                            },
                        },
                        {
                            "label": "The review's focus entries were read.",
                            "requirement": {"required_commands": ["git log"]},
                        },
                    ],
                ),
                _wave(
                    "ch7-adv-clone-training-again",
                    "git-clone/branch",
                    "Starter branch, newest snapshot",
                    ["git clone -b starter https://example.test/team/app.git", "git show"],
                    required=["git clone", "git show"],
                    forms=["git-show/head"],
                    state="clone",
                    story=(
                        "Second training cohort, same setup: copy the project stationed on its "
                        "starter branch, then open the newest snapshot there to see exactly "
                        "what state the exercises begin from."
                    ),
                    details=[{"label": "Branch to check out", "value": "starter"}],
                    evaluation={
                        "repository_initialized": True,
                        "head_branch": "starter",
                    },
                    checks=[
                        {
                            "label": "The copy is stationed on the starter branch.",
                            "requirement": {"head_branch": "starter"},
                        },
                        {
                            "label": "The starting snapshot was opened and read.",
                            "requirement": {"required_commands": ["git show"]},
                        },
                    ],
                ),
                _wave(
                    "ch7-adv-clone-ci-snapshot",
                    "git-clone/depth",
                    "CI copy, script-stable check",
                    ["git clone --depth 1 https://example.test/team/app.git", "git status --porcelain"],
                    required=["git clone", "git status --porcelain"],
                    forms=["git-status/porcelain"],
                    state="clone",
                    story=(
                        "The CI runner wants the project's current state, one snapshot deep, "
                        "then a script-stable state read it can parse before the build starts. "
                        "Do exactly that."
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
                            "label": "The state was read in script-stable form.",
                            "requirement": {"required_commands": ["git status --porcelain"]},
                        },
                    ],
                ),
            ],
        },
        {
            "slug": "fetch-before-acting",
            "title": "Fetch Before Acting",
            "waves": [
                _wave(
                    "ch7-adv-fetch-origin",
                    "git-fetch/origin",
                    "Fetch origin",
                    ["git fetch origin"],
                    state="remote",
                    story=(
                        "origin has moved ahead since the last sync, but the local main branch should "
                        "not jump forward on its own. Update the remote-tracking ref only."
                    ),
                    evaluation={
                        "rules": [
                            {"type": "fetch_updated_remote_tracking_without_moving_local", "branch": "main"},
                            {"type": "remote_branch_points_to", "remote_branch": "origin/main", "commit": "r2"},
                        ]
                    },
                    checks=[
                        {
                            "label": "origin/main updated to the remote's real tip, and local main did not move.",
                            "requirement": {
                                "rules": [
                                    {
                                        "type": "fetch_updated_remote_tracking_without_moving_local",
                                        "branch": "main",
                                    },
                                    {
                                        "type": "remote_branch_points_to",
                                        "remote_branch": "origin/main",
                                        "commit": "r2",
                                    },
                                ]
                            },
                        },
                    ],
                ),
                _wave(
                    "ch7-adv-fetch-prune",
                    "git-fetch/prune",
                    "Fetch prune",
                    ["git fetch --prune"],
                    state="remote-prune",
                    story=(
                        "A branch was deleted on origin a while ago, but this local repository still "
                        "shows a stale origin/old-feature tracking ref for it. Fetch and remove refs "
                        "for branches that no longer exist remotely."
                    ),
                    evaluation={"rules": [{"type": "remote_branch_absent", "remote_branch": "origin/old-feature"}]},
                    checks=[
                        {
                            "label": "The stale remote-tracking ref for the deleted branch is gone.",
                            "requirement": {
                                "rules": [
                                    {"type": "remote_branch_absent", "remote_branch": "origin/old-feature"}
                                ]
                            },
                        },
                    ],
                ),
                _wave(
                    "ch7-adv-fetch-then-branch",
                    "git-fetch/origin",
                    "Fetch then branch",
                    ["git fetch origin", "git branch feature/from-origin origin/main", "git switch feature/from-origin"],
                    required=["git fetch", "git branch", "git switch"],
                    forms=["git-branch/create-at-start", "git-switch/existing"],
                    state="remote",
                    story=(
                        "New work needs to start from exactly where origin currently is, not from "
                        "this local checkout's possibly-stale main. Fetch first, then branch from the "
                        "freshly updated remote-tracking ref."
                    ),
                    evaluation={
                        "head_branch": "feature/from-origin",
                        "rules": [
                            {"type": "remote_branch_points_to", "remote_branch": "origin/main", "commit": "r2"},
                            {"type": "branch_points_to", "branch": "feature/from-origin", "commit": "r2"},
                        ],
                    },
                    checks=[
                        {
                            "label": "The remote-tracking ref was refreshed with fetch before branching from it.",
                            "requirement": {
                                "rules": [
                                    {
                                        "type": "remote_branch_points_to",
                                        "remote_branch": "origin/main",
                                        "commit": "r2",
                                    }
                                ]
                            },
                        },
                        {
                            "label": "The new local branch starts exactly at the fetched remote tip.",
                            "requirement": {
                                "head_branch": "feature/from-origin",
                                "rules": [
                                    {
                                        "type": "branch_points_to",
                                        "branch": "feature/from-origin",
                                        "commit": "r2",
                                    }
                                ],
                            },
                        },
                    ],
                ),
                _wave(
                    "ch7-adv-fetch-then-inspect",
                    "git-fetch/origin",
                    "Refresh, then map both worlds",
                    ["git fetch origin", "git log --oneline --graph --all"],
                    required=["git fetch", "git log"],
                    forms=["git-log/graph-all"],
                    state="remote",
                    story=(
                        "Update what this repository knows about origin - without moving any "
                        "local branch - then draw the whole graph to see local refs and "
                        "remote-tracking refs side by side."
                    ),
                    evaluation={
                        "rules": [
                            {"type": "remote_branch_points_to", "remote_branch": "origin/main", "commit": "r2"},
                        ]
                    },
                    checks=[
                        {
                            "label": "The remote-tracking refs were refreshed.",
                            "requirement": {
                                "rules": [
                                    {
                                        "type": "remote_branch_points_to",
                                        "remote_branch": "origin/main",
                                        "commit": "r2",
                                    }
                                ]
                            },
                        },
                        {
                            "label": "Both worlds were mapped on one graph.",
                            "requirement": {"required_commands": ["git log"]},
                        },
                    ],
                ),
                _wave(
                    "ch7-adv-prune-audit",
                    "git-fetch/prune",
                    "Check the wiring, prune the dead",
                    ["git remote -v", "git fetch --prune"],
                    required=["git remote -v", "git fetch --prune"],
                    forms=["git-remote/verbose"],
                    state="remote-prune",
                    story=(
                        "Quarterly hygiene: verify which server this repository syncs with, "
                        "then refresh its remote-tracking refs while sweeping away the ones "
                        "whose branches no longer exist on origin."
                    ),
                    evaluation={
                        "rules": [{"type": "remote_branch_absent", "remote_branch": "origin/old-feature"}]
                    },
                    checks=[
                        {
                            "label": "The sync target was verified first.",
                            "requirement": {"required_commands": ["git remote -v"]},
                        },
                        {
                            "label": "The dead tracking ref is swept away.",
                            "requirement": {
                                "rules": [
                                    {"type": "remote_branch_absent", "remote_branch": "origin/old-feature"}
                                ]
                            },
                        },
                    ],
                ),
                _wave(
                    "ch7-adv-prune-then-graph",
                    "git-fetch/prune",
                    "Prune, then admire the graph",
                    ["git fetch --prune", "git log --oneline --graph --all"],
                    required=["git fetch --prune", "git log"],
                    forms=["git-log/graph-all"],
                    state="remote-prune",
                    story=(
                        "That stale tracking ref has haunted the graph for weeks. Sweep it "
                        "away with a pruning fetch, then draw the graph to see only living "
                        "branches remain."
                    ),
                    evaluation={
                        "rules": [{"type": "remote_branch_absent", "remote_branch": "origin/old-feature"}]
                    },
                    checks=[
                        {
                            "label": "The stale tracking ref is gone.",
                            "requirement": {
                                "rules": [
                                    {"type": "remote_branch_absent", "remote_branch": "origin/old-feature"}
                                ]
                            },
                        },
                        {
                            "label": "The cleaned graph was drawn afterward.",
                            "requirement": {"required_commands": ["git log"]},
                        },
                    ],
                ),
                _wave(
                    "ch7-adv-fresh-view-drill",
                    "git-fetch/prune",
                    "Names, prune, state",
                    ["git remote", "git fetch --prune", "git status"],
                    required=["git remote", "git fetch --prune", "git status"],
                    forms=["git-remote/list", "git-status/plain"],
                    state="remote-prune",
                    story=(
                        "The pre-sync ritual, end to end: read the remote names, refresh and "
                        "prune the tracking refs, then read the workspace state before any "
                        "real work begins."
                    ),
                    evaluation={
                        "rules": [{"type": "remote_branch_absent", "remote_branch": "origin/old-feature"}]
                    },
                    checks=[
                        {
                            "label": "The ritual ran: names, prune, state.",
                            "requirement": {
                                "required_commands": ["git remote", "git fetch --prune", "git status"]
                            },
                        },
                    ],
                ),
            ],
        },
    ]
