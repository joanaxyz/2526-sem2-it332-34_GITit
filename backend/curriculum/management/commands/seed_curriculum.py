from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import OperationalError

from curriculum.management.commands.seed_curriculum_validation import SeedCurriculumValidationMixin
from curriculum.management.commands.seed_curriculum_writer import SeedCurriculumWriterMixin
from curriculum.models import Story

ACTIVE_ARCANE_CHAPTER_SLUG = "module-0-orientation"


class Command(SeedCurriculumWriterMixin, SeedCurriculumValidationMixin, BaseCommand):
    help = "Seed the retired three-story curriculum fixture (not used by seed_all)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--validate",
            action="store_true",
            help="Validate published curriculum shape, simulator support, and official solutions.",
        )
        parser.add_argument(
            "--reset",
            action="store_true",
            help=(
                "Clear seeded curriculum content and dependent practice/progress rows "
                "before rebuilding the curriculum."
            ),
        )

    def handle(self, *args, **options):
        if not getattr(settings, "ALLOW_RETIRED_CURRICULUM_FIXTURE_SEED", False):
            raise CommandError(
                "The retired three-story curriculum seed is disabled outside the test suite."
            )
        if Story.objects.filter(
            slug="arcane-spire",
            chapters__slug=ACTIVE_ARCANE_CHAPTER_SLUG,
        ).exists():
            raise CommandError(
                "The active Arcane Spire is the Module 0-4 curriculum. The retired "
                "three-story fixture cannot be seeded over it."
            )
        # Seed-spec dict keys ("module", "usage", "levels", ...) are the frozen
        # authoring format of seed_data; only the ORM names are normalized.
        # Visual assets are code-defined in the frontend now — nothing to seed.
        try:
            self._seed_curriculum_rows(reset=options.get("reset", False))
        except OperationalError as exc:
            if "lock timeout" in str(exc).lower():
                raise CommandError(
                    "Curriculum seed could not acquire database locks within 15s. "
                    "Another backend request or interrupted seed is probably still "
                    "holding a transaction; stop it or terminate the stale "
                    "idle-in-transaction session, then retry."
                ) from exc
            raise
        if options.get("validate"):
            self._validate_curriculum()
        self.stdout.write(self.style.SUCCESS("Seeded curriculum."))
