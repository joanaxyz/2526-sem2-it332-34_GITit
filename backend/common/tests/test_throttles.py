from types import SimpleNamespace
from unittest.mock import patch

import pytest
from django.core.cache import cache
from django.test import override_settings
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.test import APIClient, APIRequestFactory, force_authenticate
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from accounts.views import LoginAPIView
from adventures.views import AdventureLevelTierRetryAPIView, AdventureLevelTierRunStartAPIView
from challenges.views import ChallengeRetryAPIView, ChallengeRunStartAPIView
from common.throttles import AuthenticatedRateThrottle, TrustedScopedRateThrottle


class ReadView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"ok": True})


class CommandView(ReadView):
    throttle_scope = "command_submit"


class TutorView(ReadView):
    throttle_scope = "tutor_chat"


def call(view=ReadView, user=1, **headers):
    request = APIRequestFactory().get("/api/example/", **headers)
    if user is not None:
        force_authenticate(request, user=SimpleNamespace(pk=user, is_authenticated=True))
    return view.as_view()(request)


def rate(monkeypatch, scope, value):
    monkeypatch.setitem(ScopedRateThrottle.THROTTLE_RATES, scope, value)


def test_general_limit_is_per_user_even_on_shared_ip(db, monkeypatch, django_assert_num_queries):
    rate(monkeypatch, "authenticated", "2/min")
    with django_assert_num_queries(0):
        assert call().status_code == 200
        assert call().status_code == 200
        response = call()
        assert response.status_code == 429
        assert call(user=2).status_code == 200
    assert response.data["retry_after_seconds"] == int(response["Retry-After"])


def test_general_policy_does_not_create_a_classroom_anonymous_bucket(monkeypatch):
    rate(monkeypatch, "authenticated", "1/min")
    for _ in range(5):
        assert call(user=None).status_code == 200


def test_scoped_limits_preserved_and_retry_recovers_at_expiry(monkeypatch):
    rate(monkeypatch, "command_submit", "2/min")
    with patch.object(ScopedRateThrottle, "timer", return_value=100):
        assert call(CommandView).status_code == 200
        assert call(CommandView).status_code == 200
    with patch.object(ScopedRateThrottle, "timer", return_value=110):
        response = call(CommandView)
        assert response.status_code == 429
        assert response.data["retry_after_seconds"] == 50
        assert response["Retry-After"] == "50"
        assert call(CommandView, user=2).status_code == 200
    with patch.object(ScopedRateThrottle, "timer", return_value=160):
        assert call(CommandView).status_code == 200


def test_global_policy_also_limits_scoped_views(monkeypatch):
    rate(monkeypatch, "authenticated", "1/min")
    assert call(CommandView).status_code == 200
    assert call(TutorView).status_code == 429


def test_tutor_daily_policy_is_independent_of_burst_and_other_traffic(monkeypatch):
    rate(monkeypatch, "tutor_chat_daily", "1/day")
    assert call(TutorView).status_code == 200
    assert call(TutorView).status_code == 429
    assert call(TutorView, user=2).status_code == 200
    assert call(CommandView).status_code == 200


def test_daily_policy_follows_drf_counting_when_another_throttle_rejects(monkeypatch):
    rate(monkeypatch, "tutor_chat", "1/min")
    rate(monkeypatch, "tutor_chat_daily", "2/day")
    assert call(TutorView).status_code == 200
    assert call(TutorView).status_code == 429  # Burst refuses; daily records it.
    cache.delete("throttle_tutor_chat_1")
    response = call(TutorView)
    assert response.status_code == 429
    assert int(response["Retry-After"]) > 60  # Daily, despite a fresh burst bucket.


@override_settings(DJANGO_TRUST_PROXY_HEADERS=False)
def test_untrusted_forwarding_headers_cannot_rotate_anonymous_scope(monkeypatch):
    rate(monkeypatch, "command_submit", "1/min")
    assert call(CommandView, user=None, HTTP_X_FORWARDED_FOR="203.0.113.1").status_code == 200
    assert call(CommandView, user=None, HTTP_X_FORWARDED_FOR="203.0.113.2").status_code == 429


@override_settings(DJANGO_TRUST_PROXY_HEADERS=True, DJANGO_TRUSTED_PROXY_IPS=["10.0.0.0/8"])
def test_trusted_render_chain_ignores_spoofed_prefix(monkeypatch):
    rate(monkeypatch, "command_submit", "1/min")
    headers = {"REMOTE_ADDR": "10.0.0.1"}
    assert (
        call(CommandView, None, HTTP_X_FORWARDED_FOR="1.1.1.1, 198.51.100.2", **headers).status_code
        == 200
    )
    assert (
        call(CommandView, None, HTTP_X_FORWARDED_FOR="8.8.8.8, 198.51.100.2", **headers).status_code
        == 429
    )
    assert (
        call(CommandView, None, HTTP_X_FORWARDED_FOR="198.51.100.3", **headers).status_code == 200
    )


def test_login_is_source_limited_even_with_different_authenticated_users(monkeypatch):
    rate(monkeypatch, "auth_login", "1/min")
    view = LoginAPIView()
    throttle = TrustedScopedRateThrottle()
    request = SimpleNamespace(
        user=SimpleNamespace(pk=1, is_authenticated=True), META={"REMOTE_ADDR": "198.51.100.1"}
    )
    assert throttle.allow_request(request, view)
    request.user.pk = 2
    assert not TrustedScopedRateThrottle().allow_request(request, view)


@pytest.mark.parametrize(
    "view",
    [
        AdventureLevelTierRunStartAPIView,
        AdventureLevelTierRetryAPIView,
        ChallengeRunStartAPIView,
        ChallengeRetryAPIView,
    ],
)
def test_start_and_retry_views_share_resource_policy(view, monkeypatch):
    rate(monkeypatch, "run_start", "1/min")
    request = SimpleNamespace(user=SimpleNamespace(pk=1, is_authenticated=True), META={})
    assert TrustedScopedRateThrottle().allow_request(request, view())
    assert not TrustedScopedRateThrottle().allow_request(request, view())


def test_public_readiness_is_bounded_but_liveness_stays_available(db, monkeypatch):
    rate(monkeypatch, "health_ready", "1/min")
    client = APIClient()
    assert client.get("/api/health/ready/").status_code == 200
    assert client.get("/api/health/ready/").status_code == 429
    for _ in range(3):
        assert client.get("/api/health/live/").status_code == 200


def test_public_schema_and_docs_share_a_trusted_scope(monkeypatch):
    rate(monkeypatch, "public_metadata", "1/min")
    client = APIClient()
    assert client.get("/api/docs/").status_code == 200
    assert client.get("/api/schema/").status_code == 429


def test_general_cache_check_uses_existing_user_only():
    request = SimpleNamespace(user=SimpleNamespace(pk=17, is_authenticated=True))
    assert (
        AuthenticatedRateThrottle().get_cache_key(request, ReadView())
        == "throttle_authenticated_17"
    )
    assert cache.get("throttle_authenticated_17") is None
