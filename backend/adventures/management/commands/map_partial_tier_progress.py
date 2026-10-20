"""One-time backfill: map partial tier progress onto the designed waves (decision D2).

Before the wave plan, a tier was one wave cleared N times, so an unfinished
tier holds only a clear count. This marks the first ``min(clears, waves - 1)``
of its new waves cleared, so learners keep their place without a tier ever
being completed for them. Rows that already name a published wave are left
alone, which makes a second run a no-op. Delete this command after the deploy
that runs it (docs/goals/curriculum-waves-and-repetition/PLAN.md §10).
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from adventures.models import AdventureLevelTierProgress
from adventures.tier_waves import cleared_slugs, published_waves
from progress.models import AdventureLevelTierCompletion


class Command(BaseCommand):
    help = (
        "Mark the first waves cleared for tiers left partly done before the wave plan (idempotent)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Report what would change without writing anything.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        completed = set(AdventureLevelTierCompletion.objects.values_list("player_id", "tier_id"))
        waves_by_tier: dict[int, list[str]] = {}
        mapped = waves_marked = 0
        rows = AdventureLevelTierProgress.objects.filter(successful_clears__gt=0).select_related(
            "tier"
        )
        for progress in rows.order_by("id"):
            if (progress.player_id, progress.tier_id) in completed:
                continue
            if progress.tier_id not in waves_by_tier:
                waves_by_tier[progress.tier_id] = [w.slug for w in published_waves(progress.tier)]
            slugs = waves_by_tier[progress.tier_id]
            cleared = cleared_slugs(progress)
            if not slugs or set(cleared) & set(slugs):
                continue
            first = slugs[: min(progress.successful_clears, len(slugs) - 1)]
            if not first:
                continue
            mapped += 1
            waves_marked += len(first)
            if not options["dry_run"]:
                progress.cleared_wave_slugs = [*cleared, *first]
                progress.save(update_fields=["cleared_wave_slugs", "updated_at"])
        verb = "Would map" if options["dry_run"] else "Mapped"
        self.stdout.write(
            self.style.SUCCESS(
                f"{verb} {mapped} partly done tiers onto {waves_marked} first waves."
            )
        )
