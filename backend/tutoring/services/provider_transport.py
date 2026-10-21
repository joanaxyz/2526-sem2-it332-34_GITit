"""Small REST transport: no SDK retries, secrets in URLs, or prompt logging.

One background event loop per process owns a pooled client, so provider calls
reuse warm TLS connections instead of handshaking on every learner question.
"""

import asyncio
import json
import os
import threading

import httpx

# httpx closes idle connections after 5s by default, which would re-handshake
# on nearly every chat message.
_LIMITS = httpx.Limits(max_connections=32, max_keepalive_connections=8, keepalive_expiry=60)
_lock = threading.Lock()
_runtime = None


class ProviderError(Exception):
    def __init__(self, status, retry_after=None):
        super().__init__(f"Tutor provider status {status}")
        self.status = status
        self.retry_after = retry_after


async def _new_client():
    return httpx.AsyncClient(limits=_LIMITS, follow_redirects=False)


def _io():
    """Process-local loop and client; a forked worker starts its own."""
    global _runtime
    with _lock:
        if _runtime is None or _runtime[0] != os.getpid():
            loop = asyncio.new_event_loop()
            threading.Thread(target=loop.run_forever, name="tutor-provider-io", daemon=True).start()
            client = asyncio.run_coroutine_threadsafe(_new_client(), loop).result()
            _runtime = (os.getpid(), loop, client)
        return _runtime[1], _runtime[2]


async def _post_json(client, url, headers, body, timeout):
    # This wall-clock budget also cancels a slowly streamed response body.
    async with asyncio.timeout(max(0.1, timeout)):
        for attempt in range(2):
            try:
                async with client.stream(
                    "POST",
                    url,
                    headers={
                        "Content-Type": "application/json",
                        "User-Agent": "git-it-tutor/1.0",
                        **headers,
                    },
                    json=body,
                    timeout=timeout,
                ) as response:
                    if response.status_code >= 300:
                        raise ProviderError(
                            response.status_code, response.headers.get("Retry-After")
                        )
                    chunks = bytearray()
                    async for chunk in response.aiter_bytes():
                        chunks.extend(chunk)
                        if len(chunks) > 1_000_000:
                            raise ProviderError(502)
                    return json.loads(chunks)
            except httpx.RemoteProtocolError:
                # A pooled connection the server already closed; retry once on a fresh one.
                if attempt:
                    raise
    return None


def post_json(url, headers, body, timeout):
    loop, client = _io()
    future = asyncio.run_coroutine_threadsafe(_post_json(client, url, headers, body, timeout), loop)
    try:
        # The coroutine enforces the budget; this only guards a stalled loop.
        return future.result(max(0.1, timeout) + 1)
    except (httpx.HTTPError, TimeoutError):
        future.cancel()
        raise ProviderError(503) from None
    except (ValueError, UnicodeError):
        raise ProviderError(502) from None
