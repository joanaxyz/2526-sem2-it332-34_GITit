"""Ordered provider failover for tutor replies: configured Gemini models, then Groq.

Attempts start in that order. One that has not answered within the hedge delay
keeps running while the next one starts, and the first usable reply wins, so a
stalled model costs the learner the hedge delay instead of its whole budget.
"""

from __future__ import annotations

import hashlib
import json
import logging
import math
import time
from collections.abc import Callable
from concurrent.futures import FIRST_COMPLETED, wait
from dataclasses import dataclass
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime

from django.conf import settings
from django.core.cache import cache

from tutoring.services.provider_transport import ProviderError, collect, start_json

logger = logging.getLogger(__name__)

# Identical conversations (topic chips especially) reuse a reply that already
# passed the answer guard instead of waiting on another provider round trip.
REPLY_TTL = 86400
MAX_OUTPUT_TOKENS = 1024
# A model outrun after the hedge delay sits out for a while, so the learners
# after it go straight to a model that is answering instead of each waiting.
SLOW_COOLDOWN = 120


def cooldown_key(provider, model, api_key):
    scope = hashlib.sha256(api_key.encode()).hexdigest()[:16]
    return f"tutor:cooldown:{provider}:{scope}:{model}"


def retry_seconds(value):
    try:
        return max(1, min(86400, int(float(value))))
    except (ValueError, TypeError, OverflowError):
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


def _gemini(model, key, system, turns, effort=""):
    """URL, headers, body and reply reader for one Gemini attempt."""
    config = {"temperature": 0.3, "maxOutputTokens": MAX_OUTPUT_TOKENS}
    if effort:
        config["thinkingConfig"] = {"thinkingLevel": effort.upper()}
    return (
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
        _gemini_text,
    )


def _gemini_text(response):
    return "".join(part.get("text", "") for part in response["candidates"][0]["content"]["parts"])


def _groq(model, key, system, turns, effort=""):
    """URL, headers, body and reply reader for one Groq attempt."""
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
    return (
        "https://api.groq.com/openai/v1/chat/completions",
        {"Authorization": f"Bearer {key}"},
        body,
        _groq_text,
    )


def _groq_text(response):
    return response["choices"][0]["message"]["content"]


def reply_memo(system, turns):
    digest = hashlib.sha256(json.dumps([system, list(turns)], sort_keys=True).encode()).hexdigest()
    return f"tutor:reply:{digest}"


@dataclass(frozen=True)
class Attempt:
    provider: str
    model: str
    circuit: str
    read: Callable[[dict], str]
    started: float


def _reply(attempt, future, failures):
    """The finished attempt's text, or None once its failure is recorded.

    A ProviderError that should end rotation propagates.
    """
    try:
        text = attempt.read(collect(future, 0))
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Empty reply")
    except ProviderError as exc:
        logger.warning(
            "Tutor provider unavailable provider=%s model=%s status=%s",
            attempt.provider,
            attempt.model,
            exc.status,
        )
        if exc.reason in {"budget_exhausted", "budget_unavailable"}:
            # An application budget isn't a provider failure. End rotation
            # without poisoning model cooldowns (operators may raise the cap).
            failure = {"reason": "unavailable", "budget": True}
            if exc.reason == "budget_exhausted":
                failure = {
                    "reason": "rate_limited",
                    "until": time.time() + retry_seconds(exc.retry_after),
                    "budget": True,
                }
            failures.append(failure)
            raise
        if exc.status == 429:
            seconds = retry_seconds(exc.retry_after)
            failure = {"reason": "rate_limited", "until": time.time() + seconds}
            cache.set(attempt.circuit, failure, timeout=seconds)
            failures.append(failure)
            return None
        failure = {
            "reason": "timeout"
            if exc.reason == "timeout" or exc.status in {408, 504}
            else "unavailable",
            "until": time.time() + 10,
        }
        failures.append(failure)
        if exc.status in {408, 500, 502, 503, 504}:
            cache.set(attempt.circuit, failure, timeout=10)
            return None
        # Bad credentials/configuration are not rate-limit rotation triggers.
        raise
    except (AttributeError, KeyError, IndexError, TypeError, ValueError):
        failures.append({"reason": "unavailable"})
        # A blocked or empty candidate; the next provider may still answer.
        logger.warning(
            "Tutor rejected malformed response provider=%s model=%s",
            attempt.provider,
            attempt.model,
        )
        return None
    logger.info(
        "Tutor replied provider=%s model=%s elapsed_ms=%d",
        attempt.provider,
        attempt.model,
        (time.monotonic() - attempt.started) * 1000,
    )
    return text.strip()


