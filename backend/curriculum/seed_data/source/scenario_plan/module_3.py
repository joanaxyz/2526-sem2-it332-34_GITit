"""Module 3 scenario placement: Conflict Resolution (SCENARIO_MAP.md).

Each tier's scenarios are listed in play order; each scenario's first variant is a
first-time learner's pick. Scenario slugs are stable: progress rows name them.
"""

from __future__ import annotations

from curriculum.seed_data.source.scenario_plan.types import (
    COMPOSE,
    DEBUT,
    PRACTICE,
    SPIRAL,
    TRANSFER,
    ModuleScenarios,
    ScenarioSpec,
)

SCENARIOS: ModuleScenarios = {
    # Resolving Merge Conflicts Manually
    "resolving-conflicts-manually": {
        "easy": (
            ScenarioSpec(
                "resolve-one-conflicted-file",
                "Resolve one conflicted file",
                DEBUT,
                (
                    "manual-easy-auth-copy",
                    "manual-easy-profile-copy",
                    "manual-easy-billing-copy",
                ),
            ),
            ScenarioSpec(
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
            ScenarioSpec(
                "resolve-config-conflicts",
                "Resolve config conflicts",
                PRACTICE,
                (
                    "manual-medium-router",
                    "manual-medium-policy",
                    "manual-medium-gateway",
                ),
            ),
            ScenarioSpec(
                "back-out-of-a-merge",
                "Back out of a merge",
                DEBUT,
                (
                    "manual-easy-abort-wrong-branch",
                    "manual-easy-abort-too-early",
                ),
            ),
            ScenarioSpec(
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
            ScenarioSpec(
                "resolve-with-less-guidance",
                "Resolve with less guidance",
                TRANSFER,
                (
                    "manual-hard-pricing",
                    "manual-hard-schema",
                    "manual-hard-migration",
                ),
            ),
            ScenarioSpec(
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
            ScenarioSpec(
                "resolve-in-the-merge-tool",
                "Resolve in the merge tool",
                DEBUT,
                (
                    "mergetool-easy-cache-ttl",
                    "mergetool-easy-mail-footer",
                    "mergetool-easy-upload-limit",
                ),
            ),
            ScenarioSpec(
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
            ScenarioSpec(
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
            ScenarioSpec(
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
            ScenarioSpec(
                "judge-which-side-to-keep",
                "Judge which side to keep",
                TRANSFER,
                (
                    "mergetool-hard-one-of-two",
                    "mergetool-hard-take-theirs",
                ),
            ),
            ScenarioSpec(
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
            ScenarioSpec(
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
            ScenarioSpec(
                "pick-without-committing",
                "Pick without committing",
                DEBUT,
                (
                    "cherry-medium-no-commit",
                    "cherry-medium-staged-review",
                ),
            ),
            ScenarioSpec(
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
            ScenarioSpec(
                "record-where-it-came-from",
                "Record where it came from",
                DEBUT,
                (
                    "cherry-hard-trace-source",
                    "cherry-easy-trace-source-hotfix",
                ),
            ),
            ScenarioSpec(
                "resolve-and-continue",
                "Resolve and continue",
                DEBUT,
                (
                    "cherry-hard-export-conflict",
                    "cherry-medium-conflict-continue-auth",
                ),
            ),
            ScenarioSpec(
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
            ScenarioSpec(
                "review-two-backports-before-committing",
                "Review two backports before committing",
                TRANSFER,
                (
                    "cherry-hard-review-backports-auth",
                    "cherry-hard-review-backports-export",
                ),
            ),
            ScenarioSpec(
                "backport-to-two-releases",
                "Backport to two releases",
                TRANSFER,
                (
                    "cherry-hard-two-releases",
                    "cherry-hard-two-releases-security",
                ),
            ),
            ScenarioSpec(
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
