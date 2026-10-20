from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from adventures.models import AdventureLevelTierWaveVariant
from progress.services.references import state_key, validate_refs


class Command(BaseCommand):
    help = (
        "Replay and validate KPI command references; optionally reserve a reviewed transfer case."
    )

    def add_arguments(self, parser):
        parser.add_argument("--cases", nargs="+")
        parser.add_argument("--diagnostics", action="store_true")
        parser.add_argument("--reserve", action="store_true")
        parser.add_argument("--reason", default="")

    @transaction.atomic
    def handle(self, *args, **options):
        variants = AdventureLevelTierWaveVariant.objects.filter(
            is_published=True,
            wave__is_published=True,
            wave__tier__is_published=True,
            wave__tier__adventure_level__chapter__story__slug="arcane-spire",
        ).select_related("wave__tier__adventure_level__chapter")
        if options["cases"]:
            variants = variants.filter(slug__in=options["cases"])
        variants = list(variants)
        if not variants or (options["cases"] and len(variants) != len(set(options["cases"]))):
            raise CommandError("Select existing unique published case slugs.")
        if (options["reserve"] or options["diagnostics"]) and not options["cases"]:
            raise CommandError("Reservation and diagnostic assessment require explicit --cases.")
        if options["reserve"] and not options["reason"].strip():
            raise CommandError(
                "--reserve requires an authored --reason describing the transfer difference."
            )
        reserved_ids = {v.id for v in variants} if options["reserve"] else set()
        for variant in variants:
            if options["diagnostics"]:
                variant.assess_diag = True
            if options["reserve"]:
                ordinary = variant.wave.variants.filter(
                    is_published=True, is_transfer=False
                ).exclude(pk__in=reserved_ids)
                if (
                    variant.wave.tier.adventure_level.chapter.number not in (3, 4)
                    or not ordinary.exists()
                    or any(state_key(v) == state_key(variant) for v in ordinary)
                ):
                    raise CommandError(
                        "Transfer needs Module 3–4, a distinct repository/goal, and ordinary practice content."
                    )
                variant.is_transfer = True
                variant.transfer_note = options["reason"].strip()
        try:
            counts = validate_refs(variants, allow_unscored=not options["cases"])
        except ValidationError as exc:
            raise CommandError(str(exc)) from exc
        if options["reserve"]:
            for variant in variants:
                variant.save(update_fields=["is_transfer", "transfer_note"])
        self.stdout.write(self.style.SUCCESS(f"Validated {len(counts)} reference routes."))
        unscored = [v.slug for v in variants if v.id not in counts]
        if unscored:
            self.stdout.write(
                f"Unscored diagnostic-only routes ({len(unscored)}): {', '.join(unscored)}"
            )
