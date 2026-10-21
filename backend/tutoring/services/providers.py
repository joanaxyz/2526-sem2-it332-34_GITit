"""Ordered provider failover for tutor replies: configured Gemini models, then Groq."""

from __future__ import annotations

import hashlib
import json
import logging
import time
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime

from django.conf import settings
from django.core.cache import cache

from tutoring.services.provider_transport import ProviderError, post_json

logger = logging.getLogger(__name__)

# Identical conversations (topic chips especially) reuse a reply that already
# passed the answer guard instead of waiting on another provider round trip.
REPLY_TTL = 86400
MAX_OUTPUT_TOKENS = 1024


def cooldown_key(provider, model, api_key):
    scope = hashlib.sha256(api_key.encode()).hexdigest()[:16]
    return f"tutor:cooldown:{provider}:{scope}:{model}"


def retry_seconds(value):
    try:
        return max(1, min(86400, int(float(value))))
    except (ValueError, TypeError):
        try:
            return max(
                1,
                min(86400, int((parsedate_to_datetime(value) - datetime.now(UTC)).total_seconds())),
            )
        except (ValueError, TypeError, OverflowError):
            return 60


def model_entry(value):
    """`model` or `model:effort`; effort maps to the provider's reasoning control."""
    model, _, effort = value.partition(":")
    return model.strip(), effort.strip().lower()


def _gemini(model, key, system, turns, timeout, effort=""):
    config = {"temperature": 0.3, "maxOutputTokens": MAX_OUTPUT_TOKENS}
    if effort:
        config["thinkingConfig"] = {"thinkingLevel": effort.upper()}
    response = post_json(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        {"x-goog-api-key": key},
        {
            "systemInstruction": {"parts": [{"text": system}]},
            "contents": [
                {
                    "role": "model" if turn["role"] == "assistant" else "user",
                    "parts": [{"text": turn["text"]}],
                }
                for turn in turns
            ],
            "generationConfig": config,
        },
        timeout,
    )
    return "".join(part.get("text", "") for part in response["candidates"][0]["content"]["parts"])


def _groq(model, key, system, turns, timeout, effort=""):
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            *({"role": turn["role"], "content": turn["text"]} for turn in turns),
        ],
        "temperature": 0.3,
        "max_completion_tokens": MAX_OUTPUT_TOKENS,
    }
    if effort:
        body["reasoning_effort"] = effort
        body["include_reasoning"] = False
    response = post_json(
        "https://api.groq.com/openai/v1/chat/completions",
        {"Authorization": f"Bearer {key}"},
        body,
        timeout,
    )
    return response["choices"][0]["message"]["content"]


def reply_memo(system, turns):
    digest = hashlib.sha256(json.dumps([system, list(turns)], sort_keys=True).encode()).hexdigest()
    return f"tutor:reply:{digest}"


def generate(system, turns):
    """Return provider text or None. Callers own validation of everything returned."""
    chain = [
        ("gemini", *model_entry(entry), settings.GOOGLE_AI_STUDIO_API_KEY, _gemini)
        for entry in settings.TUTOR_GEMINI_MODELS
    ] + [("groq", *model_entry(settings.TUTOR_GROQ_MODEL), settings.GROQ_API_KEY, _groq)]
    deadline = time.monotonic() + settings.TUTOR_PROVIDER_DEADLINE_SECONDS
    for provider, model, effort, key, call in chain:
        if not key or time.monotonic() >= deadline:
            continue
        circuit = cooldown_key(provider, model, key)
        if cache.get(circuit):
            continue
        started = time.monotonic()
        try:
            budget = min(settings.TUTOR_PROVIDER_ATTEMPT_SECONDS, deadline - started)
            text = call(model, key, system, turns, budget, effort)
            if not isinstance(text, str) or not text.strip():
                raise ValueError("Empty reply")
            logger.info(
                "Tutor replied provider=%s model=%s elapsed_ms=%d",
                provider,
                model,
                (time.monotonic() - started) * 1000,
            )
            return text.strip()
        except ProviderError as exc:
            logger.warning(
                "Tutor provider unavailable provider=%s model=%s status=%s",
                provider,
                model,
                exc.status,
            )
            if exc.status == 429:
                cache.set(circuit, True, timeout=retry_seconds(exc.retry_after))
                continue
            if exc.status in {408, 500, 502, 503, 504}:
                cache.set(circuit, True, timeout=10)
                continue
            # Bad credentials/configuration are not rate-limit rotation triggers.
            return None
        except (KeyError, IndexError, TypeError, ValueError):
            # A blocked or empty candidate; the next provider may still answer.
            logger.warning(
                "Tutor rejected malformed response provider=%s model=%s", provider, model
            )
            continue
    return None
