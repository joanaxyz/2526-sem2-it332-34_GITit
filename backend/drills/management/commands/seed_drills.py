"""Seed Squire's Drill content from published curriculum.

Runs after the curriculum and legacy-module seeders, because a drill is
derived from a level's command forms and authored solutions - seeding it
first would compose against an empty catalog.

Safe to re-run: content is upserted per level, so this never touches
``DrillProgress`` or an in-flight ``DrillRun``.
"""

from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError
from django.db import OperationalError

from drills.services.seeding import seed_all_level_drills


class Command(BaseCommand):
    help = "Seed Squire's Drill cards and ordering finales for every published level."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--level",
            action="append",
            type=int,
            dest="level_ids",
            help="Seed only these adventure level ids (repeatable). Defaults to all.",
        )

    def handle(self, *args, **options):
        try:
            summary = seed_all_level_drills(level_ids=options.get("level_ids"))
        except OperationalError as exc:
            if "lock timeout" in str(exc).lower():
                raise CommandError(
                    "Drill seed could not acquire database locks. Another seed or "
                    "request is probably holding a transaction; stop it and retry."
                ) from exc
            raise
        self.stdout.write(self.style.SUCCESS(f"Seeded drills: {summary.as_line()}"))
