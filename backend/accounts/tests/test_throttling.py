import pytest
from django.core.cache import cache
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.throttling import ScopedRateThrottle


@pytest.fixture()
def api_client():
    cache.clear()  # throttle counters live in the shared locmem test cache
    yield APIClient()
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
        response = api_client.post(
            "/api/auth/register/", registration_payload(n), format="json"
        )
        assert response.status_code == status.HTTP_201_CREATED
    response = api_client.post(
        "/api/auth/register/", registration_payload(2), format="json"
    )
    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS


def test_refresh_throttled_after_limit(db, api_client, monkeypatch):
    monkeypatch.setitem(ScopedRateThrottle.THROTTLE_RATES, "auth_refresh", "2/hour")
    for _ in range(2):
        response = api_client.post("/api/auth/refresh/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    response = api_client.post("/api/auth/refresh/")
    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS


def test_login_not_scope_throttled(db, api_client, monkeypatch):
    # Login relies on the app-level brute-force lockout, not ScopedRateThrottle;
    # it must not 429 from the throttle layer on repeated requests.
    monkeypatch.setitem(ScopedRateThrottle.THROTTLE_RATES, "auth_register", "1/hour")
    for _ in range(3):
        response = api_client.post(
            "/api/auth/login/",
            {"identifier": "nobody", "password": "wrong-pass"},
            format="json",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
