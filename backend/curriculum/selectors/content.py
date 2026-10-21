from __future__ import annotations

from django.db.models import Prefetch

from adventures.models import AdventureLevel, AdventureLevelTier
from curriculum.library import library_key_for_command
from curriculum.models import ChapterLesson, CommandForm, LibraryEntry

from .access import (
    _build_adventure_access,
    _build_challenge_access,
    adventure_summary_payload,
    challenge_summary_payload,
)
from .adventure_access import _build_adventure_tier_access
from .book import chapter_adventure_knowledge, lesson_summary_payload
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
        .prefetch_related(
            Prefetch(
                "command_forms",
                queryset=CommandForm.objects.select_related("command_skill").order_by(
                    "sort_order", "id"
                ),
                to_attr="overview_forms",
            ),
            Prefetch(
                "tiers",
                queryset=AdventureLevelTier.objects.filter(is_published=True),
                to_attr="overview_tiers",
            ),
        )
        .order_by("sort_order", "id")
    )
    lessons = ChapterLesson.objects.filter(chapter_id=chapter_id, is_published=True).order_by(
        "sort_order", "id"
    )
    challenges = list(challenge_queryset(chapter_id=chapter_id))
    # One tier access context for the whole chapter: a fixed handful of queries
    # however many nodes the map has.
    chapter_tiers = [tier for adventure in adventures for tier in adventure.overview_tiers]
    tier_access = _build_adventure_tier_access(player=player, tiers=chapter_tiers)
    adventure_access = _build_adventure_access(
        player=player, adventures=adventures, tiers=chapter_tiers, tier_access=tier_access
    )
    eligible_forms_by_adventure_id = {
        adventure.id: [
            form
            for form in adventure.overview_forms
            if form.is_published and form.is_playable and form.command_skill.is_published
        ]
        for adventure in adventures
    }
    library_keys = {
        library_key_for_command(form.command_skill.base_command)
        for forms in eligible_forms_by_adventure_id.values()
        for form in forms
        if form.command_skill.base_command
    }
    entries_by_key = {
        entry.command_key: entry
        for entry in LibraryEntry.objects.filter(
            command_key__in=library_keys, is_published=True
        )
    }
    knowledge_by_adventure_id = {
        adventure.id: chapter_adventure_knowledge(
            forms=eligible_forms_by_adventure_id[adventure.id],
            entries_by_key=entries_by_key,
        )
        for adventure in adventures
    }
    required_adventure_ids = {adventure.id for adventure in adventures if adventure.is_required}
    adventure_passed = required_adventure_ids <= adventure_access.passed_adventure_ids
    required_tier_ids = {
        tier.id for adventure in adventures if adventure.is_required for tier in adventure.overview_tiers
    }
    access = _build_challenge_access(
        player=player,
        chapter_id=chapter_id,
        challenges=challenges,
        adventure_passed=adventure_passed,
        # The gate opens once every tier the map already loaded is complete
        # (None for chapters without tiers).
        tiers_cleared=(
            bool(player) and required_tier_ids <= set(tier_access.completions)
            if required_tier_ids
            else None
        ),
    )
    # The frontend map lays out its floating relics in code now (frontend), so the
    # overview is just the chapter's content lists.
    adventure_payloads = [
        adventure_summary_payload(
            player=player,
            adventure=adventure,
            access=adventure_access,
            knowledge=knowledge_by_adventure_id[adventure.id],
            tiers=adventure.overview_tiers,
            tier_access=tier_access,
        )
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
