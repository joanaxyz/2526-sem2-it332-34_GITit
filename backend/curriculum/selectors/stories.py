from __future__ import annotations

from django.db.models import Count, Q

from adventures.models import AdventureLevel
from challenges.models import ChallengeLevel
from curriculum.models import Chapter, Story

from .access import _adventure_passed

# Default vertical band height per chapter (legacy fork geometry). Self-contained
# now that the old map-builder app is gone.
DEFAULT_CHAPTER_HEIGHT = 560



def published_stories():
    return Story.objects.filter(is_published=True).select_related("prerequisite_story").order_by("sort_order", "id")


def published_chapters(*, story_slug: str | None = None):
    queryset = Chapter.objects.filter(is_published=True, story__is_published=True)
    if story_slug:
        queryset = queryset.filter(story__slug=story_slug)
    return (
        queryset.select_related("story")
        .annotate(
            # Skills are global now; count the distinct commands a chapter teaches
            # via the forms scoped to it.
            command_skill_count=Count(
                "command_forms__command_skill",
                filter=Q(command_forms__is_published=True),
                distinct=True,
            ),
            challenge_count=Count(
                "challenge_levels",
                filter=Q(challenge_levels__is_published=True),
                distinct=True,
            ),
            adventure_level_count=Count(
                "adventure_levels",
                filter=Q(adventure_levels__is_published=True),
                distinct=True,
            ),
        )
        .order_by("sort_order", "number")
    )


def chapter_completed(*, player, chapter: Chapter) -> bool:
    if player is None or not chapter.is_playable:
        return False
    required_level_ids = list(
        ChallengeLevel.objects.filter(chapter=chapter, is_published=True).values_list("id", flat=True)
    )
    if required_level_ids:
        from progress.models import ChallengeLevelCompletion

        completed_ids = set(
            ChallengeLevelCompletion.objects.filter(
                player=player,
                challenge_level_id__in=required_level_ids,
            ).values_list("challenge_level_id", flat=True)
        )
        return set(required_level_ids).issubset(completed_ids)
    return _adventure_passed(player=player, chapter_id=chapter.id)


def chapter_locked(*, player, chapter: Chapter) -> tuple[bool, str]:
    if not chapter.story_id:
        return False, ""
    story_is_locked, story_reason = story_locked(player=player, story=chapter.story)
    if story_is_locked:
        return True, story_reason
    # A future book-only chapter remains browseable once its story is accessible.
    # Published playable chapters continue through the normal progression gate.
    if not chapter.is_playable:
        return False, ""
    previous = (
        Chapter.objects.filter(
            story=chapter.story,
            is_published=True,
            is_playable=True,
            sort_order__lt=chapter.sort_order,
        )
        .order_by("-sort_order", "-number")
        .first()
    )
    if previous is None:
        return False, ""
    if chapter_completed(player=player, chapter=previous):
        return False, ""
    return True, f"Clear Chapter {previous.number}'s first challenge to unlock this chapter."


def story_locked(
    *, player, story: Story, completed_map: dict[int, bool] | None = None
) -> tuple[bool, str]:
    from shop.access import owns_item
    from shop.catalog import KIND_STORY

    if not owns_item(player=player, kind=KIND_STORY, slug=story.slug):
        return True, f"Buy {story.title} in the Shop to unlock this story."

    prerequisite = story.prerequisite_story
    if prerequisite is not None:
        if completed_map is not None and prerequisite.id in completed_map:
            prerequisite_completed = completed_map[prerequisite.id]
        else:
            prerequisite_completed = story_completed(player=player, story=prerequisite)
        if not prerequisite_completed:
            return True, (
                f"Master every command in {prerequisite.title} before entering {story.title}."
            )
    return False, ""


def stories_completed_map(*, player, stories) -> dict[int, bool]:
    """A story is completed when every playable command form its required
    published levels teach has been mastered by the player.

    The denominator is derived from the levels themselves (not the whole
    chapter catalog), so a story can never demand mastery of a form it offers
    no practice for. Two queries total regardless of story count.
    """
    stories = list(stories)
    result = {story.id: False for story in stories}
    if player is None or not stories:
        return result

    rows = AdventureLevel.objects.filter(
        chapter__story__in=stories,
        chapter__is_published=True,
        is_published=True,
        is_required=True,
        command_forms__is_published=True,
        command_forms__is_playable=True,
    ).values_list("chapter__story_id", "command_forms")
    forms_by_story: dict[int, set[int]] = {}
    for story_id, form_id in rows:
        if form_id is not None:
            forms_by_story.setdefault(story_id, set()).add(form_id)
    if not forms_by_story:
        return result

    from adventures.models import SkillMastery

    all_form_ids = set().union(*forms_by_story.values())
    mastered = set(
        SkillMastery.objects.filter(
            player=player,
            mastered=True,
            command_form_id__in=all_form_ids,
        ).values_list("command_form_id", flat=True)
    )
    for story in stories:
        required = forms_by_story.get(story.id, set())
        result[story.id] = bool(required) and required <= mastered
    return result


def story_completed(*, player, story: Story) -> bool:
    return stories_completed_map(player=player, stories=[story])[story.id]


def chapter_band_offset(*, chapter_heights: dict | None, chapter_number: int) -> int:
    """Y of a chapter band's top: the sum of prior chapters' heights (each
    defaulting to DEFAULT_CHAPTER_HEIGHT unless explicitly resized)."""
    heights = chapter_heights or {}
    return sum(
        int(heights.get(str(n), DEFAULT_CHAPTER_HEIGHT)) for n in range(1, chapter_number)
    )


def _published_adventure_levels_queryset():
    return AdventureLevel.objects.filter(is_published=True)
