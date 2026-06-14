from django.db.models import Q

from authoring.selectors import content_payload, visible_content_definitions
from marketplace.access import has_entitlement
from marketplace.models import (
    ITEM_ASSET,
    ITEM_CONTENT,
    ITEM_TOWER_DESIGN,
    LISTING_ACTIVE,
    Entitlement,
    StoreListing,
)
from tower_designs.selectors import tower_design_payload, visible_tower_designs


def active_listings(*, user):
    queryset = StoreListing.objects.filter(status=LISTING_ACTIVE).select_related(
        "asset",
        "content_definition",
        "tower_design",
        "seller",
    )
    if getattr(user, "is_staff", False):
        return queryset
    return queryset.filter(
        Q(asset__visibility="store", asset__is_published=True)
        | Q(content_definition__visibility="store", content_definition__status="published")
        | Q(tower_design__visibility="store", tower_design__status="published")
    )


def listing_payloads(listings: list[StoreListing], *, user=None) -> list[dict]:
    entitlement_lookup = _entitlement_lookup(user=user, listings=listings)
    return [listing_payload(listing, user=user, entitlement_lookup=entitlement_lookup) for listing in listings]


def listing_payload(listing: StoreListing, *, user=None, entitlement_lookup: set[tuple[str, int]] | None = None) -> dict:
    item = listing.item
    item_key = _listing_item_key(listing)
    if entitlement_lookup is not None:
        entitled = bool(item and item_key and item_key in entitlement_lookup)
    else:
        entitled = bool(item and has_entitlement(user=user, item=item)) if user else False
    return {
        "id": listing.id,
        "item_kind": listing.item_kind,
        "item_id": listing.item_id,
        "seller_id": listing.seller_id,
        "price": listing.price,
        "status": listing.status,
        "owned": bool(item and getattr(item, "owner_id", None) == getattr(user, "id", None)),
        "entitled": entitled,
        "item": item_payload(listing.item_kind, item),
        "created_at": listing.created_at,
        "updated_at": listing.updated_at,
    }


def item_payload(item_kind: str, item) -> dict:
    if item is None:
        return {}
    if item_kind == ITEM_ASSET:
        return {
            "id": item.id,
            "kind": item.kind,
            "slug": item.slug,
            "label": item.label,
            "visibility": item.visibility,
            "price": item.price,
            "tags": list(item.tags or []),
        }
    if item_kind == ITEM_CONTENT:
        return content_payload(item, include_definition=False)
    if item_kind == ITEM_TOWER_DESIGN:
        return tower_design_payload(item)
    return {}


def _listing_item_key(listing: StoreListing) -> tuple[str, int] | None:
    item_id = listing.item_id
    return (listing.item_kind, int(item_id)) if item_id else None


def _entitlement_lookup(*, user, listings: list[StoreListing]) -> set[tuple[str, int]]:
    if not getattr(user, "is_authenticated", False) or not listings:
        return set()

    asset_ids = [listing.item_id for listing in listings if listing.item_kind == ITEM_ASSET]
    content_ids = [listing.item_id for listing in listings if listing.item_kind == ITEM_CONTENT]
    tower_design_ids = [listing.item_id for listing in listings if listing.item_kind == ITEM_TOWER_DESIGN]
    conditions = []
    if asset_ids:
        conditions.append(Q(item_kind=ITEM_ASSET, asset_id__in=asset_ids))
    if content_ids:
        conditions.append(Q(item_kind=ITEM_CONTENT, content_definition_id__in=content_ids))
    if tower_design_ids:
        conditions.append(Q(item_kind=ITEM_TOWER_DESIGN, tower_design_id__in=tower_design_ids))
    if not conditions:
        return set()

    query = conditions[0]
    for condition in conditions[1:]:
        query |= condition

    lookup: set[tuple[str, int]] = set()
    for entitlement in Entitlement.objects.filter(user=user).filter(query):
        if entitlement.item_kind == ITEM_ASSET and entitlement.asset_id:
            lookup.add((ITEM_ASSET, entitlement.asset_id))
        elif entitlement.item_kind == ITEM_CONTENT and entitlement.content_definition_id:
            lookup.add((ITEM_CONTENT, entitlement.content_definition_id))
        elif entitlement.item_kind == ITEM_TOWER_DESIGN and entitlement.tower_design_id:
            lookup.add((ITEM_TOWER_DESIGN, entitlement.tower_design_id))
    return lookup


def gallery_assets(*, user):
    from assets.models import Asset

    queryset = Asset.objects.filter(is_published=True)
    if not getattr(user, "is_staff", False):
        queryset = queryset.filter(Q(visibility__in=["public", "store"]) | Q(owner=user))
    return queryset.order_by("kind", "slug")


def gallery_content(*, user):
    return visible_content_definitions(user=user).order_by("kind", "title")


def gallery_tower_designs(*, user):
    return visible_tower_designs(user=user).order_by("title", "id")
