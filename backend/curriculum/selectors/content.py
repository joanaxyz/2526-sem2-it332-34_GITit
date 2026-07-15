from __future__ import annotations

from adventures.models import AdventureLevel
from curriculum.models import ChapterLesson

from .access import (
    _build_adventure_access,
    _build_challenge_access,
    adventure_summary_payload,
    challenge_summary_payload,
    command_skill_summary_payload,
)
from .book import lesson_summary_payload
from .challenge_queries import challenge_queryset
from .command_skills import command_skill_queryset


def chapter_content_page(
    *,
    player,
    chapter_id: int,
    section: str,
    cursor: int | None = None,
    limit: int = 8,
) -> dict:
    limit = max(1, min(limit, 24))
    if section == "adventures":
        adventures = list(
            AdventureLevel.objects.filter(chapter_id=chapter_id, is_published=True)
            .select_related("chapter")
            .order_by("sort_order", "id")
        )
        access = _build_adventure_access(player=player, adventures=adventures)
        return {
            "section": section,
            "results": [
                adventure_summary_payload(player=player, adventure=adventure, access=access)
                for adventure in adventures
            ],
            "next_cursor": None,
        }

    if section == "lessons":
        lessons = ChapterLesson.objects.filter(chapter_id=chapter_id, is_published=True).order_by(
            "sort_order", "id"
        )
        return {
            "section": section,
            "results": [lesson_summary_payload(lesson=lesson) for lesson in lessons],
            "next_cursor": None,
        }

    if section == "challenges":
        queryset = challenge_queryset(chapter_id=chapter_id)
        if cursor:
            queryset = queryset.filter(id__gt=cursor)
        items = list(queryset[: limit + 1])
        visible = items[:limit]
        access = _build_challenge_access(player=player, chapter_id=chapter_id, challenges=visible)
        return {
            "section": section,
            "results": [
                challenge_summary_payload(challenge=challenge, access=access)
                for challenge in visible
            ],
            "next_cursor": visible[-1].id if len(items) > limit and visible else None,
        }

    queryset = command_skill_queryset(chapter_id=chapter_id)
    if cursor:
        queryset = queryset.filter(id__gt=cursor)
    items = list(queryset[: limit + 1])
    visible = items[:limit]
    return {
        "section": "command_skills",
        "results": [command_skill_summary_payload(skill=skill) for skill in visible],
        "next_cursor": visible[-1].id if len(items) > limit and visible else None,
    }


def chapter_content_overview(*, player, chapter_id: int) -> dict:
    """Every map item for one chapter in a single payload.

    The chapter map renders chapter-owned adventure levels, lessons, and
    challenges. Chapters hold only a handful of items, so this returns them all
    in one response instead of making the map issue separate requests per
    section.
    """
    adventures = list(
        AdventureLevel.objects.filter(chapter_id=chapter_id, is_published=True)
        .select_related("chapter")
        .order_by("sort_order", "id")
    )
    lessons = ChapterLesson.objects.filter(chapter_id=chapter_id, is_published=True).order_by(
        "sort_order", "id"
    )
    challenges = list(challenge_queryset(chapter_id=chapter_id))
    access = _build_challenge_access(player=player, chapter_id=chapter_id, challenges=challenges)
    # The frontend map lays out its floating relics in code now (frontend), so the
    # overview is just the chapter's content lists.
    adventure_access = _build_adventure_access(player=player, adventures=adventures)
    adventure_payloads = [
        adventure_summary_payload(player=player, adventure=adventure, access=adventure_access)
        for adventure in adventures
    ]
    return {
        "chapter_id": chapter_id,
        "adventures": adventure_payloads,
        "lessons": [lesson_summary_payload(lesson=lesson) for lesson in lessons],
        "challenges": [
            challenge_summary_payload(challenge=challenge, access=access)
            for challenge in challenges
        ],
    }
