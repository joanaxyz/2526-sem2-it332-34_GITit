"""Backfill the default Arcane Spire kit into every existing player's registry.

Run after seeding assets so the ``arcane-spire`` tags exist:

    python manage.py seed_assets
    python manage.py grant_default_assets

Idempotent — only missing entitlements are created.
"""

from __future__ import annotations

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from assets.services import grant_default_assets


class Command(BaseCommand):
    help = "Grant the default Arcane Spire asset kit to all non-staff users."

    def handle(self, *args, **options):
        User = get_user_model()
        users = User.objects.filter(is_staff=False)
        total_users = 0
        total_grants = 0
        for user in users.iterator():
            granted = grant_default_assets(user)
            total_users += 1
            total_grants += granted
        self.stdout.write(
            self.style.SUCCESS(
                f"Granted {total_grants} new entitlements across {total_users} users."
            )
        )
