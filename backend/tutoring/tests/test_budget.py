from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch

import httpx
import pytest

from tutoring.services.budget import BudgetUnavailable, reserve_provider_call
from tutoring.services.provider_transport import ProviderError, post_json


def test_disabled_budget_does_not_touch_cache(settings):
    settings.TUTOR_PROVIDER_DAILY_LIMIT = 0
    with patch("tutoring.services.budget.caches") as cache_handles:
        assert reserve_provider_call() is None
    cache_handles.__getitem__.assert_not_called()


def test_daily_cap_and_utc_reset(settings):
    settings.TUTOR_PROVIDER_DAILY_LIMIT = 2
    with patch("tutoring.services.budget.time.time", return_value=100):
        assert reserve_provider_call() is None
        assert reserve_provider_call() is None
        assert reserve_provider_call() == 86300
    with patch("tutoring.services.budget.time.time", return_value=86401):
        assert reserve_provider_call() is None


def test_budget_failure_is_observable_and_does_not_log_connection_secrets(settings, caplog):
    settings.TUTOR_PROVIDER_DAILY_LIMIT = 2
    with patch("tutoring.services.budget.caches") as cache_handles:
        cache_handles.__getitem__.return_value.add.side_effect = ConnectionError("secret-uri")
        with pytest.raises(BudgetUnavailable):
            reserve_provider_call()
    assert "tutor_provider_budget_unavailable" in caplog.text
    assert "secret-uri" not in caplog.text


def test_budget_is_shared_by_independent_thread_cache_handles(settings):
    settings.TUTOR_PROVIDER_DAILY_LIMIT = 7
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(lambda _: reserve_provider_call(), range(30)))
    assert results.count(None) == 7
    assert all(value is None or 1 <= value <= 86400 for value in results)


def test_redis_budget_admission_is_atomic_across_clients(settings):
    # Runs in the existing PostgreSQL/Redis integration job, skips offline.
    if "django_redis" not in settings.CACHES["provider_budget"]["BACKEND"]:
        pytest.skip("Real Redis budget check requires config.integration_test_settings")
    assert settings.CACHES["provider_budget"]["OPTIONS"]["IGNORE_EXCEPTIONS"] is False
    settings.TUTOR_PROVIDER_DAILY_LIMIT = 7
    with ThreadPoolExecutor(max_workers=12) as pool:
        results = list(pool.map(lambda _: reserve_provider_call(), range(60)))
    assert results.count(None) == 7


def test_enabled_budget_does_not_inherit_default_cache_fail_open(settings):
    settings.TUTOR_PROVIDER_DAILY_LIMIT = 2
    settings.CACHES = {
        **settings.CACHES,
        "provider_budget": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": "redis://127.0.0.1:1/0",
            "OPTIONS": {**settings.REDIS_CACHE_OPTIONS, "IGNORE_EXCEPTIONS": False},
        },
    }
    with pytest.raises(BudgetUnavailable):
        reserve_provider_call()


def test_budget_accesses_only_the_strict_cache_alias(settings):
    settings.TUTOR_PROVIDER_DAILY_LIMIT = 1
    with patch("tutoring.services.budget.caches") as cache_handles:
        cache_handles.__getitem__.return_value.add.return_value = True
        assert reserve_provider_call() is None
    cache_handles.__getitem__.assert_called_once_with("provider_budget")


def test_reservation_ttl_ends_at_utc_midnight_and_outage_can_recover(settings):
    settings.TUTOR_PROVIDER_DAILY_LIMIT = 1
    with (
        patch("tutoring.services.budget.time.time", return_value=86399.2),
        patch("tutoring.services.budget.caches") as cache_handles,
    ):
        budget = cache_handles.__getitem__.return_value
        budget.add.side_effect = [ConnectionError(), True]
        with pytest.raises(BudgetUnavailable):
            reserve_provider_call()
        assert reserve_provider_call() is None
        budget.add.assert_called_with("tutor:provider-budget:utc:0", 1, timeout=1)


def test_counter_disappearing_between_add_and_increment_fails_closed(settings):
    settings.TUTOR_PROVIDER_DAILY_LIMIT = 1
    with patch("tutoring.services.budget.caches") as cache_handles:
        budget = cache_handles.__getitem__.return_value
        budget.add.return_value = False
        budget.incr.side_effect = ValueError("Key expired")
        with pytest.raises(BudgetUnavailable):
            reserve_provider_call()


