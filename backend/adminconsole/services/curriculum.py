"""Validated, audited staff ownership of curriculum stories and chapters."""

from __future__ import annotations

from django.db import transaction
from rest_framework.exceptions import ValidationError

from adminconsole.curriculum_options import SUPPORTED_STORY_WORLD_SLUGS
from adminconsole.services.actions import record_admin_action
from curriculum.models import MANAGEMENT_SOURCE_ADMIN, Chapter, Story


def story_difficulty(value, *, default: str) -> str:
    difficulty = (value or default).strip().lower()
    allowed = {choice for choice, _ in Story.DIFFICULTY_CHOICES}
    if difficulty not in allowed:
        raise ValidationError({"difficulty": f"Choose one of: {', '.join(sorted(allowed))}."})
    return difficulty


def story_prerequisite(value, *, story: Story | None = None) -> Story | None:
    if value in (None, "", 0, "0"):
        return None
    try:
        prerequisite = Story.objects.get(pk=value)
    except (Story.DoesNotExist, TypeError, ValueError) as exc:
        raise ValidationError({"prerequisite_story": "Prerequisite story not found."}) from exc
    if story is not None:
        if prerequisite.pk == story.pk:
            raise ValidationError({"prerequisite_story": "A story cannot require itself."})
        cursor = prerequisite
        visited: set[int] = set()
        while cursor is not None and cursor.pk not in visited:
            if cursor.pk == story.pk:
                raise ValidationError(
                    {"prerequisite_story": "Story prerequisites cannot form a cycle."}
                )
            visited.add(cursor.pk)
            cursor = cursor.prerequisite_story
    return prerequisite


def _story_snapshot(story: Story) -> dict:
    return {
        "slug": story.slug,
        "title": story.title,
        "summary": story.summary,
        "price": story.price,
        "world_slug": story.world_slug,
        "difficulty": story.difficulty,
        "prerequisite_story": story.prerequisite_story_id,
        "sort_order": story.sort_order,
        "is_published": story.is_published,
        "management_source": story.management_source,
    }


def _chapter_snapshot(chapter: Chapter) -> dict:
    return {
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


def _validate_world_slug(value: str) -> None:
    if value not in SUPPORTED_STORY_WORLD_SLUGS:
        allowed = ", ".join(SUPPORTED_STORY_WORLD_SLUGS)
        raise ValidationError({"world_slug": f"Choose one of: {allowed}."})


def _validate_chapter_state(*, is_published: bool, is_playable: bool) -> None:
    if is_playable and not is_published:
        raise ValidationError(
            {"is_playable": "A playable chapter must also be published."}
        )


class AdminCurriculumService:
    """Own complete Story/Chapter rows once staff mutate them."""

    @transaction.atomic
    def create_story(self, *, actor, data: dict) -> Story:
        if Story.objects.filter(slug=data["slug"]).exists():
            raise ValidationError({"slug": "A story with this slug already exists."})
        _validate_world_slug(data["world_slug"])
        if data["is_published"]:
            raise ValidationError(
                {"is_published": "Create the story as a draft, add a published chapter, then publish it."}
            )
        story = Story.objects.create(
            slug=data["slug"],
            title=data["title"],
            summary=data["summary"],
            price=data["price"],
            world_slug=data["world_slug"],
            difficulty=data["difficulty"],
            prerequisite_story=story_prerequisite(data["prerequisite_story"]),
            sort_order=data.get("sort_order", Story.objects.count() + 1),
            is_published=False,
            management_source=MANAGEMENT_SOURCE_ADMIN,
        )
        record_admin_action(
            actor=actor,
            action="story.create",
            target=story,
            after=_story_snapshot(story),
        )
        return story

    @transaction.atomic
    def update_story(self, *, actor, story: Story, data: dict) -> Story:
        story = Story.objects.select_for_update().get(pk=story.pk)
        before = _story_snapshot(story)
        if "world_slug" in data:
            _validate_world_slug(data["world_slug"])
        if data.get("is_published") and not story.chapters.filter(is_published=True).exists():
            raise ValidationError(
                {"is_published": "Publish at least one chapter before publishing this story."}
            )

        for field in (
            "title",
            "summary",
            "price",
            "world_slug",
            "difficulty",
            "sort_order",
            "is_published",
        ):
            if field in data:
                setattr(story, field, data[field])
        if "prerequisite_story" in data:
            story.prerequisite_story = story_prerequisite(
                data["prerequisite_story"],
                story=story,
            )
        story.management_source = MANAGEMENT_SOURCE_ADMIN
        story.save()
        record_admin_action(
            actor=actor,
            action="story.update",
            target=story,
            before=before,
            after=_story_snapshot(story),
        )
        return story

    @transaction.atomic
    def create_chapter(self, *, actor, data: dict) -> Chapter:
        story = Story.objects.filter(pk=data["story_id"]).first()
        if story is None:
            raise ValidationError({"story_id": "Story not found."})
        if Chapter.objects.filter(slug=data["slug"]).exists():
            raise ValidationError({"slug": "A chapter with this slug already exists."})
        if Chapter.objects.filter(story=story, number=data["number"]).exists():
            raise ValidationError(
                {"number": "This story already has a chapter with that number."}
            )
        _validate_chapter_state(
            is_published=data["is_published"],
            is_playable=data["is_playable"],
        )
        chapter = Chapter.objects.create(
            story=story,
            slug=data["slug"],
            number=data["number"],
            title=data["title"],
            description=data["description"],
            is_published=data["is_published"],
            is_playable=data["is_playable"],
            sort_order=data.get("sort_order", story.chapters.count() + 1),
            battle_stage=data["battle_stage"],
            management_source=MANAGEMENT_SOURCE_ADMIN,
        )
        record_admin_action(
            actor=actor,
            action="chapter.create",
            target=chapter,
            after=_chapter_snapshot(chapter),
        )
        return chapter

    @transaction.atomic
    def update_chapter(self, *, actor, chapter: Chapter, data: dict) -> Chapter:
        chapter = Chapter.objects.select_for_update().get(pk=chapter.pk)
        before = _chapter_snapshot(chapter)
        next_published = data.get("is_published", chapter.is_published)
        next_playable = data.get("is_playable", chapter.is_playable)
        _validate_chapter_state(
            is_published=next_published,
            is_playable=next_playable,
        )
        if (
            chapter.story.is_published
            and chapter.is_published
            and not next_published
            and not Chapter.objects.filter(
                story=chapter.story,
                is_published=True,
            )
            .exclude(pk=chapter.pk)
            .exists()
        ):
            raise ValidationError(
                {
                    "is_published": (
                        "A published story must retain at least one published chapter."
                    )
                }
            )
        next_number = data.get("number", chapter.number)
        if (
            Chapter.objects.filter(story=chapter.story, number=next_number)
            .exclude(pk=chapter.pk)
            .exists()
        ):
            raise ValidationError(
                {"number": "This story already has a chapter with that number."}
            )
        for field in (
            "number",
            "title",
            "description",
            "is_published",
            "is_playable",
            "sort_order",
            "battle_stage",
        ):
            if field in data:
                setattr(chapter, field, data[field])
        chapter.management_source = MANAGEMENT_SOURCE_ADMIN
        chapter.save()
        record_admin_action(
            actor=actor,
            action="chapter.update",
            target=chapter,
            before=before,
            after=_chapter_snapshot(chapter),
        )
        return chapter
