from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import override_settings
from rest_framework.response import Response
from rest_framework.test import APIClient, APIRequestFactory, force_authenticate
from rest_framework.views import APIView

# The production cache settings, pointed at a port where no Redis listens.
REDIS_DOWN = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:1/0",
        "OPTIONS": settings.REDIS_CACHE_OPTIONS,
    }
}
PASSWORD = "Lovelace-1843"


class CommandScopedView(APIView):
    throttle_scope = "command_submit"

    def post(self, request):
        return Response({"accepted": True})


def _signed_in_client():
    get_user_model().objects.create_user(username="ada", email="ada@example.com", password=PASSWORD)
    client = APIClient(HTTP_X_GIT_IT_CLIENT="web")
    response = client.post(
        "/api/auth/login/", {"identifier": "ada", "password": PASSWORD}, format="json"
    )
    assert response.status_code == 200
    return client


@override_settings(CACHES=REDIS_DOWN)
def test_session_refresh_survives_a_redis_outage(db):
    client = _signed_in_client()

    response = client.post("/api/auth/refresh/")

    assert response.status_code == 200
    assert response.json()["access"]


@override_settings(CACHES=REDIS_DOWN)
def test_logged_out_session_stays_revoked_without_redis(db):
    client = _signed_in_client()
    refresh_token = client.cookies[settings.GIT_IT_REFRESH_COOKIE].value

    assert client.post("/api/auth/logout/").status_code == 204
    client.cookies[settings.GIT_IT_REFRESH_COOKIE] = refresh_token

    assert client.post("/api/auth/refresh/").status_code == 401


@override_settings(CACHES=REDIS_DOWN)
def test_rate_limited_gameplay_requests_pass_through_without_redis(db, caplog):
    user = get_user_model().objects.create_user(username="grace", password=PASSWORD)
    request = APIRequestFactory().post("/api/commands/", {}, format="json")
    force_authenticate(request, user=user)

    response = CommandScopedView.as_view()(request)

    assert response.status_code == 200
    assert "Exception ignored" in caplog.text


@override_settings(CACHES=REDIS_DOWN)
def test_readiness_still_reports_the_outage(db):
    response = APIClient().get("/api/health/ready/")

    assert response.status_code == 503
    assert response.json()["cache"] == "error"
