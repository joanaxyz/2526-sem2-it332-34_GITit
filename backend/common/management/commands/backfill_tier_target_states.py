"""Backfill target_state on AdventureLevelTierWaveVariant rows.

Export from a DB that has correct target states:
    python manage.py backfill_tier_target_states --export tier_targets.json

Import into a DB with empty target states:
    python manage.py backfill_tier_target_states --import tier_targets.json
"""
from __future__ import annotations

import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from adventures.models import AdventureLevelTierWaveVariant


class Command(BaseCommand):
    help = "Export or import target_state for AdventureLevelTierWaveVariant rows."

    def add_arguments(self, parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--export", metavar="FILE", help="Export target states to a JSON file.")
        group.add_argument("--import", metavar="FILE", dest="import_file", help="Import target states from a JSON file.")

    def handle(self, *args, **options):
        if options["export"]:
            self._export(options["export"])
        else:
            self._import(options["import_file"])

    def _export(self, path: str):
        variants = AdventureLevelTierWaveVariant.objects.exclude(case_id="").exclude(target_state={})
        data = {v.case_id: v.target_state for v in variants}
        Path(path).write_text(json.dumps(data, indent=2), encoding="utf-8")
        self.stdout.write(self.style.SUCCESS(f"Exported {len(data)} target states to {path}."))

    def _import(self, path: str):
        if not Path(path).exists():
            raise CommandError(f"File not found: {path}")
        data: dict = json.loads(Path(path).read_text(encoding="utf-8"))
        variants = AdventureLevelTierWaveVariant.objects.filter(case_id__in=data.keys())
        updated = 0
        skipped = 0
        for variant in variants:
            target = data[variant.case_id]
            if variant.target_state == target:
                skipped += 1
                continue
            variant.target_state = target
            variant.save(update_fields=["target_state"])
            updated += 1
        self.stdout.write(
            self.style.SUCCESS(f"Done. Updated: {updated}, already correct: {skipped}.")
        )
