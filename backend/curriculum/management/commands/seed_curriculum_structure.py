from __future__ import annotations

from django.core.management.base import CommandError

from adventures.models import (
    AdventureLevel,
    AdventureWave,
    AdventureWaveVariant,
)
from curriculum.models import (
    Chapter,
    CommandForm,
    Story,
)
from curriculum.seed_data.adventure_levels import ADVENTURE_LEVELS
from curriculum.seed_data.adventures import ADVENTURE_SOURCES
from curriculum.seed_data.chapters import CHAPTERS
from curriculum.seed_data.stories import STORIES
from practice.services.builders import StaticLevelVariantBuilder


class SeedCurriculumStructureMixin:
    def _seed_stories(self) -> dict[str, Story]:
        live_slugs = [spec["slug"] for spec in STORIES]
        existing = {story.slug: story for story in Story.objects.all()}

        # First pass creates/updates every story without prerequisites so forward
        # references never depend on authoring order.
        rows = []
        for index, spec in enumerate(STORIES, start=1):
            rows.append(
                (
                    spec["slug"],
                    {
                        "slug": spec["slug"],
                        "title": spec["title"],
                        "summary": spec.get("summary", ""),
                        "narrative_brief": spec.get("narrative_brief", {}),
                        "price": spec.get("price", 0),
                        "sort_order": spec.get("sort_order", index),
                        "is_published": spec.get("is_published", True),
                        "world_slug": spec.get("world_slug", spec["slug"]),
                        "difficulty": spec.get("difficulty", Story.DIFFICULTY_BEGINNER),
                        "prerequisite_story": existing.get(spec.get("prerequisite_story")),
                    },
                )
            )
        by_slug = self._bulk_upsert(
            Story,
            Story.objects.all(),
            rows,
            key=lambda obj: obj.slug,
            update_fields=[
                "title",
                "summary",
                "narrative_brief",
                "price",
                "sort_order",
                "is_published",
                "world_slug",
                "difficulty",
                "prerequisite_story",
            ],
        )

        # Second pass resolves prerequisites against the complete story set.
        changed = []
        for spec in STORIES:
            story = by_slug[spec["slug"]]
            prerequisite_slug = spec.get("prerequisite_story")
            prerequisite = by_slug.get(prerequisite_slug) if prerequisite_slug else None
            if story.prerequisite_story_id != (prerequisite.id if prerequisite else None):
                story.prerequisite_story = prerequisite
                changed.append(story)
        if changed:
            Story.objects.bulk_update(changed, ["prerequisite_story"])

        Story.objects.exclude(slug__in=live_slugs).update(is_published=False)
        return {slug: by_slug[slug] for slug in live_slugs}

    def _seed_chapters(self, stories: dict[str, Story]) -> dict[str, Chapter]:
        live_slugs = []
        rows = []
        story_positions: dict[str, int] = {}
        for spec in CHAPTERS:
            live_slugs.append(spec["slug"])
            story_slug = spec.get("story", "arcane-spire")
            if story_slug not in stories:
                raise CommandError(
                    f"Chapter {spec['slug']!r} references unknown story {story_slug!r}."
                )
            story_positions[story_slug] = story_positions.get(story_slug, 0) + 1
            rows.append(
                (
                    spec["slug"],
                    {
                        "slug": spec["slug"],
                        "story": stories[story_slug],
                        "number": spec["number"],
                        "title": spec["title"],
                        "description": spec["description"],
                        "narrative_brief": spec.get("narrative_brief", {}),
                        "sort_order": spec.get("sort_order", story_positions[story_slug]),
                        "is_published": spec["slug"] in self.published_chapter_slugs,
                        "is_playable": spec.get("is_playable", story_slug == "arcane-spire"),
                        "battle_stage": spec.get("battle_stage", {}),
                    },
                )
            )
        by_slug = self._bulk_upsert(
            Chapter,
            Chapter.objects.all(),
            rows,
            key=lambda obj: obj.slug,
            update_fields=[
                "story",
                "number",
                "title",
                "description",
                "narrative_brief",
                "sort_order",
                "is_published",
                "is_playable",
                "battle_stage",
            ],
        )
        Chapter.objects.exclude(slug__in=live_slugs).exclude(slug__startswith="ugc-").update(
            is_published=False
        )
        # Preserve CHAPTERS authoring order; downstream seeding enumerates this map.
        return {slug: by_slug[slug] for slug in live_slugs}

    def _seed_adventures(self, chapters: dict[str, Chapter]) -> dict[str, Chapter]:
        """Build source adventure slug -> chapter aliases for seed specs.

        The old Adventure wrapper row is gone. Seed specs may still refer to
        historical adventure slugs, so this method keeps those names as aliases
        without creating a database wrapper.
        """
        usage_to_chapter = self._usage_to_chapter_slug()
        source_slug_to_chapter_slug: dict[str, str] = {}
        for slug, _chapter in chapters.items():
            configured_specs = ADVENTURE_SOURCES.get(slug, {})
            if isinstance(configured_specs, dict):
                configured_specs = [configured_specs]
            configured_specs = configured_specs or [{}]
            primary = configured_specs[0]
            primary_slug = primary.get("slug") or f"{slug}-adventure"
            source_slug_to_chapter_slug[primary_slug] = slug
            source_slug_to_chapter_slug[f"{slug}-command-adventure"] = slug
            source_slug_to_chapter_slug[slug] = slug
            for configured in configured_specs:
                source_slug = configured.get("slug")
                if source_slug:
                    source_slug_to_chapter_slug[source_slug] = slug
        self.adventure_source_slug_to_chapter_slug = source_slug_to_chapter_slug
        self.primary_adventures_by_chapter_slug = {
            chapter_slug: chapters[chapter_slug]
            for chapter_slug in set(usage_to_chapter.values())
            if chapter_slug in chapters
        }
        return {
            source_slug: chapters[chapter_slug]
            for source_slug, chapter_slug in source_slug_to_chapter_slug.items()
            if chapter_slug in chapters
        }

    def _seed_adventure_levels(
        self,
        forms: dict[str, CommandForm],
        adventures: dict[str, Chapter],
    ) -> None:
        from curriculum.seed_data.adventure_levels import adventure_levels_for

        builder = StaticLevelVariantBuilder()
        usage_to_chapter = self._usage_to_chapter_slug()

        problems_by_source: dict[tuple[int, str], list[dict]] = {}
        chapter_by_id: dict[int, Chapter] = {}
        for spec in ADVENTURE_LEVELS:
            chapter_slug = usage_to_chapter.get(spec["usage"])
            adventure_slug = spec.get("adventure")
            if adventure_slug:
                chapter = adventures.get(adventure_slug)
                if chapter is None:
                    raise CommandError(
                        f"Adventure level {spec['slug']!r} references unknown adventure alias {adventure_slug!r}."
                    )
            else:
                chapter = getattr(self, "primary_adventures_by_chapter_slug", {}).get(chapter_slug)
            if chapter is None:
                continue
            source_slug = adventure_slug or f"{chapter.slug}-adventure"
            problems_by_source.setdefault((chapter.id, source_slug), []).append(spec)
            chapter_by_id[chapter.id] = chapter

        from curriculum.seed_data.blueprint_overlay import BLUEPRINT_ADVENTURE_LEVELS

        blueprint_source_slugs = set(BLUEPRINT_ADVENTURE_LEVELS)
        level_rows = []
        level_keys: list[tuple[int, str]] = []
        level_groups: dict[tuple[int, str], dict] = {}
        sort_order_by_chapter: dict[int, int] = {}
        used_level_slugs_by_chapter: dict[int, set[str]] = {}
        source_order = self._adventure_source_order()
        ordered_problem_groups = sorted(
            problems_by_source.items(),
            key=lambda item: (
                chapter_by_id[item[0][0]].sort_order,
                source_order.get(item[0][1], 9999),
                item[0][1],
            ),
        )
        for (chapter_id, source_slug), problems in ordered_problem_groups:
            chapter = chapter_by_id[chapter_id]
            # Arcane Spire remains locked to its audited blueprint ledger. New
            # story sources are intentionally additive and use their own
            # dedicated aliases rather than entering the legacy blueprint map.
            allowed_arcane_additions = {"guild-archive-handoff-workflows"}
            if (
                chapter.story.slug == "arcane-spire"
                and blueprint_source_slugs
                and source_slug not in blueprint_source_slugs
                and source_slug not in allowed_arcane_additions
            ):
                continue
            for group in adventure_levels_for(source_slug, problems):
                sort_order_by_chapter[chapter_id] = sort_order_by_chapter.get(chapter_id, 0) + 1
                used_slugs = used_level_slugs_by_chapter.setdefault(chapter_id, set())
                level_slug = self._unique_seed_slug(group["slug"], used_slugs)
                key = (chapter_id, level_slug)
                level_keys.append(key)
                level_groups[key] = group
                level_rows.append(
                    (
                        key,
                        {
                            "chapter": chapter,
                            "slug": level_slug,
                            "title": group["title"],
                            "description": chapter.description or f"Practice the Git moves for {chapter.title}.",
                            "brief": group.get("brief", "") or "",
                            "narrative_brief": group.get("narrative_brief", {}),
                            "level_type": group.get("level_type", "guided_workflow"),
                            "is_required": True,
                            "sort_order": sort_order_by_chapter[chapter_id],
                            "is_published": chapter.is_published,
                            "reward_coins": group.get("reward_coins", 25),
                        },
                    )
                )
        canonical_chapters = list(chapter_by_id.values())
        levels_by_key = self._bulk_upsert(
            AdventureLevel,
            AdventureLevel.objects.filter(chapter__in=canonical_chapters),
            level_rows,
            key=lambda obj: (obj.chapter_id, obj.slug),
            update_fields=[
                "title",
                "description",
                "brief",
                "narrative_brief",
                "level_type",
                "is_required",
                "sort_order",
                "is_published",
                "reward_coins",
            ],
        )
        live_level_ids = [levels_by_key[key].id for key in level_keys]

        for key in level_keys:
            group = level_groups[key]
            form_set: list[CommandForm] = []
            seen: set[int] = set()
            usages = [
                usage
                for wave in group["waves"]
                for usage in [wave["usage"], *wave.get("command_forms", [])]
            ] + list(group.get("reuse_usages", []))
            for usage in usages:
                form = forms.get(usage)
                if form is not None and form.id not in seen:
                    seen.add(form.id)
                    form_set.append(form)
            levels_by_key[key].command_forms.set(form_set)

        wave_rows = []
        wave_keys: list[tuple[int, str]] = []
        wave_specs: dict[tuple[int, str], dict] = {}
        for key in level_keys:
            level = levels_by_key[key]
            group = level_groups[key]
            for sort_index, wave_spec in enumerate(group["waves"]):
                ctx = wave_spec.get("scenario_context") or {}
                wkey = (level.id, wave_spec["slug"])
                wave_keys.append(wkey)
                wave_specs[wkey] = wave_spec
                wave_rows.append(
                    (
                        wkey,
                        {
                            "level": level,
                            "slug": wave_spec["slug"],
                            "title": wave_spec["title"],
                            "sort_order": sort_index,
                            "story": ctx.get("story", "") or "",
                            "task": ctx.get("task", "") or "",
                            "min_counted_commands": wave_spec["min_counted_commands"],
                            "max_counted_commands": wave_spec["max_counted_commands"],
                            "objective_checks": wave_spec.get("objective_checks", []),
                            "is_published": True,
                        },
                    )
                )
        waves_by_key = self._bulk_upsert(
            AdventureWave,
            AdventureWave.objects.filter(level__chapter__in=canonical_chapters),
            wave_rows,
            key=lambda obj: (obj.level_id, obj.slug),
            update_fields=[
                "title",
                "sort_order",
                "story",
                "task",
                "min_counted_commands",
                "max_counted_commands",
                "objective_checks",
                "is_published",
            ],
        )
        live_wave_ids = [waves_by_key[wkey].id for wkey in wave_keys]
        for wkey in wave_keys:
            wave_spec = wave_specs[wkey]
            usages = [wave_spec["usage"], *list(wave_spec.get("command_forms", []))]
            form_set: list[CommandForm] = []
            seen: set[int] = set()
            for usage in usages:
                form = forms.get(usage)
                if form is not None and form.id not in seen:
                    seen.add(form.id)
                    form_set.append(form)
            waves_by_key[wkey].command_forms.set(form_set)

        self._bulk_sync_variants(
            variant_model=AdventureWaveVariant,
            level_fk="wave",
            levels_and_specs=[
                (waves_by_key[wkey], wave_specs[wkey]["variants"]) for wkey in wave_keys
            ],
            builder=builder,
        )

        official_chapter_slugs = [spec["slug"] for spec in CHAPTERS]
        AdventureWave.objects.filter(
            level__chapter__slug__in=official_chapter_slugs
        ).exclude(id__in=live_wave_ids).update(is_published=False)
        AdventureLevel.objects.filter(
            chapter__slug__in=official_chapter_slugs
        ).exclude(id__in=live_level_ids).update(is_published=False)
