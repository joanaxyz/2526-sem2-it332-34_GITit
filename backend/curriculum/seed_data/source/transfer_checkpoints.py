"""Current assessment decisions and preserved versions of transfer checkpoints.

Novelty is a changed repository decision, not a longer answer key. The outcome
suite proves the intended dependency and accepts state-equivalent Git routes.
Retired IDs stay available only to learners/studies already pinned to them.
"""

from __future__ import annotations

from typing import NotRequired, TypedDict


class TransferCheckpointSpec(TypedDict):
    case_id: str
    note: str
    prerequisites: NotRequired[tuple[str, ...]]


TRANSFER_CHECKPOINTS: dict[str, TransferCheckpointSpec] = {
    "resolving-conflicts-manually": {
        "case_id": "manual-transfer-stale-index-v2",
        "note": "Practice stages a fresh resolution. Here the staged resolution is stale: a corrected working copy must replace it before the merge is committed.",
    },
    "using-a-merge-tool": {
        "case_id": "mergetool-transfer-clean-guide-v2",
        "note": "Practice finishes marked conflicts. Here the clean auto-merged guide is inconsistent with the resolved policy and needs a separate staged correction; tool-only completion is insufficient.",
        "prerequisites": ("resolving-conflicts-manually",),
    },
    "cherry-picking-commits": {
        "case_id": "cherry-transfer-mixed-commit-v2",
        "note": "Practice selects whole commits. Here one source commit bundles a wanted fix and a forbidden release-policy change; its staged effect must be reviewed before committing.",
    },
    "recovering-from-hard-resets": {
        "case_id": "reflog-transfer-two-destinations-v2",
        "note": "Practice recovers one wanted candidate. Here both lost commits must survive with different destinations: the completed report on main and the redesign on a separate branch.",
    },
    "reversing-pushed-commits-safely": {
        "case_id": "revert-transfer-returned-regression-v2",
        "note": "Practice reverses a faulty published change. Here the old fault was already reversed; undoing it again destroys a newer correct improvement, so the later recurrence must be identified.",
    },
    "completing-rebase-recovery-sequences": {
        "case_id": "rebase-transfer-invoices-v2",
        "note": "Aborting returns to an already-incomplete branch. The correct old tip must be recovered before selective replay; recovery without the correct boundary brings the spike back.",
    },
}


# Compatibility data, never fresh assignment candidates. Keep authored content
# and audit coverage while pinned checkpoints/studies can still read/play it.
RETIRED_TRANSFER_CHECKPOINTS: dict[str, str] = {
    "manual-transfer-checkout-v2": "resolving-conflicts-manually",
    "mergetool-transfer-pricing-refresh": "using-a-merge-tool",
    "cherry-transfer-release-backport": "cherry-picking-commits",
    "reflog-transfer-report-rollback": "recovering-from-hard-resets",
    "revert-transfer-statements": "reversing-pushed-commits-safely",
    "rebase-transfer-invoices": "completing-rebase-recovery-sequences",
}
