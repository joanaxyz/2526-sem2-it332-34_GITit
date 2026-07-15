from __future__ import annotations

from adventures.models import (
    AdventureLevel,
    AdventureWave,
    AdventureWaveVariant,
)
from challenges.models import ChallengeLevel, ChallengeTrial, ChallengeTrialVariant
from curriculum.models import (
    Chapter,
    ChapterLesson,
    CommandForm,
    CommandSkill,
)
from curriculum.seed_data.adventures import ADVENTURE_SOURCES
from practice.services.builders import StaticLevelVariantBuilder


class SeedCurriculumHelperMixin:
    def _bulk_sync_variants(
        self,
        *,
        variant_model,
        level_fk: str,
        levels_and_specs: list[tuple],
        builder: StaticLevelVariantBuilder,
    ) -> None:
        """Upsert every variant across the given levels in a few round trips.

        Identity is ``(level, semantic_key)``; variants of a level that are no
        longer authored are unpublished. Building each variant
        (``compile_evaluation_spec`` etc.) is pure Python - only the DB writes
        are batched, replacing one ``update_or_create`` per variant (~190 of
        them) with a single create + update + retire. Command budget is omitted
        on purpose: it lives on the parent level, shared by all its variants.
        """
        level_objs = [level for level, _ in levels_and_specs]
        if not level_objs:
            return
        scope = variant_model.objects.filter(**{f"{level_fk}__in": level_objs})
        update_fields = [
            "slug",
            "label",
            "initial_state",
            "evaluation_spec",
            "target_state",
            "solution_commands",
            "case_id",
            "parameter_context",
            "scenario_context",
            "scaffold_policy",
            "is_published",
        ]
        rows = []
        for level, variant_specs in levels_and_specs:
            for index, variant_spec in enumerate(variant_specs, start=1):
                case = {"case_id": variant_spec["case_id"]}
                variant = builder.build(level=level, template=variant_spec, case=case, index=index)
                rows.append(
                    (
                        (level.id, variant.semantic_key),
                        {
                            level_fk: level,
                            "slug": variant.slug,
                            "label": variant.label,
                            "initial_state": variant.initial_state,
                            "evaluation_spec": variant.evaluation_spec,
                            "target_state": variant.target_state,
                            "solution_commands": variant.solution_commands,
                            "case_id": variant.case_id,
                            "semantic_key": variant.semantic_key,
                            "parameter_context": variant.parameter_context,
                            "scenario_context": variant.scenario_context,
                            "scaffold_policy": variant.scaffold_policy,
                            "is_published": True,
                        },
                    )
                )
        by_key = self._bulk_upsert(
            variant_model,
            scope,
            rows,
            key=lambda obj: (getattr(obj, f"{level_fk}_id"), obj.semantic_key),
            update_fields=update_fields,
        )
        live_ids = [by_key[row_key].id for row_key, _ in rows if row_key in by_key]
        scope.exclude(id__in=live_ids).update(is_published=False)

    def _bulk_upsert(self, model, scope, rows, *, key, update_fields):
        """Upsert ``rows`` into ``model`` in a handful of round trips.

        The seed used to call ``update_or_create`` per row - a SELECT plus an
        INSERT/UPDATE each, which is hundreds of stacked round trips against a
        remote Postgres. This instead loads the in-scope rows once, splits the
        specs into genuine inserts vs. updates, and writes each group in a single
        ``bulk_create`` / ``bulk_update``, then re-reads ``scope`` so callers get
        a clean ``{key: instance}`` map with primary keys populated.

        ``rows`` is an iterable of ``(key_value, field_dict)``. ``field_dict``
        holds every column needed to construct a new row; only ``update_fields``
        are written back onto an existing row (identity columns never change).
        These models have no custom ``save()`` or signals, so bypassing them is
        safe; ``auto_now`` is unused here so no timestamps are skipped.
        """
        existing = {key(obj): obj for obj in scope}
        to_create, to_update = [], []
        seen: set = set()
        for key_value, fields in rows:
            if key_value in seen:
                continue
            seen.add(key_value)
            obj = existing.get(key_value)
            if obj is None:
                to_create.append(model(**fields))
            else:
                for name in update_fields:
                    setattr(obj, name, fields[name])
                to_update.append(obj)
        if to_create:
            model.objects.bulk_create(to_create)
        if to_update:
            model.objects.bulk_update(to_update, update_fields)
        return {key(obj): obj for obj in scope.all()}

    def _unique_seed_slug(self, slug: str, used: set[str], *, max_length: int = 50) -> str:
        candidate = slug[:max_length]
        if candidate not in used:
            used.add(candidate)
            return candidate
        counter = 2
        while True:
            suffix = f"-{counter}"
            candidate = f"{slug[: max_length - len(suffix)]}{suffix}"
            if candidate not in used:
                used.add(candidate)
                return candidate
            counter += 1

    def _adventure_source_order(self) -> dict[str, int]:
        order: dict[str, int] = {}
        next_order = 0
        for configured_specs in ADVENTURE_SOURCES.values():
            if isinstance(configured_specs, dict):
                configured_specs = [configured_specs]
            for configured in configured_specs:
                source_slug = configured.get("slug")
                if not source_slug or source_slug in order:
                    continue
                order[source_slug] = next_order
                next_order += 1
        return order

    def _preview(self, title: str, summary: str, *, syntax: str | None = None) -> dict:
        syntax_examples = [syntax] if syntax else []
        return {
            "schema_version": 2,
            "title": title,
            "summary": summary,
            "syntax_examples": syntax_examples,
        }

    def _reset_seeded_data(self) -> None:
        """Delete curriculum-owned rows plus dependent run/progress rows.

        This keeps user accounts intact while making local reseeds predictable
        after major curriculum edits. The delete order starts with session data
        because several run/attempt models protect their selected levels and
        variants.
        """
        from adventures.models import (
            AdventureRun,
            SkillMastery,
        )
        from challenges.models import ChallengeRun
        from practice.models import CommandStep
        from progress.models import (
            AdventureLevelCompletion,
            ChallengeLevelCompletion,
            ChallengeTrialCompletion,
        )

        CommandStep.objects.all().delete()
        AdventureLevelCompletion.objects.all().delete()
        ChallengeTrialCompletion.objects.all().delete()
        ChallengeLevelCompletion.objects.all().delete()
        ChallengeRun.objects.all().delete()
        AdventureRun.objects.all().delete()
        SkillMastery.objects.all().delete()

        ChallengeTrialVariant.objects.all().delete()
        AdventureWaveVariant.objects.all().delete()
        ChallengeTrial.objects.all().delete()
        ChallengeLevel.objects.all().delete()
        AdventureWave.objects.all().delete()
        AdventureLevel.objects.all().delete()
        CommandForm.objects.all().delete()
        CommandSkill.objects.all().delete()
        ChapterLesson.objects.all().delete()
        Chapter.objects.all().delete()
        from curriculum.models import Story

        Story.objects.all().delete()
        self.stdout.write(
            self.style.WARNING("Reset curriculum rows and dependent run/progress rows.")
        )
