import json
from pathlib import Path

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.utils.dateparse import parse_datetime

from progress.models import KpiStudy
from progress.services.studies import create_study, freeze_study


class Command(BaseCommand):
    help = "Create fixed KPI study assignments, freeze at cutoff, or export the saved report."

    def add_arguments(self, parser):
        parser.add_argument("action", choices=("create", "freeze", "export"))
        parser.add_argument("slug")
        parser.add_argument("--players", nargs="+", type=int)
        parser.add_argument("--tiers", nargs="+", type=int)
        parser.add_argument("--cutoff")
        parser.add_argument("--weights", help='JSON module weights, e.g. {"3":1,"4":1}')
        parser.add_argument("--output", type=Path)

    def handle(self, *args, **options):
        try:
            if options["action"] == "create":
                cutoff = parse_datetime(options["cutoff"] or "")
                if cutoff is None or not options["players"] or not options["tiers"]:
                    raise CommandError("Create requires --players, --tiers and an aware --cutoff.")
                if KpiStudy.objects.filter(slug=options["slug"]).exists():
                    raise CommandError("That study version already exists; choose a new slug.")
                study = create_study(
                    slug=options["slug"],
                    player_ids=options["players"],
                    tier_ids=options["tiers"],
                    cutoff=cutoff,
                    weights=json.loads(options["weights"]) if options["weights"] else None,
                )
                data = study.manifest
            else:
                study = KpiStudy.objects.get(slug=options["slug"])
                if options["action"] == "freeze":
                    data = freeze_study(study)
                else:
                    if not study.frozen_at:
                        raise CommandError("Freeze the study at cutoff before exporting it.")
                    data = study.report
        except (ValidationError, KpiStudy.DoesNotExist, ValueError) as exc:
            raise CommandError(str(exc)) from exc
        rendered = json.dumps(data, indent=2)
        if options["output"]:
            options["output"].write_text(rendered + "\n", encoding="utf-8")
            self.stdout.write(f"Saved {options['action']} output to {options['output']}")
        else:
            self.stdout.write(rendered)
