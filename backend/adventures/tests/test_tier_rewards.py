"""Every tier pays its ladder reward once, and the reward is visible before play."""

from django.core.management import call_command

from adventures.models import AdventureLevel, AdventureLevelTier, AdventureLevelTierWave
from adventures.rewards import (
    TIER_REWARD_COINS,
    award_tier_reward,
    claimed_tier_reward_keys,
    tier_reward_key,
)
from curriculum.models import Chapter, Story
from curriculum.selectors.adventure_access import (
    _build_adventure_tier_access,
    adventure_level_tier_payload,
)
from players.services import get_or_create_player
from progress.models import AdventureLevelTierCompletion, CoinTransaction, Wallet


def _tiers(django_user_model):
    player = get_or_create_player(
        django_user_model.objects.create_user(username="ladder", password="pass12345")
    )
    story = Story.objects.create(slug="ladder-story", title="Story")
    chapter = Chapter.objects.create(
        story=story, slug="ladder-chapter", number=1, title="Module 1", description=""
    )
    level = AdventureLevel.objects.create(chapter=chapter, slug="ladder-level", title="Level")
    tiers = {
        difficulty: AdventureLevelTier.objects.create(adventure_level=level, difficulty=difficulty)
        for difficulty in ("easy", "medium", "hard")
    }
    for tier in tiers.values():
        AdventureLevelTierWave.objects.create(
            tier=tier,
            slug=f"wave-{tier.difficulty}",
            min_counted_commands=1,
            max_counted_commands=8,
        )
    return player, level, tiers


def test_each_tier_pays_its_ladder_amount_once(db, django_user_model):
    player, level, tiers = _tiers(django_user_model)

    paid = {
        difficulty: award_tier_reward(player=player, tier=tier)
        for difficulty, tier in tiers.items()
    }
    again = [award_tier_reward(player=player, tier=tier) for tier in tiers.values()]

    assert paid == TIER_REWARD_COINS == {"easy": 25, "medium": 35, "hard": 50}
    assert again == [0, 0, 0]
    assert Wallet.objects.get(player=player).balance == 110
    # Easy keeps the per-level key it always paid under, so nobody is paid twice.
    assert tier_reward_key(tiers["easy"]) == f"adventure-level-reward:{level.id}"
    assert tier_reward_key(tiers["hard"]) == f"adventure-tier-reward:{tiers['hard'].id}"


def test_the_level_map_shows_each_tier_reward_and_whether_it_was_paid(db, django_user_model):
    player, _, tiers = _tiers(django_user_model)
    award_tier_reward(player=player, tier=tiers["easy"])

    access = _build_adventure_tier_access(player=player, tiers=list(tiers.values()))
    rewards = {
        difficulty: adventure_level_tier_payload(tier=tier, access=access)["reward"]
        for difficulty, tier in tiers.items()
    }

    assert rewards == {
        "easy": {"coins": 25, "claimed": True},
        "medium": {"coins": 35, "claimed": False},
        "hard": {"coins": 50, "claimed": False},
    }


def test_backfill_pays_completions_that_predate_the_ladder_once(db, django_user_model):
    player, level, tiers = _tiers(django_user_model)
    # Easy was paid at the time; Medium and Hard completed before they paid anything.
    award_tier_reward(player=player, tier=tiers["easy"])
    for tier in tiers.values():
        AdventureLevelTierCompletion.objects.create(player=player, tier=tier, stars=3)

    call_command("award_missing_tier_rewards", verbosity=0)
    call_command("award_missing_tier_rewards", verbosity=0)

    assert Wallet.objects.get(player=player).balance == 25 + 35 + 50
    assert claimed_tier_reward_keys(player=player, tiers=tiers.values()) == {
        tier_reward_key(tier) for tier in tiers.values()
    }
    assert CoinTransaction.objects.filter(player=player).count() == 3
