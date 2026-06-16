from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from assets.models import KIND_TOWER_PIECE, Asset
from marketplace.access import can_remix
from tower_designs.models import (
    ORIGIN_PERSONAL,
    STATUS_PUBLISHED,
    ArtifactPlacement,
    TowerContentBinding,
    TowerDesign,
    TowerPieceInstance,
)
from tower_designs.selectors import (
    tower_design_overview,
    tower_design_payload,
    visible_tower_designs,
)
from tower_designs.services import TowerDesignService


class TowerDesignMineAPIView(APIView):
    def get(self, request):
        designs = TowerDesign.objects.filter(owner=request.user).order_by("-is_active", "-updated_at", "-id")
        return Response({"results": [tower_design_payload(design) for design in designs]})


class TowerDesignListCreateAPIView(APIView):
    def post(self, request):
        # Idempotent: "Raise your Tower" returns the existing personal tower
        # instead of erroring on the one-per-user cap.
        design = TowerDesignService().get_or_create_personal(user=request.user, data=request.data)
        return Response(tower_design_payload(design), status=201)


class TowerDesignDetailAPIView(APIView):
    def get(self, request, design_id: int):
        design = visible_tower_designs(user=request.user).get(id=design_id)
        return Response(tower_design_payload(design, include_layout=True))

    def patch(self, request, design_id: int):
        design = TowerDesign.objects.get(id=design_id)
        design = TowerDesignService().update(user=request.user, design=design, data=request.data)
        return Response(tower_design_payload(design))


class TowerDesignSetActiveAPIView(APIView):
    def post(self, request, design_id: int):
        design = TowerDesign.objects.get(id=design_id)
        design = TowerDesignService().set_active(user=request.user, design=design)
        return Response(tower_design_payload(design))


class TowerDesignPublishAPIView(APIView):
    def post(self, request, design_id: int):
        design = TowerDesign.objects.get(id=design_id)
        design = TowerDesignService().publish(user=request.user, design=design)
        return Response(tower_design_payload(design))


class TowerDesignOfficialForkAPIView(APIView):
    """Get-or-create the user's private fork of the official tower."""

    def post(self, request):
        design = TowerDesignService().get_or_create_official_fork(user=request.user)
        return Response(tower_design_payload(design, include_layout=True), status=201)


class TowerDesignShareAPIView(APIView):
    """Publish + make a personal tower public, returning its shareable identity."""

    def post(self, request, design_id: int):
        design = TowerDesign.objects.get(id=design_id)
        design = TowerDesignService().share(user=request.user, design=design)
        payload = tower_design_payload(design)
        payload["share_path"] = f"/tower/shared/{design.id}"
        return Response(payload)


class SharedTowerOverviewAPIView(APIView):
    """Public, read-only overview of a shared personal tower (no auth)."""

    permission_classes = [AllowAny]

    def get(self, request, design_id: int):
        try:
            design = TowerDesign.objects.get(id=design_id)
        except TowerDesign.DoesNotExist as exc:
            raise NotFound("Tower not found.") from exc
        is_public = design.status == STATUS_PUBLISHED and design.visibility in {"public", "store"}
        if not is_public or design.origin != ORIGIN_PERSONAL:
            raise NotFound("Tower not found.")
        return Response(tower_design_overview(design=design))


class TowerDesignRemixAPIView(APIView):
    def post(self, request, design_id: int):
        design = visible_tower_designs(user=request.user).get(id=design_id)
        if not can_remix(request.user, design):
            raise PermissionDenied("You cannot remix this tower design.")
        clone = TowerDesignService().remix(user=request.user, design=design)
        return Response(tower_design_payload(clone, include_layout=True), status=201)


class TowerDesignLayoutAPIView(APIView):
    def get(self, request, design_id: int):
        design = visible_tower_designs(user=request.user).get(id=design_id)
        return Response(tower_design_overview(design=design))


class MyTowerOverviewAPIView(APIView):
    def get(self, request):
        design = (
            TowerDesign.objects.filter(owner=request.user, is_active=True)
            .order_by("-updated_at", "-id")
            .first()
        )
        if design is None:
            return Response({"detail": "No active tower design."}, status=404)
        return Response(tower_design_overview(design=design))


class TowerStoreyCreateAPIView(APIView):
    """Append a new storey (floor) of pieces to the design."""

    def post(self, request, design_id: int):
        design = TowerDesign.objects.get(id=design_id)
        storey_index = TowerDesignService().add_storey(user=request.user, design=design)
        payload = tower_design_overview(design=design)
        payload["added_storey_index"] = storey_index
        return Response(payload, status=201)


