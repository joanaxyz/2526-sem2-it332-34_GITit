from __future__ import annotations

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone

from accounts.models import SessionRecord


class Command(BaseCommand):
    help = "Delete expired refresh-session audit rows after a retention window."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--retention-days",
            type=int,
            default=30,
            help="Keep expired/revoked session rows for this many days (default: 30).",
        )

    def handle(self, *args, **options):
        retention_days = options["retention_days"]
        if retention_days < 0:
            raise ValueError("--retention-days must be zero or greater.")
        cutoff = timezone.now() - timedelta(days=retention_days)
        deleted, _ = SessionRecord.objects.filter(
            Q(expires_at__lt=cutoff) | Q(revoked_at__lt=cutoff)
        ).delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted {deleted} expired session rows."))
