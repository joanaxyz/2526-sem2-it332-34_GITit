import logging
from dataclasses import dataclass
from datetime import UTC, datetime

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.core.cache import cache
from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import AccountIdentity, AccountSecurity, SessionRecord
from common.exceptions import Conflict
from common.http import get_client_ip
from players.services import get_or_create_player
from progress.models import StreakRecord, StudentProgress

logger = logging.getLogger(__name__)


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

        try:
            user = User.objects.create_user(
                username=normalized_username,
                email=normalized_email,
                password=password,
            )
            AccountIdentity.objects.create(
                user=user,
                username_key=normalized_username.casefold(),
                email_key=normalized_email.casefold(),
            )
            AccountSecurity.objects.create(user=user)
        except IntegrityError as exc:
            # The database identity keys close the check-then-create race across
            # workers while preserving the same public conflict response.
            raise Conflict("An account already exists for this username or email.") from exc
        player = get_or_create_player(user)
        StudentProgress.objects.create(player=player)
        StreakRecord.objects.create(player=player)
        # The default Arcane Spire story is owned implicitly by
        # everyone — nothing to grant at signup. Companions are NOT free: the
        # new player owns none yet and must buy one in the Shop before they can
        # play (see shop.access.require_companion).
        # Seed wallet so the new player can shop the companion catalog right away.
        from common.constants import PLAN_SIGNUP_GRANT
        from progress.wallet import WalletService

        WalletService().award(
            player=player,
            amount=PLAN_SIGNUP_GRANT,
            reason="signup_grant",
            award_key=f"signup:{player.id}",
        )
        return user


class TokenBlacklistService:
    key_prefix = "revoked-refresh:"

    @staticmethod
    def _token_metadata(refresh_token: str) -> tuple[str, int] | None:
        try:
            token = RefreshToken(refresh_token)
        except TokenError:
            return None
        return str(token["jti"]), int(token["exp"])

    def revoke(self, refresh_token: str) -> None:
        metadata = self._token_metadata(refresh_token)
        if metadata is None:
            # Logout with an expired/garbage cookie is routine; nothing to revoke.
            return
        jti, exp = metadata
        now = timezone.now()
        ttl = max(0, exp - int(now.timestamp()))

        # The database is the durable source of truth. Cache availability must
        # never decide whether a logout/rotation revocation is recorded.
        try:
            SessionRecord.objects.filter(refresh_jti=jti, revoked_at__isnull=True).update(
                revoked_at=now
            )
        except Exception:
            logger.exception("Refresh-token database revocation write failed.")

        try:
            cache.set(f"{self.key_prefix}{jti}", True, timeout=ttl)
        except Exception:
            logger.warning(
                "Refresh-token revocation cache write failed; database fallback remains active.",
                exc_info=True,
            )

    def revoke_all_for_user(self, user, *, except_jti: str | None = None) -> int:
        now = timezone.now()
        sessions = SessionRecord.objects.filter(user=user, revoked_at__isnull=True)
        if except_jti:
            sessions = sessions.exclude(refresh_jti=except_jti)
        rows = list(sessions.only("id", "refresh_jti", "expires_at"))
        if not rows:
            return 0
        SessionRecord.objects.filter(id__in=[row.id for row in rows]).update(revoked_at=now)
        for row in rows:
            ttl = 0
            if row.expires_at is not None:
                ttl = max(0, int((row.expires_at - now).total_seconds()))
            try:
                cache.set(f"{self.key_prefix}{row.refresh_jti}", True, timeout=ttl)
            except Exception:
                logger.warning("Could not cache account-wide token revocation.", exc_info=True)
        return len(rows)

    def is_revoked(self, refresh_token: str) -> bool:
        metadata = self._token_metadata(refresh_token)
        if metadata is None:
            return False
        jti, exp = metadata
        cache_key = f"{self.key_prefix}{jti}"

        try:
            if cache.get(cache_key):
                return True
        except Exception:
            logger.warning(
                "Revocation-cache read failed; checking the database source of truth.",
                exc_info=True,
            )

        try:
            revoked = SessionRecord.objects.filter(
                refresh_jti=jti, revoked_at__isnull=False
            ).exists()
        except Exception:
            # A simultaneous cache and database outage means authentication
            # state cannot be established safely. Fail closed.
            logger.exception("Refresh-token revocation database lookup failed; failing closed.")
            return True

        if revoked:
            ttl = max(0, exp - int(timezone.now().timestamp()))
            try:
                cache.set(cache_key, True, timeout=ttl)
            except Exception:
                logger.warning("Could not repopulate revocation cache.", exc_info=True)
        return revoked


