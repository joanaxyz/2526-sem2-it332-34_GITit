from dataclasses import dataclass

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.utils import timezone
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import SessionRecord
from common.exceptions import Conflict
from progress.models import StreakRecord, StudentProgress


@dataclass(frozen=True)
class IssuedTokens:
    access: str
    refresh: str
    refresh_jti: str


class UserService:
    @transaction.atomic
    def register_account(
        self,
        *,
        username: str,
        email: str,
        password: str,
    ):
        User = get_user_model()
        normalized_username = username.strip()
        normalized_email = User.objects.normalize_email(email).lower()

        if User.objects.filter(username__iexact=normalized_username).exists():
            raise Conflict("An account already exists for this username.")
        if User.objects.filter(email__iexact=normalized_email).exists():
            raise Conflict("An account already exists for this email.")

        user = User.objects.create_user(
            username=normalized_username,
            email=normalized_email,
            password=password,
        )
        StudentProgress.objects.create(user=user)
        StreakRecord.objects.create(user=user)
        return user


class TokenBlacklistService:
    key_prefix = "revoked-refresh:"

    def revoke(self, refresh_token: str) -> None:
        try:
            token = RefreshToken(refresh_token)
            jti = token["jti"]
            exp = token["exp"]
            ttl = max(0, exp - int(timezone.now().timestamp()))
            cache.set(f"{self.key_prefix}{jti}", True, timeout=ttl)
            SessionRecord.objects.filter(refresh_jti=jti, revoked_at__isnull=True).update(
                revoked_at=timezone.now()
            )
        except Exception:
            return

    def is_revoked(self, refresh_token: str) -> bool:
        try:
            token = RefreshToken(refresh_token)
            return bool(cache.get(f"{self.key_prefix}{token['jti']}"))
        except Exception:
            return False


class TokenService:
    blacklist_service = TokenBlacklistService()

    @staticmethod
    def _normalize_identifier(identifier: str) -> str:
        normalized = identifier.strip().lower()
        return normalized or "unknown"

    def _lockout_key(self, identifier: str, ip_address: str | None) -> str:
        safe_ip = (ip_address or "unknown").strip().lower() or "unknown"
        return f"login-lockout-until:{self._normalize_identifier(identifier)}:{safe_ip}"

    def _attempt_key(self, identifier: str, ip_address: str | None) -> str:
        safe_ip = (ip_address or "unknown").strip().lower() or "unknown"
        return f"login-attempts:{self._normalize_identifier(identifier)}:{safe_ip}"

    def get_lockout_remaining(self, *, identifier: str, ip_address: str | None) -> int:
        lockout_key = self._lockout_key(identifier, ip_address)
        try:
            lockout_until = cache.get(lockout_key)
        except Exception:
            return 0
        if lockout_until is None:
            return 0
        now_timestamp = int(timezone.now().timestamp())
        return max(0, int(lockout_until) - now_timestamp)

    def register_failed_login(self, *, identifier: str, ip_address: str | None) -> int:
        attempt_key = self._attempt_key(identifier, ip_address)
        lockout_key = self._lockout_key(identifier, ip_address)
        max_attempts = int(getattr(settings, "AUTH_LOGIN_MAX_ATTEMPTS", 5))
        lockout_seconds = int(getattr(settings, "AUTH_LOGIN_LOCKOUT_SECONDS", 300))

        try:
            attempts = cache.get(attempt_key, 0) + 1
            cache.set(attempt_key, attempts, timeout=lockout_seconds)
            if attempts >= max_attempts:
                lockout_until = int(timezone.now().timestamp()) + lockout_seconds
                cache.set(lockout_key, lockout_until, timeout=lockout_seconds)
                cache.delete(attempt_key)
                return lockout_seconds
        except Exception:
            pass
        return 0

    def clear_failed_login(self, *, identifier: str, ip_address: str | None) -> None:
        try:
            cache.delete(self._attempt_key(identifier, ip_address))
            cache.delete(self._lockout_key(identifier, ip_address))
        except Exception:
            pass

    def issue_for_user(self, user, request=None) -> IssuedTokens:
        refresh = RefreshToken.for_user(user)
        jti = str(refresh["jti"])
        SessionRecord.objects.create(
            user=user,
            refresh_jti=jti,
            user_agent=(request.META.get("HTTP_USER_AGENT", "") if request else ""),
            ip_address=(request.META.get("REMOTE_ADDR") if request else None),
        )
        return IssuedTokens(access=str(refresh.access_token), refresh=str(refresh), refresh_jti=jti)

    def authenticate_account(self, *, identifier: str, password: str, request=None):
        User = get_user_model()
        normalized_identifier = identifier.strip()

        if "@" in normalized_identifier:
            email = User.objects.normalize_email(normalized_identifier).lower()
            user = User.objects.filter(email__iexact=email).first()
        else:
            user = User.objects.filter(username__iexact=normalized_identifier).first()

        if user is None or user.is_staff:
            return None

        user = authenticate(request=request, username=user.username, password=password)
        if user is None or user.is_staff:
            return None
        return user

    def refresh_access(self, refresh_token: str) -> IssuedTokens:
        if not refresh_token:
            raise TokenError("Missing refresh token.")
        if self.blacklist_service.is_revoked(refresh_token):
            raise TokenError("Refresh token revoked.")
        refresh = RefreshToken(refresh_token)
        user_id = refresh["user_id"]
        try:
            user = get_user_model().objects.get(id=user_id)
        except ObjectDoesNotExist as exc:
            raise TokenError("User no longer exists.") from exc
        new_refresh = RefreshToken.for_user(user)
        self.blacklist_service.revoke(refresh_token)
        return IssuedTokens(
            access=str(new_refresh.access_token),
            refresh=str(new_refresh),
            refresh_jti=str(new_refresh["jti"]),
        )


def _refresh_cookie_options() -> dict:
    options = {
        "httponly": True,
        "secure": settings.GIT_IT_REFRESH_COOKIE_SECURE,
        "samesite": settings.GIT_IT_REFRESH_COOKIE_SAMESITE,
        "path": settings.GIT_IT_REFRESH_COOKIE_PATH,
    }

    if settings.GIT_IT_REFRESH_COOKIE_DOMAIN:
        options["domain"] = settings.GIT_IT_REFRESH_COOKIE_DOMAIN

    return options


def set_refresh_cookie(response, refresh_token: str) -> None:
    response.set_cookie(
        settings.GIT_IT_REFRESH_COOKIE,
        refresh_token,
        max_age=int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()),
        **_refresh_cookie_options(),
    )


def clear_refresh_cookie(response) -> None:
    options = _refresh_cookie_options()

    # delete_cookie does not need these.
    options.pop("httponly", None)
    options.pop("secure", None)

    response.delete_cookie(
        settings.GIT_IT_REFRESH_COOKIE,
        **options,
    )