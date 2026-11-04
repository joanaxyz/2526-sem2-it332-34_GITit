"""One-time backfill: credit XP for progress that predates the XP ledger.

Everything goes through the award keys the runtime uses, so this is idempotent
and pays nothing twice. Delete this command after the deploy that runs it; see
deploy/CURRICULUM_SCENARIOS_RESEED.md.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Sum

from progress.models import (
    AdventureLevelTierCompletion,
    ChallengeTrialCompletion,
    XpTransaction,
)
from progress.xp import award_gate_xp, award_tier_xp


class Command(BaseCommand):
    help = "Credit XP for tier clears and gate trials already earned (idempotent)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Report what would be credited without writing anything.",
        )

    def handle(self, *args, **options):
        before = self._total()
        with transaction.atomic():
            self._credit()
            credited = self._total() - before
            if options["dry_run"]:
                transaction.set_rollback(True)
        verb = "Would credit" if options["dry_run"] else "Credited"
        self.stdout.write(self.style.SUCCESS(f"{verb} {credited} XP."))

    def _total(self) -> int:
        return XpTransaction.objects.aggregate(total=Sum("amount"))["total"] or 0

    def _credit(self) -> None:
        completions = AdventureLevelTierCompletion.objects.select_related("player", "tier")
        for completion in completions.order_by("id"):
            award_tier_xp(player=completion.player, tier=completion.tier, stars=completion.stars)
        trials = ChallengeTrialCompletion.objects.select_related("player", "challenge_trial")
        for completion in trials.order_by("id"):
            award_gate_xp(player=completion.player, trial=completion.challenge_trial)
