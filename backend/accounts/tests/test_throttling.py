import pytest
from django.core.cache import cache
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.throttling import ScopedRateThrottle


@pytest.fixture()
def api_client():
    cache.clear()  # throttle counters live in the shared locmem test cache
    client = APIClient()
    client.credentials(HTTP_X_GIT_IT_CLIENT="web")
    yield client
    cache.clear()


def registration_payload(n):
    return {
        "username": f"throttled{n}",
        "email": f"throttled{n}@example.com",
        "password": "Password123!",
        "password_confirm": "Password123!",
    }


def test_register_throttled_after_limit(db, api_client, monkeypatch):
    # SimpleRateThrottle binds THROTTLE_RATES at class creation, so patch the
    # class attribute rather than override_settings (which it never re-reads).
    monkeypatch.setitem(ScopedRateThrottle.THROTTLE_RATES, "auth_register", "2/hour")
    for n in range(2):
        response = api_client.post("/api/auth/register/", registration_payload(n), format="json")
        assert response.status_code == status.HTTP_201_CREATED
    response = api_client.post("/api/auth/register/", registration_payload(2), format="json")
    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS


def test_refresh_throttled_after_limit(db, api_client, monkeypatch):
    monkeypatch.setitem(ScopedRateThrottle.THROTTLE_RATES, "auth_refresh", "2/hour")
    for _ in range(2):
        response = api_client.post("/api/auth/refresh/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    response = api_client.post("/api/auth/refresh/")
    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS


def test_login_scope_bounds_rotating_identifiers(db, api_client, monkeypatch):
    monkeypatch.setitem(ScopedRateThrottle.THROTTLE_RATES, "auth_login", "2/min")
    for n in range(2):
        response = api_client.post(
            "/api/auth/login/",
            {"identifier": f"nobody{n}", "password": "wrong-pass"},
            format="json",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    response = api_client.post(
        "/api/auth/login/", {"identifier": "another", "password": "wrong-pass"}, format="json"
    )
    assert response.status_code == 429
    assert int(response["Retry-After"]) == response.data["retry_after_seconds"]


def test_login_lockout_keeps_legacy_field_and_retry_header(db, api_client, settings):
    settings.AUTH_LOGIN_MAX_ATTEMPTS = 2
    payload = {"identifier": "missing", "password": "wrong-pass"}
    assert api_client.post("/api/auth/login/", payload, format="json").status_code == 401
    response = api_client.post("/api/auth/login/", payload, format="json")
    assert response.status_code == 429
    assert response.data["retry_after"] == settings.AUTH_LOGIN_LOCKOUT_SECONDS
    assert int(response["Retry-After"]) == response.data["retry_after_seconds"]


def test_classroom_login_burst_and_lockout_independence(db, api_client, settings, monkeypatch):
    settings.AUTH_LOGIN_MAX_ATTEMPTS = 2
    monkeypatch.setitem(ScopedRateThrottle.THROTTLE_RATES, "auth_login", "120/min")
    for n in range(30):
        response = api_client.post(
            "/api/auth/login/",
            {"identifier": f"student{n}", "password": "wrong-pass"},
            format="json",
        )
        assert response.status_code == 401
