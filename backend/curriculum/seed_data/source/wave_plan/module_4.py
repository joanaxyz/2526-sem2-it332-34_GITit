"""Module 4 wave placement: Advanced Recovery and History (WAVE_MAP.md).

Each tier's waves are listed in play order; each wave's first variant is a
first-time learner's pick. Wave slugs are stable: progress rows name them.
"""

from __future__ import annotations

from curriculum.seed_data.source.wave_plan.types import (
    DEBUT,
    PRACTICE,
    SPIRAL,
    TRANSFER,
    ModuleWaves,
    WaveSpec,
)

WAVES: ModuleWaves = {
    # Recovering from Hard Resets
    "recovering-from-hard-resets": {
        "easy": (
            WaveSpec(
                "recover-the-lost-tip",
                "Recover the lost tip",
                DEBUT,
                (
                    "e1",
                    "e2",
                    "e3",
                ),
            ),
            WaveSpec(
                "recover-again",
                "Recover after another reset",
                PRACTICE,
                (
                    "e4",
                    "e5",
                ),
            ),
        ),
        "medium": (
            WaveSpec(
                "deeper-in-the-reflog",
                "Deeper in the reflog",
                PRACTICE,
                (
                    "m1",
                    "m2",
                    "m3",
                    "m4",
                    "m5",
                ),
            ),
            WaveSpec(
                "recover-and-share",
                "Recover and share it",
                SPIRAL,
                (
                    "reflog-medium-recover-and-publish-search",
                    "reflog-medium-recover-and-publish-billing",
                ),
            ),
        ),
        "hard": (
            WaveSpec(
                "pick-the-right-candidate",
                "Pick the right candidate",
                TRANSFER,
                (
                    "h1",
                    "h2",
                    "h3",
                    "h4",
                    "h5",
                ),
            ),
            WaveSpec(
                "recover-and-bring-the-fix-to-main",
                "Recover, then bring the fix to main",
                SPIRAL,
                (
                    "reflog-hard-recover-then-pick-auth",
                    "reflog-hard-recover-then-pick-export",
                ),
            ),
        ),
    },
    # Reversing Pushed Commits Safely
    "reversing-pushed-commits-safely": {
        "easy": (
            WaveSpec(
                "undo-a-pushed-commit",
                "Undo a pushed commit safely",
                DEBUT,
                (
                    "re6",
                    "re7",
                    "re8",
                ),
            ),
            WaveSpec(
                "sync-then-revert",
                "Sync first, then revert",
                SPIRAL,
                (
                    "revert-easy-pull-then-revert-docs",
                    "revert-easy-pull-then-revert-api",
                ),
            ),
        ),
        "medium": (
            WaveSpec(
                "find-the-culprit",
                "Find the culprit from the symptom",
                PRACTICE,
                (
                    "rm6",
                    "rm7",
                    "rm8",
                ),
            ),
            WaveSpec(
                "revert-on-the-release-branch",
                "Revert on the release branch",
                SPIRAL,
                (
                    "revert-medium-release-branch-pricing",
                    "revert-medium-release-branch-auth",
                ),
            ),
        ),
        "hard": (
            WaveSpec(
                "two-faulty-commits-one-publish",
                "Two faulty commits, one publish",
                TRANSFER,
                (
                    "rh6",
                    "rh7",
                    "rh8",
                ),
            ),
            WaveSpec(
                "rewrite-only-unpublished",
                "Rewrite only what isn't published",
                SPIRAL,
                (
                    "revert-hard-amend-local-revert-pushed-shop",
                    "revert-hard-amend-local-revert-pushed-blog",
                ),
            ),
        ),
    },
    # Completing Rebase Recovery Sequences
    "completing-rebase-recovery-sequences": {
        "easy": (
            WaveSpec(
                "replay-onto-main",
                "Replay your branch onto main",
                DEBUT,
                (
                    "be6",
                    "be7",
                    "be8",
                ),
            ),
            WaveSpec(
                "resolve-and-continue-a-rebase",
                "Resolve and continue a rebase",
                DEBUT,
                (
                    "rebase-hard-continue",
                    "rebase-easy-continue-config",
                ),
            ),
            WaveSpec(
                "resolve-another-stopped-rebase",
                "Resolve another stopped rebase",
                PRACTICE,
                (
                    "rebase-easy-continue-styles",
                    "rebase-easy-continue-routes",
                ),
            ),
        ),
        "medium": (
            WaveSpec(
                "abandon-a-stopped-rebase",
                "Abandon a stopped rebase",
                DEBUT,
                (
                    "rebase-medium-abort",
                    "rebase-easy-abort-stopped-docs",
                ),
            ),
            WaveSpec(
                "move-only-your-commits",
                "Move only your commits",
                DEBUT,
                (
                    "bm6",
                    "bm7",
                ),
            ),
            WaveSpec(
                "reset-then-rebase",
                "Reset to the original tip, then rebase",
                DEBUT,
                (
                    "bh6",
                    "bh7",
                ),
            ),
        ),
        "hard": (
            WaveSpec(
                "abort-then-move-only-your-commits",
                "Abort, then move only your commits",
                TRANSFER,
                (
                    "rebase-hard-abort-then-onto-reports",
                    "rebase-hard-abort-then-onto-ui",
                ),
            ),
            WaveSpec(
                "continue-then-publish-safely",
                "Continue the rebase, then publish safely",
                SPIRAL,
                (
                    "rebase-hard-continue-then-lease-search",
                    "rebase-hard-continue-then-lease-billing",
                ),
            ),
            WaveSpec(
                "undo-a-bad-rebase-and-republish",
                "Undo a bad rebase and republish",
                SPIRAL,
                (
                    "rebase-hard-reset-rebase-lease-cli",
                    "rebase-hard-reset-rebase-lease-api",
                ),
            ),
        ),
    },
}
