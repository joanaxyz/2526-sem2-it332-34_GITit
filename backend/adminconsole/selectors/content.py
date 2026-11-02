"""Read-model builders for official and moderated content definitions."""

from __future__ import annotations

from django.db.models import Q

from authoring.models import STATUS_PUBLISHED as CONTENT_PUBLISHED
from authoring.models import ContentDefinition


def admin_official_content_list_payload(*, kind=None, limit: int = 200) -> dict:
    limit = min(max(limit, 0), 200)
    contents = ContentDefinition.objects.filter(
        Q(owner__isnull=True) | Q(owner__is_staff=True),
        official_chapter__isnull=False,
    ).select_related("official_chapter")
    if kind:
        contents = contents.filter(kind=kind)
    contents = contents.order_by("-updated_at")[:limit]
    return {"results": [content_payload(content) for content in contents]}


def admin_moderation_list_payload(*, limit: int = 200) -> dict:
    limit = min(max(limit, 0), 200)
    contents = (
        ContentDefinition.objects.filter(
            visibility="public",
            status=CONTENT_PUBLISHED,
            owner__is_staff=False,
        )
        .select_related("owner")
        .order_by("-updated_at")[:limit]
    )
    return {
        "content": [
            {
                "id": content.id,
                "kind": content.kind,
                "title": content.title,
                "owner": content.owner.username if content.owner else None,
                "updated_at": content.updated_at,
            }
            for content in contents
        ]
    }


def find_admin_moderation_content(item_id):
    try:
        return (
            ContentDefinition.objects.filter(
                id=item_id,
                visibility="public",
                status=CONTENT_PUBLISHED,
                owner__is_staff=False,
            )
            .select_related("owner")
            .first()
        )
    except (ValueError, TypeError):
        return None


def content_payload(content) -> dict:
    return {
        "id": content.id,
        "kind": content.kind,
        "slug": content.slug,
        "title": content.title,
        "status": content.status,
        "visibility": content.visibility,
        "official_chapter": (
            {
                "id": content.official_chapter_id,
                "title": content.official_chapter.title,
            }
            if content.official_chapter_id
            else None
        ),
        "updated_at": content.updated_at,
    }
