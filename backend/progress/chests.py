from progress.wallet import WalletService


class StoreyChestService:
    """Awards the storey's GitCoin chests when the learner's progress crosses
    their thresholds. Progress is the same number the tower shows: passed
    adventures + threshold-meeting challenge clears over the storey's total
    milestones. Each chest pays out once per (user, storey, threshold)."""

    def award_chests(self, *, user, storey) -> None:
        # Hidden runtime storeys back user-authored content. They should not
        # award official tower progress chests unless the product later adds a
        # separate community-content reward track.
        if not getattr(storey, "is_published", False):
            return
        # Local import: curriculum.selectors pulls in the adventure/challenge
        # model graph, which itself reaches back into progress.
        from curriculum.selectors import (
            storey_completion_count_map,
            storey_completion_denominator_map,
        )

        chests = storey.chest_rewards or []
        if not chests:
            return
        denominator = storey_completion_denominator_map(storey_ids=[storey.id]).get(storey.id, 0)
        if not denominator:
            return
        numerator = storey_completion_count_map(user=user, storey_ids=[storey.id]).get(storey.id, 0)
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
                reason="storey_chest",
                award_key=f"storey-chest:{storey.id}:{threshold}",
            )
