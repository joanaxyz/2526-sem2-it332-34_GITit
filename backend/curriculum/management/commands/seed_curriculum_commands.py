from __future__ import annotations

from curriculum.models import (
    Chapter,
    CommandForm,
    CommandSkill,
)
from curriculum.seed_data.adventure_levels import ADVENTURE_LEVELS
from curriculum.seed_data.challenges import CHALLENGES
from curriculum.seed_data.command_catalog import COMMAND_CATALOG


class SeedCurriculumCommandSkillsMixin:
    def _seed_command_skills(self, chapters: dict[str, Chapter]) -> dict[str, CommandForm]:
        def form_chapter(spec, form_spec) -> Chapter:
            # A usage may override the skill's default chapter (a command can teach
            # basic moves in one chapter and advanced moves in a later one).
            return chapters[form_spec.get("module", spec["module"])]

        skill_rows = []
        for skill_index, spec in enumerate(COMMAND_CATALOG, start=1):
            # The chapter book owns the complete authored command scope. Engine
            # capability is tracked separately on each form, so a command is not
            # hidden merely because its simulator implementation lands later.
            skill_is_published = any(
                form_chapter(spec, form_spec).is_published
                for form_spec in spec.get("usages", [])
            )
            skill_rows.append(
                (
                    spec["slug"],
                    {
                        "slug": spec["slug"],
                        "base_command": spec["base_command"],
                        "title": spec["title"],
                        "summary": spec["summary"],
                        "mental_model": spec.get("mental_model", {}),
                        "command_preview": self._preview(spec["title"], spec["summary"]),
                        "sort_order": skill_index,
                        "is_published": skill_is_published,
                    },
                )
            )
        skills_by_slug = self._bulk_upsert(
            CommandSkill,
            CommandSkill.objects.all(),
            skill_rows,
            key=lambda obj: obj.slug,
            update_fields=[
                "base_command",
                "title",
                "summary",
                "mental_model",
                "command_preview",
                "sort_order",
                "is_published",
            ],
        )
        live_skill_ids = [skills_by_slug[slug].id for slug, _ in skill_rows]
        skill_objs = list(skills_by_slug.values())

        form_rows = []
        form_key_to_identity: dict[str, tuple[int, str]] = {}
        for spec in COMMAND_CATALOG:
            skill = skills_by_slug[spec["slug"]]
            for form_index, form_spec in enumerate(spec.get("usages", []), start=1):
                chapter = form_chapter(spec, form_spec)
                form_key = f"{spec['slug']}/{form_spec['slug']}"
                form_is_published = chapter.is_published
                form_is_playable = form_key in self.supported_form_keys
                form_key_to_identity[form_key] = (skill.id, form_spec["slug"])
                form_rows.append(
                    (
                        (skill.id, form_spec["slug"]),
                        {
                            "command_skill": skill,
                            "chapter": chapter,
                            "slug": form_spec["slug"],
                            "usage_form": form_spec["usage_form"],
                            "label": form_spec["label"],
                            "summary": form_spec.get("summary", ""),
                            "command_preview": self._preview(
                                form_spec["usage_form"],
                                form_spec.get("summary") or spec["summary"],
                                syntax=form_spec["usage_form"],
                            ),
                            "sort_order": form_index,
                            "is_published": form_is_published,
                            "is_playable": form_is_playable,
                        },
                    )
                )
        forms_by_key = self._bulk_upsert(
            CommandForm,
            CommandForm.objects.filter(command_skill__in=skill_objs),
            form_rows,
            key=lambda obj: (obj.command_skill_id, obj.slug),
            update_fields=[
                "chapter",
                "usage_form",
                "label",
                "summary",
                "command_preview",
                "sort_order",
                "is_published",
                "is_playable",
            ],
        )
        live_form_ids = [forms_by_key[key].id for key, _ in form_rows]
        CommandForm.objects.filter(command_skill__in=skill_objs).exclude(
            id__in=live_form_ids
        ).update(is_published=False)
        CommandSkill.objects.exclude(id__in=live_skill_ids).update(is_published=False)
        return {
            form_key: forms_by_key[identity]
            for form_key, identity in form_key_to_identity.items()
        }

    def _usage_to_chapter_slug(self) -> dict[str, str]:
        usage_to_chapter = {}
        for skill_spec in COMMAND_CATALOG:
            for form_spec in skill_spec.get("usages", []):
                # A usage may override its skill's default chapter (a command can
                # span chapters: basic moves early, advanced moves later).
                module = form_spec.get("module", skill_spec["module"])
                usage_to_chapter[f"{skill_spec['slug']}/{form_spec['slug']}"] = module
        return usage_to_chapter

    def _published_chapter_slugs(self) -> set[str]:
        form_to_chapter = self._usage_to_chapter_slug()
        command_chapters = {
            form_to_chapter[spec["usage"]]
            for spec in ADVENTURE_LEVELS
            if spec["usage"] in form_to_chapter and not spec.get("engine_blocked")
        }
        reference_chapters = {
            form_spec.get("module", skill_spec["module"])
            for skill_spec in COMMAND_CATALOG
            for form_spec in skill_spec.get("usages", [])
        }
        challenge_chapters = {spec["module"] for spec in CHALLENGES}
        return command_chapters | reference_chapters | challenge_chapters
