from django.db import models

from shop.catalog import DEFAULTS, KIND_COMPANION, KIND_STORY, is_default, listings
from shop.models import Entitlement, PlayerLoadout


def _owned_set(player) -> set[tuple[str, str]]:
    if player is None:
        return set()
    return {
        (entitlement.kind, entitlement.slug)
        for entitlement in Entitlement.objects.filter(player=player).only("kind", "slug")
    }


def player_loadout(player) -> dict[str, str | None]:
    """The player's equipped companion slug.

    Companion has no free default: until the player owns and equips one, it's
    ``None`` (nothing to play with yet).
    """
    record = PlayerLoadout.objects.filter(player=player).first() if player is not None else None
    return {
        "companion": record.active_companion_slug if record else DEFAULTS[KIND_COMPANION],
    }


def _story_access(story_slug: str) -> dict | None:
    from curriculum.models import Story

    story = (
        Story.objects.filter(slug=story_slug, is_published=True)
        .annotate(chapter_count=models.Count("chapters", filter=models.Q(chapters__is_published=True)))
        .order_by("sort_order", "id")
        .first()
    )
    if story is None:
        return None
    return {
        "slug": story.slug,
        "title": story.title,
        "chapter_count": story.chapter_count,
        "world_slug": story.world_slug,
        "difficulty": story.difficulty,
        "prerequisite_story": story.prerequisite_story.slug if story.prerequisite_story_id else None,
    }


def shop_payload(*, player) -> dict:
    """The shop catalog: stories + companions, flagged owned for this player."""
    owned = _owned_set(player)
    loadout = player_loadout(player)
    items = [
        {
            **item,
            "owned": is_default(item["kind"], item["slug"]) or (item["kind"], item["slug"]) in owned,
            "active": item["kind"] == KIND_COMPANION and loadout["companion"] == item["slug"],
            **({"unlocks_story": _story_access(item["slug"])} if item["kind"] == KIND_STORY else {}),
        }
        for item in listings()
    ]
    return {
        "items": items,
        "active_companion": loadout["companion"],
    }
