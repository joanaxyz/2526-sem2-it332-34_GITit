"""Chapter 7 authored adventure levels."""

from __future__ import annotations

from .common import *  # noqa: F403

REMOTE_LOCAL = repo(
    commits=[
        commit("c0", "Initial project", [], {"README.md": "base"}),
        commit("c1", "Local main work", ["c0"], {"README.md": "base", "src/app.py": "local"}),
        commit(
            "r2", "Remote update", ["c1"], {"README.md": "remote update", "src/app.py": "local"}
        ),
    ],
    branches={"main": "c1"},
    remotes={"origin": "https://example.test/team/app.git"},
    remote_branches={"origin/main": "c1"},
    remote_updates={"origin/main": "r2"},
    upstream_tracking={"main": "origin/main"},
)

PUSH_REPO = repo(
    commits=[
        commit("c0", "Initial project", [], {"README.md": "base"}),
        commit("c1", "Add feature", ["c0"], {"README.md": "base", "src/feature.py": "feature"}),
    ],
    branches={"main": "c0", "feature/payment": "c1"},
    head="feature/payment",
    remotes={"origin": "https://example.test/team/app.git"},
    remote_branches={"origin/main": "c0"},
)

LEVELS = [
    # Chapter 7 - Remotes and Collaboration
    q(
        "git-remote/verbose",
        "inspect-remote-urls",
        "Inspect remote URLs",
        "Before fetching or pushing, confirm which remote endpoint the repository is connected to.",
        "Inspect configured remote URLs without changing repository state.",
        [
            v(
                "remote-v-origin",
                "Origin remote",
                repo(commits=BASE, remotes={"origin": "https://example.test/team/app.git"}),
                ["git remote -v"],
                ev({"repository_state_unchanged": True}, required=["git remote -v"]),
            ),
            v(
                "remote-v-upstream",
                "Upstream remote",
                repo(
                    commits=BASE,
                    remotes={
                        "origin": "https://example.test/fork/app.git",
                        "upstream": "https://example.test/team/app.git",
                    },
                ),
                ["git remote -v"],
                ev({"repository_state_unchanged": True}, required=["git remote -v"]),
            ),
        ],
        checks=[
            {
                "label": "Remote URLs were inspected without mutation.",
                "requirement": {
                    "repository_state_unchanged": True,
                    "required_commands": ["git remote -v"],
                },
            }
        ],
        min_counted_commands=0,
        max_counted_commands=2,
    ),
    q(
        "git-fetch/origin",
        "fetch-origin-updates",
        "Fetch remote updates safely",
        "The remote may have new work, but you do not want to move your local branch yet.",
        "Update remote-tracking information while leaving the local branch where it is.",
        [
            v(
                "fetch-origin-main",
                "Fetch main",
                REMOTE_LOCAL,
                ["git fetch origin"],
                ev(
                    {
                        "remote_branch_exists": ["origin/main"],
                        "rules": [
                            {
                                "type": "fetch_updated_remote_tracking_without_moving_local",
                                "branch": "main",
                            }
                        ],
                    },
                    required=["git fetch"],
                ),
            ),
            v(
                "fetch-default-main",
                "Fetch default",
                REMOTE_LOCAL,
                ["git fetch"],
                ev(
                    {
                        "remote_branch_exists": ["origin/main"],
                        "rules": [
                            {
                                "type": "fetch_updated_remote_tracking_without_moving_local",
                                "branch": "main",
                            }
                        ],
                    },
                    required=["git fetch"],
                ),
            ),
        ],
        checks=[
            {
                "label": "Remote tracking updated and the local branch stayed still.",
                "requirement": {"remote_tracking_updated": True},
            }
        ],
        prerequisites=["inspect-remote-urls"],
        workflow=True,
    ),
    q(
        "git-fetch/prune",
        "fetch-and-prune-stale-refs",
        "Fetch and prune stale remote refs",
        "A deleted remote branch is still showing locally and should be cleaned from remote-tracking refs.",
        "Update remote-tracking information and remove stale refs.",
        [
            v(
                "fetch-prune-old",
                "Prune old feature",
                repo(
                    commits=BASE,
                    remotes={"origin": "https://example.test/team/app.git"},
                    remote_branches={"origin/main": "c0", "origin/old-feature": "c0"},
                    remote_stale_branches=["old-feature"],
                ),
                ["git fetch --prune"],
                ev(
                    {
                        "remote_branch_absent": ["origin/old-feature"],
                        "remote_tracking_updated": True,
                    },
                    required=["git fetch --prune"],
                ),
            ),
            v(
                "fetch-prune-bug",
                "Prune bugfix",
                repo(
                    commits=BASE,
                    remotes={"origin": "https://example.test/team/app.git"},
                    remote_branches={"origin/main": "c0", "origin/bugfix/old": "c0"},
                    remote_stale_branches=["origin/bugfix/old"],
                ),
                ["git fetch -p origin"],
                ev(
                    {
                        "remote_branch_absent": ["origin/bugfix/old"],
                        "remote_tracking_updated": True,
                    },
                    required=["git fetch -p"],
                ),
            ),
        ],
        checks=[
            {
                "label": "The stale remote-tracking branch is gone.",
                "requirement": {"remote_tracking_updated": True},
            }
        ],
        prerequisites=["fetch-origin-updates"],
        workflow=True,
    ),
    q(
        "git-pull/default",
        "pull-fast-forward-update",
        "Pull upstream work into the current branch",
        "Remote main has a new commit, and your local main can fast-forward cleanly.",
        "Integrate the upstream update into the current branch.",
        [
            v(
                "pull-main-update",
                "Pull main update",
                REMOTE_LOCAL,
                ["git pull"],
                ev(
                    {
                        "rules": [
                            {
                                "type": "pull_moved_local_to_upstream",
                                "branch": "main",
                                "upstream": "origin/main",
                            }
                        ],
                        "remote_tracking_updated": True,
                    },
                    required=["git pull"],
                ),
            ),
            v(
                "pull-origin-main",
                "Pull explicit main",
                REMOTE_LOCAL,
                ["git pull origin main"],
                ev(
                    {
                        "rules": [
                            {
                                "type": "pull_moved_local_to_upstream",
                                "branch": "main",
                                "upstream": "origin/main",
                            }
                        ],
                        "remote_tracking_updated": True,
                    },
                    required=["git pull"],
                ),
            ),
        ],
        checks=[
            {
                "label": "Upstream updates were pulled into the local branch.",
                "requirement": {"remote_tracking_updated": True},
            }
        ],
        prerequisites=["fetch-origin-updates"],
        workflow=True,
    ),
    q(
        "git-pull/rebase",
        "pull-with-rebase",
        "Pull with rebase",
        "Your local branch has work while the remote has advanced; the team wants a linear replay on top of upstream.",
        "Integrate upstream using rebase mode.",
        [
            v(
                "pull-rebase-main",
                "Rebase local work",
                repo(
                    commits=[
                        commit("c0", "Initial", [], {"README.md": "base"}),
                        commit("c1", "Remote setup", ["c0"], {"README.md": "remote"}),
                        commit(
                            "c2", "Local note", ["c0"], {"README.md": "base", "notes.md": "local"}
                        ),
                    ],
                    branches={"main": "c2"},
                    remotes={"origin": "https://example.test/team/app.git"},
                    remote_branches={"origin/main": "c1"},
                    upstream_tracking={"main": "origin/main"},
                ),
                ["git pull --rebase"],
                ev(
                    {
                        "rules": [
                            meta_equals("pull_strategy", "rebase"),
                            meta_equals("pull_rebased_onto", "c1"),
                        ],
                        "remote_tracking_updated": True,
                    },
                    required=["git pull --rebase"],
                ),
            ),
            v(
                "pull-rebase-explicit",
                "Rebase explicit",
                repo(
                    commits=[
                        commit("c0", "Initial", [], {"README.md": "base"}),
                        commit("c1", "Remote setup", ["c0"], {"README.md": "remote"}),
                        commit(
                            "c2", "Local note", ["c0"], {"README.md": "base", "notes.md": "local"}
                        ),
                    ],
                    branches={"main": "c2"},
                    remotes={"origin": "https://example.test/team/app.git"},
                    remote_branches={"origin/main": "c1"},
                    upstream_tracking={"main": "origin/main"},
                ),
                ["git pull --rebase origin main"],
                ev(
                    {
                        "rules": [
                            meta_equals("pull_strategy", "rebase"),
                            meta_equals("pull_rebased_onto", "c1"),
                        ],
                        "remote_tracking_updated": True,
                    },
                    required=["git pull --rebase"],
                ),
            ),
        ],
        checks=[
            {
                "label": "The pull used rebase mode.",
                "requirement": {"rules": [meta_equals("pull_strategy", "rebase")]},
            }
        ],
        prerequisites=["pull-fast-forward-update"],
        workflow=True,
    ),
    q(
        "git-push/upstream",
        "push-and-set-upstream",
        "Publish a new branch and set upstream",
        "A local feature branch is ready for review, and future pushes should know its upstream.",
        "Publish the branch to origin and set tracking.",
        [
            v(
                "push-u-payment",
                "Publish payment branch",
                PUSH_REPO,
                ["git push -u origin feature/payment"],
                ev(
                    {
                        "upstream_tracking": {"feature/payment": "origin/feature/payment"},
                        "rules": [
                            {
                                "type": "push_moved_remote_to_local_tip",
                                "branch": "feature/payment",
                                "remote_branch": "origin/feature/payment",
                            }
                        ],
                    },
                    required=["git push -u"],
                ),
                details=[{"label": "Branch to publish", "value": "feature/payment"}],
            ),
            v(
                "push-u-profile",
                "Publish profile branch",
                repo(
                    commits=PUSH_REPO["commits"],
                    branches={"main": "c0", "feature/profile": "c1"},
                    head="feature/profile",
                    remotes={"origin": "https://example.test/team/app.git"},
                    remote_branches={"origin/main": "c0"},
                ),
                ["git push --set-upstream origin feature/profile"],
                ev(
                    {
                        "upstream_tracking": {"feature/profile": "origin/feature/profile"},
                        "rules": [
                            {
                                "type": "push_moved_remote_to_local_tip",
                                "branch": "feature/profile",
                                "remote_branch": "origin/feature/profile",
                            }
                        ],
                    },
                    required=["git push --set-upstream"],
                ),
                details=[{"label": "Branch to publish", "value": "feature/profile"}],
            ),
        ],
        checks=[
            {
                "label": "The branch was published to origin with upstream tracking.",
                "requirement": {
                    "rules": [
                        {
                            "type": "operation_metadata_not_equals",
                            "key": "last_push_remote_branch",
                            "value": None,
                        }
                    ]
                },
            }
        ],
        prerequisites=["inspect-remote-urls"],
        workflow=True,
    ),
    q(
        "git-push/current",
        "push-current-branch",
        "Push a tracked branch",
        "The branch already tracks a remote branch, so the new local commit can be published directly.",
        "Publish the current branch to its remote counterpart.",
        [
            v(
                "push-current-main",
                "Push main",
                repo(
                    commits=PUSH_REPO["commits"],
                    branches={"main": "c1"},
                    remotes={"origin": "https://example.test/team/app.git"},
                    remote_branches={"origin/main": "c0"},
                    upstream_tracking={"main": "origin/main"},
                ),
                ["git push"],
                ev(
                    {
                        "rules": [
                            {
                                "type": "push_moved_remote_to_local_tip",
                                "branch": "main",
                                "remote_branch": "origin/main",
                            }
                        ]
                    },
                    required=["git push"],
                ),
            ),
            v(
                "push-current-feature",
                "Push feature",
                {
                    **copy.deepcopy(PUSH_REPO),
                    "upstream_tracking": {"feature/payment": "origin/feature/payment"},
                    "remote_branches": {"origin/main": "c0", "origin/feature/payment": "c0"},
                },
                ["git push"],
                ev(
                    {
                        "rules": [
                            {
                                "type": "push_moved_remote_to_local_tip",
                                "branch": "feature/payment",
                                "remote_branch": "origin/feature/payment",
                            }
                        ]
                    },
                    required=["git push"],
                ),
            ),
        ],
        checks=[
            {
                "label": "The branch was published to its remote.",
                "requirement": {
                    "rules": [
                        {
                            "type": "operation_metadata_not_equals",
                            "key": "last_push_remote_branch",
                            "value": None,
                        }
                    ]
                },
            }
        ],
        prerequisites=["push-and-set-upstream"],
        workflow=True,
    ),
    q(
        "git-push/force-with-lease",
        "force-with-lease-after-rewrite",
        "Force safely after local rewrite",
        "A local branch was intentionally rewritten, and the safer force mode should update the remote.",
        "Publish the rewritten local tip with lease protection.",
        [
            v(
                "push-lease-feature",
                "Lease feature",
                {
                    **copy.deepcopy(PUSH_REPO),
                    "remote_branches": {"origin/main": "c0", "origin/feature/payment": "old1"},
                    "upstream_tracking": {"feature/payment": "origin/feature/payment"},
                },
                ["git push --force-with-lease"],
                ev(
                    {
                        "rules": [
                            meta_equals("force_push_with_lease", True),
                            {
                                "type": "push_moved_remote_to_local_tip",
                                "branch": "feature/payment",
                                "remote_branch": "origin/feature/payment",
                            },
                        ]
                    },
                    required=["git push --force-with-lease"],
                ),
            ),
            v(
                "push-lease-main",
                "Lease main",
                repo(
                    commits=PUSH_REPO["commits"],
                    branches={"main": "c1"},
                    remotes={"origin": "https://example.test/team/app.git"},
                    remote_branches={"origin/main": "old1"},
                    upstream_tracking={"main": "origin/main"},
                ),
                ["git push --force-with-lease origin main"],
                ev(
                    {
                        "rules": [
                            meta_equals("force_push_with_lease", True),
                            {
                                "type": "push_moved_remote_to_local_tip",
                                "branch": "main",
                                "remote_branch": "origin/main",
                            },
                        ]
                    },
                    required=["git push --force-with-lease"],
                ),
            ),
        ],
        checks=[
            {
                "label": "The push used lease-protected force mode.",
                "requirement": {"rules": [meta_equals("force_push_with_lease", True)]},
            }
        ],
        prerequisites=["push-current-branch"],
        workflow=True,
    ),
    q(
        "git-push/delete",
        "delete-remote-branch",
        "Delete a remote branch",
        "A review branch was merged and should be removed from the remote list.",
        "Delete the requested branch from origin.",
        [
            v(
                "push-del-payment",
                "Delete payment remote",
                repo(
                    commits=PUSH_REPO["commits"],
                    branches={"main": "c1"},
                    remotes={"origin": "https://example.test/team/app.git"},
                    remote_branches={"origin/main": "c1", "origin/feature/payment": "c1"},
                ),
                ["git push origin --delete feature/payment"],
                ev(
                    {
                        "remote_branch_absent": ["origin/feature/payment"],
                        "rules": [meta_equals("remote_branch_deleted", "feature/payment")],
                    },
                    required=["git push"],
                ),
                details=[{"label": "Remote branch to delete", "value": "feature/payment"}],
            ),
            v(
                "push-del-profile",
                "Delete profile remote",
                repo(
                    commits=PUSH_REPO["commits"],
                    branches={"main": "c1"},
                    remotes={"origin": "https://example.test/team/app.git"},
                    remote_branches={"origin/main": "c1", "origin/feature/profile": "c1"},
                ),
                ["git push origin --delete feature/profile"],
                ev(
                    {
                        "remote_branch_absent": ["origin/feature/profile"],
                        "rules": [meta_equals("remote_branch_deleted", "feature/profile")],
                    },
                    required=["git push"],
                ),
                details=[{"label": "Remote branch to delete", "value": "feature/profile"}],
            ),
        ],
        checks=[
            {
                "label": "The requested remote branch was deleted.",
                "requirement": {
                    "rules": [
                        {
                            "type": "operation_metadata_not_equals",
                            "key": "remote_branch_deleted",
                            "value": None,
                        }
                    ]
                },
            }
        ],
        prerequisites=["push-and-set-upstream"],
        workflow=True,
    ),
]
