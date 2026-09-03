from __future__ import annotations

import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

MAILGUN_BACKEND = "common.email_backends.MailgunEmailBackend"


class Command(BaseCommand):
    help = "Validate deployment-critical runtime configuration."

    def handle(self, *args, **options):
        errors: list[str] = []
        warnings: list[str] = []
        engine = settings.DATABASES["default"].get("ENGINE", "")

        if not settings.DEBUG:
            if "sqlite" in engine:
                errors.append("Production must use PostgreSQL, not SQLite.")
            if not settings.DATABASES["default"].get("CONN_HEALTH_CHECKS"):
                errors.append("DATABASE_CONN_HEALTH_CHECKS must be enabled in production.")
            if not settings.FRONTEND_BASE_URL.startswith("https://"):
                errors.append("FRONTEND_BASE_URL must use HTTPS in production.")
            if settings.SECURE_SSL_REDIRECT and not settings.DJANGO_TRUST_PROXY_HEADERS:
                warnings.append(
                    "SECURE_SSL_REDIRECT is enabled without trusted proxy headers. "
                    "This is correct only when Django terminates TLS directly."
                )

            if settings.EMAIL_BACKEND == MAILGUN_BACKEND:
                for key in ("MAILGUN_API_KEY", "MAILGUN_DOMAIN"):
                    if not os.environ.get(key, "").strip():
                        errors.append(
                            f"{key} is required when the Mailgun email backend is enabled."
                        )
                api_base_url = os.environ.get(
                    "MAILGUN_API_BASE_URL", "https://api.mailgun.net"
                ).strip()
                if not api_base_url.startswith("https://"):
                    errors.append("MAILGUN_API_BASE_URL must use HTTPS.")
                if "@" not in settings.DEFAULT_FROM_EMAIL:
                    errors.append("DEFAULT_FROM_EMAIL must contain a sender email address.")

        for warning in warnings:
            self.stdout.write(self.style.WARNING(f"WARNING: {warning}"))
        if errors:
            raise CommandError("Runtime configuration invalid:\n- " + "\n- ".join(errors))

        self.stdout.write(
            self.style.SUCCESS(
                "Runtime configuration is valid "
                f"(debug={settings.DEBUG}, database={engine}, version={settings.DEPLOYMENT_VERSION})."
            )
        )
