"""Module 4 scenario placement: Advanced Recovery and History (SCENARIO_MAP.md).

Each tier's scenarios are listed in play order; each scenario's first variant is a
first-time learner's pick. Scenario slugs are stable: progress rows name them.
"""

from __future__ import annotations

from curriculum.seed_data.source.scenario_plan.types import (
    DEBUT,
    PRACTICE,
    SPIRAL,
    TRANSFER,
    ModuleScenarios,
    ScenarioSpec,
)

SCENARIOS: ModuleScenarios = {
    # Recovering from Hard Resets
    "recovering-from-hard-resets": {
        "easy": (
            ScenarioSpec(
                "recover-the-lost-tip",
                "Recover the lost tip",
                DEBUT,
                (
                    "e1",
                    "e2",
                    "e3",
                ),
            ),
            ScenarioSpec(
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
            ScenarioSpec(
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
            ScenarioSpec(
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
            ScenarioSpec(
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
            ScenarioSpec(
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
            ScenarioSpec(
                "undo-a-pushed-commit",
                "Undo a pushed commit safely",
                DEBUT,
                (
                    "re6",
                    "re7",
                    "re8",
                ),
            ),
            ScenarioSpec(
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
            ScenarioSpec(
                "find-the-culprit",
                "Find the culprit from the symptom",
                PRACTICE,
                (
                    "rm6",
                    "rm7",
                    "rm8",
                ),
            ),
            ScenarioSpec(
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
            ScenarioSpec(
                "two-faulty-commits-one-publish",
                "Two faulty commits, one publish",
                TRANSFER,
                (
                    "rh6",
                    "rh7",
                    "rh8",
                ),
            ),
            ScenarioSpec(
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
            ScenarioSpec(
                "replay-onto-main",
                "Replay your branch onto main",
                DEBUT,
                (
                    "be6",
                    "be7",
                    "be8",
                ),
            ),
            ScenarioSpec(
                "resolve-and-continue-a-rebase",
                "Resolve and continue a rebase",
                DEBUT,
                (
                    "rebase-hard-continue",
                    "rebase-easy-continue-config",
                ),
            ),
            ScenarioSpec(
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
            ScenarioSpec(
                "abandon-a-stopped-rebase",
                "Abandon a stopped rebase",
                DEBUT,
                (
                    "rebase-medium-abort",
                    "rebase-easy-abort-stopped-docs",
                ),
            ),
            ScenarioSpec(
                "move-only-your-commits",
                "Move only your commits",
                DEBUT,
                (
                    "bm6",
                    "bm7",
                ),
            ),
            ScenarioSpec(
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
            ScenarioSpec(
                "abort-then-move-only-your-commits",
                "Abort, then move only your commits",
                TRANSFER,
                (
                    "rebase-hard-abort-then-onto-reports",
                    "rebase-hard-abort-then-onto-ui",
                ),
            ),
            ScenarioSpec(
                "continue-then-publish-safely",
                "Continue the rebase, then publish safely",
                SPIRAL,
                (
                    "rebase-hard-continue-then-lease-search",
                    "rebase-hard-continue-then-lease-billing",
                ),
            ),
            ScenarioSpec(
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