def generate(system, turns, *, deadline=None, diagnostics=None):
    """Return provider text or None. Callers own validation of everything returned."""
    if diagnostics is not None:
        diagnostics.clear()
    chain = iter(
        [
            ("gemini", *model_entry(entry), settings.GOOGLE_AI_STUDIO_API_KEY, _gemini)
            for entry in settings.TUTOR_GEMINI_MODELS
        ]
        + [("groq", *model_entry(settings.TUTOR_GROQ_MODEL), settings.GROQ_API_KEY, _groq)]
    )
    hedge = settings.TUTOR_PROVIDER_HEDGE_SECONDS
    deadline = min(
        deadline or float("inf"), time.monotonic() + settings.TUTOR_PROVIDER_DEADLINE_SECONDS
    )
    running = {}
    failures = []

    def launch():
        """Start the next attempt with a key and no cooldown; False when none is left."""
        for provider, model, effort, key, build in chain:
            started = time.monotonic()
            if not key or started >= deadline:
                continue
            circuit = cooldown_key(provider, model, key)
            cooling = cache.get(circuit)
            if cooling:
                failures.append(cooling if isinstance(cooling, dict) else {"reason": "unavailable"})
                continue
            url, headers, body, read = build(model, key, system, turns, effort)
            budget = min(settings.TUTOR_PROVIDER_ATTEMPT_SECONDS, deadline - started)
            running[start_json(url, headers, body, budget)] = Attempt(
                provider, model, circuit, read, started
            )
            return True
        return False

    rotating = True
    try:
        while True:
            now = time.monotonic()
            if rotating and all(now - attempt.started >= hedge for attempt in running.values()):
                # Nothing running is still inside its hedge window (or nothing is
                # running): keep waiting on those, and start the next model alongside.
                rotating = launch()
                continue
            if not running or now >= deadline:
                break  # Budgets end by the deadline; that check only guards a stalled loop.
            newest = max(attempt.started for attempt in running.values())
            until = min(newest + hedge, deadline) if rotating else deadline
            done, _ = wait(running, timeout=max(0, until - now), return_when=FIRST_COMPLETED)
            for future in done:
                attempt = running.pop(future)
                try:
                    text = _reply(attempt, future, failures)
                except ProviderError:
                    rotating = False
                    continue
                if text is None:
                    continue
                finished = time.monotonic()
                for other, slower in running.items():
                    if not other.done() and finished - slower.started >= hedge:
                        logger.warning(
                            "Tutor provider slow provider=%s model=%s",
                            slower.provider,
                            slower.model,
                        )
                        cache.set(slower.circuit, True, timeout=SLOW_COOLDOWN)
                return text
    finally:
        if running:
            failures.append({"reason": "timeout"})
        for future in running:
            future.cancel()
    if diagnostics is not None:
        reason = "unavailable"
        budget_failure = next((failure for failure in failures if failure.get("budget")), None)
        if budget_failure is not None:
            # The shared budget gates every model, even one whose own cooldown
            # ends sooner. Earlier provider failures cannot shorten its wait.
            reason = budget_failure["reason"]
            if reason == "rate_limited":
                diagnostics["retry_after_seconds"] = max(
                    1, math.ceil(budget_failure["until"] - time.time())
                )
        elif failures and all(failure["reason"] == "rate_limited" for failure in failures):
            reason = "rate_limited"
            diagnostics["retry_after_seconds"] = max(
                1, math.ceil(min(f["until"] for f in failures) - time.time())
            )
        elif (
            any(failure["reason"] == "timeout" for failure in failures)
            or time.monotonic() >= deadline
        ):
            reason = "timeout"
        diagnostics["unavailable_reason"] = reason
    return None
