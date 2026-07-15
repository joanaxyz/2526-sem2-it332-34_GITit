from progress.wallet import WalletService

# Fixed reward schedule for every chapter: percent-of-chapter-completion
# thresholds, each paying GitCoins once. The 100% chest is the chapter
# completion reward. Computed at runtime - no per-chapter authoring needed,
# since the threshold is already a percentage and doesn't care how many
# levels the chapter has.
CHEST_SCHEDULE = [
    {"threshold": 25, "coins": 25},
    {"threshold": 50, "coins": 60},
    {"threshold": 75, "coins": 100},
    {"threshold": 100, "coins": 150},
]


class ChapterChestService:
    """Awards the chapter's GitCoin chests when the learner's progress crosses
    the fixed schedule's thresholds. Progress is the same number the track map
    shows: passed adventures + threshold-meeting challenge clears over the
    chapter's total milestones. Each chest pays out once per (player, chapter,
    threshold)."""

    def award_chests(self, *, player, chapter) -> None:
        # Hidden runtime chapters back user-authored content. They should not
        # award official track progress chests unless the product later adds a
        # separate community-content reward track.
        if not getattr(chapter, "is_published", False):
            return
        # Local import: curriculum.selectors pulls in the adventure/challenge
        # model graph, which itself reaches back into progress.
        from curriculum.selectors import (
            chapter_completion_count_map,
            chapter_completion_denominator_map,
        )

        denominator = chapter_completion_denominator_map(chapter_ids=[chapter.id]).get(chapter.id, 0)
        if not denominator:
            return
        numerator = chapter_completion_count_map(player=player, chapter_ids=[chapter.id]).get(chapter.id, 0)
        progress = (numerator / denominator) * 100
        wallet = WalletService()
        for chest in CHEST_SCHEDULE:
            threshold = chest["threshold"]
            coins = chest["coins"]
            if progress < threshold:
                continue
            wallet.award(
                player=player,
                amount=coins,
                reason="chapter_chest",
                award_key=f"chapter-chest:{chapter.id}:{threshold}",
            )
