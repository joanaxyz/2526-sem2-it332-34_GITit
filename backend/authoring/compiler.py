from __future__ import annotations

import hashlib
import json
from typing import Any

from django.db import transaction
from django.utils.text import slugify

from adventures.models import (
    AdventureLevel,
    AdventureWave,
    AdventureWaveVariant,
)
from authoring.models import ContentDefinition, ContentKind, PublishedContentRuntime
from authoring.schemas import (
    challenge_is_nested,
    content_levels,
    level_trials,
    level_waves,
)
from challenges.models import ChallengeLevel, ChallengeTrial, ChallengeTrialVariant
from curriculum.models import (
    Chapter,
    ChapterLesson,
    CommandForm,
    CommandSkill,
)
from simulator.services import RepositoryStateSimulator

HIDDEN_CHAPTER_NUMBER_BASE = 900_000
GROUPED_CHAPTER_NUMBER_BASE = 800_000


class ContentRuntimeCompiler:
    def __init__(self) -> None:
        self.simulator = RepositoryStateSimulator()

    @transaction.atomic
    def compile(self, *, content: ContentDefinition) -> PublishedContentRuntime:
        signature = self._signature(content.definition)
        runtime = getattr(content, "runtime", None)
        if runtime and runtime.definition_signature == signature:
            return runtime
        chapter = self._runtime_chapter(content)
        adventure = challenge = lesson = None
        if content.kind == ContentKind.ADVENTURE:
            adventure = self._compile_adventure(content, chapter)
        elif content.kind == ContentKind.CHALLENGE:
            challenge = self._compile_challenge(content, chapter)
        elif content.kind == ContentKind.LESSON:
            lesson = self._compile_lesson(content, chapter)
        runtime, _created = PublishedContentRuntime.objects.update_or_create(
            content_definition=content,
            defaults={
                "chapter": chapter,
                "adventure": adventure,
                "challenge": challenge,
                "lesson": lesson,
                "definition_signature": signature,
            },
        )
        return runtime

    def _runtime_chapter(self, content: ContentDefinition) -> Chapter:
        if content.chapter_id is not None:
            chapter = content.chapter
            number = GROUPED_CHAPTER_NUMBER_BASE + chapter.id
            slug = f"ugc-chapter-{chapter.id}"
            title = chapter.title
            description = chapter.summary
        else:
            number = HIDDEN_CHAPTER_NUMBER_BASE + content.id
            slug = f"ugc-{content.kind}-{content.id}"
            title = content.title
            description = content.summary
        return Chapter.objects.update_or_create(
            slug=slug,
            defaults={
                "number": number,
                "title": title,
                "description": description,
                # UGC runtime chapters stay unpublished: they back the level-editor
                # playtest surface, not the official track, so ChapterChestService's
                # is_published gate already keeps them out of the reward schedule.
                "is_published": False,
                "sort_order": number,
                "battle_stage": {},
            },
        )[0]

    def _compile_adventure(self, content: ContentDefinition, chapter: Chapter) -> AdventureLevel:
        fallback_form = self._command_form_for_content(content=content, chapter=chapter)
        AdventureLevel.objects.filter(source_content_definition=content).delete()
        first_level = None
        for index, authored in enumerate(content_levels(content.definition)):
            level = AdventureLevel.objects.create(
                chapter=chapter,
                slug=authored["slug"],
                title=authored["title"],
                is_published=True,
                sort_order=index,
                source_content_definition=content,
            )
            if first_level is None:
                first_level = level
            level_forms = self._resolve_level_forms(authored, fallback=fallback_form)
            level.command_forms.set(level_forms)
            for wave_index, authored_wave in enumerate(level_waves(authored)):
                ctx = authored_wave.get("scenario_context") or {}
                budget = authored_wave.get("command_budget") or {}
                wave = AdventureWave.objects.create(
                    level=level,
                    slug=authored_wave.get("slug") or f"{level.slug}-wave-{wave_index + 1}",
                    title=authored_wave.get("title", "") or "",
                    sort_order=wave_index,
                    story=ctx.get("story", "") or "",
                    task=ctx.get("task", "") or "",
                    min_counted_commands=int(
                        budget.get("min_counted_commands")
                        or authored_wave.get("min_counted_commands")
                        or 1
                    ),
                    max_counted_commands=int(
                        budget.get("max_counted_commands")
                        or authored_wave.get("max_counted_commands")
                        or 8
                    ),
                    objective_checks=authored_wave.get("objective_checks") or [],
                    is_published=True,
                )
                wave_forms = self._resolve_level_forms(
                    authored_wave,
                    fallback=None,
                    required=False,
                )
                wave.command_forms.set(wave_forms or level_forms)
                self._replace_variants(
                    parent=wave,
                    variant_model=AdventureWaveVariant,
                    parent_field="wave",
                    authored=authored_wave,
                    index=wave_index,
                )
        if first_level is None:
            first_level = AdventureLevel.objects.create(
                chapter=chapter,
                slug=f"ugc-adventure-{content.id}",
                title=content.title,
                is_published=True,
                source_content_definition=content,
            )
        return first_level


    def _compile_challenge(self, content: ContentDefinition, chapter: Chapter) -> ChallengeLevel:
        # Grouped authored chapters share one runtime Chapter, so challenge
        # level slugs must include the source definition identity. Without this
        # namespace, compiling a second challenge in the same chapter collides
        # with the first chapter-level slug.
        slug_base = (
            f"ugc-chapter-{content.chapter_id}-challenge-{content.id}"
            if content.chapter_id
            else f"ugc-challenge-{content.id}"
        )
        ChallengeLevel.objects.filter(source_content_definition=content).delete()
        fallback_form = self._command_form_for_content(
            content=content, chapter=chapter, required=False
        )
        authored_levels = content_levels(content.definition)
        if challenge_is_nested(content.definition):
            level_groups = [
                (
                    (
                        f"{slug_base}-{slugify(authored.get('slug') or f'level-{index + 1}')}"
                        if content.chapter_id
                        else authored.get("slug") or f"{slug_base}-level-{index + 1}"
                    ),
                    authored.get("title") or content.title,
                    authored,
                    level_trials(authored),
                )
                for index, authored in enumerate(authored_levels)
            ]
        else:
            level_groups = [
                (
                    f"{slug_base}-level-1",
                    content.title,
                    None,
                    authored_levels,
                )
            ]
        first_level = None
        for level_index, (slug, title, authored_level, trials) in enumerate(level_groups):
            challenge_level = ChallengeLevel.objects.create(
                chapter=chapter,
                slug=slug,
                title=title,
                summary=content.summary,
                narrative=content.definition.get("narrative", content.summary),
                is_published=True,
                sort_order=level_index,
                source_content_definition=content,
            )
            if first_level is None:
                first_level = challenge_level
            forms = self._resolve_level_forms(
                authored_level or {}, fallback=fallback_form, required=False
            )
            if forms:
                challenge_level.command_forms.set(forms)
            for index, authored in enumerate(trials):
                ctx = authored.get("scenario_context") or {}
                budget = authored.get("command_budget") or {}
                trial = ChallengeTrial.objects.create(
                    challenge_level=challenge_level,
                    difficulty=authored.get("difficulty") or content.difficulty or "easy",
                    story=ctx.get("story", "") or "",
                    task=ctx.get("task", "") or "",
                    min_counted_commands=int(
                        budget.get("min_counted_commands")
                        or authored.get("min_counted_commands")
                        or 1
                    ),
                    max_counted_commands=int(
                        budget.get("max_counted_commands")
                        or authored.get("max_counted_commands")
                        or 8
                    ),
                    objective_checks=authored.get("objective_checks") or [],
                    is_published=True,
                )
                self._replace_variants(
                    parent=trial,
                    variant_model=ChallengeTrialVariant,
                    parent_field="trial",
                    authored=authored,
                    index=index,
                )
        if first_level is None:
            first_level = ChallengeLevel.objects.create(
                chapter=chapter,
                slug=f"{slug_base}-level-1",
                title=content.title,
                summary=content.summary,
                narrative=content.definition.get("narrative", content.summary),
                is_published=True,
                source_content_definition=content,
            )
        return first_level


    def _compile_lesson(self, content: ContentDefinition, chapter: Chapter) -> ChapterLesson:
        definition = content.definition or {}
        return ChapterLesson.objects.update_or_create(
            chapter=chapter,
            slug=f"ugc-lesson-{content.id}",
            defaults={
                "title": content.title,
                "summary": content.summary,
                "pages": definition.get("pages") or [],
                "is_published": True,
                "sort_order": 0,
                "source_content_definition": content,
            },
        )[0]


    def _command_form_for_content(
        self,
        *,
        content: ContentDefinition,
        chapter: Chapter,
        required: bool = True,
    ) -> CommandForm | None:
        base_command = content.command_family or str(
            (content.definition or {}).get("base_command") or ""
        ).strip()
        if not base_command:
            if required:
                base_command = "git"
            else:
                return None
        skill = CommandSkill.objects.update_or_create(
            slug=f"{slugify(base_command) or 'git'}-ugc-{content.id}",
            defaults={
                "base_command": base_command,
                "title": content.title,
                "summary": content.summary,
                "is_published": True,
                "sort_order": 0,
            },
        )[0]
        return CommandForm.objects.update_or_create(
            command_skill=skill,
            slug="authored",
            defaults={
                "chapter": chapter,
                "usage_form": base_command,
                "label": content.title,
                "summary": content.summary,
                "is_published": True,
                "sort_order": 0,
            },
        )[0]

    def _resolve_level_forms(
        self,
        authored: dict[str, Any],
        *,
        fallback: CommandForm | None,
        required: bool = True,
    ) -> list[CommandForm]:
        """The command forms a level introduces/reuses (the spiral).

        Authors may list existing ``CommandForm`` ids in ``command_forms``; an
        unspecified level falls back to the single synthesized form for the
        content so legacy definitions keep their one-form mastery behaviour."""
        ids = authored.get("command_forms")
        if isinstance(ids, list) and ids:
            forms = list(
                CommandForm.objects.filter(
                    id__in=[i for i in ids if isinstance(i, int)]
                )
            )
            if forms:
                return forms
        if fallback is not None:
            return [fallback]
        return [] if not required else ([fallback] if fallback else [])

    def _replace_variants(
        self,
        *,
        parent,
        variant_model,
        parent_field: str,
        authored: dict[str, Any],
        index: int,
    ) -> None:
        kept_slugs: set[str] = set()
        parent_key = self._parent_key(parent)
        # A wave carries its own slug; a challenge trial is keyed by difficulty
        # and has none, so fall back to the parent's stable key.
        primary_slug = authored.get("variant_slug") or authored.get("slug") or parent_key
        self._upsert_variant(
            parent=parent,
            variant_model=variant_model,
            parent_field=parent_field,
            source=authored,
            slug=primary_slug,
            label=authored.get("variant_label") or "Authored",
            case_id=authored.get("case_id") or f"{parent_key}-{index}",
            semantic_source=authored,
        )
        kept_slugs.add(primary_slug)
        for extra_index, extra in enumerate(self._authored_variants(authored)):
            slug = self._unique_variant_slug(
                extra.get("slug") or f"{primary_slug}-case-{extra_index + 1}",
                kept_slugs,
            )
            self._upsert_variant(
                parent=parent,
                variant_model=variant_model,
                parent_field=parent_field,
                source=extra,
                slug=slug,
                label=extra.get("label") or f"Case {extra_index + 1}",
                case_id=extra.get("case_id") or f"{parent_key}-{index}-{extra_index + 1}",
                semantic_source={"slug": slug, **extra},
                inherit=authored,
            )
            kept_slugs.add(slug)
        parent.variants.exclude(slug__in=kept_slugs).update(is_published=False)

    def _upsert_variant(
        self,
        *,
        parent,
        variant_model,
        parent_field: str,
        source: dict[str, Any],
        slug: str,
        label: str,
        case_id: str,
        semantic_source: dict[str, Any],
        inherit: dict[str, Any] | None = None,
    ):
        base = inherit or {}
        initial_state = self.simulator.normalize_state(source.get("initial_state") or {})
        solution_commands = list(source.get("solution_commands") or [])
        target_state = self._target_state(initial_state, source)
        return variant_model.objects.update_or_create(
            **{parent_field: parent},
            slug=slug,
            defaults={
                "label": label,
                "initial_state": initial_state,
                "evaluation_spec": source.get("evaluation_spec")
                or base.get("evaluation_spec")
                or {"completion_policy": {"mode": "state_hash"}},
                "target_state": target_state,
                "solution_commands": solution_commands,
                "case_id": case_id,
                "semantic_key": self._semantic_key(self._parent_key(parent), semantic_source),
                "parameter_context": source.get("parameter_context") or {},
                "scenario_context": source.get("scenario_context")
                or base.get("scenario_context")
                or {},
                "scaffold_policy": source.get("scaffold_policy") or {},
                "is_published": True,
            },
        )[0]

    @staticmethod
    def _parent_key(parent) -> str:
        """Stable string identity for a variant parent.

        ``AdventureLevel`` is keyed by its ``slug``; a ``ChallengeTrial`` has no
        slug (it is identified by difficulty within its level), so fall back to
        ``<level-slug>-<difficulty>`` and finally the primary key.
        """
        slug = getattr(parent, "slug", None)
        if slug:
            return str(slug)
        difficulty = getattr(parent, "difficulty", None)
        if difficulty is not None:
            level = getattr(parent, "challenge_level", None)
            level_slug = getattr(level, "slug", "") or ""
            return f"{level_slug}-{difficulty}" if level_slug else str(difficulty)
        return str(parent.pk)

    @staticmethod
    def _authored_variants(authored: dict[str, Any]) -> list[dict[str, Any]]:
        raw = authored.get("variants")
        if not isinstance(raw, list):
            return []
        return [entry for entry in raw if isinstance(entry, dict)]

    @staticmethod
    def _unique_variant_slug(slug: str, taken: set[str]) -> str:
        base = slugify(slug) or "case"
        candidate = base
        suffix = 2
        while candidate in taken:
            candidate = f"{base}-{suffix}"
            suffix += 1
        return candidate

    def _target_state(self, initial_state: dict, authored: dict[str, Any]) -> dict:
        authored_target = authored.get("target_state")
        if isinstance(authored_target, dict) and authored_target:
            return self.simulator.normalize_state(authored_target)
        return self.simulator.normalize_state(initial_state)

    def _signature(self, definition: dict) -> str:
        return hashlib.sha256(
            json.dumps(
                definition,
                sort_keys=True,
                separators=(",", ":"),
                default=str,
            ).encode("utf-8")
        ).hexdigest()

    def _semantic_key(self, slug: str, authored: dict[str, Any]) -> str:
        return hashlib.sha256(
            json.dumps({"slug": slug, "authored": authored}, sort_keys=True, default=str).encode(
                "utf-8"
            )
        ).hexdigest()[:40]
