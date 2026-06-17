from progress.wallet import WalletService


class ChapterChestService:
    """Awards the chapter's GitCoin chests when the learner's progress crosses
    their thresholds. Progress is the same number the tower shows: passed
    adventures + threshold-meeting challenge clears over the chapter's total
    milestones. Each chest pays out once per (user, chapter, threshold)."""

    def award_chests(self, *, user, chapter) -> None:
        # Hidden runtime chapters back user-authored content. They should not
        # award official tower progress chests unless the product later adds a
        # separate community-content reward track.
        if not getattr(chapter, "is_published", False):
            return
        # Local import: curriculum.selectors pulls in the adventure/challenge
        # model graph, which itself reaches back into progress.
        from curriculum.selectors import (
            chapter_completion_count_map,
            chapter_completion_denominator_map,
        )

        chests = chapter.chest_rewards or []
        if not chests:
            return
        denominator = chapter_completion_denominator_map(chapter_ids=[chapter.id]).get(chapter.id, 0)
        if not denominator:
            return
        numerator = chapter_completion_count_map(user=user, chapter_ids=[chapter.id]).get(chapter.id, 0)
        progress = (numerator / denominator) * 100
        wallet = WalletService()
        for chest in chests:
            threshold = int(chest.get("threshold", 0))
            coins = int(chest.get("coins", 0))
            if threshold <= 0 or coins <= 0 or progress < threshold:
                continue
            wallet.award(
                user=user,
                amount=coins,
                reason="chapter_chest",
                award_key=f"chapter-chest:{chapter.id}:{threshold}",
            )
