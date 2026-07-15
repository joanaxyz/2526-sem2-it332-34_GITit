from __future__ import annotations

from django.db import connection, transaction

from curriculum.engine_capabilities import ENGINE_SUPPORTED_REFERENCE_FORMS
from curriculum.management.commands.seed_curriculum_challenges import (
    SeedCurriculumChallengeLessonMixin,
)
from curriculum.management.commands.seed_curriculum_commands import SeedCurriculumCommandSkillsMixin
from curriculum.management.commands.seed_curriculum_helpers import SeedCurriculumHelperMixin
from curriculum.management.commands.seed_curriculum_structure import SeedCurriculumStructureMixin
from curriculum.seed_data.adventure_levels import ADVENTURE_LEVEL_PLAN, ADVENTURE_LEVELS


class SeedCurriculumWriterMixin(
    SeedCurriculumStructureMixin,
    SeedCurriculumCommandSkillsMixin,
    SeedCurriculumChallengeLessonMixin,
    SeedCurriculumHelperMixin,
):
    def _seed_curriculum_rows(self, *, reset: bool) -> None:
        with transaction.atomic():
            self._relax_session_timeouts()
            if reset:
                self._reset_seeded_data()
            self._seed_curriculum_rows_in_transaction()

    def _seed_curriculum_rows_in_transaction(self) -> None:
        self.supported_form_keys = {
            spec["usage"] for spec in ADVENTURE_LEVELS if not spec.get("engine_blocked")
        }
        self.supported_form_keys.update(ENGINE_SUPPORTED_REFERENCE_FORMS)
        # Forms a level only *reuses* (the spiral - e.g. the log/show variants
        # practised inside a workflow that has no standalone level of its own) are
        # still taught, so they must stay published.
        for plan_levels in ADVENTURE_LEVEL_PLAN.values():
            for plan_level in plan_levels:
                self.supported_form_keys.update(plan_level.get("reuse_usages", []))
        self.published_chapter_slugs = self._published_chapter_slugs()
        stories = self._seed_stories()
        chapters = self._seed_chapters(stories)
        forms = self._seed_command_skills(chapters)
        adventures = self._seed_adventures(chapters)
        self._seed_adventure_levels(forms, adventures)
        self._seed_challenges(chapters)
        self._seed_lessons(chapters)

    def _relax_session_timeouts(self) -> None:
        """Lift web-app statement/idle timeouts for the row-seed transaction only.

        The row reset/upsert transaction can legitimately take far longer than a
        normal web request:

        - ``statement_timeout`` (a server-side default on Supabase) cancels the
          slow bulk resets, e.g. the ``CommandLog`` cascade delete.
        - ``idle_in_transaction_session_timeout`` may be set aggressively for
          web requests, but this command performs Python-side seed compilation
          between batches.

        It must NOT, however, wait for a *lock* forever. The Supabase pooler
        silently ignores the ``lock_timeout`` set via libpq startup options
        (``SHOW lock_timeout`` reports 0 through the pooler), so with
        ``statement_timeout`` also lifted, a ``--reset`` DELETE that contends for
        a lock - against a live request, or an orphaned in-transaction backend
        left by an interrupted earlier seed - blocks indefinitely (the "seed
        takes an hour" symptom). Bounding ``lock_timeout`` here makes contention
        fail fast and loudly instead, while still allowing the seed's own
        statements to run as long as they need.

        ``SET LOCAL`` scopes all three to this transaction, so the guardrails on
        pooled web connections are untouched.
        """
        if connection.vendor != "postgresql":
            return
        with connection.cursor() as cursor:
            cursor.execute("SET LOCAL idle_in_transaction_session_timeout = 0")
            cursor.execute("SET LOCAL statement_timeout = 0")
            cursor.execute("SET LOCAL lock_timeout = '15s'")