class TowerPieceListCreateAPIView(APIView):
    def post(self, request, design_id: int):
        design = TowerDesign.objects.get(id=design_id)
        piece = TowerDesignService().add_piece(user=request.user, design=design, data=request.data)
        return Response(_piece_payload(piece), status=201)


class TowerPieceDetailAPIView(APIView):
    def patch(self, request, design_id: int, piece_id: int):
        design = TowerDesign.objects.get(id=design_id)
        TowerDesignService().assert_owner(user=request.user, design=design)
        piece = design.pieces.get(id=piece_id)
        # Swapping which asset fills a structural slot keeps the slot's piece_type.
        if "piece_asset_id" in request.data:
            asset = Asset.objects.get(id=request.data["piece_asset_id"])
            if asset.kind != KIND_TOWER_PIECE:
                raise ValidationError({"piece_asset_id": "Asset must be a tower piece."})
            piece.piece_asset = asset
        for field in ("sort_order", "transform", "config"):
            if field in request.data:
                setattr(piece, field, request.data[field])
        piece.full_clean()
        piece.save()
        return Response(_piece_payload(piece))

    def delete(self, request, design_id: int, piece_id: int):
        design = TowerDesign.objects.get(id=design_id)
        TowerDesignService().assert_owner(user=request.user, design=design)
        design.pieces.get(id=piece_id).delete()
        return Response(status=204)


class TowerBindingCreateAPIView(APIView):
    def post(self, request, design_id: int):
        design = TowerDesign.objects.get(id=design_id)
        binding = TowerDesignService().bind_content(user=request.user, design=design, data=request.data)
        return Response(_binding_payload(binding), status=201)


class TowerBindingDetailAPIView(APIView):
    def delete(self, request, design_id: int, binding_id: int):
        design = TowerDesign.objects.get(id=design_id)
        TowerDesignService().assert_owner(user=request.user, design=design)
        TowerContentBinding.objects.get(id=binding_id, piece_instance__tower_design=design).delete()
        return Response(status=204)


class ArtifactPlacementCreateAPIView(APIView):
    def post(self, request, design_id: int):
        design = TowerDesign.objects.get(id=design_id)
        placement = TowerDesignService().place_artifact(user=request.user, design=design, data=request.data)
        return Response(_artifact_payload(placement), status=201)


class ArtifactPlacementDetailAPIView(APIView):
    def patch(self, request, design_id: int, placement_id: int):
        design = TowerDesign.objects.get(id=design_id)
        TowerDesignService().assert_owner(user=request.user, design=design)
        placement = ArtifactPlacement.objects.get(id=placement_id, tower_design=design)
        for field in (
            "target_piece_instance_id",
            "x",
            "y",
            "scale",
            "width",
            "height",
            "rotation",
            "anchor",
            "z_index",
            "role",
            "content_definition_id",
        ):
            if field in request.data:
                setattr(placement, field, request.data[field])
        placement.save()
        return Response(_artifact_payload(placement))

    def delete(self, request, design_id: int, placement_id: int):
        design = TowerDesign.objects.get(id=design_id)
        TowerDesignService().assert_owner(user=request.user, design=design)
        ArtifactPlacement.objects.get(id=placement_id, tower_design=design).delete()
        return Response(status=204)


def _piece_payload(piece: TowerPieceInstance) -> dict:
    return {
        "id": piece.id,
        "tower_design_id": piece.tower_design_id,
        "piece_asset_id": piece.piece_asset_id,
        "piece_type": piece.piece_type,
        "storey_index": piece.storey_index,
        "sort_order": piece.sort_order,
        "parent_instance_id": piece.parent_instance_id,
        "transform": piece.transform,
        "config": piece.config,
    }


def _binding_payload(binding: TowerContentBinding) -> dict:
    return {
        "id": binding.id,
        "piece_instance_id": binding.piece_instance_id,
        "content_definition_id": binding.content_definition_id,
    }


def _artifact_payload(placement: ArtifactPlacement) -> dict:
    return {
        "id": placement.id,
        "tower_design_id": placement.tower_design_id,
        "target_piece_instance_id": placement.target_piece_instance_id,
        "artifact_asset_id": placement.artifact_asset_id,
        "x": placement.x,
        "y": placement.y,
        "scale": placement.scale,
        "width": placement.width,
        "height": placement.height,
        "rotation": placement.rotation,
        "anchor": placement.anchor,
        "z_index": placement.z_index,
        "role": placement.role,
        "content_definition_id": placement.content_definition_id,
    }
