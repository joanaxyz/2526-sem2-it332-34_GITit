from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from marketplace.access import can_remix
from archive.models import (
    ORIGIN_PERSONAL,
    STATUS_PUBLISHED,
    ArchiveDesign,
    RelicPlacement,
)
from archive.selectors import (
    archive_design_overview,
    archive_design_payload,
    visible_archive_designs,
)
from archive.services import ArchiveDesignService


class ArchiveDesignMineAPIView(APIView):
    def get(self, request):
        designs = ArchiveDesign.objects.filter(owner=request.user).order_by(
            "-is_active", "-updated_at", "-id"
        )
        return Response({"results": [archive_design_payload(design) for design in designs]})


class ArchiveDesignListCreateAPIView(APIView):
    def post(self, request):
        # Idempotent: "Raise your Archive" returns the existing personal archive.
        design = ArchiveDesignService().get_or_create_personal(user=request.user, data=request.data)
        return Response(archive_design_payload(design), status=201)


class ArchiveDesignDetailAPIView(APIView):
    def get(self, request, design_id: int):
        design = visible_archive_designs(user=request.user).get(id=design_id)
        return Response(archive_design_payload(design, include_layout=True))

    def patch(self, request, design_id: int):
        design = ArchiveDesign.objects.get(id=design_id)
        design = ArchiveDesignService().update(user=request.user, design=design, data=request.data)
        return Response(archive_design_payload(design))


class ArchiveDesignSetActiveAPIView(APIView):
    def post(self, request, design_id: int):
        design = ArchiveDesign.objects.get(id=design_id)
        design = ArchiveDesignService().set_active(user=request.user, design=design)
        return Response(archive_design_payload(design))


class ArchiveDesignPublishAPIView(APIView):
    def post(self, request, design_id: int):
        design = ArchiveDesign.objects.get(id=design_id)
        design = ArchiveDesignService().publish(user=request.user, design=design)
        return Response(archive_design_payload(design))


class ArchiveDesignOfficialForkAPIView(APIView):
    """Get-or-create the user's private fork of the official Archive."""

    def post(self, request):
        design = ArchiveDesignService().get_or_create_official_fork(user=request.user)
        return Response(archive_design_payload(design, include_layout=True), status=201)


class ArchiveDesignShareAPIView(APIView):
    """Publish + make a personal archive public, returning its shareable identity."""

    def post(self, request, design_id: int):
        design = ArchiveDesign.objects.get(id=design_id)
        design = ArchiveDesignService().share(user=request.user, design=design)
        payload = archive_design_payload(design)
        payload["share_path"] = f"/archive/shared/{design.id}"
        return Response(payload)


class SharedArchiveOverviewAPIView(APIView):
    """Public, read-only overview of a shared personal archive (no auth)."""

    permission_classes = [AllowAny]

    def get(self, request, design_id: int):
        try:
            design = ArchiveDesign.objects.get(id=design_id)
        except ArchiveDesign.DoesNotExist as exc:
            raise NotFound("Archive not found.") from exc
        is_public = design.status == STATUS_PUBLISHED and design.visibility in {"public", "store"}
        if not is_public or design.origin != ORIGIN_PERSONAL:
            raise NotFound("Archive not found.")
        return Response(archive_design_overview(design=design))


class ArchiveDesignRemixAPIView(APIView):
    def post(self, request, design_id: int):
        design = visible_archive_designs(user=request.user).get(id=design_id)
        if not can_remix(request.user, design):
            raise PermissionDenied("You cannot remix this archive.")
        clone = ArchiveDesignService().remix(user=request.user, design=design)
        return Response(archive_design_payload(clone, include_layout=True), status=201)


class ArchiveDesignLayoutAPIView(APIView):
    def get(self, request, design_id: int):
        design = visible_archive_designs(user=request.user).get(id=design_id)
        return Response(archive_design_overview(design=design))


class MyArchiveOverviewAPIView(APIView):
    def get(self, request):
        design = (
            ArchiveDesign.objects.filter(owner=request.user, is_active=True)
            .order_by("-updated_at", "-id")
            .first()
        )
        if design is None:
            return Response({"detail": "No active archive."}, status=404)
        return Response(archive_design_overview(design=design))


class ArchiveChapterCreateAPIView(APIView):
    """Reserve the next empty chapter tab (creates no relics)."""

    def post(self, request, design_id: int):
        design = ArchiveDesign.objects.get(id=design_id)
        chapter_index = ArchiveDesignService().add_chapter(user=request.user, design=design)
        payload = archive_design_overview(design=design)
        payload["added_chapter_index"] = chapter_index
        return Response(payload, status=201)


class RelicPlacementCreateAPIView(APIView):
    def post(self, request, design_id: int):
        design = ArchiveDesign.objects.get(id=design_id)
        placement = ArchiveDesignService().add_relic(
            user=request.user, design=design, data=request.data
        )
        return Response(_relic_payload(placement), status=201)


class RelicPlacementDetailAPIView(APIView):
    _FIELDS = (
        "chapter_index",
        "x",
        "y",
        "scale",
        "width",
        "height",
        "rotation",
        "z_index",
        "kind",
        "content_definition_id",
        "interactive_viewbox",
        "landing_viewbox",
        "config",
    )

    def patch(self, request, design_id: int, placement_id: int):
        design = ArchiveDesign.objects.get(id=design_id)
        ArchiveDesignService().assert_owner(user=request.user, design=design)
        placement = RelicPlacement.objects.get(id=placement_id, archive_design=design)
        if "relic_asset_id" in request.data:
            placement.relic_asset_id = request.data["relic_asset_id"]
        for field in self._FIELDS:
            if field in request.data:
                setattr(placement, field, request.data[field])
        placement.save()
        return Response(_relic_payload(placement))

    def delete(self, request, design_id: int, placement_id: int):
        design = ArchiveDesign.objects.get(id=design_id)
        ArchiveDesignService().assert_owner(user=request.user, design=design)
        RelicPlacement.objects.get(id=placement_id, archive_design=design).delete()
        return Response(status=204)


def _relic_payload(placement: RelicPlacement) -> dict:
    return {
        "id": placement.id,
        "archive_design_id": placement.archive_design_id,
        "relic_asset_id": placement.relic_asset_id,
        "assetSlug": placement.relic_asset.slug,
        "kind": placement.kind,
        "chapter_index": placement.chapter_index,
        "x": placement.x,
        "y": placement.y,
        "scale": placement.scale,
        "width": placement.width,
        "height": placement.height,
        "rotation": placement.rotation,
        "z_index": placement.z_index,
        "content_definition_id": placement.content_definition_id,
        "interactive_viewbox": placement.interactive_viewbox,
        "landing_viewbox": placement.landing_viewbox,
    }
