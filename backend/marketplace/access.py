from authoring.models import STATUS_PUBLISHED as CONTENT_PUBLISHED
from authoring.models import VISIBILITY_PUBLIC, VISIBILITY_STORE
from marketplace.models import (
    ITEM_ASSET,
    ITEM_CONTENT,
    ITEM_TOWER_DESIGN,
    LISTING_ACTIVE,
    Entitlement,
    StoreListing,
)
from tower_designs.models import STATUS_PUBLISHED as TOWER_PUBLISHED


def can_edit(user, item) -> bool:
    return bool(getattr(user, "is_staff", False) or getattr(item, "owner_id", None) == getattr(user, "id", None))


def can_view(user, item) -> bool:
    if can_edit(user, item):
        return True
    status = getattr(item, "status", None)
    visibility = getattr(item, "visibility", None)
    if status in {CONTENT_PUBLISHED, TOWER_PUBLISHED} and visibility in {VISIBILITY_PUBLIC, VISIBILITY_STORE}:
        return True
    if getattr(item, "is_published", False) and visibility in {VISIBILITY_PUBLIC, VISIBILITY_STORE, None}:
        return True
    return has_entitlement(user=user, item=item)


def can_launch(user, content_definition) -> bool:
    if can_edit(user, content_definition):
        return True
    if (
        content_definition.status == CONTENT_PUBLISHED
        and content_definition.visibility == VISIBILITY_PUBLIC
    ):
        return True
    return has_entitlement(user=user, item=content_definition) or has_free_listing(item=content_definition)


def can_use_asset(user, asset) -> bool:
    if can_edit(user, asset):
        return True
    if asset.is_published and asset.visibility == VISIBILITY_PUBLIC:
        return True
    return has_entitlement(user=user, item=asset) or has_free_listing(item=asset)


def can_use_tower_design(user, tower_design) -> bool:
    if can_edit(user, tower_design):
        return True
    if tower_design.status == TOWER_PUBLISHED and tower_design.visibility == VISIBILITY_PUBLIC:
        return True
    return has_entitlement(user=user, item=tower_design) or has_free_listing(item=tower_design)


def can_remix(user, item) -> bool:
    if not getattr(user, "is_authenticated", False):
        return False
    if can_edit(user, item):
        return True
    visibility = getattr(item, "visibility", None)
    status = getattr(item, "status", None)
    if getattr(item, "is_published", False) and visibility == VISIBILITY_PUBLIC:
        return True
    if status in {CONTENT_PUBLISHED, TOWER_PUBLISHED} and visibility == VISIBILITY_PUBLIC:
        return True
    return has_entitlement(user=user, item=item) or has_free_listing(item=item)


def has_entitlement(*, user, item) -> bool:
    if not getattr(user, "is_authenticated", False):
        return False
    item_kind, field = _item_kind_and_field(item)
    return Entitlement.objects.filter(user=user, item_kind=item_kind, **{field: item}).exists()


def has_free_listing(*, item) -> bool:
    item_kind, field = _item_kind_and_field(item)
    return StoreListing.objects.filter(
        item_kind=item_kind,
        status=LISTING_ACTIVE,
        price=0,
        **{field: item},
    ).exists()


def entitlement_kwargs_for(item) -> dict:
    item_kind, field = _item_kind_and_field(item)
    return {"item_kind": item_kind, field: item}


def _item_kind_and_field(item) -> tuple[str, str]:
    app_label = item._meta.app_label
    model_name = item._meta.model_name
    if app_label == "assets" and model_name == "asset":
        return ITEM_ASSET, "asset"
    if app_label == "authoring" and model_name == "contentdefinition":
        return ITEM_CONTENT, "content_definition"
    if app_label == "towers" and model_name == "towerdesign":
        return ITEM_TOWER_DESIGN, "tower_design"
    raise TypeError(f"Unsupported marketplace item: {item!r}")
