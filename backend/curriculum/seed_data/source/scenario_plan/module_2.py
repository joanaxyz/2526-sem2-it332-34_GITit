"""Module 2 scenario placement: Branching and Collaboration (SCENARIO_MAP.md).

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
    # Creating and Switching Branches
    "creating-and-switching-branches": {
        "easy": (
            ScenarioSpec(
                "create-and-switch",
                "Create a branch and switch to it",
                DEBUT,
                (
                    "v21e-auth",
                    "v21e-login",
                    "v21e-ui",
                    "bc-easy-capstone-db",
                    "bc-easy-corp-hotfix",
                    "bc-med-oss-develop",
                ),
            ),
            ScenarioSpec(
                "go-back-to-main",
                "Go back to main",
                DEBUT,
                (
                    "switch-easy-back-to-main-docs",
                    "switch-easy-back-to-main-api",
                ),
            ),
            ScenarioSpec(
                "branch-off-then-return",
                "Branch off, then come back",
                COMPOSE,
                (
                    "switch-easy-branch-then-return-docs",
                    "switch-easy-branch-then-return-api",
                ),
            ),
        ),
        "medium": (
            ScenarioSpec(
                "create-without-switching",
                "Create a branch without switching",
                DEBUT,
                (
                    "v21m-payments",
                    "v21m-notifications",
                    "v21m-export",
                ),
            ),
            ScenarioSpec(
                "start-from-another-tip",
                "Start from a chosen commit",
                DEBUT,
                (
                    "v21h-from-develop",
                    "v21h-hotfix-c1",
                ),
            ),
        ),
        "hard": (
            ScenarioSpec(
                "save-detached-work-then-return",
                "Save detached work, then go back",
                TRANSFER,
                (
                    "bc-hard-review-snap",
                    "switch-hard-detached-save-and-return",
                ),
            ),
            ScenarioSpec(
                "mark-a-release-point",
                "Mark a release point without leaving main",
                TRANSFER,
                (
                    "branch-hard-mark-release-point",
                    "branch-hard-mark-audit-point",
                ),
            ),
        ),
    },
    # Branch Naming Conventions
    "branch-naming-and-housekeeping": {
        "easy": (
            ScenarioSpec(
                "follow-the-convention",
                "Follow the naming convention",
                PRACTICE,
                (
                    "bn-easy-corp-jira",
                    "bn-easy-startup-feat",
                    "bn-easy-oss-user",
                    "bn-easy-cap-initials",
                    "bn-easy-free-client",
                ),
            ),
            ScenarioSpec(
                "delete-a-merged-branch",
                "Delete a merged branch",
                DEBUT,
                (
                    "bn-easy-delete-merged-typo",
                    "bn-easy-delete-merged-spike",
                ),
            ),
            ScenarioSpec(
                "replace-a-badly-named-branch",
                "Replace a badly named branch",
                COMPOSE,
                (
                    "bn-hard-oss-rename",
                    "bn-hard-corp-rename",
                ),
            ),
        ),
        "medium": (
            ScenarioSpec(
                "build-the-name-from-the-brief",
                "Build the name from the brief",
                PRACTICE,
                (
                    "bn-med-corp-notif",
                    "bn-med-startup-bugfix",
                    "bn-med-devops-scope",
                    "bn-med-oss-infer",
                ),
            ),
            ScenarioSpec(
                "fix-the-name-keep-the-convention",
                "Fix the name, keep the convention",
                COMPOSE,
                (
                    "bn-hard-startup-prefix",
                    "bn-hard-qa-camel",
                ),
            ),
        ),
        "hard": (
            ScenarioSpec(
                "start-the-fix-on-a-well-named-branch",
                "Start the fix on a well-named branch",
                SPIRAL,
                (
                    "bn-hard-named-branch-commit-parser",
                    "bn-hard-named-branch-commit-billing",
                ),
            ),
            ScenarioSpec(
                "clear-out-merged-branches",
                "Clear out the merged branches",
                TRANSFER,
                (
                    "bn-hard-clear-merged-sprint",
                    "bn-hard-clear-merged-release",
                ),
            ),
        ),
    },
    # Stashing Work in Progress
    "stashing-work-in-progress": {
        "easy": (
            ScenarioSpec(
                "shelve-and-switch",
                "Shelve work and switch",
                DEBUT,
                (
                    "v23e-auth",
                    "v23e-notify",
                    "v23e-cache",
                    "stash-easy-cap-review",
                    "stash-easy-docs-switch",
                ),
            ),
            ScenarioSpec(
                "bring-it-back",
                "Bring the shelved work back",
                DEBUT,
                (
                    "stash-easy-pop-search",
                    "stash-easy-pop-profile",
                ),
            ),
            ScenarioSpec(
                "stash-visit-return-restore",
                "Stash, visit, return, restore",
                COMPOSE,
                (
                    "v23m-to-main",
                    "v23m-to-hotfix",
                    "v23m-to-release",
                    "stash-med-corp-named",
                ),
            ),
        ),
        "medium": (
            ScenarioSpec(
                "discard-a-cancelled-draft",
                "Discard a cancelled draft",
                DEBUT,
                (
                    "v23h-dropped-auth",
                    "v23h-dropped-api",
                ),
            ),
            ScenarioSpec(
                "two-stashes-keep-the-right-one",
                "Two stashes, keep the right one",
                COMPOSE,
                (
                    "stash-hard-oss-multi",
                    "stash-hard-two-stashes-reports",
                ),
            ),
        ),
        "hard": (
            ScenarioSpec(
                "cancelled-work-clean-exit",
                "Cancelled work, clean exit",
                TRANSFER,
                (
                    "v23h-dropped-refactor",
                    "stash-hard-cancelled-experiment",
                ),
            ),
            ScenarioSpec(
                "park-the-draft-for-later",
                "Park the draft for later",
                TRANSFER,
                (
                    "stash-hard-park-draft-search",
                    "stash-hard-park-draft-billing",
                ),
            ),
        ),
    },
    # Pushing to a Remote
    "pushing-to-a-remote": {
        "easy": (
            ScenarioSpec(
                "publish-a-branch",
                "Publish a branch",
                DEBUT,
                (
                    "v24e-auth",
                    "v24e-orders",
                    "v24e-parser",
                    "push-easy-cap-auth",
                    "push-easy-free-landing",
                ),
            ),
            ScenarioSpec(
                "publish-and-track",
                "Publish and track",
                DEBUT,
                (
                    "v24m-auth",
                    "v24m-orders",
                ),
            ),
            ScenarioSpec(
                "track-another-branch",
                "Publish and track another branch",
                PRACTICE,
                (
                    "v24m-parser",
                    "push-med-docs-track",
                ),
            ),
        ),
        "medium": (
            ScenarioSpec(
                "branch-commit-publish",
                "Branch, commit, publish",
                SPIRAL,
                (
                    "push-medium-branch-commit-publish-search",
                    "push-medium-branch-commit-publish-invoices",
                ),
            ),
            ScenarioSpec(
                "republish-rewritten-history",
                "Republish rewritten history safely",
                DEBUT,
                (
                    "v24h-auth",
                    "v24h-orders",
                ),
            ),
        ),
        "hard": (
            ScenarioSpec(
                "amend-then-republish",
                "Amend a published commit, republish",
                SPIRAL,
                (
                    "push-hard-amend-then-lease-api",
                    "push-hard-amend-then-lease-docs",
                ),
            ),
            ScenarioSpec(
                "rewritten-branch-careful-publish",
                "Rewritten branch, careful publish",
                TRANSFER,
                (
                    "v24h-parser",
                    "push-hard-devops-fwl",
                ),
            ),
        ),
    },
    # Fetching and Pulling from a Remote
    "fetching-and-pulling": {
        "easy": (
            ScenarioSpec(
                "see-whats-new",
                "See what's new on origin",
                DEBUT,
                (
                    "v25e-main",
                    "v25e-feature",
                    "v25e-develop",
                ),
            ),
            ScenarioSpec(
                "bring-new-commits-in",
                "Bring the new commits in",
                DEBUT,
                (
                    "v25m-main",
                    "v25m-feature",
                ),
            ),
            ScenarioSpec(
                "check-origin-again",
                "Check origin again",
                PRACTICE,
                (
                    "fetch-easy-cap-check",
                    "fetch-easy-corp-list",
                ),
            ),
            ScenarioSpec(
                "bring-more-commits-in",
                "Bring more commits in",
                PRACTICE,
                (
                    "v25m-develop",
                    "pull-med-free-client",
                ),
            ),
        ),
        "medium": (
            ScenarioSpec(
                "review-before-integrating",
                "Review before integrating",
                COMPOSE,
                (
                    "v25h-main",
                    "v25h-feature",
                ),
            ),
            ScenarioSpec(
                "update-then-branch",
                "Update, then branch from fresh main",
                SPIRAL,
                (
                    "pull-medium-update-then-branch-ui",
                    "pull-medium-update-then-branch-api",
                ),
            ),
        ),
        "hard": (
            ScenarioSpec(
                "review-incoming-work",
                "Review incoming work",
                TRANSFER,
                (
                    "v25h-develop",
                    "fetch-hard-oss-review",
                ),
            ),
            ScenarioSpec(
                "pull-with-work-in-progress",
                "Pull with local work in progress",
                SPIRAL,
                (
                    "pull-hard-stash-pull-pop-docs",
                    "pull-hard-stash-pull-pop-app",
                ),
            ),
        ),
    },
    # Reconciling Diverged Local and Remote Histories
    "reconciling-diverged-histories": {
        "easy": (
            ScenarioSpec(
                "pull-then-push-again",
                "Pull, then push again",
                PRACTICE,
                (
                    "v26e-auth",
                    "v26e-payments",
                    "v26e-hotfix",
                    "rec-easy-cap-ui",
                    "rec-easy-docs-chapter",
                ),
            ),
            ScenarioSpec(
                "fetch-merge-push",
                "Fetch, merge the remote branch, push",
                DEBUT,
                (
                    "v26m-auth",
                    "v26m-payments",
                ),
            ),
            ScenarioSpec(
                "fetch-merge-push-practice",
                "Reconcile a teammate's branch",
                PRACTICE,
                (
                    "v26m-hotfix",
                    "rec-med-qa-testrunner",
                ),
            ),
        ),
        "medium": (
            ScenarioSpec(
                "commit-reconcile-publish",
                "Commit, reconcile, publish",
                SPIRAL,
                (
                    "rec-medium-commit-then-reconcile-docs",
                    "rec-medium-commit-then-reconcile-api",
                ),
            ),
            ScenarioSpec(
                "reconcile-from-the-wrong-branch",
                "Reconcile from the wrong branch",
                TRANSFER,
                (
                    "v26h-auth",
                    "v26h-payments",
                ),
            ),
        ),
        "hard": (
            ScenarioSpec(
                "reconcile-and-publish-under-pressure",
                "Reconcile and publish under pressure",
                TRANSFER,
                (
                    "v26h-hotfix",
                    "rec-hard-corp-audit",
                ),
            ),
            ScenarioSpec(
                "commit-fetch-merge-publish",
                "Commit, fetch, merge, publish",
                SPIRAL,
                (
                    "rec-hard-commit-fetch-merge-search",
                    "rec-hard-commit-fetch-merge-billing",
                ),
            ),
        ),
    },
    # Completing Branch Merges
    "completing-branch-merges": {
        "easy": (
            ScenarioSpec(
                "fast-forward-merge",
                "Fast-forward merge",
                PRACTICE,
                (
                    "v27e-auth",
                    "v27e-payments",
                    "v27e-hotfix",
                    "merge-easy-cap-docs",
                    "merge-easy-free-contact",
                ),
            ),
            ScenarioSpec(
                "keep-a-visible-merge",
                "Keep a visible merge commit",
                DEBUT,
                (
                    "v27m-auth",
                    "v27m-payments",
                ),
            ),
            ScenarioSpec(
                "no-ff-practice",
                "Merge with a merge commit",
                PRACTICE,
                (
                    "v27m-hotfix",
                    "merge-med-corp-sso",
                ),
            ),
        ),
        "medium": (
            ScenarioSpec(
                "finish-then-land",
                "Finish the feature, then land it",
                SPIRAL,
                (
                    "merge-medium-commit-switch-noff-reports",
                    "merge-medium-commit-switch-noff-auth",
                ),
            ),
            ScenarioSpec(
                "land-from-the-wrong-branch",
                "Land from the wrong branch",
                TRANSFER,
                (
                    "v27h-auth",
                    "v27h-payments",
                ),
            ),
        ),
        "hard": (
            ScenarioSpec(
                "land-a-release-fix-from-the-wrong-branch",
                "Land a release fix from the wrong branch",
                TRANSFER,
                (
                    "v27h-hotfix",
                    "merge-hard-devops-cert",
                ),
            ),
            ScenarioSpec(
                "land-publish-tidy-up",
                "Land, publish, tidy up",
                SPIRAL,
                (
                    "merge-hard-land-publish-tidy-search",
                    "merge-hard-land-publish-tidy-billing",
                ),
            ),
        ),
    },
    # Squash Merging
    "squash-merging": {
        "easy": (
            ScenarioSpec(
                "squash-into-one-commit",
                "Squash a branch into one commit",
                DEBUT,
                (
                    "v28e-auth",
                    "v28e-orders",
                    "v28e-parser",
                    "squash-easy-cap-report",
                    "squash-easy-free-payment",
                ),
            ),
            ScenarioSpec(
                "squash-then-force-delete",
                "Squash, then force-delete the branch",
                DEBUT,
                (
                    "v28h-auth",
                    "v28h-orders",
                ),
            ),
            ScenarioSpec(
                "one-commit-no-leftovers",
                "One commit, no leftovers",
                PRACTICE,
                (
                    "v28h-parser",
                    "squash-hard-devops-log",
                ),
            ),
        ),
        "medium": (
            ScenarioSpec(
                "squash-a-remote-branch",
                "Squash a teammate's remote branch",
                PRACTICE,
                (
                    "v28m-auth",
                    "v28m-orders",
                    "v28m-parser",
                    "squash-med-corp-gdpr",
                ),
            ),
            ScenarioSpec(
                "squash-and-publish",
                "Squash and publish",
                SPIRAL,
                (
                    "squash-medium-squash-publish-onboarding",
                    "squash-medium-squash-publish-export",
                ),
            ),
        ),
        "hard": (
            ScenarioSpec(
                "squash-land-from-another-branch",
                "Squash-land from another branch",
                SPIRAL,
                (
                    "squash-hard-switch-squash-cleanup-cli",
                    "squash-hard-switch-squash-cleanup-ui",
                ),
            ),
            ScenarioSpec(
                "squash-a-remote-branch-publish-tidy",
                "Squash a remote branch, publish, tidy up",
                TRANSFER,
                (
                    "squash-hard-remote-publish-tidy-search",
                    "squash-hard-remote-publish-tidy-docs",
                ),
            ),
        ),
    },
    # Deleting and Recovering Remote Branches
    "deleting-and-recovering-remote-branches": {
        "easy": (
            ScenarioSpec(
                "delete-a-remote-branch",
                "Delete a remote branch",
                DEBUT,
                (
                    "v29e-auth",
                    "v29e-orders",
                    "v29e-parser",
                    "rb-easy-cap-group",
                    "rb-easy-corp-sprint",
                ),
            ),
            ScenarioSpec(
                "prune-stale-refs",
                "Prune stale remote-tracking refs",
                DEBUT,
                (
                    "v29m-auth",
                    "v29m-orders",
                    "v29m-parser",
                    "rb-med-free-prune",
                ),
            ),
            ScenarioSpec(
                "delete-then-prune",
                "Delete one, prune the rest",
                COMPOSE,
                (
                    "rb-easy-delete-then-prune-docs",
                    "rb-easy-delete-then-prune-api",
                ),
            ),
        ),
        "medium": (
            ScenarioSpec(
                "retire-a-branch-everywhere",
                "Retire a branch everywhere",
                COMPOSE,
                (
                    "v29h-auth",
                    "v29h-orders",
                ),
            ),
            ScenarioSpec(
                "land-and-retire",
                "Land and retire",
                SPIRAL,
                (
                    "rb-medium-land-and-retire-search",
                    "rb-medium-land-and-retire-billing",
                ),
            ),
        ),
        "hard": (
            ScenarioSpec(
                "retire-safely",
                "Retire safely",
                TRANSFER,
                (
                    "v29h-parser",
                    "rb-hard-oss-full",
                ),
            ),
            ScenarioSpec(
                "fetch-land-publish-retire-prune",
                "Fetch, land, publish, retire, prune",
                SPIRAL,
                (
                    "rb-hard-capstone-release-notes",
                    "rb-hard-capstone-payments",
                ),
            ),
        ),
    },
}
