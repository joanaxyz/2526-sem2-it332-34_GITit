from __future__ import annotations

import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import serializers

from accounts.models import AccountSecurity
from accounts.services.core import TokenBlacklistService

logger = logging.getLogger(__name__)


class PasswordResetService:
    public_message = "If an account exists for that email, a reset link has been sent."

    def request(self, *, email: str) -> None:
        User = get_user_model()
        normalized_email = User.objects.normalize_email(email).lower()
        user = User.objects.filter(email__iexact=normalized_email, is_active=True).first()
        if user is None or not user.has_usable_password():
            return

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_url = f"{settings.FRONTEND_BASE_URL}/reset-password/{uid}/{token}"
        context = {"user": user, "reset_url": reset_url}
        subject = "Reset your GIT it! password"
        text_body = render_to_string("accounts/email/password_reset.txt", context)
        html_body = render_to_string("accounts/email/password_reset.html", context)
        message = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        message.attach_alternative(html_body, "text/html")
        self._send_safely(message, context="password reset")

    def resolve_user(self, *, uid: str, token: str):
        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = get_user_model().objects.get(pk=user_id, is_active=True)
        except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
            return None
        if not default_token_generator.check_token(user, token):
            return None
        return user

    @transaction.atomic
    def reset(self, *, user, password: str) -> None:
        try:
            validate_password(password, user=user)
        except DjangoValidationError as exc:
            raise serializers.ValidationError({"password": exc.messages}) from exc
        user.set_password(password)
        user.save(update_fields=["password"])
        self._invalidate_sessions(user)
        self._queue_password_changed_email(user)

    @transaction.atomic
    def change(self, *, user, current_password: str, password: str) -> None:
        if not user.check_password(current_password):
            raise serializers.ValidationError({"current_password": "Current password is incorrect."})
        try:
            validate_password(password, user=user)
        except DjangoValidationError as exc:
            raise serializers.ValidationError({"password": exc.messages}) from exc
        user.set_password(password)
        user.save(update_fields=["password"])
        self._invalidate_sessions(user)
        self._queue_password_changed_email(user)

    @staticmethod
    def _send_safely(message: EmailMultiAlternatives, *, context: str) -> None:
        try:
            message.send(fail_silently=False)
        except Exception:
            # Password-reset request responses must not disclose whether an
            # account exists by failing only for registered addresses.
            logger.exception("Could not send %s email.", context)

    def _queue_password_changed_email(self, user) -> None:
        def send_notification() -> None:
            context = {"user": user}
            message = EmailMultiAlternatives(
                subject="Your GIT it! password was changed",
                body=render_to_string("accounts/email/password_changed.txt", context),
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email],
            )
            message.attach_alternative(
                render_to_string("accounts/email/password_changed.html", context),
                "text/html",
            )
            self._send_safely(message, context="password changed")

        transaction.on_commit(send_notification)

    @staticmethod
    def _invalidate_sessions(user) -> None:
        security, _created = AccountSecurity.objects.select_for_update().get_or_create(user=user)
        security.auth_version += 1
        security.password_changed_at = timezone.now()
        security.save(update_fields=["auth_version", "password_changed_at", "updated_at"])
        TokenBlacklistService().revoke_all_for_user(user)
