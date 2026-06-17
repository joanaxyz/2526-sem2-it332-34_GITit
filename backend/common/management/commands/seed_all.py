"""One command to reset and (re)seed all official data.

Runs the whole seed pipeline in dependency order:

1. ``seed_curriculum_v2`` — chapters, command catalog, adventures, challenges,
   tomes. It calls ``seed_assets`` itself (monsters, characters, battle
   artifacts, tower pieces), so assets are always refreshed first. With
   ``--reset`` (the default here) it first clears the seeded curriculum and the
   dependent practice/progress rows (runs, attempts, completions, mastery).
2. ``seed_command_library`` — the Chapter Book ``LibraryEntry`` rows.
3. ``grant_default_assets`` — registers the default Arcane Spire kit (Blue, the
   tower pieces, the crystal) into every player's asset registry.

Scope of "reset": only the official seeded content and the progress that depends
on it. It deliberately does NOT touch user accounts, player-authored UGC
(authoring content, tower designs) or marketplace listings — those survive.

Usage:
    python manage.py seed_all                 # reset + seed everything
    python manage.py seed_all --no-reset      # upsert in place, keep progress
    python manage.py seed_all --validate      # also validate the curriculum
    python manage.py seed_all --skip-grants   # don't grant the default kit
"""

from __future__ import annotations

from typing import Any

from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Reset and seed all official data: assets, v2 curriculum, command library, and default grants."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--no-reset",
            action="store_true",
            help="Upsert in place instead of clearing seeded curriculum + dependent progress first.",
        )
        parser.add_argument(
            "--validate",
            action="store_true",
            help="Validate the curriculum (shape, simulator support, official solutions) after seeding.",
        )
        parser.add_argument(
            "--skip-grants",
            action="store_true",
            help="Skip granting the default Arcane Spire kit to existing users.",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        verbosity = options.get("verbosity", 1)
        reset = not options.get("no_reset")

        self.stdout.write(self.style.MIGRATE_HEADING("1/3 Curriculum + assets"))
        call_command(
            "seed_curriculum_v2",
            reset=reset,
            validate=options.get("validate", False),
            verbosity=verbosity,
        )

        self.stdout.write(self.style.MIGRATE_HEADING("2/3 Command library"))
        call_command("seed_command_library", verbosity=verbosity)

        if options.get("skip_grants"):
            self.stdout.write(self.style.MIGRATE_HEADING("3/3 Default-asset grants (skipped)"))
        else:
            self.stdout.write(self.style.MIGRATE_HEADING("3/3 Default-asset grants"))
            call_command("grant_default_assets", verbosity=verbosity)

        mode = "reset and seeded" if reset else "seeded (no reset)"
        self.stdout.write(self.style.SUCCESS(f"seed_all complete — {mode} all official data."))
