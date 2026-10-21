"""The Challenge Gate at the end of each module; see CONTENT_AUTHORING_GUIDE.md.

A gate is one ChallengeLevel with an Easy, a Medium and a Hard trial. Each
trial is a workflow that combines what the module taught, in two variants so
a retry gets a fresh scenario. The gate opens once every level of the module
has cleared all three tiers; inside it, the trials open Easy, Medium, Hard.

Scenario text and answer keys live in ``wave_scenarios.md``; repositories and
grading in ``scenario_fixtures/gates.py``.
"""

from __future__ import annotations

CHALLENGE_GATES: dict[int, dict] = {
    1: {
        "slug": "module-1-challenge-gate",
        "title": "Foundations Gate",
        "summary": "Start a repository, shape commits and repair the last one before it leaves your machine.",
        "narrative": (
            "Raven, Sage and Maeve want proof that you can keep a project's history clean "
            "on your own: first snapshots, precise staging, and fixing your own mistakes."
        ),
        "trials": {
            "easy": [
                "gate1-easy-two-commit-start-field-log",
                "gate1-easy-two-commit-start-quiz",
            ],
            "medium": [
                "gate1-medium-complete-last-commit-search",
                "gate1-medium-complete-last-commit-upload",
            ],
            "hard": [
                "gate1-hard-reword-then-commit-export",
                "gate1-hard-reword-then-commit-billing",
            ],
        },
    },
    2: {
        "slug": "module-2-challenge-gate",
        "title": "Collaboration Gate",
        "summary": "Branch from fresh work, sync without losing yours, and land and retire a feature.",
        "narrative": (
            "The group now shares one remote. Show that you can keep up with it, interrupt "
            "your own work safely, and finish a feature branch from review to cleanup."
        ),
        "trials": {
            "easy": ["gate2-easy-fresh-branch-search", "gate2-easy-fresh-branch-invoices"],
            "medium": [
                "gate2-medium-stash-and-sync-reports",
                "gate2-medium-stash-and-sync-profile",
            ],
            "hard": ["gate2-hard-land-and-retire-filters", "gate2-hard-land-and-retire-export"],
        },
    },
    3: {
        "slug": "module-3-challenge-gate",
        "title": "Conflict Gate",
        "summary": "Settle a merge conflict, backport a fix with its origin, and back out the wrong merge.",
        "narrative": (
            "Conflicts are decisions. Resolve them deliberately, copy fixes where they are "
            "needed, and know when to abandon a merge instead of finishing it."
        ),
        "trials": {
            "easy": [
                "gate3-easy-merge-then-backport-banner",
                "gate3-easy-merge-then-backport-footer",
            ],
            "medium": ["gate3-medium-backport-tax", "gate3-medium-backport-locale"],
            "hard": [
                "gate3-hard-abort-then-tool-merge-pricing",
                "gate3-hard-abort-then-tool-merge-copy",
            ],
        },
    },
    4: {
        "slug": "module-4-challenge-gate",
        "title": "Recovery Gate",
        "summary": "Rescue lost work, undo local and published mistakes correctly, and move a branch.",
        "narrative": (
            "Every team breaks history sometimes. Prove you can recover what was lost, choose "
            "between rewriting and reversing, and republish rewritten work safely."
        ),
        "trials": {
            "easy": [
                "gate4-easy-recover-replay-publish-search",
                "gate4-easy-recover-replay-publish-receipts",
            ],
            "medium": [
                "gate4-medium-drop-local-revert-published-banner",
                "gate4-medium-drop-local-revert-published-alerts",
            ],
            "hard": [
                "gate4-hard-move-branch-onto-main-receipts",
                "gate4-hard-move-branch-onto-main-coupons",
            ],
        },
    },
}

# Tier command budgets (PLAN.md §3); a trial's minimum is its variants' answer key.
GATE_MAX_COUNTED_COMMANDS = {"easy": 12, "medium": 10, "hard": 8}
