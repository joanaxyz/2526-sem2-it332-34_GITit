"""GitCoin rewards for adventure tiers: one ladder, paid once per tier.

A tier pays on its first completion, never on a replay. Easy keeps the
per-level key it has always paid under, so a learner who cleared Easy before
the ladder existed is not paid twice.
"""

from __future__ import annotations

from collections.abc import Iterable

from common.constants import DIFFICULTY_EASY, DIFFICULTY_HARD, DIFFICULTY_MEDIUM
from progress.wallet import WalletService

TIER_REWARD_COINS = {DIFFICULTY_EASY: 25, DIFFICULTY_MEDIUM: 35, DIFFICULTY_HARD: 50}
# A module's Challenge Gate trials, seeded into ChallengeTrial.reward_coins and
# paid once per trial by the challenge runtime (decision D12).
CHALLENGE_GATE_REWARD_COINS = {DIFFICULTY_EASY: 50, DIFFICULTY_MEDIUM: 75, DIFFICULTY_HARD: 100}


def tier_reward_coins(tier) -> int:
    return TIER_REWARD_COINS.get(tier.difficulty, 0)


def tier_reward_key(tier) -> str:
    if tier.difficulty == DIFFICULTY_EASY:
        return f"adventure-level-reward:{tier.adventure_level_id}"
    return f"adventure-tier-reward:{tier.id}"


def tier_reward_payload(tier, *, claimed_keys: set[str]) -> dict:
    return {"coins": tier_reward_coins(tier), "claimed": tier_reward_key(tier) in claimed_keys}


def claimed_tier_reward_keys(*, player, tiers: Iterable) -> set[str]:
    """The tier rewards this player has already been paid, in one query."""
    if player is None:
        return set()
    keys = [tier_reward_key(tier) for tier in tiers]
    return WalletService().awarded_keys(player=player, award_keys=keys) if keys else set()


def award_tier_reward(*, player, tier) -> int:
    """Pay the tier's reward once; returns the coins newly credited."""
    coins = tier_reward_coins(tier)
    reason = (
        "adventure_level_reward" if tier.difficulty == DIFFICULTY_EASY else "adventure_tier_reward"
    )
    paid = WalletService().award(
        player=player, amount=coins, reason=reason, award_key=tier_reward_key(tier)
    )
    return coins if paid else 0
