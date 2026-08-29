"""Idempotently create the optional first administrator from environment secrets."""

from __future__ import annotations

import os

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

ENVIRONMENT_KEYS = (
    "DJANGO_SUPERUSER_USERNAME",
    "DJANGO_SUPERUSER_EMAIL",
    "DJANGO_SUPERUSER_PASSWORD",
)


class Command(BaseCommand):
    help = "Create or refresh the optional environment-configured bootstrap superuser."

    @transaction.atomic
    def handle(self, *args, **options) -> None:
        values = {key: os.environ.get(key, "").strip() for key in ENVIRONMENT_KEYS}
        configured = [key for key, value in values.items() if value]
        if not configured:
            self.stdout.write("Bootstrap superuser not configured; skipping.")
            return

        missing = [key for key, value in values.items() if not value]
        if missing:
            raise CommandError(
                "Bootstrap superuser configuration is incomplete; missing " + ", ".join(missing)
            )

        User = get_user_model()
        username = values["DJANGO_SUPERUSER_USERNAME"]
        email = User.objects.normalize_email(values["DJANGO_SUPERUSER_EMAIL"])
        password = values["DJANGO_SUPERUSER_PASSWORD"]

        user = User.objects.select_for_update().filter(username__iexact=username).first()
        created = user is None
        if created:
            user = User(username=username)

        user.email = email
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        validate_password(password, user=user)
        user.set_password(password)
        user.save()

        action = "created" if created else "updated"
        self.stdout.write(self.style.SUCCESS(f"Bootstrap superuser {action}."))
