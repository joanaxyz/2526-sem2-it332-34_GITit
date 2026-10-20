"""Module 3 wave placement: Conflict Resolution (WAVE_MAP.md).

Each tier's waves are listed in play order; each wave's first variant is a
first-time learner's pick. Wave slugs are stable: progress rows name them.
"""

from __future__ import annotations

from curriculum.seed_data.source.wave_plan.types import (
    COMPOSE,
    DEBUT,
    PRACTICE,
    SPIRAL,
    TRANSFER,
    ModuleWaves,
    WaveSpec,
)

WAVES: ModuleWaves = {
    # Resolving Merge Conflicts Manually
    "resolving-conflicts-manually": {
        "easy": (
            WaveSpec(
                "resolve-one-conflicted-file",
                "Resolve one conflicted file",
                DEBUT,
                (
                    "manual-easy-auth-copy",
                    "manual-easy-profile-copy",
                    "manual-easy-billing-copy",
                ),
            ),
            WaveSpec(
                "resolve-another-file",
                "Resolve another file",
                PRACTICE,
                (
                    "manual-easy-config-copy",
                    "manual-easy-navbar-copy",
                ),
            ),
        ),
        "medium": (
            WaveSpec(
                "resolve-config-conflicts",
                "Resolve config conflicts",
                PRACTICE,
                (
                    "manual-medium-router",
                    "manual-medium-policy",
                    "manual-medium-gateway",
                ),
            ),
            WaveSpec(
                "back-out-of-a-merge",
                "Back out of a merge",
                DEBUT,
                (
                    "manual-easy-abort-wrong-branch",
                    "manual-easy-abort-too-early",
                ),
            ),
            WaveSpec(
                "a-pull-that-conflicts",
                "A pull that conflicts",
                SPIRAL,
                (
                    "manual-medium-pull-conflict-readme",
                    "manual-medium-pull-conflict-config",
                ),
            ),
        ),
        "hard": (
            WaveSpec(
                "resolve-with-less-guidance",
                "Resolve with less guidance",
                TRANSFER,
                (
                    "manual-hard-pricing",
                    "manual-hard-schema",
                    "manual-hard-migration",
                ),
            ),
            WaveSpec(
                "abort-wrong-resolve-right",
                "Abort the wrong merge, resolve the right one",
                TRANSFER,
                (
                    "manual-hard-abort-redo",
                    "manual-hard-abort-redo-payments",
                ),
            ),
        ),
    },
    # Resolving Conflicts Using a Merge Tool
    "using-a-merge-tool": {
        "easy": (
            WaveSpec(
                "resolve-in-the-merge-tool",
                "Resolve in the merge tool",
                DEBUT,
                (
                    "mergetool-easy-cache-ttl",
                    "mergetool-easy-mail-footer",
                    "mergetool-easy-upload-limit",
                ),
            ),
            WaveSpec(
                "merge-tool-practice",
                "Another conflict, same tool",
                PRACTICE,
                (
                    "mergetool-easy-app-locale",
                    "mergetool-easy-labels",
                ),
            ),
        ),
        "medium": (
            WaveSpec(
                "two-files-in-one-pass",
                "Two files in one pass",
                PRACTICE,
                (
                    "mergetool-medium-checkout-copy",
                    "mergetool-medium-api-limits",
                    "mergetool-medium-db-names",
                    "mergetool-medium-docs-sync",
                ),
            ),
            WaveSpec(
                "set-up-the-team-tool",
                "Set up the team's tool first",
                DEBUT,
                (
                    "mergetool-hard-choose-tool",
                    "mergetool-medium-configure-tool-billing",
                ),
            ),
        ),
        "hard": (
            WaveSpec(
                "judge-which-side-to-keep",
                "Judge which side to keep",
                TRANSFER,
                (
                    "mergetool-hard-one-of-two",
                    "mergetool-hard-take-theirs",
                ),
            ),
            WaveSpec(
                "no-leftovers",
                "No leftovers",
                TRANSFER,
                (
                    "mergetool-hard-no-leftovers",
                    "mergetool-hard-no-backup-api",
                ),
            ),
        ),
    },
    # Cherry-Picking Commits
    "cherry-picking-commits": {
        "easy": (
            WaveSpec(
                "copy-one-commit",
                "Copy one commit",
                DEBUT,
                (
                    "cherry-easy-login-timeout",
                    "cherry-easy-invoice-rounding",
                    "cherry-easy-export-null",
                    "cherry-easy-rate-limit",
                    "cherry-easy-null-check",
                ),
            ),
            WaveSpec(
                "pick-without-committing",
                "Pick without committing",
                DEBUT,
                (
                    "cherry-medium-no-commit",
                    "cherry-medium-staged-review",
                ),
            ),
            WaveSpec(
                "two-fixes-one-reviewed-commit",
                "Two fixes, one reviewed commit",
                COMPOSE,
                (
                    "cherry-medium-two-fixes-one-commit-login",
                    "cherry-medium-two-fixes-one-commit-tax",
                ),
            ),
        ),
        "medium": (
            WaveSpec(
                "record-where-it-came-from",
                "Record where it came from",
                DEBUT,
                (
                    "cherry-hard-trace-source",
                    "cherry-easy-trace-source-hotfix",
                ),
            ),
            WaveSpec(
                "resolve-and-continue",
                "Resolve and continue",
                DEBUT,
                (
                    "cherry-hard-export-conflict",
                    "cherry-medium-conflict-continue-auth",
                ),
            ),
            WaveSpec(
                "cancel-a-stopped-pick",
                "Cancel a stopped pick",
                DEBUT,
                (
                    "cherry-hard-abort-conflict",
                    "cherry-medium-abort-stopped-pick",
                ),
            ),
        ),
        "hard": (
            WaveSpec(
                "review-two-backports-before-committing",
                "Review two backports before committing",
                TRANSFER,
                (
                    "cherry-hard-review-backports-auth",
                    "cherry-hard-review-backports-export",
                ),
            ),
            WaveSpec(
                "backport-to-two-releases",
                "Backport to two releases",
                TRANSFER,
                (
                    "cherry-hard-two-releases",
                    "cherry-hard-two-releases-security",
                ),
            ),
            WaveSpec(
                "abort-the-wrong-pick-backport-the-right-one",
                "Abort the wrong pick, backport the right one",
                SPIRAL,
                (
                    "cherry-hard-backport-capstone-export",
                    "cherry-hard-backport-capstone-login",
                ),
            ),
        ),
    },
}
