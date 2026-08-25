"""Official-content and moderation HTTP adapters for the admin console."""

from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from adminconsole.selectors import (
    admin_moderation_list_payload,
    admin_official_content_list_payload,
    find_admin_moderation_content,
)
from adminconsole.serializers import (
    AdminContentListQuerySerializer,
    AdminContentListResponseSerializer,
    AdminModerationListResponseSerializer,
    AdminModerationUnpublishRequestSerializer,
    AdminOkayResponseSerializer,
)
from adminconsole.services import unpublish_moderation_content
from common.permissions import IsStaff


class AdminContentListAPIView(APIView):
    """Official content definitions: staff-authored (or owner-less) adventures,
    challenges, and lessons. Create/edit happens in the existing level editor."""

    permission_classes = [IsStaff]

    @extend_schema(
        parameters=[AdminContentListQuerySerializer],
        responses={200: AdminContentListResponseSerializer},
    )
    def get(self, request):
        query_serializer = AdminContentListQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)
        return Response(
            admin_official_content_list_payload(
                kind=query_serializer.validated_data.get("kind"),
            )
        )


class AdminModerationListAPIView(APIView):
    """Shared player-generated content: public published content definitions."""

    permission_classes = [IsStaff]

    @extend_schema(responses={200: AdminModerationListResponseSerializer})
    def get(self, request):
        return Response(admin_moderation_list_payload())


class AdminModerationUnpublishAPIView(APIView):
    permission_classes = [IsStaff]

    @extend_schema(
        request=AdminModerationUnpublishRequestSerializer,
        responses={200: AdminOkayResponseSerializer},
    )
    def post(self, request):
        serializer = AdminModerationUnpublishRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        content = find_admin_moderation_content(serializer.validated_data["id"])
        if content is None:
            raise NotFound("Moderation item not found.")
        unpublish_moderation_content(actor=request.user, content=content)
        return Response({"ok": True})
