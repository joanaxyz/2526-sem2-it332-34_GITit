from __future__ import annotations

from adventures.models import AdventureLevel
from curriculum.models import ChapterLesson

from .access import (
    _build_adventure_access,
    _build_challenge_access,
    adventure_summary_payload,
    challenge_summary_payload,
)
from .book import lesson_summary_payload
from .challenge_queries import challenge_queryset


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
    adventure_access = _build_adventure_access(player=player, adventures=adventures)
    required_adventure_ids = {
        adventure.id for adventure in adventures if adventure.is_required
    }
    adventure_passed = required_adventure_ids <= adventure_access.passed_adventure_ids
    access = _build_challenge_access(
        player=player,
        chapter_id=chapter_id,
        challenges=challenges,
        adventure_passed=adventure_passed,
    )
    # The frontend map lays out its floating relics in code now (frontend), so the
    # overview is just the chapter's content lists.
    adventure_payloads = [
        adventure_summary_payload(player=player, adventure=adventure, access=adventure_access)
        for adventure in adventures
    ]
    return {
        "chapter_id": chapter_id,
        "adventures": adventure_payloads,
        "lessons": [lesson_summary_payload(lesson=lesson) for lesson in lessons],
        "challenges": [
            challenge_summary_payload(
                challenge=challenge,
                access=access,
                sibling_levels=challenges,
            )
            for challenge in challenges
        ],
    }
