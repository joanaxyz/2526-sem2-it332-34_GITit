"""Read-model builders for stories and chapters in the admin console."""

from __future__ import annotations


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
    }
