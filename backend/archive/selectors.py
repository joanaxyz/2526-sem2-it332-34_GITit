from django.db.models import Q

from authoring.selectors import content_payload
from archive.models import (
    RELIC_KIND_NORMAL,
    STATUS_PUBLISHED,
    ArchiveDesign,
    RelicPlacement,
)


def visible_archive_designs(*, user):
    if getattr(user, "is_staff", False):
        return ArchiveDesign.objects.all()
    public_filter = Q(status=STATUS_PUBLISHED, visibility__in=["public", "store"])
    if getattr(user, "is_authenticated", False):
        return ArchiveDesign.objects.filter(public_filter | Q(owner=user))
    return ArchiveDesign.objects.filter(public_filter)


def archive_design_payload(design: ArchiveDesign, *, include_layout: bool = False) -> dict:
    payload = {
        "id": design.id,
        "owner_id": design.owner_id,
        "source_design_id": design.source_design_id,
        "visibility": design.visibility,
        "status": design.status,
        "origin": design.origin,
        "slug": design.slug,
        "title": design.title,
        "summary": design.summary,
        "is_active": design.is_active,
        "created_at": design.created_at,
        "updated_at": design.updated_at,
    }
    if include_layout:
        payload.update(archive_design_overview(design=design))
    return payload


def relic_placement_payload(placement: RelicPlacement) -> dict:
    relic_detail = getattr(placement.relic_asset, "relic", None)
    interactive = placement.interactive_viewbox or (
        getattr(relic_detail, "interactive_viewbox", None) or {}
    )
    landing = placement.landing_viewbox or (
        getattr(relic_detail, "landing_viewbox", None) or {}
    )
    return {
        "id": placement.id,
        "assetSlug": placement.relic_asset.slug,
        "kind": placement.kind,
        "chapterIndex": placement.chapter_index,
        "x": placement.x,
        "y": placement.y,
        "scale": placement.scale,
        "width": placement.width,
        "height": placement.height,
        "rotation": placement.rotation,
        "zIndex": placement.z_index,
        "interactiveViewbox": interactive,
        "landingViewbox": landing,
    }


def archive_design_overview(*, design: ArchiveDesign) -> dict:
    relics = []
    content = {"adventures": {}, "challenges": {}, "tomes": {}}
    placements = design.relics.select_related(
        "relic_asset", "relic_asset__relic", "content_definition"
    ).order_by("chapter_index", "z_index", "id")
    for placement in placements:
        payload = relic_placement_payload(placement)
        binding_payload = None
        if placement.kind != RELIC_KIND_NORMAL and placement.content_definition_id:
            definition = placement.content_definition
            binding_payload = {"kind": definition.kind, "id": definition.id}
            bucket = {"adventure": "adventures", "challenge": "challenges", "tome": "tomes"}[
                definition.kind
            ]
            content[bucket][str(definition.id)] = content_payload(
                definition, include_definition=definition.kind == "tome"
            )
        payload["contentBinding"] = binding_payload
        relics.append(payload)
    return {
        "design": archive_design_payload(design, include_layout=False),
        "relic_layout": {"designId": design.id, "relics": relics},
        "content": content,
    }
