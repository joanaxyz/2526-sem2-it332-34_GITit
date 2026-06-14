from django.db.models import Q

from authoring.selectors import content_payload
from tower_designs.models import STATUS_PUBLISHED, TowerDesign


def visible_tower_designs(*, user):
    if getattr(user, "is_staff", False):
        return TowerDesign.objects.all()
    public_filter = Q(status=STATUS_PUBLISHED, visibility__in=["public", "store"])
    if getattr(user, "is_authenticated", False):
        return TowerDesign.objects.filter(public_filter | Q(owner=user))
    return TowerDesign.objects.filter(public_filter)


def tower_design_payload(design: TowerDesign, *, include_layout: bool = False) -> dict:
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
        payload.update(tower_design_overview(design=design))
    return payload


def tower_design_overview(*, design: TowerDesign) -> dict:
    pieces = list(
        design.pieces.select_related("piece_asset", "content_binding__content_definition").order_by("sort_order", "id")
    )
    layout_pieces = []
    content = {"adventures": {}, "challenges": {}, "tomes": {}}
    for piece in pieces:
        binding = getattr(piece, "content_binding", None)
        binding_payload = None
        if binding:
            definition = binding.content_definition
            binding_payload = {"kind": definition.kind, "id": definition.id}
            bucket = {"adventure": "adventures", "challenge": "challenges", "tome": "tomes"}[definition.kind]
            content[bucket][str(definition.id)] = content_payload(definition, include_definition=definition.kind == "tome")
        layout_pieces.append(
            {
                "instanceId": f"tower-{design.id}-piece-{piece.id}",
                "assetSlug": piece.piece_asset.slug,
                "pieceType": piece.piece_type,
                "storeyIndex": piece.storey_index,
                "contentBinding": binding_payload,
                "transform": piece.transform,
                "config": piece.config,
            }
        )
    artifacts = [
        {
            "id": placement.id,
            "targetInstanceId": f"tower-{design.id}-piece-{placement.target_piece_instance_id}",
            "assetSlug": placement.artifact_asset.slug,
            "x": placement.x,
            "y": placement.y,
            "scale": placement.scale,
            "rotation": placement.rotation,
            "anchor": placement.anchor,
            "zIndex": placement.z_index,
        }
        for placement in design.artifact_placements.select_related("artifact_asset").order_by("z_index", "id")
    ]
    return {
        "design": tower_design_payload(design, include_layout=False),
        "tower_layout": {"storeyId": None, "designId": design.id, "pieces": layout_pieces},
        "content": content,
        "artifacts": artifacts,
    }
