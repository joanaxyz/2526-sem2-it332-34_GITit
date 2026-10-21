import asyncio
import time

import httpx
import pytest

from tutoring.services import provider_transport
from tutoring.services.provider_transport import ProviderError, post_json


@pytest.fixture
def mock_transport(monkeypatch):
    def install(handler):
        transport = httpx.MockTransport(handler)
        original = httpx.AsyncClient
        created = []

        def factory(**kwargs):
            created.append(kwargs)
            return original(transport=transport, **kwargs)

        monkeypatch.setattr(httpx, "AsyncClient", factory)
        # Each test gets its own process-local loop and pooled client.
        monkeypatch.setattr(provider_transport, "_runtime", None)
        return created

    return install


def test_transport_wall_deadline_cancels_slow_progressing_stream(mock_transport):
    class SlowStream(httpx.AsyncByteStream):
        async def __aiter__(self):
            for value in b'{"ok":true}':
                await asyncio.sleep(0.04)
                yield bytes([value])

    mock_transport(lambda _: httpx.Response(200, stream=SlowStream()))
    started = time.monotonic()
    with pytest.raises(ProviderError) as exc:
        post_json("https://example.test", {}, {}, 0.12)
    assert exc.value.status == 503
    assert time.monotonic() - started < 0.4


def test_transport_preserves_rate_limit_retry_header(mock_transport):
    mock_transport(lambda _: httpx.Response(429, headers={"Retry-After": "25"}))
    with pytest.raises(ProviderError) as exc:
        post_json("https://example.test", {}, {}, 1)
    assert exc.value.status == 429 and exc.value.retry_after == "25"


def test_transport_reuses_one_pooled_client(mock_transport):
    created = mock_transport(lambda _: httpx.Response(200, json={"ok": True}))
    assert post_json("https://example.test", {}, {}, 1) == {"ok": True}
    assert post_json("https://example.test", {}, {}, 1) == {"ok": True}
    assert len(created) == 1
    assert created[0]["limits"].keepalive_expiry >= 30


def test_transport_retries_a_connection_the_server_already_closed(mock_transport):
    calls = []

    def handler(request):
        calls.append(request)
        if len(calls) == 1:
            raise httpx.RemoteProtocolError("Server disconnected without sending a response.")
        return httpx.Response(200, json={"ok": True})

    mock_transport(handler)
    assert post_json("https://example.test", {}, {}, 1) == {"ok": True}
    assert len(calls) == 2
