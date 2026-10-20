"""Module 1 wave placement: Local Repository Foundations (WAVE_MAP.md).

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
    # Initializing Repositories
    "initializing-a-local-repository": {
        "easy": (
            WaveSpec(
                "track-this-folder",
                "Track this folder",
                DEBUT,
                (
                    "init-easy-current-empty",
                    "init-easy-trunk-branch",
                ),
            ),
            WaveSpec(
                "new-project-folder",
                "Start a new project folder",
                PRACTICE,
                (
                    "init-easy-invoice",
                    "init-med-oss",
                ),
            ),
        ),
        "medium": (
            WaveSpec(
                "folder-and-branch-from-brief",
                "Folder and branch from the brief",
                PRACTICE,
                (
                    "init-medium-docs-site",
                    "init-medium-trunk-api-playground",
                ),
            ),
            WaveSpec(
                "existing-files-stay-untracked",
                "Existing files stay untracked",
                PRACTICE,
                (
                    "init-medium-existing-files",
                    "init-hard-ci",
                ),
            ),
        ),
        "hard": (
            WaveSpec(
                "only-the-right-subfolder",
                "Only the right subfolder",
                TRANSFER,
                (
                    "init-hard-research-log",
                    "init-hard-ui-kit",
                ),
            ),
            WaveSpec(
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
            WaveSpec(
                "clone-a-repository",
                "Clone a repository",
                DEBUT,
                (
                    "clone-easy-docs-portal",
                    "clone-easy-oss-ssh",
                ),
            ),
            WaveSpec(
                "clone-into-named-folder",
                "Clone into a named folder",
                DEBUT,
                (
                    "clone-easy-api-lab",
                    "clone-easy-corp",
                ),
            ),
            WaveSpec(
                "clone-a-specific-branch",
                "Clone a specific branch",
                DEBUT,
                (
                    "clone-easy-profile-starter",
                    "clone-med-feature",
                    "clone-medium-cli-starter-folder",
                ),
            ),
        ),
        "medium": (
            WaveSpec(
                "ssh-into-named-folder",
                "SSH address, named folder",
                PRACTICE,
                (
                    "clone-medium-analytics-ssh",
                    "clone-hard-research-log-ssh",
                ),
            ),
            WaveSpec(
                "shallow-history",
                "Shallow history",
                DEBUT,
                (
                    "clone-medium-css-kit-shallow",
                    "clone-medium-shallow-metrics",
                ),
            ),
        ),
        "hard": (
            WaveSpec(
                "shallow-copy-of-one-branch",
                "Shallow copy of one branch",
                TRANSFER,
                (
                    "clone-hard-mobile-ui-shallow-branch",
                    "clone-hard-lab-notebook-depth-branch",
                ),
            ),
            WaveSpec(
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
            WaveSpec(
                "stage-and-commit-one-change",
                "Stage and commit one change",
                DEBUT,
                (
                    "commit-easy-form-validation",
                    "commit-easy-readme-setup",
                    "commit-easy-navbar-spacing",
                    "commit-easy-auth-dir",
                ),
            ),
            WaveSpec(
                "stage-several-files",
                "Stage several files at once",
                DEBUT,
                (
                    "commit-easy-initial",
                    "commit-med-docker",
                ),
            ),
        ),
        "medium": (
            WaveSpec(
                "a-two-file-change",
                "A two-file change",
                PRACTICE,
                (
                    "commit-medium-profile-card",
                    "commit-medium-search-results",
                    "commit-medium-export-flow",
                ),
            ),
            WaveSpec(
                "first-snapshot-of-a-new-project",
                "First snapshot of a new project",
                SPIRAL,
                (
                    "commit-medium-new-project-portfolio",
                    "commit-medium-new-project-recipes",
                ),
            ),
        ),
        "hard": (
            WaveSpec(
                "leave-the-distractor-out",
                "Leave the distractor out",
                TRANSFER,
                (
                    "commit-hard-selective",
                    "commit-hard-profile-distractor",
                    "commit-hard-export-distractor",
                ),
            ),
            WaveSpec(
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
            WaveSpec(
                "stage-one-hunk",
                "Stage one hunk",
                DEBUT,
                (
                    "partial-easy-billing",
                    "partial-easy-auth-validation",
                    "partial-easy-export-format",
                ),
            ),
            WaveSpec(
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
            WaveSpec(
                "one-hunk-out-of-many",
                "One hunk out of many",
                PRACTICE,
                (
                    "partial-med-three-hunk",
                    "partial-medium-profile-validation",
                    "partial-medium-payment-rounding",
                    "partial-medium-dashboard-filter",
                ),
            ),
            WaveSpec(
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
            WaveSpec(
                "hunks-across-code-and-tests",
                "Hunks across code and tests",
                TRANSFER,
                (
                    "partial-hard-terraform",
                    "partial-hard-auth-cross-file",
                    "partial-hard-search-cross-file",
                    "partial-hard-export-cross-file",
                ),
            ),
            WaveSpec(
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
            WaveSpec(
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
            WaveSpec(
                "add-the-forgotten-file",
                "Add the forgotten file",
                PRACTICE,
                (
                    "amend-easy-forgot",
                    "amend-medium-profile-missing-css",
                ),
            ),
        ),
        "medium": (
            WaveSpec(
                "amend-content-and-message",
                "Amend content and message",
                PRACTICE,
                (
                    "amend-med-both",
                    "amend-medium-export-doc",
                    "amend-medium-search-template",
                ),
            ),
            WaveSpec(
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
            WaveSpec(
                "missing-file-and-wrong-message",
                "Missing file and wrong message",
                TRANSFER,
                (
                    "amend-hard-profile-message-and-layout",
                    "amend-hard-auth-message-and-test",
                    "amend-hard-export-message-and-doc",
                ),
            ),
            WaveSpec(
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
            WaveSpec(
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
            WaveSpec(
                "throw-away-a-working-change",
                "Throw away a working change",
                DEBUT,
                (
                    "restore-easy-discard",
                    "restore-easy-discard-theme",
                ),
            ),
        ),
        "medium": (
            WaveSpec(
                "unstage-one-discard-another",
                "Unstage one, discard another",
                COMPOSE,
                (
                    "restore-med-unstage-discard",
                    "restore-medium-app-debug",
                    "restore-medium-docs-scratch",
                    "restore-medium-css-build",
                ),
            ),
            WaveSpec(
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
            WaveSpec(
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
            WaveSpec(
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
