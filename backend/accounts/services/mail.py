"""Branded account emails: one shared layout, a plain-text twin, and a send that never raises."""

from __future__ import annotations

import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


def build_account_email(
    *,
    subject: str,
    template: str,
    context: dict,
    to: list[str],
) -> EmailMultiAlternatives:
    """Render accounts/email/<template>.txt and .html into one message.

    Brevo cannot embed inline images, so the logo and guide portrait are linked
    from the web app host, which serves them as static files and never sleeps.
    """

    asset_url = settings.EMAIL_ASSET_BASE_URL
    full_context = {
        **context,
        "site_url": settings.FRONTEND_BASE_URL,
        "logo_url": f"{asset_url}/email/git-it-logo.png",
        "mascot_url": f"{asset_url}/email/guide-mascot.png",
    }
    message = EmailMultiAlternatives(
        subject=subject,
        body=render_to_string(f"accounts/email/{template}.txt", full_context),
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=to,
    )
    message.attach_alternative(
        render_to_string(f"accounts/email/{template}.html", full_context),
        "text/html",
    )
    return message


def send_safely(message: EmailMultiAlternatives, *, context: str) -> None:
    try:
        message.send(fail_silently=False)
    except Exception:
        # Account-email endpoints answer the same way whether or not an account
        # exists, so a provider outage must never surface as a different response.
        logger.exception("Could not send %s email.", context)
