from shop.catalog import KIND_COMPANION, listings
from shop.models import Entitlement, PlayerLoadout


def _owned_slugs(player) -> set[tuple[str, str]]:
    if player is None:
        return set()
    return {
        (entitlement.kind, entitlement.slug)
        for entitlement in Entitlement.objects.filter(player=player).only("kind", "slug")
    }


def player_loadout(player) -> dict[str, str | None]:
    """The player's equipped companion slug.

    There is no free default: until the player owns and equips one, it's
    ``None`` (nothing to play with yet).
    """
    record = PlayerLoadout.objects.filter(player=player).first() if player is not None else None
    return {"companion": record.active_companion_slug if record else None}


def shop_payload(*, player) -> dict:
    """The shop catalog - companions, flagged owned/active for this player."""
    from adminconsole.flags import feature_enabled

    owned = _owned_slugs(player)
    loadout = player_loadout(player)
    items = [
        {
            **item,
            "owned": (item["kind"], item["slug"]) in owned,
            "active": item["kind"] == KIND_COMPANION and loadout["companion"] == item["slug"],
        }
        for item in listings()
    ]
    return {
        "items": items,
        "active_companion": loadout["companion"],
        "purchases_enabled": feature_enabled("shop-purchases"),
    }
