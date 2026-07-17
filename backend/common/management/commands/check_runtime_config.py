from __future__ import annotations

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


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
