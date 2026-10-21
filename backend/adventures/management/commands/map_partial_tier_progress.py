"""One-time backfill: map partial tier progress onto the designed scenarios (decision D2).

Before the scenario plan, a tier was one scenario cleared N times, so an unfinished
tier holds only a clear count. This marks the first ``min(clears, scenarios - 1)``
of its new scenarios cleared, so learners keep their place without a tier ever
being completed for them. Rows that already name a published scenario are left
alone, which makes a second run a no-op. Delete this command after the deploy
that runs it; see deploy/CURRICULUM_SCENARIOS_RESEED.md.
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from adventures.models import AdventureLevelTierProgress
from adventures.tier_scenarios import cleared_slugs, published_scenarios
from progress.models import AdventureLevelTierCompletion


class Command(BaseCommand):
    help = "Mark the first scenarios cleared for tiers left partly done before the scenario plan (idempotent)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Report what would change without writing anything.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        completed = set(AdventureLevelTierCompletion.objects.values_list("player_id", "tier_id"))
        scenarios_by_tier: dict[int, list[str]] = {}
        mapped = scenarios_marked = 0
        rows = AdventureLevelTierProgress.objects.filter(successful_clears__gt=0).select_related(
            "tier"
        )
        for progress in rows.order_by("id"):
            if (progress.player_id, progress.tier_id) in completed:
                continue
            if progress.tier_id not in scenarios_by_tier:
                scenarios_by_tier[progress.tier_id] = [
                    w.slug for w in published_scenarios(progress.tier)
                ]
            slugs = scenarios_by_tier[progress.tier_id]
            cleared = cleared_slugs(progress)
            if not slugs or set(cleared) & set(slugs):
                continue
            first = slugs[: min(progress.successful_clears, len(slugs) - 1)]
            if not first:
                continue
            mapped += 1
            scenarios_marked += len(first)
            if not options["dry_run"]:
                progress.cleared_scenario_slugs = [*cleared, *first]
                progress.save(update_fields=["cleared_scenario_slugs", "updated_at"])
        verb = "Would map" if options["dry_run"] else "Mapped"
        self.stdout.write(
            self.style.SUCCESS(
                f"{verb} {mapped} partly done tiers onto {scenarios_marked} first scenarios."
            )
        )
