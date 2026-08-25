"""Economy HTTP adapters for the admin console."""

from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from adminconsole.selectors import (
    admin_economy_adjustment_payload,
    admin_transaction_list_payload,
    find_admin_user,
)
from adminconsole.serializers import (
    AdminEconomyAdjustRequestSerializer,
    AdminEconomyAdjustResponseSerializer,
    AdminTransactionListQuerySerializer,
    AdminTransactionListResponseSerializer,
)
from adminconsole.services import AdminEconomyService
from common.permissions import IsStaff
from players.services import get_or_create_player


class AdminTransactionListAPIView(APIView):
    permission_classes = [IsStaff]

    @extend_schema(
        parameters=[AdminTransactionListQuerySerializer],
        responses={200: AdminTransactionListResponseSerializer},
    )
    def get(self, request):
        query_serializer = AdminTransactionListQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)
        return Response(
            admin_transaction_list_payload(
                user_id=query_serializer.validated_data.get("user_id"),
            )
        )


class AdminEconomyAdjustAPIView(APIView):
    permission_classes = [IsStaff]

    @extend_schema(
        request=AdminEconomyAdjustRequestSerializer,
        responses={200: AdminEconomyAdjustResponseSerializer},
    )
    def post(self, request):
        serializer = AdminEconomyAdjustRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        target = find_admin_user(data["user_id"])
        if target is None:
            raise NotFound("User not found.")
        player = get_or_create_player(target)
        applied = AdminEconomyService().adjust(
            actor=request.user,
            player=player,
            amount=data["amount"],
            reason=data["reason"],
            request_id=data["request_id"],
        )
        return Response(
            admin_economy_adjustment_payload(
                player=player,
                applied=applied,
            )
        )
