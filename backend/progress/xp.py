"""XP: the lifetime score behind ranks and the leaderboard.

XP is never spent, so it only ever rises. Each source pays once per player
through its award key, which lets replays and the backfill call these freely.
"""

from __future__ import annotations

from django.db import IntegrityError, models, transaction

from common.constants import DIFFICULTY_EASY, DIFFICULTY_HARD, DIFFICULTY_MEDIUM
from progress.models import XpTransaction

TIER_XP = {DIFFICULTY_EASY: 25, DIFFICULTY_MEDIUM: 35, DIFFICULTY_HARD: 50}
GATE_XP = {DIFFICULTY_EASY: 50, DIFFICULTY_MEDIUM: 75, DIFFICULTY_HARD: 100}
XP_PER_STAR = 10


class XpService:
    def award(self, *, player, amount: int, reason: str, award_key: str) -> bool:
        """Credit XP once per (player, award_key); True when newly awarded."""
        if amount <= 0:
            return False
        try:
            # Inner savepoint so a duplicate award does not poison the caller's
            # surrounding transaction.
            with transaction.atomic():
                XpTransaction.objects.create(
                    player=player, amount=amount, reason=reason, award_key=award_key
                )
        except IntegrityError:
            return False
        return True

    def total(self, *, player) -> int:
        total = XpTransaction.objects.filter(player=player).aggregate(total=models.Sum("amount"))[
            "total"
        ]
        return total or 0


def award_tier_xp(*, player, tier, stars: int) -> int:
    """Pay a cleared tier and each star earned so far; returns the XP newly credited.

    A replay that lifts the tier's best grade therefore pays only the new stars.
    """
    awards = [(f"tier:{tier.id}", TIER_XP.get(tier.difficulty, 0), "tier_clear")]
    awards += [
        (f"tier-star:{tier.id}:{star}", XP_PER_STAR, "tier_star") for star in range(1, stars + 1)
    ]
    paid = set(
        XpTransaction.objects.filter(
            player=player, award_key__in=[key for key, _amount, _reason in awards]
        ).values_list("award_key", flat=True)
    )
    service = XpService()
    return sum(
        amount
        for key, amount, reason in awards
        if key not in paid
        and service.award(player=player, amount=amount, reason=reason, award_key=key)
    )


def gate_xp(trial) -> int:
    return GATE_XP.get(trial.difficulty, 0)


def award_gate_xp(*, player, trial) -> int:
    """Pay a cleared Challenge Gate trial once; returns the XP newly credited."""
    amount = gate_xp(trial)
    paid = XpService().award(
        player=player, amount=amount, reason="gate_trial", award_key=f"trial:{trial.id}"
    )
    return amount if paid else 0
