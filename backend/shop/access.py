from common.exceptions import Locked
from shop.catalog import KIND_COMPANION
from shop.models import Entitlement


def owns_item(*, player, kind: str, slug: str) -> bool:
    """Nothing in the shop is free, so ownership is entirely entitlement-based."""
    if player is None:
        return False
    return Entitlement.objects.filter(player=player, kind=kind, slug=slug).exists()


def has_any_companion(player) -> bool:
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
