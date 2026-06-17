from django.db.models import Q

from authoring.models import (
    STATUS_PUBLISHED,
    VISIBILITY_PUBLIC,
    VISIBILITY_STORE,
    AuthoringChapter,
    ContentDefinition,
)


def chapter_payload(chapter: AuthoringChapter) -> dict:
    return {
        "id": chapter.id,
        "owner_id": chapter.owner_id,
        "slug": chapter.slug,
        "title": chapter.title,
        "summary": chapter.summary,
        "sort_order": chapter.sort_order,
        "chest_rewards": chapter.chest_rewards,
        "mob_roster": chapter.mob_roster,
        "boss_roster": chapter.boss_roster,
        "pass_bar_fraction": chapter.pass_bar_fraction,
        "battle_stage": chapter.battle_stage,
        "created_at": chapter.created_at,
        "updated_at": chapter.updated_at,
    }


def visible_content_definitions(*, user):
    if getattr(user, "is_staff", False):
        return ContentDefinition.objects.all()
    public_filter = Q(status=STATUS_PUBLISHED, visibility__in=[VISIBILITY_PUBLIC, VISIBILITY_STORE])
    if getattr(user, "is_authenticated", False):
        return ContentDefinition.objects.filter(public_filter | Q(owner=user))
    return ContentDefinition.objects.filter(public_filter)


def content_payload(content: ContentDefinition, *, include_definition: bool = True) -> dict:
    payload = {
        "id": content.id,
        "kind": content.kind,
        "owner_id": content.owner_id,
        "chapter_id": content.chapter_id,
        "source_definition_id": content.source_definition_id,
        "visibility": content.visibility,
        "status": content.status,
        "slug": content.slug,
        "title": content.title,
        "summary": content.summary,
        "tags": content.tags,
        "command_family": content.command_family,
        "difficulty": content.difficulty,
        "validation_errors": content.validation_errors,
        "published_at": content.published_at,
        "created_at": content.created_at,
        "updated_at": content.updated_at,
    }
    if include_definition:
        payload["definition"] = content.definition
    return payload
