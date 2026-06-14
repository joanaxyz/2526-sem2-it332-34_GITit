from __future__ import annotations

import copy

from django.db import transaction
from rest_framework.exceptions import PermissionDenied, ValidationError

from assets.models import Asset
from authoring.models import STATUS_PUBLISHED as CONTENT_STATUS_PUBLISHED, ContentDefinition
from towers.models import (
    STATUS_PUBLISHED,
    ArtifactPlacement,
    TowerContentBinding,
    TowerDesign,
    TowerPieceInstance,
)


class TowerDesignService:
    def assert_owner(self, *, user, design: TowerDesign) -> None:
        if not getattr(user, "is_staff", False) and design.owner_id != getattr(user, "id", None):
            raise PermissionDenied("You do not own this tower design.")

    @transaction.atomic
    def create(self, *, user, data: dict) -> TowerDesign:
        design = TowerDesign.objects.create(
            owner=user,
            slug=data["slug"],
            title=data["title"],
            summary=data.get("summary", ""),
            visibility=data.get("visibility", "private"),
        )
        return design

    @transaction.atomic
    def update(self, *, user, design: TowerDesign, data: dict) -> TowerDesign:
        self.assert_owner(user=user, design=design)
        for field in ("slug", "title", "summary", "visibility"):
            if field in data:
                setattr(design, field, data[field])
        design.full_clean()
        design.save()
        return design

    @transaction.atomic
    def set_active(self, *, user, design: TowerDesign) -> TowerDesign:
        self.assert_owner(user=user, design=design)
        TowerDesign.objects.filter(owner=user, is_active=True).exclude(id=design.id).update(is_active=False)
        design.is_active = True
        design.save(update_fields=["is_active", "updated_at"])
        return design

    @transaction.atomic
    def publish(self, *, user, design: TowerDesign) -> TowerDesign:
        self.assert_owner(user=user, design=design)
        errors = self.publish_errors(design=design)
        if errors:
            raise ValidationError({"validation_errors": errors})
        design.status = STATUS_PUBLISHED
        design.save(update_fields=["status", "updated_at"])
        return design

    def publish_errors(self, *, design: TowerDesign) -> list[dict[str, str]]:
        errors: list[dict[str, str]] = []
        for piece in design.pieces.prefetch_related("content_binding__content_definition"):
            if piece.piece_type not in {"adventure_section", "challenge_section", "tome"}:
                continue
            binding = getattr(piece, "content_binding", None)
            if not binding:
                errors.append({"field": f"piece:{piece.id}", "message": "Interactive piece needs a content binding."})
                continue
            if binding.content_definition.status != CONTENT_STATUS_PUBLISHED:
                errors.append({"field": f"piece:{piece.id}", "message": "Bound content must be published."})
        return errors

    @transaction.atomic
    def add_piece(self, *, user, design: TowerDesign, data: dict) -> TowerPieceInstance:
        self.assert_owner(user=user, design=design)
        asset = Asset.objects.get(id=data["piece_asset_id"])
        piece = TowerPieceInstance.objects.create(
            tower_design=design,
            piece_asset=asset,
            piece_type=data.get("piece_type") or asset.tower_piece.piece_type,
            sort_order=data.get("sort_order", design.pieces.count()),
            parent_instance_id=data.get("parent_instance_id"),
            transform=data.get("transform") or {},
            config=data.get("config") or {},
        )
        return piece

    @transaction.atomic
    def bind_content(self, *, user, design: TowerDesign, data: dict) -> TowerContentBinding:
        self.assert_owner(user=user, design=design)
        piece = design.pieces.get(id=data["piece_instance_id"])
        content = ContentDefinition.objects.get(id=data["content_definition_id"])
        binding, _created = TowerContentBinding.objects.update_or_create(
            piece_instance=piece,
            defaults={"content_definition": content},
        )
        return binding

    @transaction.atomic
    def place_artifact(self, *, user, design: TowerDesign, data: dict) -> ArtifactPlacement:
        self.assert_owner(user=user, design=design)
        placement = ArtifactPlacement.objects.create(
            tower_design=design,
            target_piece_instance=design.pieces.get(id=data["target_piece_instance_id"]),
            artifact_asset=Asset.objects.get(id=data["artifact_asset_id"]),
            x=data.get("x", 0),
            y=data.get("y", 0),
            scale=data.get("scale", 1),
            rotation=data.get("rotation", 0),
            anchor=data.get("anchor", ""),
            z_index=data.get("z_index", 0),
        )
        return placement

    @transaction.atomic
    def remix(self, *, user, design: TowerDesign) -> TowerDesign:
        clone = TowerDesign.objects.create(
            owner=user,
            source_design=design,
            visibility="private",
            status="draft",
            slug=_next_remix_slug(user=user, source=design),
            title=f"{design.title} Remix",
            summary=design.summary,
        )
        piece_map = {}
        for piece in design.pieces.order_by("sort_order", "id"):
            copied = TowerPieceInstance.objects.create(
                tower_design=clone,
                piece_asset=piece.piece_asset,
                piece_type=piece.piece_type,
                sort_order=piece.sort_order,
                transform=copy.deepcopy(piece.transform),
                config=copy.deepcopy(piece.config),
            )
            piece_map[piece.id] = copied
            binding = getattr(piece, "content_binding", None)
            if binding:
                TowerContentBinding.objects.create(piece_instance=copied, content_definition=binding.content_definition)
        for placement in design.artifact_placements.order_by("id"):
            ArtifactPlacement.objects.create(
                tower_design=clone,
                target_piece_instance=piece_map[placement.target_piece_instance_id],
                artifact_asset=placement.artifact_asset,
                x=placement.x,
                y=placement.y,
                scale=placement.scale,
                rotation=placement.rotation,
                anchor=placement.anchor,
                z_index=placement.z_index,
            )
        return clone


def _next_remix_slug(*, user, source: TowerDesign) -> str:
    base = f"{source.slug}-remix"
    slug = base
    index = 2
    while TowerDesign.objects.filter(owner=user, slug=slug).exists():
        slug = f"{base}-{index}"
        index += 1
    return slug
