"""Module 1 scenario placement: Local Repository Foundations (SCENARIO_MAP.md).

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
    # Initializing Repositories
    "initializing-a-local-repository": {
        "easy": (
            ScenarioSpec(
                "start-tracking-this-folder",
                "Start tracking this folder",
                DEBUT,
                (
                    "init-easy-plain-notes",
                    "init-easy-plain-recipes",
                ),
            ),
            ScenarioSpec(
                "track-this-folder",
                "Choose the first branch",
                DEBUT,
                (
                    "init-easy-current-empty",
                    "init-easy-trunk-branch",
                ),
            ),
            ScenarioSpec(
                "new-project-folder",
                "Start a new project folder",
                DEBUT,
                (
                    "init-easy-invoice",
                    "init-med-oss",
                ),
            ),
            ScenarioSpec(
                "new-folder-among-other-files",
                "A new folder among other files",
                PRACTICE,
                (
                    "init-hard-ci",
                    "init-easy-new-folder-among-files",
                ),
            ),
        ),
        "medium": (
            ScenarioSpec(
                "folder-and-branch-from-brief",
                "Folder and branch from the brief",
                PRACTICE,
                (
                    "init-medium-docs-site",
                    "init-medium-trunk-api-playground",
                ),
            ),
            ScenarioSpec(
                "existing-files-stay-untracked",
                "Existing files stay untracked",
                PRACTICE,
                (
                    "init-medium-existing-files",
                    "init-medium-existing-sketches",
                ),
            ),
        ),
        "hard": (
            ScenarioSpec(
                "only-the-right-subfolder",
                "Only the right subfolder",
                TRANSFER,
                (
                    "init-hard-research-log",
                    "init-hard-ui-kit",
                ),
            ),
            ScenarioSpec(
                "nested-project-folder",
                "A nested project folder",
                TRANSFER,
                (
                    "init-hard-nested-service",
                    "init-hard-nested-course",
                ),
            ),
        ),
    },
    # Cloning Remote Repositories
    "cloning-a-remote-repository": {
        "easy": (
            ScenarioSpec(
                "clone-a-repository",
                "Clone a repository",
                DEBUT,
                (
                    "clone-easy-docs-portal",
                    "clone-easy-style-guide",
                ),
            ),
            ScenarioSpec(
                "clone-into-named-folder",
                "Clone into a named folder",
                DEBUT,
                (
                    "clone-easy-api-lab",
                    "clone-easy-corp",
                ),
            ),
            ScenarioSpec(
                "clone-a-specific-branch",
                "Clone a specific branch",
                DEBUT,
                (
                    "clone-easy-profile-starter",
                    "clone-med-feature",
                ),
            ),
            ScenarioSpec(
                "branch-into-named-folder",
                "A branch into a named folder",
                COMPOSE,
                (
                    "clone-medium-cli-starter-folder",
                    "clone-easy-branch-folder-handbook",
                ),
            ),
        ),
        "medium": (
            ScenarioSpec(
                "shallow-history",
                "Shallow history",
                DEBUT,
                (
                    "clone-medium-css-kit-shallow",
                    "clone-medium-shallow-icons",
                ),
            ),
            ScenarioSpec(
                "ssh-into-named-folder",
                "SSH address, named folder",
                DEBUT,
                (
                    "clone-medium-analytics-ssh",
                    "clone-hard-research-log-ssh",
                ),
            ),
        ),
        "hard": (
            ScenarioSpec(
                "shallow-copy-of-one-branch",
                "Shallow copy of one branch",
                TRANSFER,
                (
                    "clone-hard-mobile-ui-shallow-branch",
                    "clone-hard-lab-notebook-depth-branch",
                ),
            ),
            ScenarioSpec(
                "shallow-review-copy-over-ssh",
                "Shallow review copy over SSH",
                TRANSFER,
                (
                    "clone-hard-ssh-shallow",
                    "clone-hard-shallow-ssh-audit",
                ),
            ),
        ),
    },
    # Staging and Committing
    "staging-and-committing-basic-workflow": {
        "easy": (
            ScenarioSpec(
                "stage-and-commit-one-change",
                "Stage and commit one change",
                DEBUT,
                (
                    "commit-easy-form-validation",
                    "commit-easy-readme-setup",
                    "commit-easy-navbar-spacing",
                ),
            ),
            ScenarioSpec(
                "stage-several-files",
                "Stage several files at once",
                DEBUT,
                (
                    "commit-med-docker",
                    "commit-medium-profile-card",
                ),
            ),
            ScenarioSpec(
                "a-two-file-change",
                "A two-file change",
                PRACTICE,
                (
                    "commit-medium-search-results",
                    "commit-medium-export-flow",
                ),
            ),
        ),
        "medium": (
            ScenarioSpec(
                "first-snapshot-of-a-new-project",
                "First snapshot of a new project",
                SPIRAL,
                (
                    "commit-medium-new-project-portfolio",
                    "commit-medium-new-project-recipes",
                ),
            ),
            ScenarioSpec(
                "a-bigger-change",
                "A bigger change",
                PRACTICE,
                (
                    "commit-easy-initial",
                    "commit-medium-three-file-release",
                ),
            ),
        ),
        "hard": (
            ScenarioSpec(
                "leave-the-distractor-out",
                "Leave the distractor out",
                TRANSFER,
                (
                    "commit-hard-selective",
                    "commit-hard-profile-distractor",
                    "commit-hard-export-distractor",
                ),
            ),
            ScenarioSpec(
                "two-targets-two-distractors",
                "Two targets, two distractors",
                TRANSFER,
                (
                    "commit-hard-parser",
                    "commit-hard-search-two-targets-one-distractor",
                ),
            ),
        ),
    },
    # Partial Staging
    "partial-staging-and-git-add-p": {
        "easy": (
            ScenarioSpec(
                "stage-one-hunk",
                "Stage one hunk",
                DEBUT,
                (
                    "partial-easy-billing",
                    "partial-easy-auth-validation",
                    "partial-easy-export-format",
                ),
            ),
            ScenarioSpec(
                "another-file-another-hunk",
                "Another file, another hunk",
                PRACTICE,
                (
                    "partial-easy-routes",
                    "partial-easy-search-ranking",
                ),
            ),
        ),
        "medium": (
            ScenarioSpec(
                "one-hunk-out-of-many",
                "One hunk out of many",
                PRACTICE,
                (
                    "partial-med-three-hunk",
                    "partial-medium-profile-validation",
                    "partial-medium-payment-rounding",
                    "partial-medium-dashboard-filter",
                    "partial-hard-terraform",
                ),
            ),
            ScenarioSpec(
                "a-hunk-and-a-whole-file",
                "A hunk and a whole file",
                SPIRAL,
                (
                    "partial-medium-hunk-plus-test",
                    "partial-medium-hunk-plus-doc",
                ),
            ),
        ),
        "hard": (
            ScenarioSpec(
                "hunks-across-code-and-tests",
                "Hunks across code and tests",
                TRANSFER,
                (
                    "partial-hard-auth-cross-file",
                    "partial-hard-search-cross-file",
                    "partial-hard-export-cross-file",
                ),
            ),
            ScenarioSpec(
                "split-one-file-into-two-commits",
                "Split one file into two commits",
                COMPOSE,
                (
                    "partial-hard-split-two-commits-api",
                    "partial-hard-split-two-commits-ui",
                ),
            ),
        ),
    },
    # Amending Commits
    "amending-commits": {
        "easy": (
            ScenarioSpec(
                "fix-the-last-message",
                "Fix the last commit message",
                DEBUT,
                (
                    "amend-easy-typo",
                    "amend-easy-login-copy-message",
                    "amend-easy-readme-message",
                    "amend-easy-navbar-message",
                    "amend-hard-convention",
                ),
            ),
            ScenarioSpec(
                "add-the-forgotten-file",
                "Add the forgotten file",
                PRACTICE,
                (
                    "amend-easy-forgot",
                    "amend-medium-profile-missing-css",
                    "amend-medium-export-doc",
                    "amend-medium-search-template",
                ),
            ),
        ),
        "medium": (
            ScenarioSpec(
                "amend-content-and-message",
                "Amend content and message",
                PRACTICE,
                (
                    "amend-med-both",
                    "amend-hard-profile-message-and-layout",
                ),
            ),
            ScenarioSpec(
                "amend-in-one-hunk",
                "Amend in one hunk",
                SPIRAL,
                (
                    "amend-medium-hunk-into-last-checkout",
                    "amend-medium-hunk-into-last-search",
                ),
            ),
        ),
        "hard": (
            ScenarioSpec(
                "missing-file-and-wrong-message",
                "Missing file and wrong message",
                TRANSFER,
                (
                    "amend-hard-auth-message-and-test",
                    "amend-hard-export-message-and-doc",
                ),
            ),
            ScenarioSpec(
                "fix-the-message-then-commit-the-rest",
                "Fix the last message, then commit the rest",
                COMPOSE,
                (
                    "amend-hard-fix-message-then-commit-api",
                    "amend-hard-fix-message-then-commit-docs",
                ),
            ),
        ),
    },
    # Unstaging and Discarding Changes
    "unstaging-and-discarding-changes": {
        "easy": (
            ScenarioSpec(
                "throw-away-a-working-change",
                "Throw away a working change",
                DEBUT,
                (
                    "restore-easy-discard",
                    "restore-easy-discard-theme",
                ),
            ),
            ScenarioSpec(
                "unstage-keep-the-edit",
                "Unstage but keep the edit",
                DEBUT,
                (
                    "restore-easy-unstage",
                    "restore-easy-unstage-app",
                    "restore-easy-unstage-guide",
                    "restore-easy-unstage-css",
                ),
            ),
            ScenarioSpec(
                "unstage-and-discard-together",
                "Unstage one, discard another",
                COMPOSE,
                (
                    "restore-med-unstage-discard",
                    "restore-medium-app-debug",
                ),
            ),
        ),
        "medium": (
            ScenarioSpec(
                "unstage-one-discard-another",
                "Sort out a mixed folder",
                COMPOSE,
                (
                    "restore-medium-docs-scratch",
                    "restore-medium-css-build",
                ),
            ),
            ScenarioSpec(
                "fix-the-staging-then-commit",
                "Fix the staging, then commit",
                SPIRAL,
                (
                    "restore-medium-unstage-then-commit-login",
                    "restore-medium-unstage-then-commit-cart",
                ),
            ),
        ),
        "hard": (
            ScenarioSpec(
                "several-to-unstage-one-to-discard",
                "Several to unstage, one to discard",
                TRANSFER,
                (
                    "restore-hard-cleanup",
                    "restore-hard-mixed-profile",
                    "restore-hard-mixed-export",
                    "restore-hard-mixed-search",
                ),
            ),
            ScenarioSpec(
                "clean-up-then-commit-only-the-fix",
                "Clean up, then commit only the fix",
                SPIRAL,
                (
                    "restore-hard-capstone-report",
                    "restore-hard-capstone-invoice",
                ),
            ),
        ),
    },
}
