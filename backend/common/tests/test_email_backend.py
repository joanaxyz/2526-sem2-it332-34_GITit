from __future__ import annotations

import base64
from unittest import mock

import pytest
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import EmailMultiAlternatives

from common.email_backends import MailgunEmailBackend


def test_mailgun_backend_sends_mime_message_over_https(monkeypatch):
    monkeypatch.setenv("MAILGUN_API_KEY", "key-test-secret")
    monkeypatch.setenv("MAILGUN_DOMAIN", "mg.example.com")
    monkeypatch.setenv("MAILGUN_API_BASE_URL", "https://api.mailgun.net")

    response = mock.MagicMock()
    response.status = 200
    response.read.return_value = b'{"id":"queued"}'
    response.__enter__.return_value = response
    response.__exit__.return_value = False

    message = EmailMultiAlternatives(
        subject="Reset your GIT it! password",
        body="Plain reset body",
        from_email="GIT it! <no-reply@mg.example.com>",
        to=["student@example.com"],
    )
    message.attach_alternative("<p>HTML reset body</p>", "text/html")

    with mock.patch("common.email_backends.urlopen", return_value=response) as urlopen:
        sent = MailgunEmailBackend().send_messages([message])

    assert sent == 1
    request = urlopen.call_args.args[0]
    assert request.full_url == "https://api.mailgun.net/v3/mg.example.com/messages.mime"
    assert urlopen.call_args.kwargs["timeout"] == 10.0
    assert request.get_header("Content-type").startswith("multipart/form-data; boundary=")
    expected_auth = base64.b64encode(b"api:key-test-secret").decode("ascii")
    assert request.get_header("Authorization") == f"Basic {expected_auth}"
    assert b"student@example.com" in request.data
    assert b"Plain reset body" in request.data
    assert b"HTML reset body" in request.data


def test_mailgun_backend_requires_api_key_and_domain(monkeypatch):
    monkeypatch.delenv("MAILGUN_API_KEY", raising=False)
    monkeypatch.delenv("MAILGUN_DOMAIN", raising=False)

    message = EmailMultiAlternatives(
        subject="Test",
        body="Body",
        from_email="no-reply@example.com",
        to=["student@example.com"],
    )

    with pytest.raises(ImproperlyConfigured, match="MAILGUN_API_KEY, MAILGUN_DOMAIN"):
        MailgunEmailBackend().send_messages([message])


def test_mailgun_backend_honors_fail_silently(monkeypatch):
    monkeypatch.setenv("MAILGUN_API_KEY", "key-test-secret")
    monkeypatch.setenv("MAILGUN_DOMAIN", "mg.example.com")

    message = EmailMultiAlternatives(
        subject="Test",
        body="Body",
        from_email="no-reply@mg.example.com",
        to=["student@example.com"],
    )

    with mock.patch("common.email_backends.urlopen", side_effect=OSError("provider unavailable")):
        assert MailgunEmailBackend(fail_silently=True).send_messages([message]) == 0
