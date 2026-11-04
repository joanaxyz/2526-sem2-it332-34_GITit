"""Self-service account identity updates and proof of a replacement inbox."""

import secrets

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.utils import timezone
from django.utils.crypto import constant_time_compare, salted_hmac
from rest_framework.exceptions import Throttled, ValidationError

from accounts.models import AccountIdentity, PendingEmailChange
from accounts.services.mail import build_account_email, send_safely
from accounts.services.verification import (
    CODE_TTL,
    MAX_FAILED_ATTEMPTS,
    RESEND_COOLDOWN,
    EmailVerificationService,
)
from common.exceptions import Conflict


class AccountSettingsService:
    @staticmethod
    def _check_available(user, field, value):
        users = get_user_model().objects.exclude(pk=user.pk)
        identities = AccountIdentity.objects.exclude(user=user)
        if (
            users.filter(**{f"{field}__iexact": value}).exists()
            or identities.filter(**{f"{field}_key": value.casefold()}).exists()
        ):
            raise ValidationError({field: f"An account already exists for this {field}."})

    @staticmethod
    def _save_identity(user):
        try:
            with transaction.atomic():
                user.save(update_fields=["username", "email"])
                AccountIdentity.objects.update_or_create(
                    user=user,
                    defaults={
                        "username_key": user.username.casefold(),
                        "email_key": user.email.casefold(),
                    },
                )
        except IntegrityError as exc:
            raise Conflict("An account already exists for this username or email.") from exc

    @transaction.atomic
    def update(self, *, user, username=None, email=None):
        user = get_user_model().objects.select_for_update().get(pk=user.pk)
        username = user.username if username is None else username
        email = user.email if email is None else email
        self._check_available(user, "username", username)
        self._check_available(user, "email", email)
        pending_email = None
        if email.casefold() != user.email.casefold():
            self._request_email_change(user, email)
            pending_email = email
        user.username = username
        self._save_identity(user)
        return user, pending_email

    def _request_email_change(self, user, email):
        pending = PendingEmailChange.objects.filter(user=user).first()
        now = timezone.now()
        if pending and now - pending.last_sent_at < RESEND_COOLDOWN:
            if pending.email == email:
                return
            remaining = (RESEND_COOLDOWN - (now - pending.last_sent_at)).total_seconds()
            raise Throttled(wait=remaining, detail="Wait a minute before requesting another code.")
        code = f"{secrets.randbelow(1_000_000):06d}"
        PendingEmailChange.objects.update_or_create(
            user=user,
            defaults={
                "email": email,
                "code_hash": self._hash(user.pk, email, code),
                "code_expires_at": now + CODE_TTL,
                "failed_attempts": 0,
                "last_sent_at": now,
            },
        )
        message = build_account_email(
            subject=f"{code} is your GIT it! email change code",
            template="change_email",
            context={
                "user": user,
                "code": code,
                "expires_minutes": int(CODE_TTL.total_seconds() // 60),
            },
            to=[email],
        )
        transaction.on_commit(lambda: send_safely(message, context="email change"))

    @transaction.atomic
    def confirm_email(self, *, user, code):
        user = get_user_model().objects.select_for_update().get(pk=user.pk)
        pending = PendingEmailChange.objects.select_for_update().filter(user=user).first()
        if (
            pending is None
            or pending.code_expires_at <= timezone.now()
            or pending.failed_attempts >= MAX_FAILED_ATTEMPTS
        ):
            return None
        if not constant_time_compare(pending.code_hash, self._hash(user.pk, pending.email, code)):
            pending.failed_attempts += 1
            pending.save(update_fields=["failed_attempts"])
            return None
        self._check_available(user, "email", pending.email)
        user.email = pending.email
        self._save_identity(user)
        EmailVerificationService.mark_verified(user)
        pending.delete()
        return user

    @staticmethod
    def _hash(user_id, email, code):
        return salted_hmac(
            "accounts.email_change", f"{user_id}:{email}:{code}", algorithm="sha256"
        ).hexdigest()
