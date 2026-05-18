from dataclasses import dataclass

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import SessionRecord, StudentProfile
from common.exceptions import Conflict
from progress.models import StreakRecord, StudentProgress

CIT_EMAIL_DOMAIN = "@cit.edu"


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
        student_id: str,
        first_name: str,
        last_name: str,
    ):
        User = get_user_model()
        normalized_email = User.objects.normalize_email(email).lower()
        normalized_student_id = student_id.strip().upper()
        if User.objects.filter(email__iexact=normalized_email).exists():
            raise Conflict("A student account already exists for this email.")
        if StudentProfile.objects.filter(student_id__iexact=normalized_student_id).exists():
            raise Conflict("A student account already exists for this student ID.")

        user = User.objects.create_user(
            username=normalized_email,
            email=normalized_email,
            password=password,
            first_name=first_name.strip(),
            last_name=last_name.strip(),
        )
        StudentProfile.objects.create(user=user, student_id=normalized_student_id)
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
            if not email.endswith(CIT_EMAIL_DOMAIN):
                return None
            user = User.objects.filter(email__iexact=email).first()
        else:
            profile = StudentProfile.objects.select_related("user").filter(
                student_id__iexact=normalized_identifier
            ).first()
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
        user = get_user_model().objects.get(id=user_id)
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
