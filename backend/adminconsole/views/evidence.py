from django.http import HttpResponse
from drf_spectacular.utils import OpenApiTypes, extend_schema
from rest_framework.views import APIView

from adminconsole.serializers import AdminUserListQuerySerializer
from adminconsole.services.kpi_evidence import build_evidence
from common.permissions import IsStaff
from progress.services.kpi_range import KPI_TIMEZONE


class AdminKpiEvidenceAPIView(APIView):
    permission_classes = [IsStaff]

    @extend_schema(
        parameters=[AdminUserListQuerySerializer],
        responses={
            (
                200,
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ): OpenApiTypes.BINARY
        },
    )
    def get(self, request):
        serializer = AdminUserListQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        content, cutoff = build_evidence(serializer.validated_data.get("q", ""))
        response = HttpResponse(
            content,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = (
            f'attachment; filename="GITit_Learner_KPI_Evidence_{cutoff.astimezone(KPI_TIMEZONE):%Y-%m-%d}.xlsx"'
        )
        response["Cache-Control"] = "no-store"
        return response
