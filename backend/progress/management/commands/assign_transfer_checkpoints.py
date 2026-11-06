"""Offer reviewed checkpoints to existing mastery without inventing exposure."""

import json

from django.core.management.base import BaseCommand
from django.db import transaction

from players.models import Player
from progress.models import AdventureLevelTierCompletion, KpiCheckpoint
from progress.objectives import transfer_expected
from progress.services.checkpoints import assign_transfer, eligible_transfer_variant
from progress.services.transfer_policy import study_transfer_pins


class Command(BaseCommand):
    help = "Preview eligible mastered tiers; --apply creates their first transfer assignment."

    def add_arguments(self, parser):
        parser.add_argument("--modules", nargs="+", type=int, choices=(1, 2, 3, 4), default=[1, 2])
        parser.add_argument("--players", nargs="+", type=int)
        parser.add_argument("--apply", action="store_true")

    @transaction.atomic
    def handle(self, *args, **options):
        completions = (
            AdventureLevelTierCompletion.objects.filter(
                tier__difficulty="hard",
                tier__is_published=True,
                tier__adventure_level__is_required=True,
                tier__adventure_level__is_published=True,
                tier__adventure_level__chapter__is_published=True,
                tier__adventure_level__chapter__story__slug="arcane-spire",
                tier__adventure_level__chapter__number__in=options["modules"],
                player__user__is_staff=False,
            )
            .select_related("player", "tier__adventure_level__chapter")
            .order_by("player_id", "tier_id")
        )
        if options["players"]:
            completions = completions.filter(player_id__in=options["players"])
        counts = {
            "mastered": 0,
            "unselected": 0,
            "existing": 0,
            "ineligible": 0,
            "eligible": 0,
            "created": 0,
        }
        for completion in completions:
            counts["mastered"] += 1
            tier, player = completion.tier, completion.player
            if options["apply"]:
                # Match launch/enrollment locking before reading exposure or pins.
                Player.objects.select_for_update().get(pk=player.pk)
            if (
                not transfer_expected(
                    tier.adventure_level.chapter.number, tier.difficulty, tier.adventure_level.slug
                )
                and not study_transfer_pins([player.id], [tier.id])[player.id, tier.id]
            ):
                counts["unselected"] += 1
                continue
            if KpiCheckpoint.objects.filter(player=player, tier=tier, kind="transfer").exists():
                counts["existing"] += 1
                continue
            if eligible_transfer_variant(player=player, tier=tier) is None:
                counts["ineligible"] += 1
                continue
            counts["eligible"] += 1
            if options["apply"] and assign_transfer(player=player, tier=tier) is not None:
                counts["created"] += 1
        self.stdout.write(
            json.dumps(
                {"mode": "apply" if options["apply"] else "dry-run", **counts}, sort_keys=True
            )
        )
