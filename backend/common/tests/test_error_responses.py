from unittest import mock

from django.test import override_settings
from rest_framework.test import APIClient

from common.api import SERVER_ERROR_DETAIL
from common.views import LivenessAPIView


@override_settings(DEBUG=False)
def test_unknown_api_route_returns_json_404():
    response = APIClient().get("/api/no-such-route/")

    assert response.status_code == 404
    assert response["Content-Type"] == "application/json"
    assert response.json() == {"detail": "Not found."}


@override_settings(DEBUG=False)
def test_unhandled_api_error_returns_json_500_without_internals():
    client = APIClient(raise_request_exception=False)
    with mock.patch.object(LivenessAPIView, "get", side_effect=RuntimeError("secret detail")):
        response = client.get("/api/health/live/")

    assert response.status_code == 500
    assert response["Content-Type"] == "application/json"
    assert response.json() == {"detail": SERVER_ERROR_DETAIL}
    assert b"secret detail" not in response.content


@override_settings(DEBUG=False)
def test_non_api_routes_keep_django_error_pages():
    response = APIClient().get("/no-such-page/")

    assert response.status_code == 404
    assert response["Content-Type"].startswith("text/html")
