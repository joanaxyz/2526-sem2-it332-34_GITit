from unittest import mock

from rest_framework.test import APIClient


def test_health_ok(db):
    response = APIClient().get("/api/health/")
    assert response.status_code == 200
    assert response.data == {"status": "ok", "db": "ok", "cache": "ok"}


def test_health_reports_cache_outage(db):
    with mock.patch("common.views.cache.set", side_effect=ConnectionError):
        response = APIClient().get("/api/health/")
    assert response.status_code == 503
    assert response.data["cache"] == "error"
    assert response.data["status"] == "degraded"
