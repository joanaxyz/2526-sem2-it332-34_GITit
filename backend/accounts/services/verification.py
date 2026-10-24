"""Sign-up email verification by six-digit one-time code."""

from __future__ import annotations

import secrets
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from django.utils.crypto import constant_time_compare, salted_hmac

from accounts.models import EmailVerification
from accounts.services.mail import build_account_email, send_safely

CODE_TTL = timedelta(minutes=15)
RESEND_COOLDOWN = timedelta(seconds=60)
# Five guesses at a one-in-a-million code, then the code is burned and the
# player must request a new one (itself rate-limited by RESEND_COOLDOWN).
MAX_FAILED_ATTEMPTS = 5


class EmailVerificationService:
    resend_message = "If that account still needs verification, a new code is on its way."
    invalid_code_message = "That code is incorrect or has expired. Check it or send a new one."

    @staticmethod
    def is_pending(user) -> bool:
        return EmailVerification.objects.filter(user=user, verified_at__isnull=True).exists()

    def start(self, user) -> None:
        """Open a pending verification for a just-registered account and email its code."""

        verification = EmailVerification.objects.create(user=user)
        self._issue_and_send(verification)

    @transaction.atomic
    def resend(self, *, email: str) -> None:
        verification = self._pending_for_email(email)
        if verification is None or self._cooling_down(verification):
            return
        self._issue_and_send(verification)

    @transaction.atomic
    def send_if_no_live_code(self, user) -> None:
        """A blocked sign-in mails a fresh code only when the last one is unusable."""

        verification = (
            EmailVerification.objects.select_for_update()
            .filter(user=user, verified_at__isnull=True)
            .first()
        )
        if verification is None or self._cooling_down(verification):
            return
        if self._code_is_live(verification):
            return
        self._issue_and_send(verification)

    @transaction.atomic
    def confirm(self, *, email: str, code: str):
        """Return the verified user, or None for any wrong, expired, or spent code."""

        verification = self._pending_for_email(email)
        if verification is None or not self._code_is_live(verification):
            return None
        if not constant_time_compare(
            verification.code_hash, self._hash(verification.user_id, code)
        ):
            verification.failed_attempts += 1
            verification.save(update_fields=["failed_attempts"])
            return None
        verification.verified_at = timezone.now()
        verification.code_hash = ""
        verification.code_expires_at = None
        verification.save(update_fields=["verified_at", "code_hash", "code_expires_at"])
        return verification.user

    @staticmethod
    def mark_verified(user) -> None:
        """A completed password reset proves the inbox, so it also verifies it."""

        EmailVerification.objects.filter(user=user, verified_at__isnull=True).update(
            verified_at=timezone.now(), code_hash="", code_expires_at=None
        )

    @staticmethod
    def _pending_for_email(email: str) -> EmailVerification | None:
        User = get_user_model()
        normalized_email = User.objects.normalize_email(email).lower()
        return (
            EmailVerification.objects.select_for_update()
            .select_related("user")
            .filter(
                user__email__iexact=normalized_email,
                user__is_active=True,
                verified_at__isnull=True,
            )
            .first()
        )

    @staticmethod
    def _cooling_down(verification: EmailVerification) -> bool:
        return (
            verification.last_sent_at is not None
            and timezone.now() - verification.last_sent_at < RESEND_COOLDOWN
        )

    @staticmethod
    def _code_is_live(verification: EmailVerification) -> bool:
        return (
            bool(verification.code_hash)
            and verification.code_expires_at is not None
            and verification.code_expires_at > timezone.now()
            and verification.failed_attempts < MAX_FAILED_ATTEMPTS
        )

    @staticmethod
    def _hash(user_id: int, code: str) -> str:
        return salted_hmac(
            "accounts.email_verification", f"{user_id}:{code}", algorithm="sha256"
        ).hexdigest()

    def _issue_and_send(self, verification: EmailVerification) -> None:
        code = f"{secrets.randbelow(1_000_000):06d}"
        now = timezone.now()
        verification.code_hash = self._hash(verification.user_id, code)
        verification.code_expires_at = now + CODE_TTL
        verification.failed_attempts = 0
        verification.last_sent_at = now
        verification.save(
            update_fields=["code_hash", "code_expires_at", "failed_attempts", "last_sent_at"]
        )
        user = verification.user
        message = build_account_email(
            subject=f"{code} is your GIT it! verification code",
            template="verify_email",
            context={
                "user": user,
                "code": code,
                "expires_minutes": int(CODE_TTL.total_seconds() // 60),
            },
            to=[user.email],
        )
        # Mail only once the code is committed, so a rolled-back sign-up never
        # sends a code for an account that does not exist.
        transaction.on_commit(lambda: send_safely(message, context="email verification"))
