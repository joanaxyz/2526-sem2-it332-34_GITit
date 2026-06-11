from django.core.cache import cache
from django.db import connection
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthAPIView(APIView):
    """Liveness/readiness probe for load balancers and uptime monitors.

    Reports DB and cache reachability; 503 when either is down so a probe can
    pull the instance out of rotation before users hit real errors.
    """

    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = []

    def get(self, request):
        checks = {"db": "ok", "cache": "ok"}
        healthy = True

        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
        except Exception:
            checks["db"] = "error"
            healthy = False

        try:
            cache.set("health-check", "ok", timeout=5)
            if cache.get("health-check") != "ok":
                raise RuntimeError("cache read-back mismatch")
        except Exception:
            checks["cache"] = "error"
            healthy = False

        return Response(
            {"status": "ok" if healthy else "degraded", **checks},
            status=200 if healthy else 503,
        )
