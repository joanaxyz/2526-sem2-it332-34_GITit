"""User-management HTTP adapters for the admin console."""

from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from adminconsole.selectors import (
    admin_user_list_payload,
    find_admin_user,
    user_detail,
)
from adminconsole.serializers import (
    AdminUserActionRequestSerializer,
    AdminUserDetailSerializer,
    AdminUserListQuerySerializer,
    AdminUserListResponseSerializer,
)
from adminconsole.services import AdminEconomyService, AdminUserActionService
from common.permissions import IsStaff
from players.models import Player
from players.services import get_or_create_player
from progress.services import MetricsService


def _require_user(user_id):
    user = find_admin_user(user_id)
    if user is None:
        raise NotFound("User not found.")
    return user


class AdminUserListAPIView(APIView):
    permission_classes = [IsStaff]

    @extend_schema(
        parameters=[AdminUserListQuerySerializer],
        responses={200: AdminUserListResponseSerializer},
    )
    def get(self, request):
        query_serializer = AdminUserListQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)
        return Response(
            admin_user_list_payload(
                query=query_serializer.validated_data.get("q", ""),
            )
        )


class AdminUserDetailAPIView(APIView):
    permission_classes = [IsStaff]

    @extend_schema(responses={200: AdminUserDetailSerializer})
    def get(self, request, user_id: int):
        return Response(user_detail(_require_user(user_id)))


class AdminUserActionAPIView(APIView):
    """Run a staff action on a user: grant/deduct coins, toggle staff or
    active. One action per call via the ``action`` field."""

    permission_classes = [IsStaff]

    @extend_schema(
        request=AdminUserActionRequestSerializer,
        responses={200: AdminUserDetailSerializer},
    )
    def post(self, request, user_id: int):
        serializer = AdminUserActionRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        target = _require_user(user_id)
        action = data["action"]
        if action == "grant_coins":
            player = get_or_create_player(target)
            AdminEconomyService().adjust(
                actor=request.user,
                player=player,
                amount=data["amount"],
                reason=data["reason"],
                request_id=data["request_id"],
            )
        elif action == "set_staff":
            target = AdminUserActionService().set_staff(
                actor=request.user,
                target=target,
                value=data["value"],
            )
        elif action == "set_active":
            target = AdminUserActionService().set_active(
                actor=request.user,
                target=target,
                value=data["value"],
            )
        return Response(user_detail(target))


class AdminUserKpisAPIView(APIView):
    """Per-user learning KPIs for the admin console detail panel."""

    permission_classes = [IsStaff]

    def get(self, request, user_id: int):
        user = _require_user(user_id)
        player = Player.objects.filter(user=user).first()
        if player is None:
            return Response({"has_data": False, "kpis": None, "modules": []})

        summary = MetricsService().performance_summary(player=player)
        kpis = summary["kpis"]
        modules = summary["modules"]

        # RTA: retry sessions where changed-variant first attempt succeeded.
        # A changed-variant retry is a run where prior_run is set and the
        # variant differs from the prior run's variant. A successful one
        # completes on the first attempt of that retry session (retry_index==1
        # means one retry was started, i.e. this IS the first retry attempt).
        from adventures.models import AdventureLevelTierRun
        from common.constants import SESSION_STATUS_COMPLETED

        rta_qs = AdventureLevelTierRun.objects.filter(
            player=player,
            is_replay=False,
            prior_run__isnull=False,
            tier__adventure_level__chapter__story__slug=MetricsService.PERFORMANCE_STORY_SLUG,
            tier__adventure_level__chapter__number__in=MetricsService.PERFORMANCE_MODULE_NUMBERS,
        )
        eligible = rta_qs.count()
        successful = rta_qs.filter(
            status=SESSION_STATUS_COMPLETED,
            retry_index=1,
        ).count()
        rta = {
            "value": round(successful / eligible * 100, 1) if eligible else None,
            "numerator": successful,
            "denominator": eligible,
        }

        return Response({
            "has_data": summary["completed_sessions"] > 0 or eligible > 0,
            "kpis": {
                "scr": kpis["scr"],
                "car": kpis["car"],
                "hlcr": kpis["hlcr"],
                "rtr": kpis["rtr"],
                "arc": kpis["arc"],
                "rta": rta,
            },
            "modules": modules,
        })
