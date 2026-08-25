"""Feature-flag HTTP adapter for the admin console."""

from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from adminconsole.selectors import admin_settings_payload, flag_payload
from adminconsole.serializers import (
    AdminFeatureFlagSerializer,
    AdminFeatureFlagUpdateRequestSerializer,
    AdminSettingsResponseSerializer,
)
from adminconsole.services import update_feature_flag
from common.permissions import IsStaff


class AdminSettingsAPIView(APIView):
    permission_classes = [IsStaff]

    @extend_schema(responses={200: AdminSettingsResponseSerializer})
    def get(self, request):
        return Response(admin_settings_payload())

    @extend_schema(
        request=AdminFeatureFlagUpdateRequestSerializer,
        responses={200: AdminFeatureFlagSerializer},
    )
    def post(self, request):
        serializer = AdminFeatureFlagUpdateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        flag = update_feature_flag(
            actor=request.user,
            key=data["key"],
            enabled=data["enabled"],
        )
        return Response(flag_payload(flag))
