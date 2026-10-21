"""One-time backfill: pay tier rewards for completions that predate the ladder.

Before the ladder only a level's first Easy clear paid GitCoins. This credits
every existing tier completion through the same award keys the runtime uses,
so it is idempotent and never pays a tier twice. Delete this command after the
deploy that runs it; see deploy/CURRICULUM_WAVES_RESEED.md.
"""

from django.core.management.base import BaseCommand

from adventures.rewards import (
    award_tier_reward,
    claimed_tier_reward_keys,
    tier_reward_coins,
    tier_reward_key,
)
from progress.models import AdventureLevelTierCompletion


class Command(BaseCommand):
    help = "Pay first-clear GitCoins for tier completions that were never paid (idempotent)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Report what would be paid without writing anything.",
        )

    def handle(self, *args, **options):
        completions = AdventureLevelTierCompletion.objects.select_related(
            "player", "tier"
        ).order_by("id")
        paid = coins = 0
        if options["dry_run"]:
            for completion in completions:
                tier = completion.tier
                claimed = claimed_tier_reward_keys(player=completion.player, tiers=[tier])
                if tier_reward_key(tier) not in claimed and tier_reward_coins(tier):
                    paid += 1
                    coins += tier_reward_coins(tier)
            self.stdout.write(f"Would pay {paid} tier rewards ({coins} GitCoins).")
            return
        for completion in completions:
            awarded = award_tier_reward(player=completion.player, tier=completion.tier)
            if awarded:
                paid += 1
                coins += awarded
        self.stdout.write(self.style.SUCCESS(f"Paid {paid} tier rewards ({coins} GitCoins)."))
