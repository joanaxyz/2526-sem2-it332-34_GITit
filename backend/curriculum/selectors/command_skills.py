from __future__ import annotations

from django.db.models import Prefetch

from adventures.models import AdventureLevel, SkillMastery
from curriculum.models import Chapter, CommandForm, CommandSkill


def command_skill_queryset(*, chapter_id: int):
    # Global skills scoped to a chapter through their forms; prefetch only the
    # forms taught in this chapter so a split command shows its chapter-local moves.
    return (
        CommandSkill.objects.filter(
            command_forms__chapter_id=chapter_id,
            command_forms__is_published=True,
            is_published=True,
        )
        .distinct()
        .prefetch_related(
            Prefetch(
                "command_forms",
                queryset=CommandForm.objects.filter(chapter_id=chapter_id, is_published=True),
            ),
            "command_forms__adventure_levels",
        )
        .order_by("sort_order", "id")
    )


def learned_command_skills(*, player) -> list[dict]:
    """The player's registry of learned commands.

    SkillMastery is the player-to-command relationship. ``introduced`` means the
    learner has seen a command in an adventure; ``learned_at`` means they have
    solved with it at least once. The spellbook uses learned_at so spells are
    earned incrementally during an adventure and never disappear if Leitner
    strength is later demoted.
    """
    if player is None:
        return []
    skill_ids = set(
        SkillMastery.objects.filter(
            player=player,
            learned_at__isnull=False,
            command_form__is_published=True,
            command_form__command_skill__is_published=True,
        )
        .values_list("command_form__command_skill_id", flat=True)
        .distinct()
    )

    # Legacy/data-repair fallback for saved runs that already passed before the
    # permanent learned_at marker existed.
    passed_adventures = (
        AdventureLevel.objects.filter(
            runs__player=player,
            runs__is_replay=False,
            runs__passed_at__isnull=False,
            is_published=True,
        )
        .select_related("chapter")
        .distinct()
    )
    from adventures.services import adventure_command_form_ids

    fallback_form_ids: set[int] = set()
    for adventure in passed_adventures:
        fallback_form_ids |= adventure_command_form_ids(adventure)
    if fallback_form_ids:
        skill_ids |= set(
            CommandForm.objects.filter(id__in=fallback_form_ids).values_list(
                "command_skill_id", flat=True
            )
        )

    if not skill_ids:
        return []
    # Skills are a global library; a command's "chapter" for the spellbook is the
    # one where it is introduced (its earliest published form).
    intro_chapter_by_skill: dict[int, Chapter] = {}
    for form in (
        CommandForm.objects.filter(
            command_skill_id__in=skill_ids, is_published=True, chapter__isnull=False
        )
        .select_related("chapter")
        .order_by("chapter__sort_order")
    ):
        intro_chapter_by_skill.setdefault(form.command_skill_id, form.chapter)

    skills = CommandSkill.objects.filter(id__in=skill_ids, is_published=True)
    rows = []
    for skill in skills:
        chapter = intro_chapter_by_skill.get(skill.id)
        rows.append(
            {
                "id": skill.id,
                "slug": skill.slug,
                "base_command": skill.base_command,
                "title": skill.title,
                "summary": skill.summary,
                "chapter_id": chapter.id if chapter else None,
                "chapter_number": chapter.number if chapter else 0,
                "chapter_title": chapter.title if chapter else "",
                "_sort": (chapter.sort_order if chapter else 0, skill.sort_order, skill.id),
            }
        )
    rows.sort(key=lambda row: row.pop("_sort"))
    return rows
