from django.db.models import Q

from assets.models import TOWER_PIECE_CROWN
from authoring.selectors import content_payload
from tower_designs.models import (
    ARTIFACT_ROLE_NORMAL,
    SPIRE_STOREY_INDEX,
    STATUS_PUBLISHED,
    STOREY_TEMPLATE_INDEX,
    TowerDesign,
    TowerPieceInstance,
)


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
    all_pieces = list(
        design.pieces.select_related("piece_asset", "parent_instance").order_by("sort_order", "id")
    )
    pieces = canonical_design_pieces(all_pieces)
    visible_piece_ids = {piece.id for piece in pieces}
    layout_pieces = []
    content = {"adventures": {}, "challenges": {}, "tomes": {}}
    for piece in pieces:
        layout_pieces.append(
            {
                "instanceId": f"tower-{design.id}-piece-{piece.id}",
                "assetSlug": piece.piece_asset.slug,
                "pieceType": piece.piece_type,
                "storeyIndex": canonical_storey_index(piece),
                "parentInstanceId": (
                    f"tower-{design.id}-piece-{piece.parent_instance_id}"
                    if piece.parent_instance_id in visible_piece_ids
                    else None
                ),
                "transform": piece.transform,
                "config": piece.config,
            }
        )
    artifacts = []
    for placement in design.artifact_placements.select_related(
        "artifact_asset", "content_definition", "target_piece_instance"
    ).order_by("z_index", "id"):
        if placement.target_piece_instance_id not in visible_piece_ids:
            continue
        binding_payload = None
        if placement.role != ARTIFACT_ROLE_NORMAL and placement.content_definition_id:
            definition = placement.content_definition
            binding_payload = {"kind": definition.kind, "id": definition.id}
            bucket = {"adventure": "adventures", "challenge": "challenges", "tome": "tomes"}[
                definition.kind
            ]
            content[bucket][str(definition.id)] = content_payload(
                definition, include_definition=definition.kind == "tome"
            )
        artifacts.append(
            {
                "id": placement.id,
                "targetInstanceId": f"tower-{design.id}-piece-{placement.target_piece_instance_id}",
                "assetSlug": placement.artifact_asset.slug,
                "role": placement.role,
                "contentBinding": binding_payload,
                "x": placement.x,
                "y": placement.y,
                "scale": placement.scale,
                "width": placement.width,
                "height": placement.height,
                "rotation": placement.rotation,
                "anchor": placement.anchor,
                "zIndex": placement.z_index,
            }
        )
    return {
        "design": tower_design_payload(design, include_layout=False),
        "tower_layout": {"storeyId": None, "designId": design.id, "pieces": layout_pieces},
        "content": content,
        "artifacts": artifacts,
    }


def canonical_design_pieces(pieces: list[TowerPieceInstance]) -> list[TowerPieceInstance]:
    """Return the one editable spire plus the one repeatable storey template.

    Old designs may still contain several storey_index groups. Reading chooses a
    canonical view without deleting the hidden historical rows: the first crown
    by sort order and the explicit template group when present, otherwise the
    first non-crown group by sort order.
    """
    ordered = sorted(pieces, key=lambda piece: (piece.sort_order, piece.id))
    crown = next((piece for piece in ordered if piece.piece_type == TOWER_PIECE_CROWN), None)
    non_crown = [piece for piece in ordered if piece.piece_type != TOWER_PIECE_CROWN]
    template = [
        piece for piece in non_crown if piece.storey_index == STOREY_TEMPLATE_INDEX
    ]
    if not template and non_crown:
        first_template_index = non_crown[0].storey_index
        template = [piece for piece in non_crown if piece.storey_index == first_template_index]
    return ([crown] if crown else []) + template


def canonical_storey_index(piece: TowerPieceInstance) -> int:
    return SPIRE_STOREY_INDEX if piece.piece_type == TOWER_PIECE_CROWN else STOREY_TEMPLATE_INDEX
