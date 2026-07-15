from __future__ import annotations

import logging

from django.conf import settings
from django.core.cache import cache
from django.db import connection
from drf_spectacular.utils import OpenApiTypes, extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)


class HealthProbeAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = []


class LivenessAPIView(HealthProbeAPIView):
    """Process-only probe. Dependency outages must not restart healthy workers."""

    @extend_schema(responses={200: OpenApiTypes.OBJECT})
    def get(self, request):
        return Response(
            {
                "status": "ok",
                "version": settings.DEPLOYMENT_VERSION,
            }
        )


class ReadinessAPIView(HealthProbeAPIView):
    """Traffic-readiness probe for database and shared-cache reachability."""

    @extend_schema(responses={200: OpenApiTypes.OBJECT, 503: OpenApiTypes.OBJECT})
    def get(self, request):
        checks = {"db": "ok", "cache": "ok"}
        healthy = True

        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
        except Exception:
            logger.exception("Readiness database check failed.")
            checks["db"] = "error"
            healthy = False

        try:
            cache_key = "health-check:ready"
            cache.set(cache_key, "ok", timeout=5)
            if cache.get(cache_key) != "ok":
                raise RuntimeError("cache read-back mismatch")
        except Exception:
            logger.exception("Readiness cache check failed.")
            checks["cache"] = "error"
            healthy = False

        return Response(
            {
                "status": "ok" if healthy else "degraded",
                "version": settings.DEPLOYMENT_VERSION,
                **checks,
            },
            status=200 if healthy else 503,
        )


# Backward-compatible name for imports and the existing /api/health/ route.
HealthAPIView = ReadinessAPIView