# Transport-level assertions live here alongside the budget policy. Reuse the
# established mocked HTTP transport fixture without ever contacting a provider.
@pytest.fixture
def budget_transport(monkeypatch):
    from tutoring.services import provider_transport

    original = httpx.AsyncClient

    def install(handler):
        monkeypatch.setattr(
            httpx,
            "AsyncClient",
            lambda **kwargs: original(transport=httpx.MockTransport(handler), **kwargs),
        )
        monkeypatch.setattr(provider_transport, "_runtime", None)

    return install


def test_transport_protocol_retry_also_requires_reservation(settings, budget_transport):
    settings.TUTOR_PROVIDER_DAILY_LIMIT = 1
    calls = []

    def handler(request):
        calls.append(request)
        raise httpx.RemoteProtocolError("closed")

    budget_transport(handler)
    with pytest.raises(ProviderError) as exc:
        post_json("https://example.test", {}, {}, 1)
    assert exc.value.status == 429
    assert exc.value.reason == "budget_exhausted"
    assert len(calls) == 1


def test_budget_outage_prevents_http_only(settings, budget_transport):
    settings.TUTOR_PROVIDER_DAILY_LIMIT = 1
    calls = []
    budget_transport(lambda request: calls.append(request) or httpx.Response(200, json={}))
    with patch(
        "tutoring.services.provider_transport.reserve_provider_call", side_effect=BudgetUnavailable
    ):
        with pytest.raises(ProviderError) as exc:
            post_json("https://example.test", {}, {}, 1)
    assert exc.value.reason == "budget_unavailable"
    assert not calls


def test_embedding_and_generation_failover_share_the_physical_budget(settings, budget_transport):
    from tutoring.services.providers import generate
    from tutoring.services.scenario_recognition import embed

    settings.TUTOR_PROVIDER_DAILY_LIMIT = 2
    settings.GOOGLE_AI_STUDIO_API_KEY = "test-google"
    settings.GROQ_API_KEY = "test-groq"
    settings.TUTOR_GEMINI_MODELS = ("first",)
    calls = []

    def handler(request):
        calls.append(request.url.path)
        if request.url.path.endswith(":batchEmbedContents"):
            return httpx.Response(200, json={"embeddings": [{"values": [1.0] + [0.0] * 767}]})
        return httpx.Response(429, headers={"Retry-After": "25"})

    budget_transport(handler)
    assert len(embed(["What is staging?"], "RETRIEVAL_QUERY")) == 1
    diagnostics = {}
    assert generate("system", [], diagnostics=diagnostics) is None
    assert len(calls) == 2  # Embedding + Gemini; Groq denied before HTTP.
    assert diagnostics["unavailable_reason"] == "rate_limited"
    assert 1 <= diagnostics["retry_after_seconds"] <= 86400


def test_overlapping_hedges_each_reserve_before_http(settings, budget_transport):
    import asyncio
    import threading

    from tutoring.services.providers import generate

    settings.TUTOR_PROVIDER_DAILY_LIMIT = 2
    settings.GOOGLE_AI_STUDIO_API_KEY = "test-google"
    settings.GROQ_API_KEY = "test-groq"
    settings.TUTOR_GEMINI_MODELS = ("first",)
    settings.TUTOR_PROVIDER_HEDGE_SECONDS = 0.01
    settings.TUTOR_PROVIDER_DEADLINE_SECONDS = 1
    release = threading.Event()
    calls = []

    async def handler(request):
        calls.append(request.url.path)
        if request.url.host == "api.groq.com":
            release.set()
            return httpx.Response(200, json={"choices": [{"message": {"content": "Answer"}}]})
        while not release.is_set():
            await asyncio.sleep(0.001)
        return httpx.Response(
            200, json={"candidates": [{"content": {"parts": [{"text": "Answer"}]}}]}
        )

    budget_transport(handler)
    try:
        assert generate("system", []) == "Answer"
    finally:
        release.set()
    assert len(calls) == 2
    assert reserve_provider_call() is not None


def test_slow_admission_respects_deadline_and_never_sends_after_cancellation(budget_transport):
    import threading

    entered, release, exited = threading.Event(), threading.Event(), threading.Event()
    calls = []
    budget_transport(lambda request: calls.append(request) or httpx.Response(200, json={}))

    def slow_admission():
        entered.set()
        release.wait(2)
        exited.set()

    with patch(
        "tutoring.services.provider_transport.reserve_provider_call", side_effect=slow_admission
    ):
        try:
            with pytest.raises(ProviderError) as exc:
                post_json("https://example.test", {}, {}, 0.1)
            assert entered.is_set()
            assert exc.value.reason == "timeout"
        finally:
            release.set()
        assert exited.wait(1)
    assert not calls
