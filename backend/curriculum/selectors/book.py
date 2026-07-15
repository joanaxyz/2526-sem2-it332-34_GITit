from __future__ import annotations

from django.db.models import Prefetch

from curriculum.library import library_key_for_command
from curriculum.models import Chapter, ChapterLesson, CommandForm, CommandSkill, LibraryEntry


def chapter_book(*, chapter_id: int) -> dict | None:
    """The Chapter Book: every command registered for the chapter, each resolved to
    its rich authored content from the library, plus the chapter's authored
    lesson lessons.

    There is no terminal demo here - the book is reference material. Pages come
    from the seeded ``LibraryEntry`` for the skill's command (authored in
    ``library.py``, persisted by ``seed_command_library``); a minimal summary
    page is synthesized as a fallback so a registered command never renders
    empty. Lessons use the same page/block schema and are surfaced in the book's
    navigation rather than on an interactive map screen."""
    chapter = (
        Chapter.objects.filter(id=chapter_id, is_published=True)
        .only("id", "slug", "number", "title", "description")
        .first()
    )
    if chapter is None:
        return None

    # The commands taught in this chapter = the global skills that have a published
    # form scoped to it. A command split across chapters (e.g. `git add`) shows up
    # in each chapter's book, resolved to the same shared library entry.
    skills = list(
        CommandSkill.objects.filter(
            command_forms__chapter_id=chapter_id,
            command_forms__is_published=True,
            is_published=True,
        )
        .distinct()
        .prefetch_related(
            Prefetch(
                "command_forms",
                queryset=CommandForm.objects.filter(
                    chapter_id=chapter_id,
                    is_published=True,
                ).order_by("sort_order", "id"),
                to_attr="chapter_forms",
            )
        )
        .order_by("sort_order", "id")
    )
    # One query for the whole book: resolve every skill's library entry in bulk
    # so a chapter with N commands does not cost N round trips.
    keys = {library_key_for_command(skill.base_command) for skill in skills if skill.base_command}
    entries = {
        entry.command_key: entry
        for entry in LibraryEntry.objects.filter(command_key__in=keys, is_published=True)
    }
    commands = [
        book_command_payload(
            skill=skill,
            entry=entries.get(library_key_for_command(skill.base_command))
            if skill.base_command
            else None,
        )
        for skill in skills
    ]
    lessons = list(
        ChapterLesson.objects.filter(chapter_id=chapter_id, is_published=True).order_by(
            "sort_order", "id"
        )
    )
    return {
        "chapter_id": chapter.id,
        "slug": chapter.slug,
        "number": chapter.number,
        "title": chapter.title,
        "description": chapter.description,
        "command_count": len(commands),
        "commands": commands,
        "lesson_count": len(lessons),
        "lessons": [lesson_summary_payload(lesson=lesson) for lesson in lessons],
    }


def book_command_payload(*, skill: CommandSkill, entry: LibraryEntry | None) -> dict:
    if entry and entry.pages:
        pages = entry.pages
    else:
        pages = [
            {
                "id": f"{skill.slug}-overview",
                "title": "Overview",
                "heading": skill.title,
                "eyebrow": skill.base_command,
                "section_type": "overview",
                "blocks": [{"type": "paragraph", "body": skill.summary}] if skill.summary else [],
            }
        ]
    return {
        "id": skill.id,
        "slug": skill.slug,
        "base_command": skill.base_command,
        "title": skill.title,
        "summary": skill.summary,
        "tags": list(entry.tags) if entry and entry.tags else [],
        "forms": [
            {
                "id": form.id,
                "slug": form.slug,
                "usage_form": form.usage_form,
                "label": form.label,
                "summary": form.summary,
                "is_playable": form.is_playable,
            }
            for form in getattr(skill, "chapter_forms", [])
        ],
        "pages": pages,
    }


def lesson_summary_payload(*, lesson: ChapterLesson) -> dict:
    """Lessons are always-unlocked reading: pages ship inline so opening the
    reader needs no second request."""
    return {
        "item_type": "lesson",
        "id": lesson.id,
        "slug": lesson.slug,
        "title": lesson.title,
        "summary": lesson.summary,
        "pages": lesson.pages,
    }

