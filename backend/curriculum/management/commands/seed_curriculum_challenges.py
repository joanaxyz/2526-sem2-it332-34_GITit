from __future__ import annotations

from adventures.models import (
    AdventureWave,
)
from challenges.models import ChallengeLevel, ChallengeTrial, ChallengeTrialVariant
from curriculum.models import (
    Chapter,
    ChapterLesson,
)
from curriculum.seed_data.challenges import CHALLENGES
from curriculum.seed_data.chapters import CHAPTERS
from curriculum.seed_data.lessons import LESSONS
from practice.services.builders import StaticLevelVariantBuilder


class SeedCurriculumChallengeLessonMixin:
    def _seed_challenges(self, chapters: dict[str, Chapter]) -> None:
        builder = StaticLevelVariantBuilder()
        level_rows = []
        sort_order_by_chapter: dict[int, int] = {}
        for spec in CHALLENGES:
            chapter = chapters[spec["module"]]
            sort_order_by_chapter[chapter.id] = sort_order_by_chapter.get(chapter.id, 0) + 1
            level_rows.append(
                (
                    (chapter.id, spec["slug"]),
                    {
                        "chapter": chapter,
                        "slug": spec["slug"],
                        "title": spec["title"],
                        "summary": chapter.description or spec["summary"],
                        "narrative": spec["narrative"],
                        "sort_order": sort_order_by_chapter[chapter.id],
                        "is_published": chapter.is_published,
                    },
                )
            )
        challenge_levels_by_key = self._bulk_upsert(
            ChallengeLevel,
            ChallengeLevel.objects.filter(chapter__in=list(chapters.values())),
            level_rows,
            key=lambda obj: (obj.chapter_id, obj.slug),
            update_fields=["title", "summary", "narrative", "sort_order", "is_published"],
        )
        live_challenge_level_ids = [challenge_levels_by_key[key].id for key, _ in level_rows]
        ChallengeLevel.objects.filter(chapter__in=list(chapters.values())).exclude(
            id__in=live_challenge_level_ids
        ).update(is_published=False)

        levels_by_spec_slug = {
            spec["slug"]: challenge_levels_by_key[(chapters[spec["module"]].id, spec["slug"])]
            for spec in CHALLENGES
        }
        wave_by_slug = {
            wave.slug: wave
            for wave in AdventureWave.objects.filter(
                level__chapter__slug__in=[spec["slug"] for spec in CHAPTERS],
                is_published=True,
                level__is_published=True,
            ).prefetch_related("command_forms")
        }
        for spec in CHALLENGES:
            command_forms = []
            seen_form_ids: set[int] = set()
            for level_spec in spec.get("levels", []):
                for wave_slug in level_spec.get("uses_adventure_levels", []):
                    adventure_wave = wave_by_slug.get(wave_slug)
                    if adventure_wave is None:
                        continue
                    for form in adventure_wave.command_forms.all():
                        if form.id not in seen_form_ids:
                            seen_form_ids.add(form.id)
                            command_forms.append(form)
            if command_forms:
                levels_by_spec_slug[spec["slug"]].command_forms.set(command_forms)

        trial_rows = []
        for spec in CHALLENGES:
            challenge_level = levels_by_spec_slug[spec["slug"]]
            for level_spec in spec.get("levels", []):
                ctx = level_spec.get("scenario_context") or {}
                trial_rows.append(
                    (
                        (challenge_level.id, level_spec["difficulty"]),
                        {
                            "challenge_level": challenge_level,
                            "difficulty": level_spec["difficulty"],
                            "story": ctx.get("story", "") or "",
                            "task": ctx.get("task", "") or "",
                            "min_counted_commands": level_spec["min_counted_commands"],
                            "max_counted_commands": level_spec["max_counted_commands"],
                            "reward_coins": level_spec.get("reward_coins", 0),
                            "objective_checks": level_spec.get("objective_checks", []),
                            "is_published": challenge_level.is_published,
                        },
                    )
                )
        trials_by_key = self._bulk_upsert(
            ChallengeTrial,
            ChallengeTrial.objects.filter(challenge_level__in=list(levels_by_spec_slug.values())),
            trial_rows,
            key=lambda obj: (obj.challenge_level_id, obj.difficulty),
            update_fields=[
                "story",
                "task",
                "min_counted_commands",
                "max_counted_commands",
                "reward_coins",
                "objective_checks",
                "is_published",
            ],
        )
        live_trial_ids = [trials_by_key[key].id for key, _ in trial_rows]
        ChallengeTrial.objects.filter(challenge_level__in=list(levels_by_spec_slug.values())).exclude(
            id__in=live_trial_ids
        ).update(is_published=False)

        levels_and_specs = []
        for spec in CHALLENGES:
            challenge_level = levels_by_spec_slug[spec["slug"]]
            for level_spec in spec.get("levels", []):
                difficulty = level_spec["difficulty"]
                trial = trials_by_key[(challenge_level.id, difficulty)]
                levels_and_specs.append((trial, level_spec["variants"]))
        self._bulk_sync_variants(
            variant_model=ChallengeTrialVariant,
            level_fk="trial",
            levels_and_specs=levels_and_specs,
            builder=builder,
        )

    def _seed_lessons(self, chapters: dict[str, Chapter]) -> None:
        """Seed reading lessons attached directly to chapters."""
        rows = []
        for index, spec in enumerate(LESSONS, start=1):
            chapter = chapters[spec["module"]]
            rows.append(
                (
                    (chapter.id, spec["slug"]),
                    {
                        "chapter": chapter,
                        "slug": spec["slug"],
                        "title": spec["title"],
                        "summary": spec.get("summary", ""),
                        "pages": spec["pages"],
                        "sort_order": index,
                        "is_published": chapter.is_published,
                    },
                )
            )
        by_key = self._bulk_upsert(
            ChapterLesson,
            ChapterLesson.objects.filter(chapter__in=list(chapters.values())),
            rows,
            key=lambda obj: (obj.chapter_id, obj.slug),
            update_fields=["title", "summary", "pages", "sort_order", "is_published"],
        )
        live_ids = [by_key[key].id for key, _ in rows]
        ChapterLesson.objects.filter(source_content_definition__isnull=True).exclude(id__in=live_ids).update(
            is_published=False
        )
