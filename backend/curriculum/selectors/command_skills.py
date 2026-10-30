from __future__ import annotations

from adventures.models import SkillMastery
from curriculum.library import library_key_for_command
from curriculum.models import Chapter, CommandForm, LibraryEntry

from .book import chapter_adventure_knowledge


def learned_command_skills(*, player) -> list[dict]:
    """The player's registry of learned commands.

    SkillMastery is the player-to-command relationship. ``introduced`` means the
    learner has seen a command in an adventure; ``learned_at`` means they have
    successfully executed it at least once. The spellbook uses learned_at so spells are
    earned incrementally during an adventure and never disappear if Leitner
    strength is later demoted.
    """
    if player is None:
        return []
    learned_forms_by_skill_id: dict[int, list[CommandForm]] = {}
    learned_at_by_skill_id = {}
    for mastery in (
        SkillMastery.objects.filter(
            player=player,
            learned_at__isnull=False,
            command_form__is_published=True,
            command_form__command_skill__is_published=True,
        )
        .select_related("command_form__command_skill")
        .order_by("-learned_at", "command_form__sort_order", "command_form_id")
    ):
        form = mastery.command_form
        learned_forms_by_skill_id.setdefault(form.command_skill_id, []).append(form)
        learned_at_by_skill_id.setdefault(form.command_skill_id, mastery.learned_at)
    skill_ids = set(learned_at_by_skill_id)

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

    # Reuse the map's compact Chapter Book projection, restricted to forms this
    # player has learned. Resolve the library in one batch for the spellbook.
    library_keys = {
        library_key_for_command(forms[0].command_skill.base_command)
        for forms in learned_forms_by_skill_id.values()
    }
    entries_by_key = {
        entry.command_key: entry
        for entry in LibraryEntry.objects.filter(command_key__in=library_keys, is_published=True)
    }
    rows = []
    for forms in learned_forms_by_skill_id.values():
        skill = forms[0].command_skill
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
                "learned_at": learned_at_by_skill_id[skill.id],
                "knowledge": chapter_adventure_knowledge(
                    forms=forms, entries_by_key=entries_by_key
                ),
                "_sort": (chapter.sort_order if chapter else 0, skill.sort_order, skill.id),
            }
        )
    rows.sort(key=lambda row: row.pop("_sort"))
    return rows
