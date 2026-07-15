from unittest import mock

from django.test import override_settings
from rest_framework.test import APIClient


@override_settings(DEPLOYMENT_VERSION="test-sha")
def test_liveness_does_not_touch_dependencies():
    with mock.patch("common.views.connection.cursor") as cursor, mock.patch(
        "common.views.cache.set"
    ) as cache_set:
        response = APIClient().get("/api/health/live/")

    assert response.status_code == 200
    assert response.data == {"status": "ok", "version": "test-sha"}
    cursor.assert_not_called()
    cache_set.assert_not_called()


@override_settings(DEPLOYMENT_VERSION="test-sha")
def test_readiness_ok(db):
    response = APIClient().get("/api/health/ready/")
    assert response.status_code == 200
    assert response.data == {
        "status": "ok",
        "version": "test-sha",
        "db": "ok",
        "cache": "ok",
    }


def test_legacy_health_route_remains_readiness(db):
    response = APIClient().get("/api/health/")
    assert response.status_code == 200
    assert response.data["db"] == "ok"
    assert response.data["cache"] == "ok"


def test_readiness_reports_cache_outage(db):
    with mock.patch("common.views.cache.set", side_effect=ConnectionError):
        response = APIClient().get("/api/health/ready/")
    assert response.status_code == 503
    assert response.data["cache"] == "error"
    assert response.data["status"] == "degraded"
