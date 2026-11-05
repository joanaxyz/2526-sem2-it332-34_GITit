"""Each Module 3-4 level's transfer checkpoint, the RTA task that closes the level.

Seeding reserves the case on the first scenario of the level's Hard tier, so it
never appears in practice, retries, replays or drills. Unlike the scenario's own
variants, a checkpoint is not a reskin: it composes what the level taught into a
route no practice variant uses, and its note records that difference (see
KPI_METHODOLOGY.md, "Transfer and exposure").
"""

from __future__ import annotations

TRANSFER_CHECKPOINTS: dict[str, dict[str, str]] = {
    "resolving-conflicts-manually": {
        "case_id": "manual-transfer-checkout-v2",
        "note": "Practice settles one conflicted file; this abandons a wrong merge, then settles two files in the right one.",
    },
    "using-a-merge-tool": {
        "case_id": "mergetool-transfer-pricing-refresh",
        "note": "Practice starts with a tool configured and one conflict; this sets the tool up from nothing, then settles two conflicted files beside a clean auto-merge.",
    },
    "cherry-picking-commits": {
        "case_id": "cherry-transfer-release-backport",
        "note": "Practice uses one picking technique per task; this clears a wrong pick, traces a conflicting fix, then folds two more fixes into one commit.",
    },
    "recovering-from-hard-resets": {
        "case_id": "reflog-transfer-report-rollback",
        "note": "Practice recovers one commit; this gives two lost commits different fates, a safe branch for one and a hard reset of main to the other.",
    },
    "reversing-pushed-commits-safely": {
        "case_id": "revert-transfer-statements",
        "note": "Practice separates or lightly pairs these moves; this rewrites one unpublished commit, then reverses two published ones in order, in one publish.",
    },
    "completing-rebase-recovery-sequences": {
        "case_id": "rebase-transfer-invoices",
        "note": "Practice repairs one rebase mistake; this aborts a rebase, restores the pushed tip from the reflog, replays with --onto and publishes safely.",
    },
}
