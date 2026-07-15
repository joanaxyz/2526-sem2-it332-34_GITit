from authoring.models import STATUS_PUBLISHED as CONTENT_PUBLISHED
from authoring.models import VISIBILITY_PUBLIC, VISIBILITY_STORE
from common.exceptions import Locked
from shop.catalog import KIND_COMPANION, is_default
from shop.models import Entitlement


def can_edit(user, item) -> bool:
    return bool(getattr(user, "is_staff", False) or getattr(item, "owner_id", None) == getattr(user, "id", None))


def can_view(user, item) -> bool:
    if can_edit(user, item):
        return True
    status = getattr(item, "status", None)
    visibility = getattr(item, "visibility", None)
    if status == CONTENT_PUBLISHED and visibility in {VISIBILITY_PUBLIC, VISIBILITY_STORE}:
        return True
    return bool(getattr(item, "is_published", False) and visibility in {VISIBILITY_PUBLIC, VISIBILITY_STORE, None})


def can_launch(user, content_definition) -> bool:
    """Content is no longer sold — published public content is launchable by all."""
    if can_edit(user, content_definition):
        return True
    return (
        content_definition.status == CONTENT_PUBLISHED
        and content_definition.visibility == VISIBILITY_PUBLIC
    )


def can_remix(user, item) -> bool:
    if not getattr(user, "is_authenticated", False):
        return False
    if can_edit(user, item):
        return True
    return bool(
        getattr(item, "status", None) == CONTENT_PUBLISHED
        and getattr(item, "visibility", None) == VISIBILITY_PUBLIC
    )


def owns_item(*, player, kind: str, slug: str) -> bool:
    """An item is owned if it is a free default or the player has an entitlement."""
    if is_default(kind, slug):
        return True
    if player is None:
        return False
    return Entitlement.objects.filter(player=player, kind=kind, slug=slug).exists()


def has_any_companion(player) -> bool:
    """No companion is free anymore, so ownership is entirely entitlement-based."""
    if player is None:
        return False
    return Entitlement.objects.filter(player=player, kind=KIND_COMPANION).exists()


def require_companion(player) -> None:
    """Raise 423 Locked if the player hasn't bought a companion yet.

    Called from adventure/challenge run-start so nobody can play without
    picking an adventurer first.
    """
    if not has_any_companion(player):
        raise Locked("Choose a companion in the Shop before starting an adventure.")
