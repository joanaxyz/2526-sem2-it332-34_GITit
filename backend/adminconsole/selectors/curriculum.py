"""Read-model builders for stories and chapters in the admin console."""

from __future__ import annotations

from django.db.models import Count

from adminconsole.curriculum_options import SUPPORTED_STORY_WORLD_SLUGS
from curriculum.models import Chapter, Story


def find_admin_story(story_id):
    try:
        return Story.objects.filter(pk=story_id).first()
    except (ValueError, TypeError):
        return None


def find_admin_chapter(chapter_id):
    try:
        return Chapter.objects.filter(pk=chapter_id).first()
    except (ValueError, TypeError):
        return None


def admin_story_list_payload() -> dict:
    stories = Story.objects.select_related("prerequisite_story").order_by("sort_order", "id")
    counts = {
        row["story"]: row["n"] for row in Chapter.objects.values("story").annotate(n=Count("id"))
    }
    return {
        "results": [story_payload(story, counts.get(story.id, 0)) for story in stories],
        "world_options": SUPPORTED_STORY_WORLD_SLUGS,
    }


def admin_story_detail_payload(story) -> dict:
    return story_payload(story, story.chapters.count())


def admin_chapter_list_payload(*, story_id=None) -> dict:
    chapters = Chapter.objects.all().order_by("sort_order", "number")
    if story_id:
        chapters = chapters.filter(story_id=story_id)
    return {"results": [chapter_payload(chapter) for chapter in chapters]}


def story_payload(story, chapter_count: int) -> dict:
    return {
        "id": story.id,
        "slug": story.slug,
        "title": story.title,
        "summary": story.summary,
        "price": story.price,
        "world_slug": story.world_slug,
        "difficulty": story.difficulty,
        "prerequisite_story": (
            {
                "id": story.prerequisite_story_id,
                "slug": story.prerequisite_story.slug,
                "title": story.prerequisite_story.title,
            }
            if story.prerequisite_story_id
            else None
        ),
        "sort_order": story.sort_order,
        "is_published": story.is_published,
        "chapter_count": chapter_count,
        "management_source": story.management_source,
    }


def chapter_payload(chapter) -> dict:
    return {
        "id": chapter.id,
        "story_id": chapter.story_id,
        "slug": chapter.slug,
        "number": chapter.number,
        "title": chapter.title,
        "description": chapter.description,
        "is_published": chapter.is_published,
        "is_playable": chapter.is_playable,
        "sort_order": chapter.sort_order,
        "battle_stage": chapter.battle_stage,
        "management_source": chapter.management_source,
    }
