"""Blueprint adventure levels for publish-work."""

from __future__ import annotations

from .helpers import _wave

ADVENTURE_LEVELS = [
        {
            "slug": "publish-work",
            "title": "Publish Work",
            "waves": [
                _wave(
                    "ch7-adv-push-set-upstream",
                    "git-push/upstream",
                    "Push set upstream",
                    ["git push -u origin feature/payment"],
                    state="push",
                    story=(
                        "feature/payment only exists locally so far. Publish it to origin for the "
                        "first time and set up tracking so future push/pull need no arguments."
                    ),
                    evaluation={
                        "rules": [
                            {"type": "upstream_tracking_set", "branch": "feature/payment"},
                            {
                                "type": "remote_branch_matches_local",
                                "remote_branch": "origin/feature/payment",
                                "branch": "feature/payment",
                            },
                        ]
                    },
                    checks=[
                        {
                            "label": "feature/payment now exists on origin and matches the local tip.",
                            "requirement": {
                                "rules": [
                                    {
                                        "type": "remote_branch_matches_local",
                                        "remote_branch": "origin/feature/payment",
                                        "branch": "feature/payment",
                                    }
                                ]
                            },
                        },
                        {
                            "label": "Upstream tracking is set for feature/payment.",
                            "requirement": {
                                "rules": [{"type": "upstream_tracking_set", "branch": "feature/payment"}]
                            },
                        },
                    ],
                ),
                _wave(
                    "ch7-adv-push-current",
                    "git-push/current",
                    "Push current",
                    ["git push"],
                    state="push-tracked",
                    story=(
                        "feature/payment already tracks its remote counterpart, and a new commit is "
                        "ready to share. Publish it with a plain push."
                    ),
                    evaluation={
                        "rules": [
                            {
                                "type": "remote_branch_matches_local",
                                "remote_branch": "origin/feature/payment",
                                "branch": "feature/payment",
                            }
                        ]
                    },
                    checks=[
                        {
                            "label": "The remote branch advances to match the new local commit.",
                            "requirement": {
                                "rules": [
                                    {
                                        "type": "remote_branch_matches_local",
                                        "remote_branch": "origin/feature/payment",
                                        "branch": "feature/payment",
                                    }
                                ]
                            },
                        },
                    ],
                ),
                _wave(
                    "ch7-adv-force-with-lease",
                    "git-push/force-with-lease",
                    "Force with lease",
                    ["git push --force-with-lease"],
                    state="push-tracked",
                    story=(
                        "A deliberate local rewrite needs to reach origin, but only if nobody else has "
                        "pushed to feature/payment since the last fetch. Publish it with the safety "
                        "check in place, not a bare force push."
                    ),
                    evaluation={
                        "rules": [
                            {"type": "operation_metadata_equals", "key": "force_with_lease", "value": True},
                            {
                                "type": "remote_branch_matches_local",
                                "remote_branch": "origin/feature/payment",
                                "branch": "feature/payment",
                            },
                        ]
                    },
                    checks=[
                        {
                            "label": "The rewrite published only under the force-with-lease safety check.",
                            "requirement": {
                                "rules": [
                                    {
                                        "type": "operation_metadata_equals",
                                        "key": "force_with_lease",
                                        "value": True,
                                    }
                                ]
                            },
                        },
                        {
                            "label": "The remote branch now matches the rewritten local tip.",
                            "requirement": {
                                "rules": [
                                    {
                                        "type": "remote_branch_matches_local",
                                        "remote_branch": "origin/feature/payment",
                                        "branch": "feature/payment",
                                    }
                                ]
                            },
                        },
                    ],
                ),
                _wave(
                    "ch7-adv-delete-remote-branch",
                    "git-push/delete",
                    "Delete remote branch",
                    ["git push origin --delete feature/payment"],
                    state="push-delete",
                    story=(
                        "feature/payment has already been merged and abandoned locally, but its remote "
                        "counterpart is still sitting on origin. Remove the remote branch."
                    ),
                    evaluation={"rules": [{"type": "remote_branch_absent", "remote_branch": "origin/feature/payment"}]},
                    checks=[
                        {
                            "label": "The merged branch's remote counterpart is removed from origin.",
                            "requirement": {
                                "rules": [
                                    {"type": "remote_branch_absent", "remote_branch": "origin/feature/payment"}
                                ]
                            },
                        },
                    ],
                ),
                _wave(
                    "ch7-adv-push-after-commit",
                    "git-push/current",
                    "Read the unshared work, then share",
                    ["git log -n 1", "git push"],
                    required=["git log", "git push"],
                    forms=["git-log/limit"],
                    state="push-tracked",
                    story=(
                        "One finished commit sits on the tracked branch, still unshared. Read "
                        "exactly that one entry to know what is about to go out, then share it "
                        "with a plain push."
                    ),
                    evaluation={
                        "rules": [
                            {
                                "type": "remote_branch_matches_local",
                                "remote_branch": "origin/feature/payment",
                                "branch": "feature/payment",
                            }
                        ],
                    },
                    checks=[
                        {
                            "label": "The outgoing commit was read before sharing.",
                            "requirement": {"required_commands": ["git log"]},
                        },
                        {
                            "label": "The remote branch matches the local tip.",
                            "requirement": {
                                "rules": [
                                    {
                                        "type": "remote_branch_matches_local",
                                        "remote_branch": "origin/feature/payment",
                                        "branch": "feature/payment",
                                    }
                                ]
                            },
                        },
                    ],
                ),
                _wave(
                    "ch7-adv-push-status-loop",
                    "git-push/current",
                    "Check, then share",
                    ["git status", "git push"],
                    required=["git status", "git push"],
                    forms=["git-status/plain"],
                    state="push-tracked",
                    story=(
                        "A finished commit is waiting to be shared from the tracked branch. "
                        "Read the state to confirm nothing else is in flight, then publish it "
                        "with a plain push."
                    ),
                    evaluation={
                        "rules": [
                            {
                                "type": "remote_branch_matches_local",
                                "remote_branch": "origin/feature/payment",
                                "branch": "feature/payment",
                            }
                        ]
                    },
                    checks=[
                        {
                            "label": "The state was read before sharing.",
                            "requirement": {"required_commands": ["git status"]},
                        },
                        {
                            "label": "The remote branch matches the local tip.",
                            "requirement": {
                                "rules": [
                                    {
                                        "type": "remote_branch_matches_local",
                                        "remote_branch": "origin/feature/payment",
                                        "branch": "feature/payment",
                                    }
                                ]
                            },
                        },
                    ],
                ),
                _wave(
                    "ch7-adv-push-quick",
                    "git-push/current",
                    "Share, then confirm calm",
                    ["git push", "git status"],
                    required=["git push", "git status"],
                    forms=["git-status/plain"],
                    state="push-tracked",
                    story=(
                        "The commit is ready and review starts in five minutes. Publish it "
                        "with a plain push, then read the state to confirm local and upstream "
                        "agree."
                    ),
                    evaluation={
                        "rules": [
                            {
                                "type": "remote_branch_matches_local",
                                "remote_branch": "origin/feature/payment",
                                "branch": "feature/payment",
                            }
                        ]
                    },
                    checks=[
                        {
                            "label": "The remote branch matches the local tip.",
                            "requirement": {
                                "rules": [
                                    {
                                        "type": "remote_branch_matches_local",
                                        "remote_branch": "origin/feature/payment",
                                        "branch": "feature/payment",
                                    }
                                ]
                            },
                        },
                        {
                            "label": "The agreement was confirmed afterward.",
                            "requirement": {"required_commands": ["git status"]},
                        },
                    ],
                ),
                _wave(
                    "ch7-adv-first-publish-verify",
                    "git-push/upstream",
                    "Verify target, publish with tracking",
                    ["git remote -v", "git push -u origin feature/payment"],
                    required=["git remote -v", "git push -u"],
                    forms=["git-remote/verbose"],
                    state="push",
                    story=(
                        "A first publish deserves a checked destination. Verify the remote's "
                        "URLs, then publish the local-only branch with tracking so every "
                        "future sync needs no arguments."
                    ),
                    evaluation={
                        "rules": [
                            {"type": "upstream_tracking_set", "branch": "feature/payment"},
                            {
                                "type": "remote_branch_matches_local",
                                "remote_branch": "origin/feature/payment",
                                "branch": "feature/payment",
                            },
                        ]
                    },
                    checks=[
                        {
                            "label": "The destination was verified before publishing.",
                            "requirement": {"required_commands": ["git remote -v"]},
                        },
                        {
                            "label": "The branch is published with tracking set.",
                            "requirement": {
                                "rules": [{"type": "upstream_tracking_set", "branch": "feature/payment"}]
                            },
                        },
                    ],
                ),
                _wave(
                    "ch7-adv-publish-then-log",
                    "git-push/upstream",
                    "Publish, then read the record",
                    ["git push -u origin feature/payment", "git log --oneline"],
                    required=["git push -u", "git log"],
                    forms=["git-log/oneline"],
                    state="push",
                    story=(
                        "Publish the local-only branch with tracking, then read the compact "
                        "history - the same commits, now visible to everyone on the team."
                    ),
                    evaluation={
                        "rules": [
                            {"type": "upstream_tracking_set", "branch": "feature/payment"},
                            {
                                "type": "remote_branch_matches_local",
                                "remote_branch": "origin/feature/payment",
                                "branch": "feature/payment",
                            },
                        ]
                    },
                    checks=[
                        {
                            "label": "The branch is published with tracking set.",
                            "requirement": {
                                "rules": [{"type": "upstream_tracking_set", "branch": "feature/payment"}]
                            },
                        },
                        {
                            "label": "The now-shared record was read.",
                            "requirement": {"required_commands": ["git log"]},
                        },
                    ],
                ),
                _wave(
                    "ch7-adv-first-share",
                    "git-push/upstream",
                    "First share, then the state",
                    ["git push -u origin feature/payment", "git status"],
                    required=["git push -u", "git status"],
                    forms=["git-status/plain"],
                    state="push",
                    story=(
                        "The feature's first appearance upstream: publish it with tracking, "
                        "then read the state to see the branch now reporting against its "
                        "remote counterpart."
                    ),
                    evaluation={
                        "rules": [
                            {"type": "upstream_tracking_set", "branch": "feature/payment"},
                            {
                                "type": "remote_branch_matches_local",
                                "remote_branch": "origin/feature/payment",
                                "branch": "feature/payment",
                            },
                        ]
                    },
                    checks=[
                        {
                            "label": "The branch is published with tracking set.",
                            "requirement": {
                                "rules": [{"type": "upstream_tracking_set", "branch": "feature/payment"}]
                            },
                        },
                        {
                            "label": "The tracked state was read afterward.",
                            "requirement": {"required_commands": ["git status"]},
                        },
                    ],
                ),
            ],
        },
        {
            "slug": "publish-drills",
            "title": "Publish Drills",
            "waves": [
                _wave(
                    "ch7-adv-lease-after-amend",
                    "git-push/force-with-lease",
                    "Publish a rewrite, safely",
                    ["git log -n 1", "git push --force-with-lease"],
                    required=["git log", "git push --force-with-lease"],
                    forms=["git-log/limit"],
                    state="push-amend",
                    story=(
                        "The local history rewrite is done and correct; the remote still has "
                        "the old shape. Confirm the rewritten tip with one history entry, then "
                        "publish it under the lease safety check."
                    ),
                    evaluation={
                        "rules": [
                            {"type": "operation_metadata_equals", "key": "force_with_lease", "value": True},
                            {
                                "type": "remote_branch_matches_local",
                                "remote_branch": "origin/feature/payment",
                                "branch": "feature/payment",
                            },
                        ]
                    },
                    checks=[
                        {
                            "label": "The rewritten tip was confirmed first.",
                            "requirement": {"required_commands": ["git log"]},
                        },
                        {
                            "label": "The rewrite published only under the lease check.",
                            "requirement": {
                                "rules": [
                                    {
                                        "type": "operation_metadata_equals",
                                        "key": "force_with_lease",
                                        "value": True,
                                    }
                                ]
                            },
                        },
                    ],
                ),
                _wave(
                    "ch7-adv-amend-then-lease",
                    "git-push/force-with-lease",
                    "Rewrite, then lease it out",
                    ["git commit --amend -m 'Payment: final copy'", "git push --force-with-lease"],
                    required=["git commit --amend", "git push --force-with-lease"],
                    forms=["git-commit/amend"],
                    state="push-tracked",
                    story=(
                        "The tracked branch's newest commit needs its message corrected before "
                        "review - a rewrite that origin must receive safely. Amend in place, "
                        "then publish under the lease check, never a bare force."
                    ),
                    details=[{"label": "New message", "value": "Payment: final copy"}],
                    evaluation={
                        "latest_commit": {
                            "branch": "feature/payment",
                            "message_contains": ["Payment: final copy"],
                        },
                        "rules": [
                            {"type": "operation_metadata_equals", "key": "force_with_lease", "value": True},
                        ],
                    },
                    checks=[
                        {
                            "label": "The commit was rewritten with the corrected message.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "feature/payment",
                                    "message_contains": ["Payment: final copy"],
                                }
                            },
                        },
                        {
                            "label": "The rewrite published only under the lease check.",
                            "requirement": {
                                "rules": [
                                    {
                                        "type": "operation_metadata_equals",
                                        "key": "force_with_lease",
                                        "value": True,
                                    }
                                ]
                            },
                        },
                    ],
                ),
                _wave(
                    "ch7-adv-lease-verify-drill",
                    "git-push/force-with-lease",
                    "Lease out, then confirm calm",
                    ["git push --force-with-lease", "git status"],
                    required=["git push --force-with-lease", "git status"],
                    forms=["git-status/plain"],
                    state="push-amend",
                    story=(
                        "Publish the finished local rewrite under the lease safety check, "
                        "then read the state to confirm local and remote tips agree again."
                    ),
                    evaluation={
                        "rules": [
                            {"type": "operation_metadata_equals", "key": "force_with_lease", "value": True},
                            {
                                "type": "remote_branch_matches_local",
                                "remote_branch": "origin/feature/payment",
                                "branch": "feature/payment",
                            },
                        ]
                    },
                    checks=[
                        {
                            "label": "The rewrite published under the lease check.",
                            "requirement": {
                                "rules": [
                                    {
                                        "type": "operation_metadata_equals",
                                        "key": "force_with_lease",
                                        "value": True,
                                    }
                                ]
                            },
                        },
                        {
                            "label": "The agreement was confirmed afterward.",
                            "requirement": {"required_commands": ["git status"]},
                        },
                    ],
                ),
                _wave(
                    "ch7-adv-lease-final",
                    "git-push/force-with-lease",
                    "Lease out, read the record",
                    ["git push --force-with-lease", "git log --oneline"],
                    required=["git push --force-with-lease", "git log"],
                    forms=["git-log/oneline"],
                    state="push-amend",
                    story=(
                        "One rewritten commit, one safe publish. Push it under the lease "
                        "check, then read the compact history - the shape everyone will now "
                        "see."
                    ),
                    evaluation={
                        "rules": [
                            {"type": "operation_metadata_equals", "key": "force_with_lease", "value": True},
                            {
                                "type": "remote_branch_matches_local",
                                "remote_branch": "origin/feature/payment",
                                "branch": "feature/payment",
                            },
                        ]
                    },
                    checks=[
                        {
                            "label": "The rewrite published under the lease check.",
                            "requirement": {
                                "rules": [
                                    {
                                        "type": "operation_metadata_equals",
                                        "key": "force_with_lease",
                                        "value": True,
                                    }
                                ]
                            },
                        },
                        {
                            "label": "The shared shape was read afterward.",
                            "requirement": {"required_commands": ["git log"]},
                        },
                    ],
                ),
                _wave(
                    "ch7-adv-delete-after-check",
                    "git-push/delete",
                    "Verify, then retire remotely",
                    ["git remote -v", "git push origin --delete feature/payment"],
                    required=["git remote -v", "git push origin --delete"],
                    forms=["git-remote/verbose"],
                    state="push-delete",
                    story=(
                        "Before deleting anything on a server, verify which server you are "
                        "talking to. Then remove the merged branch's remote counterpart from "
                        "origin."
                    ),
                    evaluation={
                        "rules": [
                            {"type": "remote_branch_absent", "remote_branch": "origin/feature/payment"}
                        ]
                    },
                    checks=[
                        {
                            "label": "The server was verified before the deletion.",
                            "requirement": {"required_commands": ["git remote -v"]},
                        },
                        {
                            "label": "The remote branch is retired.",
                            "requirement": {
                                "rules": [
                                    {"type": "remote_branch_absent", "remote_branch": "origin/feature/payment"}
                                ]
                            },
                        },
                    ],
                ),
                _wave(
                    "ch7-adv-delete-then-prune",
                    "git-push/delete",
                    "Retire remotely, sweep locally",
                    ["git push origin --delete feature/payment", "git fetch --prune"],
                    required=["git push origin --delete", "git fetch --prune"],
                    forms=["git-fetch/prune"],
                    state="push-delete",
                    story=(
                        "Finish the cleanup on both sides: remove the merged branch from "
                        "origin, then run a pruning fetch so no stale tracking ref lingers "
                        "locally either."
                    ),
                    evaluation={
                        "rules": [
                            {"type": "remote_branch_absent", "remote_branch": "origin/feature/payment"}
                        ]
                    },
                    checks=[
                        {
                            "label": "The remote branch is retired and nothing stale lingers.",
                            "requirement": {
                                "rules": [
                                    {"type": "remote_branch_absent", "remote_branch": "origin/feature/payment"}
                                ]
                            },
                        },
                    ],
                ),
                _wave(
                    "ch7-adv-delete-then-graph",
                    "git-push/delete",
                    "Retire, then redraw",
                    ["git push origin --delete feature/payment", "git log --oneline --graph --all"],
                    required=["git push origin --delete", "git log"],
                    forms=["git-log/graph-all"],
                    state="push-delete",
                    story=(
                        "Remove the finished branch from origin, then draw the graph and "
                        "enjoy the view: only living lines remain in the picture."
                    ),
                    evaluation={
                        "rules": [
                            {"type": "remote_branch_absent", "remote_branch": "origin/feature/payment"}
                        ]
                    },
                    checks=[
                        {
                            "label": "The remote branch is retired.",
                            "requirement": {
                                "rules": [
                                    {"type": "remote_branch_absent", "remote_branch": "origin/feature/payment"}
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
                    "ch7-adv-cleanup-both-sides",
                    "git-push/delete",
                    "Retire, then count the remotes",
                    ["git push origin --delete feature/payment", "git remote"],
                    required=["git push origin --delete", "git remote"],
                    forms=["git-remote/list"],
                    state="push-delete",
                    story=(
                        "After retiring the merged branch on origin, read the remote names "
                        "once more - the wiring stays, only the dead branch is gone."
                    ),
                    evaluation={
                        "rules": [
                            {"type": "remote_branch_absent", "remote_branch": "origin/feature/payment"}
                        ]
                    },
                    checks=[
                        {
                            "label": "The remote branch is retired.",
                            "requirement": {
                                "rules": [
                                    {"type": "remote_branch_absent", "remote_branch": "origin/feature/payment"}
                                ]
                            },
                        },
                        {
                            "label": "The surviving wiring was read afterward.",
                            "requirement": {"required_commands": ["git remote"]},
                        },
                    ],
                ),
                _wave(
                    "ch7-adv-retire-remote-final",
                    "git-push/delete",
                    "State first, then retire",
                    ["git status", "git push origin --delete feature/payment"],
                    required=["git status", "git push origin --delete"],
                    forms=["git-status/plain"],
                    state="push-delete",
                    story=(
                        "Same discipline for destructive remote actions as local ones: read "
                        "the state first, then remove the long-merged branch from origin."
                    ),
                    evaluation={
                        "rules": [
                            {"type": "remote_branch_absent", "remote_branch": "origin/feature/payment"}
                        ]
                    },
                    checks=[
                        {
                            "label": "The state was read before the deletion.",
                            "requirement": {"required_commands": ["git status"]},
                        },
                        {
                            "label": "The remote branch is retired.",
                            "requirement": {
                                "rules": [
                                    {"type": "remote_branch_absent", "remote_branch": "origin/feature/payment"}
                                ]
                            },
                        },
                    ],
                ),
                _wave(
                    "ch7-adv-share-the-fix",
                    "git-push/current",
                    "Share the fix, read the record",
                    ["git push", "git log --oneline"],
                    required=["git push", "git log"],
                    forms=["git-log/oneline"],
                    state="push-tracked",
                    story=(
                        "The fix is committed on the tracked branch; the team is waiting. "
                        "Share it with a plain push, then read the record showing your commit "
                        "published at the tip."
                    ),
                    evaluation={
                        "rules": [
                            {
                                "type": "remote_branch_matches_local",
                                "remote_branch": "origin/feature/payment",
                                "branch": "feature/payment",
                            }
                        ],
                    },
                    checks=[
                        {
                            "label": "The fix was shared upstream.",
                            "requirement": {
                                "rules": [
                                    {
                                        "type": "remote_branch_matches_local",
                                        "remote_branch": "origin/feature/payment",
                                        "branch": "feature/payment",
                                    }
                                ]
                            },
                        },
                        {
                            "label": "The published record was read afterward.",
                            "requirement": {"required_commands": ["git log"]},
                        },
                    ],
                ),
                _wave(
                    "ch7-adv-ship-tracked-note",
                    "git-push/current",
                    "Confirm the destination, then ship",
                    ["git remote -v", "git push"],
                    required=["git remote -v", "git push"],
                    forms=["git-remote/verbose"],
                    state="push-tracked",
                    story=(
                        "The finished release notes commit is waiting on the tracked branch. "
                        "Verify exactly which server will receive it, then send it upstream "
                        "where the whole team reads it."
                    ),
                    evaluation={
                        "rules": [
                            {
                                "type": "remote_branch_matches_local",
                                "remote_branch": "origin/feature/payment",
                                "branch": "feature/payment",
                            }
                        ],
                    },
                    checks=[
                        {
                            "label": "The destination was verified before shipping.",
                            "requirement": {"required_commands": ["git remote -v"]},
                        },
                        {
                            "label": "The notes commit is published upstream.",
                            "requirement": {
                                "rules": [
                                    {
                                        "type": "remote_branch_matches_local",
                                        "remote_branch": "origin/feature/payment",
                                        "branch": "feature/payment",
                                    }
                                ]
                            },
                        },
                    ],
                ),
                _wave(
                    "ch7-adv-publish-with-remotes-read",
                    "git-push/upstream",
                    "Know the wiring, then publish",
                    ["git remote", "git push -u origin feature/payment"],
                    required=["git remote", "git push -u"],
                    forms=["git-remote/list"],
                    state="push",
                    story=(
                        "Quick wiring check, then the first publish: read the remote names, "
                        "then put the local-only branch upstream with tracking configured."
                    ),
                    evaluation={
                        "rules": [
                            {"type": "upstream_tracking_set", "branch": "feature/payment"},
                            {
                                "type": "remote_branch_matches_local",
                                "remote_branch": "origin/feature/payment",
                                "branch": "feature/payment",
                            },
                        ]
                    },
                    checks=[
                        {
                            "label": "The wiring was read before publishing.",
                            "requirement": {"required_commands": ["git remote"]},
                        },
                        {
                            "label": "The branch is published with tracking set.",
                            "requirement": {
                                "rules": [{"type": "upstream_tracking_set", "branch": "feature/payment"}]
                            },
                        },
                    ],
                ),
            ],
        },
        {
            "slug": "full-collaboration-loops",
            "title": "Full Collaboration Loops",
            "waves": [
                _wave(
                    "ch7-adv-branch-publish-merge-cleanup",
                    "git-fetch/origin",
                    "Branch publish merge cleanup",
                    [
                        "git fetch origin",
                        "git switch -c feature/review",
                        "git add README.md",
                        "git commit -m 'Add review work'",
                        "git push -u origin feature/review",
                        "git fetch --prune",
                    ],
                    required=["git fetch", "git switch -c", "git commit", "git push -u", "git fetch --prune"],
                    forms=["git-switch/create", "git-add/file", "git-commit/message", "git-push/upstream", "git-fetch/prune"],
                    state="remote-dirty",
                    story=(
                        "A complete feature branch lifecycle, start to finish: sync with origin first, "
                        "branch off for the review work, commit it, publish the branch with tracking, "
                        "and refresh remote-tracking refs afterward."
                    ),
                    evaluation={
                        "head_branch": "feature/review",
                        "latest_commit": {
                            "branch": "feature/review",
                            "contains_paths": ["README.md"],
                            "message_contains": ["Add review work"],
                        },
                        "rules": [
                            {"type": "upstream_tracking_set", "branch": "feature/review"},
                            {
                                "type": "remote_branch_matches_local",
                                "remote_branch": "origin/feature/review",
                                "branch": "feature/review",
                            },
                        ],
                    },
                    checks=[
                        {
                            "label": "The review work was branched off after syncing with origin, then committed.",
                            "requirement": {
                                "head_branch": "feature/review",
                                "latest_commit": {
                                    "branch": "feature/review",
                                    "contains_paths": ["README.md"],
                                    "message_contains": ["Add review work"],
                                },
                            },
                        },
                        {
                            "label": "The branch is published to origin with tracking set, and remote refs are refreshed.",
                            "requirement": {
                                "rules": [
                                    {"type": "upstream_tracking_set", "branch": "feature/review"},
                                    {
                                        "type": "remote_branch_matches_local",
                                        "remote_branch": "origin/feature/review",
                                        "branch": "feature/review",
                                    },
                                ]
                            },
                        },
                    ],
                ),
                _wave(
                    "ch7-adv-sync-diverged-work",
                    "git-fetch/origin",
                    "Sync diverged work",
                    ["git fetch origin", "git pull --rebase", "git push"],
                    required=["git fetch", "git pull --rebase", "git push"],
                    forms=["git-pull/rebase", "git-push/current"],
                    state="remote-diverged",
                    story=(
                        "A teammate advanced origin/main while a local commit was still unpublished. "
                        "Sync by replaying the local work on top of the teammate's commits, then "
                        "publish the result."
                    ),
                    evaluation={
                        "rules": [
                            {
                                "type": "remote_branch_matches_local",
                                "remote_branch": "origin/main",
                                "branch": "main",
                            },
                            {"type": "operation_metadata_equals", "key": "pull_strategy", "value": "rebase"},
                        ]
                    },
                    checks=[
                        {
                            "label": "The local commit was replayed on top of the teammate's work, not merged or dropped.",
                            "requirement": {
                                "rules": [
                                    {
                                        "type": "operation_metadata_equals",
                                        "key": "pull_strategy",
                                        "value": "rebase",
                                    }
                                ]
                            },
                        },
                        {
                            "label": "origin/main now matches the rebased local tip.",
                            "requirement": {
                                "rules": [
                                    {
                                        "type": "remote_branch_matches_local",
                                        "remote_branch": "origin/main",
                                        "branch": "main",
                                    }
                                ]
                            },
                        },
                    ],
                ),
                _wave(
                    "ch7-adv-rewrite-and-lease",
                    "git-fetch/origin",
                    "Rewrite and lease",
                    ["git fetch origin", "git commit --amend -m 'Correct local history'", "git push --force-with-lease"],
                    required=["git fetch", "git commit --amend", "git push --force-with-lease"],
                    forms=["git-commit/amend", "git-push/force-with-lease"],
                    state="push-amend",
                    story=(
                        "The latest commit on feature/payment needs a corrected message before anyone "
                        "reviews it. Confirm origin hasn't moved since the last fetch, rewrite the "
                        "commit locally, then publish the correction safely."
                    ),
                    evaluation={
                        "latest_commit": {"branch": "feature/payment", "message_contains": ["Correct local history"]},
                        "rules": [
                            {"type": "branch_tip_replaces_commit", "branch": "feature/payment", "old": "c1"},
                            {"type": "operation_metadata_equals", "key": "force_with_lease", "value": True},
                            {
                                "type": "remote_branch_matches_local",
                                "remote_branch": "origin/feature/payment",
                                "branch": "feature/payment",
                            },
                        ],
                    },
                    checks=[
                        {
                            "label": "The commit was rewritten in place with the corrected message.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "feature/payment",
                                    "message_contains": ["Correct local history"],
                                },
                                "rules": [
                                    {
                                        "type": "branch_tip_replaces_commit",
                                        "branch": "feature/payment",
                                        "old": "c1",
                                    }
                                ],
                            },
                        },
                        {
                            "label": "The rewrite published safely under a lease, and origin now matches it.",
                            "requirement": {
                                "rules": [
                                    {
                                        "type": "operation_metadata_equals",
                                        "key": "force_with_lease",
                                        "value": True,
                                    },
                                    {
                                        "type": "remote_branch_matches_local",
                                        "remote_branch": "origin/feature/payment",
                                        "branch": "feature/payment",
                                    },
                                ]
                            },
                        },
                    ],
                ),
                _wave(
                    "ch7-adv-daily-loop",
                    "git-pull/default",
                    "The daily loop",
                    ["git pull", "git add README.md", "git commit -m 'Daily update'", "git push"],
                    required=["git pull", "git add", "git commit", "git push"],
                    forms=["git-add/file", "git-commit/message", "git-push/current"],
                    state="remote",
                    story=(
                        "The loop every collaborative day is built on: bring the team's work "
                        "in, add your own on top, seal it, and send it back out. Run it once, "
                        "end to end."
                    ),
                    details=[{"label": "Commit message", "value": "Daily update"}],
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["README.md"],
                            "message_contains": ["Daily update"],
                        },
                        "rules": [
                            {
                                "type": "remote_branch_matches_local",
                                "remote_branch": "origin/main",
                                "branch": "main",
                            }
                        ],
                    },
                    workspace_files=[
                        {
                            "after_command_index": 1,
                            "path": "README.md",
                            "content": "remote update\nlocal daily note\n",
                        }
                    ],
                    checks=[
                        {
                            "label": "Your work was sealed on top of the team's.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "message_contains": ["Daily update"],
                                }
                            },
                        },
                        {
                            "label": "The loop closed: upstream matches your tip.",
                            "requirement": {
                                "required_commands": ["git pull", "git push"],
                            },
                        },
                    ],
                ),
                _wave(
                    "ch7-adv-morning-sync-evening-ship",
                    "git-push/current",
                    "Morning sync, evening ship",
                    [
                        "git status -s",
                        "git pull",
                        "git add README.md",
                        "git commit -m 'Evening ship'",
                        "git push",
                    ],
                    required=["git status -s", "git pull", "git add", "git commit", "git push"],
                    forms=["git-status/short", "git-pull/default", "git-add/file", "git-commit/message"],
                    state="remote",
                    story=(
                        "A whole workday in one wave: glance at the state, sync with the "
                        "team, do the day's work, seal it in the evening, and ship it before "
                        "logging off."
                    ),
                    details=[{"label": "Commit message", "value": "Evening ship"}],
                    workspace_files=[
                        {
                            "after_command_index": 2,
                            "path": "README.md",
                            "content": "remote update\nevening work\n",
                        }
                    ],
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["README.md"],
                            "message_contains": ["Evening ship"],
                        },
                        "rules": [
                            {
                                "type": "remote_branch_matches_local",
                                "remote_branch": "origin/main",
                                "branch": "main",
                            }
                        ],
                    },
                    checks=[
                        {
                            "label": "The day's work was sealed after the morning sync.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "message_contains": ["Evening ship"],
                                }
                            },
                        },
                        {
                            "label": "The evening ship went out.",
                            "requirement": {"required_commands": ["git push"]},
                        },
                    ],
                ),
                _wave(
                    "ch7-adv-publish-fresh-branch-loop",
                    "git-push/upstream",
                    "Sync, branch, build, publish",
                    [
                        "git pull",
                        "git switch -c feature/metrics",
                        "git add README.md",
                        "git commit -m 'Metrics seed'",
                        "git push -u origin feature/metrics",
                    ],
                    required=["git pull", "git switch -c", "git add", "git commit", "git push -u"],
                    forms=["git-pull/default", "git-switch/create", "git-add/file", "git-commit/message"],
                    state="remote",
                    story=(
                        "Start the metrics feature the professional way: sync with origin "
                        "first, branch off the fresh tip, seed the work, and publish the new "
                        "line with tracking on your first push."
                    ),
                    details=[
                        {"label": "New branch", "value": "feature/metrics"},
                        {"label": "Commit message", "value": "Metrics seed"},
                    ],
                    workspace_files=[
                        {
                            "after_command_index": 2,
                            "path": "README.md",
                            "content": "remote update\nmetrics seed\n",
                        }
                    ],
                    evaluation={
                        "head_branch": "feature/metrics",
                        "latest_commit": {
                            "branch": "feature/metrics",
                            "contains_paths": ["README.md"],
                            "message_contains": ["Metrics seed"],
                        },
                        "rules": [
                            {"type": "upstream_tracking_set", "branch": "feature/metrics"},
                            {
                                "type": "remote_branch_matches_local",
                                "remote_branch": "origin/feature/metrics",
                                "branch": "feature/metrics",
                            },
                        ],
                    },
                    checks=[
                        {
                            "label": "The feature branched off a freshly synced tip.",
                            "requirement": {
                                "head_branch": "feature/metrics",
                                "latest_commit": {
                                    "branch": "feature/metrics",
                                    "message_contains": ["Metrics seed"],
                                },
                            },
                        },
                        {
                            "label": "The new line is published with tracking set.",
                            "requirement": {
                                "rules": [{"type": "upstream_tracking_set", "branch": "feature/metrics"}]
                            },
                        },
                    ],
                ),
                _wave(
                    "ch7-adv-second-publish",
                    "git-push/upstream",
                    "Pointer, move, build, publish",
                    [
                        "git pull",
                        "git branch feature/alerts",
                        "git switch feature/alerts",
                        "git add README.md",
                        "git commit -m 'Alerts seed'",
                        "git push -u origin feature/alerts",
                    ],
                    required=["git pull", "git branch", "git switch", "git add", "git commit", "git push -u"],
                    forms=["git-pull/default", "git-branch/create", "git-switch/existing", "git-add/file", "git-commit/message"],
                    state="remote",
                    story=(
                        "The alerts work starts properly: sync with origin, create the pointer "
                        "as a deliberate two-step, seed the feature on it, and publish the line "
                        "with tracking configured."
                    ),
                    details=[
                        {"label": "New branch", "value": "feature/alerts"},
                        {"label": "Commit message", "value": "Alerts seed"},
                    ],
                    workspace_files=[
                        {
                            "after_command_index": 3,
                            "path": "README.md",
                            "content": "remote update\nalerts seed\n",
                        }
                    ],
                    evaluation={
                        "head_branch": "feature/alerts",
                        "latest_commit": {
                            "branch": "feature/alerts",
                            "contains_paths": ["README.md"],
                            "message_contains": ["Alerts seed"],
                        },
                        "rules": [
                            {"type": "upstream_tracking_set", "branch": "feature/alerts"},
                            {
                                "type": "remote_branch_matches_local",
                                "remote_branch": "origin/feature/alerts",
                                "branch": "feature/alerts",
                            },
                        ],
                    },
                    checks=[
                        {
                            "label": "The alerts work was seeded on its own line.",
                            "requirement": {
                                "head_branch": "feature/alerts",
                                "latest_commit": {
                                    "branch": "feature/alerts",
                                    "message_contains": ["Alerts seed"],
                                },
                            },
                        },
                        {
                            "label": "The line is published with tracking set.",
                            "requirement": {
                                "rules": [{"type": "upstream_tracking_set", "branch": "feature/alerts"}]
                            },
                        },
                    ],
                ),
                _wave(
                    "ch7-adv-publish-audit",
                    "git-push/upstream",
                    "Publish, then map both worlds",
                    ["git push -u origin feature/payment", "git log --oneline --graph --all"],
                    required=["git push -u", "git log"],
                    forms=["git-log/graph-all"],
                    state="push",
                    story=(
                        "Publish the local-only branch with tracking, then draw the full "
                        "graph: local refs and their new remote counterparts, finally telling "
                        "the same story."
                    ),
                    evaluation={
                        "rules": [
                            {"type": "upstream_tracking_set", "branch": "feature/payment"},
                            {
                                "type": "remote_branch_matches_local",
                                "remote_branch": "origin/feature/payment",
                                "branch": "feature/payment",
                            },
                        ]
                    },
                    checks=[
                        {
                            "label": "The branch is published with tracking set.",
                            "requirement": {
                                "rules": [{"type": "upstream_tracking_set", "branch": "feature/payment"}]
                            },
                        },
                        {
                            "label": "Both worlds were mapped afterward.",
                            "requirement": {"required_commands": ["git log"]},
                        },
                    ],
                ),
                _wave(
                    "ch7-adv-push-current-final",
                    "git-push/current",
                    "Glance, share, read the record",
                    ["git status -s", "git push", "git log --oneline"],
                    required=["git status -s", "git push", "git log"],
                    forms=["git-status/short", "git-log/oneline"],
                    state="push-tracked",
                    story=(
                        "The last plain push of the chapter: glance at the tracked branch's "
                        "state, share the waiting commit, and read the record one more time "
                        "with everything in sync."
                    ),
                    evaluation={
                        "rules": [
                            {
                                "type": "remote_branch_matches_local",
                                "remote_branch": "origin/feature/payment",
                                "branch": "feature/payment",
                            }
                        ]
                    },
                    checks=[
                        {
                            "label": "The waiting commit was shared upstream.",
                            "requirement": {
                                "rules": [
                                    {
                                        "type": "remote_branch_matches_local",
                                        "remote_branch": "origin/feature/payment",
                                        "branch": "feature/payment",
                                    }
                                ]
                            },
                        },
                        {
                            "label": "The synced record was read afterward.",
                            "requirement": {"required_commands": ["git log"]},
                        },
                    ],
                ),
                _wave(
                    "ch7-adv-upstream-final",
                    "git-push/upstream",
                    "Read, then publish with tracking",
                    ["git log --oneline", "git push -u origin feature/payment"],
                    required=["git log", "git push -u"],
                    forms=["git-log/oneline"],
                    state="push",
                    story=(
                        "One last first-publish: read the compact history you are about to "
                        "share, then put the branch upstream with tracking - the curriculum's "
                        "closing move."
                    ),
                    evaluation={
                        "rules": [
                            {"type": "upstream_tracking_set", "branch": "feature/payment"},
                            {
                                "type": "remote_branch_matches_local",
                                "remote_branch": "origin/feature/payment",
                                "branch": "feature/payment",
                            },
                        ]
                    },
                    checks=[
                        {
                            "label": "The history was read before sharing.",
                            "requirement": {"required_commands": ["git log"]},
                        },
                        {
                            "label": "The branch is published with tracking set.",
                            "requirement": {
                                "rules": [{"type": "upstream_tracking_set", "branch": "feature/payment"}]
                            },
                        },
                    ],
                ),
            ],
        },
    ]
