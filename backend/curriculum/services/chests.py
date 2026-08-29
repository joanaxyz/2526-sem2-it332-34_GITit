"""Chapter progress reward policy and orchestration."""

from curriculum.selectors.progress_counts import (
    chapter_completion_count_map,
    chapter_completion_denominator_map,
)
from progress.wallet import WalletService

CHEST_SCHEDULE = [
    {"threshold": 25, "coins": 25},
    {"threshold": 50, "coins": 60},
    {"threshold": 75, "coins": 100},
    {"threshold": 100, "coins": 150},
]


class ChapterChestService:
    """Award fixed chapter milestones once through the wallet ledger."""

    def award_chests(self, *, player, chapter) -> None:
        if not getattr(chapter, "is_published", False):
            return

        denominator = chapter_completion_denominator_map(chapter_ids=[chapter.id]).get(
            chapter.id,
            0,
        )
        if not denominator:
            return
        numerator = chapter_completion_count_map(
            player=player,
            chapter_ids=[chapter.id],
        ).get(chapter.id, 0)
        progress = (numerator / denominator) * 100
        wallet = WalletService()
        for chest in CHEST_SCHEDULE:
            threshold = chest["threshold"]
            if progress < threshold:
                continue
            wallet.award(
                player=player,
                amount=chest["coins"],
                reason="chapter_chest",
                award_key=f"chapter-chest:{chapter.id}:{threshold}",
            )
