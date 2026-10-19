from __future__ import annotations

import re
from django.db.models import Prefetch

from curriculum.library import library_key_for_command
from curriculum.library_commands import ARGUMENT_PLACEHOLDER_ALIASES
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


def chapter_adventure_knowledge(*, forms, entries_by_key: dict[str, LibraryEntry]) -> list[dict]:
    """Project concise book-backed guidance for the playable forms on one level.

    The caller batches LibraryEntry reads across the chapter. This function only
    filters the already-loaded page sections against each form's exact syntax.
    """
    knowledge: list[dict] = []
    for form in forms:
        skill = form.command_skill
        if not form.is_published or not form.is_playable or not skill.is_published:
            continue
        command = (skill.base_command or "").strip()
        syntax = (form.usage_form or "").strip()
        if not command or not syntax:
            continue

        when_to_use = (form.summary or "").strip() or (form.label or "").strip()
        summary = (skill.summary or "").strip()
        if summary:
            knowledge.append(
                {
                    "id": f"form:{form.id}:command",
                    "kind": "command",
                    "command": command,
                    "title": (form.label or "Command form").strip(),
                    "token": "",
                    "syntax": syntax,
                    "text": summary,
                    "when_to_use": when_to_use,
                }
            )

        entry = entries_by_key.get(library_key_for_command(command))
        pages = entry.pages if entry and isinstance(entry.pages, list) else []
        semantic_pages = [
            page
            for page in pages
            if isinstance(page, dict)
            and _page_kind(page) in {"option", "argument"}
            and _page_explanation(page)
        ]
        matches = _matching_semantic_pages(
            command_key=library_key_for_command(command), syntax=syntax, pages=semantic_pages
        )
        for page in matches:
            token = _page_token(page)
            explanation = _page_explanation(page)
            if not token or not explanation:
                continue
            page_id = str(page.get("id") or "page")
            knowledge.append(
                {
                    "id": f"form:{form.id}:{page_id}",
                    "kind": _page_kind(page),
                    "command": command,
                    "title": str(page.get("title") or token).strip(),
                    "token": token,
                    "syntax": syntax,
                    "text": explanation,
                    "when_to_use": when_to_use,
                }
            )
    return knowledge


def _page_kind(page: dict) -> str:
    return str(page.get("type") or page.get("section_type") or "").strip().lower()


def _page_token(page: dict) -> str:
    return str(page.get("token") or page.get("eyebrow") or "").strip()


def _page_explanation(page: dict) -> str:
    blocks = page.get("content")
    if not isinstance(blocks, list):
        blocks = page.get("blocks")
    if not isinstance(blocks, list):
        return ""
    for block in blocks:
        if not isinstance(block, dict) or block.get("type") != "paragraph":
            continue
        body = str(block.get("body") or block.get("text") or "").strip()
        if body:
            return body
    return ""


def _matching_semantic_pages(*, command_key: str, syntax: str, pages: list[dict]) -> list[dict]:
    option_pages = [page for page in pages if _page_kind(page) == "option"]
    argument_pages = [page for page in pages if _page_kind(page) == "argument"]
    matching: list[dict] = []

    option_hits: set[int] = set()
    ambiguous_options: set[int] = set()
    for alias in _option_aliases_for_pages(option_pages):
        if not _contains_option(syntax, alias):
            continue
        hits = [index for index, page in enumerate(option_pages) if alias in _page_option_aliases(page)]
        if len(hits) > 1:
            ambiguous_options.update(hits)
        else:
            option_hits.update(hits)
    matching.extend(
        page for index, page in enumerate(option_pages) if index in option_hits and index not in ambiguous_options
    )

    placeholders = list(re.finditer(r"<[^<>]+>", syntax))
    argument_hits: set[int] = set()
    ambiguous_arguments: set[int] = set()
    for placeholder in placeholders:
        value = placeholder.group(0).casefold()
        before = syntax[: placeholder.start()]
        hits = [
            index
            for index, page in enumerate(argument_pages)
            if _page_matches_placeholder(
                command_key=command_key, page=page, placeholder=value, before=before
            )
        ]
        if len(hits) > 1:
            ambiguous_arguments.update(hits)
        else:
            argument_hits.update(hits)
    matching.extend(
        page
        for index, page in enumerate(argument_pages)
        if index in argument_hits and index not in ambiguous_arguments
    )
    return matching


def _option_aliases_for_pages(pages: list[dict]) -> set[str]:
    return {alias for page in pages for alias in _page_option_aliases(page)}


def _page_option_aliases(page: dict) -> set[str]:
    token = _page_token(page)
    return {alias.strip() for alias in re.split(r"\s*/\s*", token) if alias.strip()}


def _contains_option(syntax: str, alias: str) -> bool:
    return bool(re.search(rf"(?<!\S){re.escape(alias)}(?=$|[=\s])", syntax))


def _page_matches_placeholder(*, command_key: str, page: dict, placeholder: str, before: str) -> bool:
    page_id = str(page.get("id") or "")
    token = _page_token(page).casefold()
    if placeholder == token:
        return True

    if command_key == "git-config" and placeholder == "<name>":
        is_alias_key = bool(re.search(r"\balias\.$", before, flags=re.IGNORECASE))
        if page_id == "argument-key":
            return is_alias_key
        if page_id == "argument-value":
            return not is_alias_key

    aliases = ARGUMENT_PLACEHOLDER_ALIASES.get((command_key, page_id), frozenset())
    return placeholder in {alias.casefold() for alias in aliases}


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
