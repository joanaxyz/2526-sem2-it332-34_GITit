import re

from rest_framework.test import APIClient


def test_request_id_is_generated_and_returned():
    response = APIClient().get("/api/health/live/")
    assert re.fullmatch(r"[0-9a-f]{32}", response["X-Request-ID"])


def test_safe_request_id_is_preserved():
    response = APIClient().get("/api/health/live/", HTTP_X_REQUEST_ID="trace-123")
    assert response["X-Request-ID"] == "trace-123"


def test_unsafe_request_id_is_replaced():
    response = APIClient().get("/api/health/live/", HTTP_X_REQUEST_ID="bad id\n")
    assert response["X-Request-ID"] != "bad id\n"
