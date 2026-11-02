from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from common.views import LivenessAPIView, ReadinessAPIView


class PublicSchemaAPIView(SpectacularAPIView):
    throttle_scope = "public_metadata"


class PublicDocsAPIView(SpectacularSwaggerView):
    throttle_scope = "public_metadata"


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", ReadinessAPIView.as_view(), name="health"),
    path("api/health/live/", LivenessAPIView.as_view(), name="health-live"),
    path("api/health/ready/", ReadinessAPIView.as_view(), name="health-ready"),
    path("api/schema/", PublicSchemaAPIView.as_view(), name="schema"),
    path("api/docs/", PublicDocsAPIView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/auth/", include("accounts.urls")),
    path("api/player/", include("players.urls")),
    path("api/", include("challenges.urls")),
    path("api/", include("adventures.urls")),
    path("api/", include("drills.urls")),
    path("api/", include("tutoring.urls")),
    path("api/", include("curriculum.urls")),
    path("api/", include("shop.urls")),
    path("api/progress/", include("progress.urls")),
    path("api/admin/", include("adminconsole.urls")),
]

handler404 = "common.api.api_not_found"
handler500 = "common.api.api_server_error"
