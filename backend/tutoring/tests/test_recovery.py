from concurrent.futures import Future
from unittest.mock import patch

import pytest
from django.core.cache import cache
from rest_framework.exceptions import Throttled

from tutoring.services.chat import chat
from tutoring.services.provider_transport import ProviderError
from tutoring.services.providers import generate, retry_seconds
from tutoring.services.scenario_recognition import UNMATCHED, Recognition


@pytest.fixture(autouse=True)
def configured_providers(settings):
    settings.GOOGLE_AI_STUDIO_API_KEY = "test-google"
    settings.GROQ_API_KEY = "test-groq"
    settings.TUTOR_GEMINI_MODELS = ("first",)
    cache.clear()


def transport_error(error):
    def start(*args):
        future = Future()
        future.set_exception(error)
        return future

    return start


def test_all_rate_limited_providers_report_their_remaining_cooldown():
    with patch(
        "tutoring.services.providers.start_json",
        side_effect=transport_error(ProviderError(429, "25")),
    ) as start:
        diagnostics = {}
        assert generate("system", [], diagnostics=diagnostics) is None
        assert diagnostics == {"unavailable_reason": "rate_limited", "retry_after_seconds": 25}
        assert start.call_count == 2
        assert generate("system", [], diagnostics=diagnostics) is None
        assert 1 <= diagnostics["retry_after_seconds"] <= 25
        assert start.call_count == 2


@pytest.mark.parametrize("value", [None, "bad", "nan", "inf"])
def test_bad_provider_retry_after_defaults_to_sixty_seconds(value):
    assert retry_seconds(value) == 60


def test_missing_keys_and_malformed_responses_are_unavailable(settings):
    settings.GOOGLE_AI_STUDIO_API_KEY = settings.GROQ_API_KEY = ""
    diagnostics = {}
    with patch("tutoring.services.providers.start_json", side_effect=AssertionError):
        assert generate("system", [], diagnostics=diagnostics) is None
    assert diagnostics["unavailable_reason"] == "unavailable"
    settings.GROQ_API_KEY = "test-key"
    future = Future()
    future.set_result({"choices": [{"message": {"content": " "}}]})
    with patch("tutoring.services.providers.start_json", return_value=future):
        assert generate("system", [], diagnostics=diagnostics) is None
    assert diagnostics["unavailable_reason"] == "unavailable"


def test_provider_timeouts_and_expired_budget_are_distinguished():
    diagnostics = {}
    with patch(
        "tutoring.services.providers.start_json",
        side_effect=transport_error(ProviderError(503, reason="timeout")),
    ):
        assert generate("system", [], diagnostics=diagnostics) is None
    assert diagnostics["unavailable_reason"] == "timeout"
    with patch("tutoring.services.providers.start_json", side_effect=AssertionError):
        assert generate("system", [], diagnostics=diagnostics, deadline=1) is None
    assert diagnostics["unavailable_reason"] == "timeout"


def test_malformed_nested_provider_data_rotates_and_recovers():
    future = Future()
    future.set_result({"candidates": [{"content": {"parts": ["malformed"]}}]})
    diagnostics = {}
    with patch("tutoring.services.providers.start_json", return_value=future) as start:
        assert generate("system", [], diagnostics=diagnostics) is None
    assert start.call_count == 2
    assert diagnostics["unavailable_reason"] == "unavailable"


def test_api_throttle_has_machine_readable_retry_timing(client):
    with patch("tutoring.views.TutorChatAPIView.check_throttles", side_effect=Throttled(wait=7.2)):
        response = client.post(
            "/api/tutoring/chat/", {"message": "hi", "context": {"surface": "home"}}, format="json"
        )
    assert response.status_code == 429
    assert response.data["retry_after_seconds"] == 8
    assert "short break" in response.data["detail"]


def test_guarded_rewrite_failure_reports_outage_and_uses_same_deadline(teaching_run):
    deadlines = []

    def provider(system, turns, *, deadline, diagnostics):
        deadlines.append(deadline)
        if len(deadlines) == 1:
            return "Stage README.md first."
        diagnostics.update(unavailable_reason="rate_limited", retry_after_seconds=60)
        return None

    with (
        patch("tutoring.services.chat.guide_run", return_value=(teaching_run, "git add <path>")),
        patch(
            "tutoring.services.chat.recognize_all",
            side_effect=lambda texts, **kwargs: [Recognition(UNMATCHED) for _ in texts],
        ),
        patch("tutoring.services.chat.generate", side_effect=provider),
    ):
        result = chat(teaching_run.player, "Explain this guide", {"surface": "command_guide"})
    assert result["response_kind"] == "unavailable"
    assert result["unavailable_reason"] == "rate_limited"
    assert result["retry_after_seconds"] == 60
    assert "README.md" not in result["reply"]
    assert len(deadlines) == 2 and deadlines[0] == deadlines[1]


def test_recognition_and_generation_share_a_thirty_second_budget():
    with (
        patch("tutoring.services.chat.time.monotonic", return_value=100),
        patch(
            "tutoring.services.chat.recognize_all", return_value=[Recognition(UNMATCHED)]
        ) as recognize,
        patch("tutoring.services.chat.generate", return_value="Hi! Ask me about Git.") as provider,
    ):
        chat(None, "hello", {"surface": "home"})
    assert recognize.call_args.kwargs["deadline"] == provider.call_args.kwargs["deadline"] == 130


@pytest.mark.parametrize("reason,status", [("budget_exhausted", 429), ("budget_unavailable", 503)])
def test_application_budget_stops_rotation_without_poisoning_provider_cooldowns(reason, status):
    with patch(
        "tutoring.services.providers.start_json",
        side_effect=transport_error(ProviderError(status, "25", reason=reason)),
    ) as start:
        diagnostics = {}
        assert generate("system", [], diagnostics=diagnostics) is None
        assert start.call_count == 1
        assert generate("system", [], diagnostics=diagnostics) is None
        assert start.call_count == 2  # Budget can recover without a model cooldown.
    assert diagnostics["unavailable_reason"] == (
        "rate_limited" if reason == "budget_exhausted" else "unavailable"
    )
