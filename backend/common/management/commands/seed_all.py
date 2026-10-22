"""Seed the sole official Arcane Spire curriculum and its derived data.

Usage:
    python manage.py seed_all
        Upsert the Arcane Spire Module 0-4 curriculum and command-library rows.
        Player progress is preserved.

The retired multi-story seed owned the old reset implementation, so reset is
now rejected rather than recreating those records or risking active progress.
"""

from __future__ import annotations

from typing import Any

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Safely seed all official data: curriculum and command library."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Retired option; resets are refused to preserve active curriculum progress.",
        )
        parser.add_argument(
            "--confirm-reset",
            action="store_true",
            help="Required together with --reset to acknowledge destructive deletion.",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        reset = bool(options.get("reset"))
        confirmed = bool(options.get("confirm_reset"))

        if confirmed and not reset:
            raise CommandError("--confirm-reset is only valid together with --reset.")
        if reset and not confirmed:
            raise CommandError(
                "Destructive reset refused. Re-run with both --reset and --confirm-reset."
            )
        if reset:
            raise CommandError(
                "seed_all reset is retired because it belonged to the removed "
                "three-story curriculum. Use the non-destructive canonical seed."
            )

        verbosity = options.get("verbosity", 1)
        self.stdout.write(self.style.MIGRATE_HEADING("1/3 Arcane Spire curriculum"))
        call_command("seed_curriculum", verbosity=verbosity)

        self.stdout.write(self.style.MIGRATE_HEADING("2/3 Command library"))
        call_command("seed_command_library", verbosity=verbosity)

        # Last: drill content is derived from the command forms and authored
        # solutions the two steps above have just written.
        self.stdout.write(self.style.MIGRATE_HEADING("3/3 Squire's Drill"))
        call_command("seed_drills", verbosity=verbosity)

        self.stdout.write(self.style.SUCCESS("seed_all complete — safely upserted official data."))
