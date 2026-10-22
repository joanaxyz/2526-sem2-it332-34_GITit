"""Chapter progress reward policy and orchestration."""

from rest_framework.exceptions import ValidationError

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

    def _eligible_thresholds(self, *, player, chapter) -> set[int]:
        if player is None or not getattr(chapter, "is_published", False):
            return set()
        denominator = chapter_completion_denominator_map(chapter_ids=[chapter.id]).get(
            chapter.id,
            0,
        )
        if not denominator:
            return set()
        numerator = chapter_completion_count_map(
            player=player,
            chapter_ids=[chapter.id],
        ).get(chapter.id, 0)
        return {
            chest["threshold"]
            for chest in CHEST_SCHEDULE
            if numerator * 100 >= chest["threshold"] * denominator
        }

    @staticmethod
    def _award_key(*, chapter, threshold: int) -> str:
        return f"chapter-chest:{chapter.id}:{threshold}"

    def reward_summary(self, *, player, chapter) -> dict:
        eligible = self._eligible_thresholds(player=player, chapter=chapter)
        wallet = WalletService()
        claimed = wallet.awarded_keys(
            player=player,
            award_keys=[
                self._award_key(chapter=chapter, threshold=chest["threshold"])
                for chest in CHEST_SCHEDULE
            ],
        )
        return {
            "results": [
                {
                    **chest,
                    "unlocked": chest["threshold"] in eligible,
                    "claimed": self._award_key(chapter=chapter, threshold=chest["threshold"])
                    in claimed,
                }
                for chest in CHEST_SCHEDULE
            ],
            "balance": wallet.summary(player=player)["balance"],
            "coins_awarded": 0,
        }

    def open_chest(self, *, player, chapter, threshold: int) -> dict:
        summary = self.reward_summary(player=player, chapter=chapter)
        chest = next((row for row in summary["results"] if row["threshold"] == threshold), None)
        if chest is None:
            raise ValidationError({"threshold": "Unknown progress chest."})
        if not chest["claimed"]:
            if not chest["unlocked"]:
                raise ValidationError(
                    {"threshold": f"Reach {threshold}% chapter completion to open this chest."}
                )
            if self._award(player=player, chapter=chapter, chest=chest):
                summary["coins_awarded"] = chest["coins"]
            chest["claimed"] = True
            summary["balance"] = WalletService().summary(player=player)["balance"]
        return summary

    def _award(self, *, player, chapter, chest: dict) -> bool:
        return WalletService().award(
            player=player,
            amount=chest["coins"],
            reason="chapter_chest",
            award_key=self._award_key(chapter=chapter, threshold=chest["threshold"]),
        )

    def award_chests(self, *, player, chapter) -> list[dict]:
        awarded: list[dict] = []
        eligible = self._eligible_thresholds(player=player, chapter=chapter)
        for chest in CHEST_SCHEDULE:
            if chest["threshold"] in eligible and self._award(
                player=player, chapter=chapter, chest=chest
            ):
                awarded.append(dict(chest))
        return awarded
