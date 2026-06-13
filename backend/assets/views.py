from rest_framework.response import Response
from rest_framework.views import APIView

from assets.descriptors import descriptor_map
from assets.models import ASSET_KINDS
from common.performance import timing


class AssetDescriptorAPIView(APIView):
    def get(self, request):
        kind = request.query_params.get("kind") or ""
        valid_kinds = {value for value, _label in ASSET_KINDS}
        if kind not in valid_kinds:
            return Response(
                {"detail": "Unknown asset kind.", "valid_kinds": sorted(valid_kinds)},
                status=400,
            )
        with timing("assets.descriptors", kind=kind):
            return Response({"kind": kind, "results": descriptor_map(kind)})
