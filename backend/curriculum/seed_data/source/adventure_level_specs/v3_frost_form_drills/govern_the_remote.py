"""Frostbound Citadel Chapter 6: Govern the Remote form drills."""

from __future__ import annotations

from ..common import q
from ..form_drill_support import (
    CORE_FORM_TAGS,
    GRAPH_COMMAND,
    STATUS_COMMAND,
    build_clean_form_state,
    build_drill_variants,
    build_read_evaluation,
    build_requirement_evaluation,
    required_command_check,
)
from ._fixtures import (
    _behind_remote,
    _meta,
    _meta_set,
    _retire_remote,
    _stale_remote,
)


DRILLS = [
    q(
        "git-branch/tracking",
        "fg-intro-branch-vv",
        "Read the upstream tracking table",
        "Before anything is pulled or pushed, find out which local branches track which upstream branches and how far ahead or behind each one sits.",
        "Show upstream tracking information for every local branch.",
        build_drill_variants("fg-intro-branch-vv", build_clean_form_state, ["git branch -vv"], build_read_evaluation(["git branch -vv"])),
        checks=[required_command_check("Upstream tracking was inspected.", ["git branch -vv"])],
        adventure="frost-govern-the-remote-drills",
    ),
    q(
        "git-fetch/all-advanced",
        "fg-intro-fetch-all",
        "Fetch from every remote",
        "Several remotes may hold newer work than your local copies show. Update the remote-tracking refs from every configured remote in one command.",
        "Fetch from all configured remotes.",
        build_drill_variants(
            "fg-intro-fetch-all",
            build_clean_form_state,
            ["git fetch --all"],
            build_requirement_evaluation({}, ["git fetch --all"], rules=[_meta("last_fetch_all", True)]),
        ),
        checks=[
            {
                "label": "Every remote's refs were refreshed.",
                "requirement": {"rules": [_meta("last_fetch_all", True)]},
            }
        ],
        adventure="frost-govern-the-remote-drills",
        workflow=True,
    ),
    q(
        "git-fetch/prune-advanced",
        "fg-intro-fetch-prune",
        "Fetch and remove stale tracking refs",
        "The branch old-experiment was deleted on the remote, but your repository still shows a tracking ref for it. Fetch with pruning so refs that no longer exist upstream disappear locally.",
        "Fetch updates and prune tracking refs that were deleted upstream.",
        build_drill_variants(
            "fg-intro-fetch-prune",
            _stale_remote,
            ["git fetch --prune"],
            build_requirement_evaluation({}, ["git fetch --prune"], rules=[_meta_set("fetch_pruned_refs")]),
        ),
        checks=[
            {
                "label": "Stale remote-tracking refs were pruned.",
                "requirement": {"rules": [_meta_set("fetch_pruned_refs")]},
            }
        ],
        details=["old-experiment"],
        adventure="frost-govern-the-remote-drills",
        workflow=True,
    ),
    q(
        "git-pull/ff-only-advanced",
        "fg-intro-pull-ff-only",
        "Pull only if it can fast-forward",
        "The remote has newer commits and your local main has none of its own. Pull with the fast-forward-only rule so the branch advances only if no merge commit would be invented.",
        "Pull upstream work using the fast-forward-only rule.",
        build_drill_variants(
            "fg-intro-pull-ff-only",
            _behind_remote,
            ["git pull --ff-only"],
            build_requirement_evaluation({}, ["git pull --ff-only"], rules=[_meta("pull_strategy", "ff-only")]),
        ),
        checks=[
            {
                "label": "The branch advanced with a plain fast-forward.",
                "requirement": {"rules": [_meta("pull_strategy", "ff-only")]},
            }
        ],
        adventure="frost-govern-the-remote-drills",
        workflow=True,
    ),
    q(
        "git-pull/rebase-advanced",
        "fg-intro-pull-rebase",
        "Pull with rebase",
        "The remote moved ahead while your local commits were in progress. Pull with the rebase rule so your local commits are replayed on top of the newer upstream history.",
        "Pull upstream work, replaying local commits on top.",
        build_drill_variants(
            "fg-intro-pull-rebase",
            _behind_remote,
            ["git pull --rebase"],
            build_requirement_evaluation({}, ["git pull --rebase"], rules=[_meta("pull_strategy", "rebase")]),
        ),
        checks=[
            {
                "label": "Local work was replayed on top of upstream.",
                "requirement": {"rules": [_meta("pull_strategy", "rebase")]},
            }
        ],
        adventure="frost-govern-the-remote-drills",
        workflow=True,
    ),
    q(
        "git-push/force-with-lease-advanced",
        "fg-intro-push-lease",
        "Publish rewritten history safely",
        "A reviewed rewrite must replace the published branch — but only if nobody pushed something newer in the meantime. Push with the force-with-lease guard instead of a plain force.",
        "Publish the rewritten branch with force-with-lease.",
        build_drill_variants(
            "fg-intro-push-lease",
            build_clean_form_state,
            ["git push --force-with-lease"],
            build_requirement_evaluation({}, ["git push --force-with-lease"], rules=[_meta("force_with_lease", True)]),
        ),
        checks=[
            {
                "label": "The rewrite was published under the lease guard.",
                "requirement": {"rules": [_meta("force_with_lease", True)]},
            }
        ],
        adventure="frost-govern-the-remote-drills",
        workflow=True,
    ),
    q(
        "git-push/delete-advanced",
        "fg-intro-push-delete",
        "Delete a branch on the remote",
        "The experiment is finished and its published branch old-experiment must not attract new work. Delete that branch from the origin remote.",
        "Delete the branch old-experiment from origin.",
        build_drill_variants(
            "fg-intro-push-delete",
            _stale_remote,
            ["git push origin --delete old-experiment"],
            build_requirement_evaluation({}, ["git push origin --delete"], rules=[_meta("remote_branch_deleted", "old-experiment")]),
        ),
        checks=[
            {
                "label": "The retired branch is gone from the remote.",
                "requirement": {"rules": [_meta_set("remote_branch_deleted")]},
            }
        ],
        details=["old-experiment"],
        adventure="frost-govern-the-remote-drills",
        workflow=True,
    ),
    q(
        "git-remote/set-url-advanced",
        "fg-intro-set-url",
        "Point origin at a new URL",
        "The project's hosting moved to a new server. Change the origin remote's URL to https://relay.frost.test/operations.git so future syncs reach the right place.",
        "Change origin's URL to the new address.",
        build_drill_variants(
            "fg-intro-set-url",
            build_clean_form_state,
            ["git remote set-url origin https://relay.frost.test/operations.git"],
            build_requirement_evaluation(
                {},
                ["git remote set-url"],
                rules=[{"type": "remote_url_matches", "remote": "origin", "url": "https://relay.frost.test/operations.git"}],
            ),
        ),
        checks=[
            {
                "label": "Origin points at the new address.",
                "requirement": {
                    "rules": [
                        {"type": "remote_url_matches", "remote": "origin", "url": "https://relay.frost.test/operations.git"}
                    ]
                },
            }
        ],
        details=["https://relay.frost.test/operations.git"],
        adventure="frost-govern-the-remote-drills",
        workflow=True,
    ),
]

