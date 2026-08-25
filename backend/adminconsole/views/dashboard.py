"""Overview and analytics HTTP adapters for the admin console."""

from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from adminconsole.selectors import admin_analytics_payload, admin_overview_payload
from adminconsole.serializers import (
    AdminAnalyticsResponseSerializer,
    AdminOverviewResponseSerializer,
)
from common.permissions import IsStaff


class AdminOverviewAPIView(APIView):
    permission_classes = [IsStaff]

    @extend_schema(responses={200: AdminOverviewResponseSerializer})
    def get(self, request):
        return Response(admin_overview_payload())


class AdminAnalyticsAPIView(APIView):
    permission_classes = [IsStaff]

    @extend_schema(responses={200: AdminAnalyticsResponseSerializer})
    def get(self, request):
        return Response(admin_analytics_payload())