class TokenService:
    blacklist_service = TokenBlacklistService()

    @staticmethod
    def auth_version_for_user(user) -> int:
        security, _created = AccountSecurity.objects.get_or_create(user=user)
        return int(security.auth_version)

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
            logger.warning("Login-lockout cache read failed.", exc_info=True)
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
            # add + incr is atomic on Redis and supported by Django's local
            # development cache. It prevents concurrent failed logins from
            # overwriting one another with the same counter value.
            cache.add(attempt_key, 0, timeout=lockout_seconds)
            attempts = cache.incr(attempt_key)
            try:
                cache.touch(attempt_key, lockout_seconds)
            except (AttributeError, NotImplementedError):
                pass
            if attempts >= max_attempts:
                lockout_until = int(timezone.now().timestamp()) + lockout_seconds
                cache.set(lockout_key, lockout_until, timeout=lockout_seconds)
                cache.delete(attempt_key)
                return lockout_seconds
        except Exception:
            # Without the cache the brute-force counter is inert - log it.
            logger.warning("Failed-login counter cache write failed.", exc_info=True)
        return 0

    def clear_failed_login(self, *, identifier: str, ip_address: str | None) -> None:
        try:
            cache.delete(self._attempt_key(identifier, ip_address))
            cache.delete(self._lockout_key(identifier, ip_address))
        except Exception:
            logger.warning("Failed-login counter cache clear failed.", exc_info=True)

    def issue_for_user(self, user, request=None) -> IssuedTokens:
        refresh = RefreshToken.for_user(user)
        refresh["auth_version"] = self.auth_version_for_user(user)
        jti = str(refresh["jti"])
        SessionRecord.objects.create(
            user=user,
            refresh_jti=jti,
            user_agent=(request.META.get("HTTP_USER_AGENT", "") if request else ""),
            ip_address=(get_client_ip(request) if request else None),
            expires_at=datetime.fromtimestamp(int(refresh["exp"]), tz=UTC),
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

        if user is None:
            return None

        # Staff sign in through the same front door so they can reach the in-app
        # admin console (the SPA gates /admin on the `is_staff` flag).
        user = authenticate(request=request, username=user.username, password=password)
        if user is None:
            return None
        return user

    @transaction.atomic
    def refresh_access(self, refresh_token: str, request=None) -> IssuedTokens:
        if not refresh_token:
            raise TokenError("Missing refresh token.")

        refresh = RefreshToken(refresh_token)
        jti = str(refresh["jti"])

        # A cache-only revocation still fails closed, but the row lock below is
        # what makes rotation single-use under concurrent requests.
        if self.blacklist_service.is_revoked(refresh_token):
            raise TokenError("Refresh token revoked.")

        try:
            session = (
                SessionRecord.objects.select_for_update()
                .select_related("user")
                .get(refresh_jti=jti)
            )
        except SessionRecord.DoesNotExist as exc:
            raise TokenError("Refresh session does not exist.") from exc

        if session.revoked_at is not None:
            raise TokenError("Refresh token revoked.")
        if session.expires_at is not None and session.expires_at <= timezone.now():
            raise TokenError("Refresh token expired.")

        user = session.user
        if not user.is_active:
            raise TokenError("User is inactive.")
        token_auth_version = int(refresh.get("auth_version", 1))
        if token_auth_version != self.auth_version_for_user(user):
            raise TokenError("Session expired.")

        now = timezone.now()
        claimed = SessionRecord.objects.filter(
            pk=session.pk,
            revoked_at__isnull=True,
        ).update(revoked_at=now)
        if claimed != 1:
            raise TokenError("Refresh token revoked.")
        session.revoked_at = now

        new_refresh = RefreshToken.for_user(user)
        new_refresh["auth_version"] = self.auth_version_for_user(user)
        new_jti = str(new_refresh["jti"])
        SessionRecord.objects.create(
            user=user,
            refresh_jti=new_jti,
            user_agent=(request.META.get("HTTP_USER_AGENT", "") if request else ""),
            ip_address=(get_client_ip(request) if request else None),
            expires_at=datetime.fromtimestamp(int(new_refresh["exp"]), tz=UTC),
        )

        old_exp = int(refresh["exp"])
        ttl = max(0, old_exp - int(now.timestamp()))

        def cache_revocation() -> None:
            try:
                cache.set(
                    f"{self.blacklist_service.key_prefix}{jti}",
                    True,
                    timeout=ttl,
                )
            except Exception:
                logger.warning("Could not cache rotated-token revocation.", exc_info=True)

        transaction.on_commit(cache_revocation)
        return IssuedTokens(
            access=str(new_refresh.access_token),
            refresh=str(new_refresh),
            refresh_jti=new_jti,
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