WORKFLOWS = [
    q(
        "git-fetch/all-advanced",
        "fg-apply-survey-then-sweep",
        "Read tracking, then fetch everything",
        "Read the tracking table first, then refresh every remote's refs in one sweep and check what changed.",
        "Inspect tracking, fetch from all remotes, then verify the state.",
        build_drill_variants(
            "fg-apply-survey-then-sweep",
            build_clean_form_state,
            ["git branch -vv", "git fetch --all", STATUS_COMMAND, GRAPH_COMMAND],
            build_requirement_evaluation(
                {},
                ["git branch -vv", "git fetch --all", "git status", "git log"],
                rules=[_meta("last_fetch_all", True)],
            ),
        ),
        checks=[
            required_command_check("The tracking table was read first.", ["git branch -vv"]),
            {
                "label": "Every remote's refs were refreshed.",
                "requirement": {"rules": [_meta("last_fetch_all", True)]},
            },
        ],
        command_forms=["git-branch/tracking", *CORE_FORM_TAGS],
        adventure="frost-govern-the-remote-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-fetch/prune-advanced",
        "fg-apply-clean-the-board",
        "Read tracking, then prune stale refs",
        "Read the tracking table, then fetch with pruning so the deleted old-experiment ref disappears, and confirm the cleaned picture.",
        "Inspect tracking, fetch with pruning, then verify the state.",
        build_drill_variants(
            "fg-apply-clean-the-board",
            _stale_remote,
            ["git branch -vv", "git fetch --prune", STATUS_COMMAND, GRAPH_COMMAND],
            build_requirement_evaluation(
                {},
                ["git branch -vv", "git fetch --prune", "git status", "git log"],
                rules=[_meta_set("fetch_pruned_refs")],
            ),
        ),
        checks=[
            required_command_check("The tracking table was read first.", ["git branch -vv"]),
            {
                "label": "Stale remote-tracking refs were pruned.",
                "requirement": {"rules": [_meta_set("fetch_pruned_refs")]},
            },
        ],
        details=["old-experiment"],
        command_forms=["git-branch/tracking", *CORE_FORM_TAGS],
        adventure="frost-govern-the-remote-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-pull/ff-only-advanced",
        "fg-apply-guarded-advance",
        "Fetch everything, then pull safely",
        "Refresh every remote's refs, then advance main under the fast-forward-only rule and confirm the branch landed on the remote's newest commit.",
        "Fetch all remotes, pull with the fast-forward rule, then verify.",
        build_drill_variants(
            "fg-apply-guarded-advance",
            _behind_remote,
            ["git fetch --all", "git pull --ff-only", STATUS_COMMAND, GRAPH_COMMAND],
            build_requirement_evaluation(
                {},
                ["git fetch --all", "git pull --ff-only", "git status", "git log"],
                rules=[_meta("pull_strategy", "ff-only")],
            ),
        ),
        checks=[
            required_command_check("The remote refs were refreshed first.", ["git fetch --all"]),
            {
                "label": "The branch advanced with a plain fast-forward.",
                "requirement": {"rules": [_meta("pull_strategy", "ff-only")]},
            },
        ],
        command_forms=["git-fetch/all-advanced", *CORE_FORM_TAGS],
        adventure="frost-govern-the-remote-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-pull/rebase-advanced",
        "fg-apply-replay-over-upstream",
        "Read tracking, then pull with rebase",
        "Read the tracking table, then pull with the rebase rule so local work is replayed over the remote's newer history. Confirm the straightened history afterward.",
        "Inspect tracking, pull with rebase, then verify the history.",
        build_drill_variants(
            "fg-apply-replay-over-upstream",
            _behind_remote,
            ["git branch -vv", "git pull --rebase", STATUS_COMMAND, GRAPH_COMMAND],
            build_requirement_evaluation(
                {},
                ["git branch -vv", "git pull --rebase", "git status", "git log"],
                rules=[_meta("pull_strategy", "rebase")],
            ),
        ),
        checks=[
            required_command_check("The tracking table was read first.", ["git branch -vv"]),
            {
                "label": "Local work was replayed on top of upstream.",
                "requirement": {"rules": [_meta("pull_strategy", "rebase")]},
            },
        ],
        command_forms=["git-branch/tracking", *CORE_FORM_TAGS],
        adventure="frost-govern-the-remote-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-push/force-with-lease-advanced",
        "fg-apply-leased-publication",
        "Check tracking, then publish the rewrite",
        "Read the tracking table, publish the reviewed rewrite under the lease guard, and confirm the published state matches the local branch.",
        "Inspect tracking, push with force-with-lease, then verify.",
        build_drill_variants(
            "fg-apply-leased-publication",
            build_clean_form_state,
            ["git branch -vv", "git push --force-with-lease", STATUS_COMMAND, GRAPH_COMMAND],
            build_requirement_evaluation(
                {},
                ["git branch -vv", "git push --force-with-lease", "git status", "git log"],
                rules=[_meta("force_with_lease", True)],
            ),
        ),
        checks=[
            required_command_check("The tracking table was read first.", ["git branch -vv"]),
            {
                "label": "The rewrite was published under the lease guard.",
                "requirement": {"rules": [_meta("force_with_lease", True)]},
            },
        ],
        command_forms=["git-branch/tracking", *CORE_FORM_TAGS],
        adventure="frost-govern-the-remote-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-push/force-with-lease-advanced",
        "fg-apply-refresh-then-lease",
        "Fetch first, then take the lease",
        "Refresh every remote's refs so the lease is taken against current knowledge, then publish the rewrite and verify the result.",
        "Fetch all remotes, push with force-with-lease, then verify.",
        build_drill_variants(
            "fg-apply-refresh-then-lease",
            build_clean_form_state,
            ["git fetch --all", "git push --force-with-lease", STATUS_COMMAND, GRAPH_COMMAND],
            build_requirement_evaluation(
                {},
                ["git fetch --all", "git push --force-with-lease", "git status", "git log"],
                rules=[_meta("force_with_lease", True)],
            ),
        ),
        checks=[
            required_command_check("Remote knowledge was refreshed before the lease.", ["git fetch --all"]),
            {
                "label": "The rewrite was published under the lease guard.",
                "requirement": {"rules": [_meta("force_with_lease", True)]},
            },
        ],
        command_forms=["git-fetch/all-advanced", *CORE_FORM_TAGS],
        adventure="frost-govern-the-remote-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-push/delete-advanced",
        "fg-apply-prune-then-retire",
        "Prune first, then delete the branch",
        "Fetch with pruning to clear the already-deleted tmp-probe ref, then delete the retired old-experiment branch from origin and confirm the result.",
        "Fetch with pruning, delete the remote branch, then verify.",
        build_drill_variants(
            "fg-apply-prune-then-retire",
            _retire_remote,
            ["git fetch --prune", "git push origin --delete old-experiment", STATUS_COMMAND, GRAPH_COMMAND],
            build_requirement_evaluation(
                {},
                ["git fetch --prune", "git push origin --delete", "git status", "git log"],
                rules=[_meta("remote_branch_deleted", "old-experiment")],
            ),
        ),
        checks=[
            required_command_check("The remote picture was pruned first.", ["git fetch --prune"]),
            {
                "label": "The retired branch is gone from the remote.",
                "requirement": {"rules": [_meta_set("remote_branch_deleted")]},
            },
        ],
        details=["old-experiment"],
        command_forms=["git-fetch/prune-advanced", *CORE_FORM_TAGS],
        adventure="frost-govern-the-remote-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-push/delete-advanced",
        "fg-apply-survey-then-retire",
        "Check tracking, then delete deliberately",
        "Read the tracking table, delete the retired old-experiment branch from origin, and confirm the deletion registered.",
        "Inspect tracking, delete the remote branch, then verify.",
        build_drill_variants(
            "fg-apply-survey-then-retire",
            _stale_remote,
            ["git branch -vv", "git push origin --delete old-experiment", STATUS_COMMAND, GRAPH_COMMAND],
            build_requirement_evaluation(
                {},
                ["git branch -vv", "git push origin --delete", "git status", "git log"],
                rules=[_meta("remote_branch_deleted", "old-experiment")],
            ),
        ),
        checks=[
            required_command_check("The tracking table was read first.", ["git branch -vv"]),
            {
                "label": "The retired branch is gone from the remote.",
                "requirement": {"rules": [_meta_set("remote_branch_deleted")]},
            },
        ],
        details=["old-experiment"],
        command_forms=["git-branch/tracking", *CORE_FORM_TAGS],
        adventure="frost-govern-the-remote-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-remote/set-url-advanced",
        "fg-apply-repoint-and-verify",
        "Change the URL, then verify tracking",
        "Point origin at the new address https://relay.frost.test/operations.git, then read the tracking table to confirm everything still lines up.",
        "Change origin's URL, inspect tracking, then verify the state.",
        build_drill_variants(
            "fg-apply-repoint-and-verify",
            build_clean_form_state,
            ["git remote set-url origin https://relay.frost.test/operations.git", "git branch -vv", STATUS_COMMAND, GRAPH_COMMAND],
            build_requirement_evaluation(
                {},
                ["git remote set-url", "git branch -vv", "git status", "git log"],
                rules=[{"type": "remote_url_matches", "remote": "origin", "url": "https://relay.frost.test/operations.git"}],
            ),
        ),
        checks=[
            {
                "label": "Origin points at the new address.",
                "requirement": {
                    "rules": [
                        {"type": "remote_url_matches", "remote": "origin", "url": "https://relay.frost.test/operations.git"}
                    ]
                },
            },
            required_command_check("The tracking table was verified afterward.", ["git branch -vv"]),
        ],
        details=["https://relay.frost.test/operations.git"],
        command_forms=["git-branch/tracking", *CORE_FORM_TAGS],
        adventure="frost-govern-the-remote-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-remote/set-url-advanced",
        "fg-apply-migrate-the-mirror",
        "Switch to the mirror URL",
        "The primary server is down for maintenance, so syncs must temporarily go through the mirror. Point origin at https://mirror.frost.test/operations.git and verify the state.",
        "Change origin's URL to the mirror address and verify the state.",
        build_drill_variants(
            "fg-apply-migrate-the-mirror",
            build_clean_form_state,
            [STATUS_COMMAND, "git remote set-url origin https://mirror.frost.test/operations.git", GRAPH_COMMAND],
            build_requirement_evaluation(
                {},
                ["git status", "git remote set-url", "git log"],
                rules=[{"type": "remote_url_matches", "remote": "origin", "url": "https://mirror.frost.test/operations.git"}],
            ),
        ),
        checks=[
            {
                "label": "Origin points at the mirror address.",
                "requirement": {
                    "rules": [
                        {"type": "remote_url_matches", "remote": "origin", "url": "https://mirror.frost.test/operations.git"}
                    ]
                },
            },
            required_command_check("The switch was verified.", ["git log"]),
        ],
        details=["https://mirror.frost.test/operations.git"],
        command_forms=CORE_FORM_TAGS,
        adventure="frost-govern-the-remote-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-pull/ff-only-advanced",
        "fg-apply-prune-then-advance",
        "Prune, then pull under the guard",
        "Fetch with pruning so the picture is honest, then advance main under the fast-forward-only rule and verify the landing.",
        "Fetch with pruning, pull with the fast-forward rule, then verify.",
        build_drill_variants(
            "fg-apply-prune-then-advance",
            _behind_remote,
            ["git fetch --prune", "git pull --ff-only", STATUS_COMMAND, GRAPH_COMMAND],
            build_requirement_evaluation(
                {},
                ["git fetch --prune", "git pull --ff-only", "git status", "git log"],
                rules=[_meta("pull_strategy", "ff-only")],
            ),
        ),
        checks=[
            required_command_check("The remote picture was pruned first.", ["git fetch --prune"]),
            {
                "label": "The branch advanced with a plain fast-forward.",
                "requirement": {"rules": [_meta("pull_strategy", "ff-only")]},
            },
        ],
        command_forms=["git-fetch/prune-advanced", *CORE_FORM_TAGS],
        adventure="frost-govern-the-remote-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-pull/rebase-advanced",
        "fg-apply-sweep-then-replay",
        "Fetch everything, then pull with rebase",
        "Refresh every remote's refs, then pull with the rebase rule and confirm local work now sits on top of the remote's newest history.",
        "Fetch all remotes, pull with rebase, then verify the history.",
        build_drill_variants(
            "fg-apply-sweep-then-replay",
            _behind_remote,
            ["git fetch --all", "git pull --rebase", STATUS_COMMAND, GRAPH_COMMAND],
            build_requirement_evaluation(
                {},
                ["git fetch --all", "git pull --rebase", "git status", "git log"],
                rules=[_meta("pull_strategy", "rebase")],
            ),
        ),
        checks=[
            required_command_check("The remote refs were refreshed first.", ["git fetch --all"]),
            {
                "label": "Local work was replayed on top of upstream.",
                "requirement": {"rules": [_meta("pull_strategy", "rebase")]},
            },
        ],
        command_forms=["git-fetch/all-advanced", *CORE_FORM_TAGS],
        adventure="frost-govern-the-remote-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
]

