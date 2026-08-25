"""Transactional email backends used by production deployments."""

from __future__ import annotations

import base64
import os
import uuid
from urllib.parse import quote
from urllib.request import Request, urlopen

from django.core.exceptions import ImproperlyConfigured
from django.core.mail.backends.base import BaseEmailBackend


class MailgunEmailBackend(BaseEmailBackend):
    """Send Django email messages through Mailgun's HTTPS MIME API.

    Render Free blocks outbound SMTP ports, so production uses Mailgun's REST
    endpoint over HTTPS instead. Keeping this as a Django email backend means
    application code can continue using EmailMessage/EmailMultiAlternatives.
    """

    def __init__(
        self,
        *args,
        api_key: str | None = None,
        domain: str | None = None,
        api_base_url: str | None = None,
        timeout: float | None = None,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.api_key = (
            api_key if api_key is not None else os.getenv("MAILGUN_API_KEY", "")
        ).strip()
        self.domain = (
            domain if domain is not None else os.getenv("MAILGUN_DOMAIN", "")
        ).strip()
        self.api_base_url = (
            api_base_url
            if api_base_url is not None
            else os.getenv("MAILGUN_API_BASE_URL", "https://api.mailgun.net")
        ).strip().rstrip("/")
        if timeout is None:
            raw_timeout = os.getenv("MAILGUN_TIMEOUT_SECONDS", "10").strip() or "10"
            try:
                timeout = float(raw_timeout)
            except ValueError as exc:
                raise ImproperlyConfigured("MAILGUN_TIMEOUT_SECONDS must be a number.") from exc
        self.timeout = timeout

    def send_messages(self, email_messages) -> int:
        if not email_messages:
            return 0

        sent = 0
        for email_message in email_messages:
            recipients = email_message.recipients()
            if not recipients:
                continue
            try:
                self._send_message(email_message, recipients)
            except Exception:
                if self.fail_silently:
                    continue
                raise
            sent += 1
        return sent

    def _send_message(self, email_message, recipients: list[str]) -> None:
        self._validate_configuration()
        mime_bytes = email_message.message().as_bytes()
        body, boundary = _multipart_mime_payload(recipients, mime_bytes)
        credentials = base64.b64encode(f"api:{self.api_key}".encode()).decode("ascii")
        domain = quote(self.domain, safe="")
        request = Request(
            f"{self.api_base_url}/v3/{domain}/messages.mime",
            data=body,
            headers={
                "Authorization": f"Basic {credentials}",
                "Content-Type": f"multipart/form-data; boundary={boundary}",
                "User-Agent": "GIT-it-MailgunBackend/1.0",
            },
            method="POST",
        )

        with urlopen(request, timeout=self.timeout) as response:
            status = getattr(response, "status", None)
            if status is None:
                status = response.getcode()
            if not 200 <= int(status) < 300:
                raise RuntimeError(f"Mailgun returned HTTP {status}.")
            response.read()

    def _validate_configuration(self) -> None:
        missing = []
        if not self.api_key:
            missing.append("MAILGUN_API_KEY")
        if not self.domain:
            missing.append("MAILGUN_DOMAIN")
        if missing:
            raise ImproperlyConfigured(
                "Mailgun email backend is missing required configuration: " + ", ".join(missing)
            )
        if not self.api_base_url.startswith("https://"):
            raise ImproperlyConfigured("MAILGUN_API_BASE_URL must use HTTPS.")
        if self.timeout <= 0:
            raise ImproperlyConfigured("MAILGUN_TIMEOUT_SECONDS must be greater than 0.")


def _multipart_mime_payload(recipients: list[str], mime_bytes: bytes) -> tuple[bytes, str]:
    """Build Mailgun's multipart/form-data payload without an HTTP dependency."""

    boundary = f"git-it-mailgun-{uuid.uuid4().hex}"
    boundary_bytes = boundary.encode("ascii")
    chunks: list[bytes] = []

    for recipient in recipients:
        chunks.extend(
            [
                b"--" + boundary_bytes + b"\r\n",
                b'Content-Disposition: form-data; name="to"\r\n\r\n',
                str(recipient).encode(),
                b"\r\n",
            ]
        )

    chunks.extend(
        [
            b"--" + boundary_bytes + b"\r\n",
            b'Content-Disposition: form-data; name="message"; filename="message.eml"\r\n',
            b"Content-Type: message/rfc822\r\n\r\n",
            mime_bytes,
            b"\r\n--" + boundary_bytes + b"--\r\n",
        ]
    )
    return b"".join(chunks), boundary
