from django.db.models import Q

from authoring.selectors import content_payload, visible_content_definitions
from marketplace.access import has_entitlement
from marketplace.models import ITEM_ASSET, ITEM_CONTENT, ITEM_TOWER_DESIGN, LISTING_ACTIVE, StoreListing
from towers.selectors import tower_design_payload, visible_tower_designs


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


def listing_payload(listing: StoreListing, *, user=None) -> dict:
    item = listing.item
    return {
        "id": listing.id,
        "item_kind": listing.item_kind,
        "item_id": listing.item_id,
        "seller_id": listing.seller_id,
        "price": listing.price,
        "status": listing.status,
        "owned": bool(item and getattr(item, "owner_id", None) == getattr(user, "id", None)),
        "entitled": bool(item and has_entitlement(user=user, item=item)) if user else False,
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
        }
    if item_kind == ITEM_CONTENT:
        return content_payload(item, include_definition=False)
    if item_kind == ITEM_TOWER_DESIGN:
        return tower_design_payload(item)
    return {}


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
