import json
import time
from dataclasses import dataclass
from pathlib import Path

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.utils import timezone
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import SessionRecord, StudentProfile
from common.exceptions import Conflict
from progress.models import StreakRecord, StudentProgress

_DEBUG_LOG_PATH = Path(__file__).resolve().parents[2] / "debug-4ce873.log"


def _agent_debug_log(hypothesis_id: str, location: str, message: str, data: dict) -> None:
    # #region agent log
    try:
        payload = {
            "sessionId": "4ce873",
            "hypothesisId": hypothesis_id,
            "location": location,
            "message": message,
            "data": data,
            "timestamp": int(time.time() * 1000),
        }
        with open(_DEBUG_LOG_PATH, "a", encoding="utf-8") as log_file:
            log_file.write(json.dumps(payload) + "\n")
    except OSError:
        pass
    # #endregion


@dataclass(frozen=True)
class IssuedTokens:
    access: str
    refresh: str
    refresh_jti: str


class UserService:
    @transaction.atomic
    def register_student(
        self,
        *,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
    ):
        User = get_user_model()
        normalized_email = User.objects.normalize_email(email).lower()
        if User.objects.filter(email__iexact=normalized_email).exists():
            raise Conflict("An account already exists for this email.")

        user = User.objects.create_user(
            username=normalized_email,
            email=normalized_email,
            password=password,
            first_name=first_name.strip(),
            last_name=last_name.strip(),
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
        # #region agent log
        _agent_debug_log(
            "B",
            "services.py:get_lockout_remaining",
            "About to read lockout from cache",
            {
                "lockout_key_prefix": lockout_key.split(":")[0],
                "cache_backend": settings.CACHES["default"]["BACKEND"],
                "cache_location_redacted": str(settings.CACHES["default"].get("LOCATION", ""))[:80],
            },
        )
        # #endregion
        try:
            lockout_until = cache.get(lockout_key)
        except Exception as exc:
            # #region agent log
            _agent_debug_log(
                "C",
                "services.py:get_lockout_remaining",
                "cache unavailable; skipping lockout check",
                {"error_type": type(exc).__name__, "error": str(exc)[:300], "runId": "post-fix"},
            )
            # #endregion
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
        except Exception as exc:
            # #region agent log
            _agent_debug_log(
                "C",
                "services.py:register_failed_login",
                "cache unavailable; skipping failed-login tracking",
                {"error_type": type(exc).__name__, "error": str(exc)[:300], "runId": "post-fix"},
            )
            # #endregion
        return 0

    def clear_failed_login(self, *, identifier: str, ip_address: str | None) -> None:
        try:
            cache.delete(self._attempt_key(identifier, ip_address))
            cache.delete(self._lockout_key(identifier, ip_address))
        except Exception as exc:
            # #region agent log
            _agent_debug_log(
                "C",
                "services.py:clear_failed_login",
                "cache unavailable; skipping failed-login clear",
                {"error_type": type(exc).__name__, "error": str(exc)[:300], "runId": "post-fix"},
            )
            # #endregion

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

    def authenticate_student(self, *, identifier: str, password: str, request=None):
        User = get_user_model()
        normalized_identifier = identifier.strip()
        if "@" in normalized_identifier:
            email = User.objects.normalize_email(normalized_identifier).lower()
            user = User.objects.filter(email__iexact=email).first()
        else:
            profile = (
                StudentProfile.objects.select_related("user")
                .filter(student_id__iexact=normalized_identifier)
                .first()
            )
            user = profile.user if profile else None

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


def set_refresh_cookie(response, refresh_token: str) -> None:
    response.set_cookie(
        settings.GIT_IT_REFRESH_COOKIE,
        refresh_token,
        max_age=int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()),
        httponly=True,
        secure=settings.GIT_IT_REFRESH_COOKIE_SECURE,
        samesite="Strict",
        path="/api/auth/",
    )


def clear_refresh_cookie(response) -> None:
    response.delete_cookie(settings.GIT_IT_REFRESH_COOKIE, path="/api/auth/", samesite="Strict")
