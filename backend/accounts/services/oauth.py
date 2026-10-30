"""GitHub and Google sign-in (OAuth 2.0 authorization-code flow).

The browser goes start -> provider -> callback. The callback never hands the
browser a session directly: it redirects to the SPA with a single-use ticket,
which the SPA exchanges through the API for the usual access token and refresh
cookie, exactly like a password sign-in.
"""

from __future__ import annotations

import hashlib
import re
import secrets
from dataclasses import dataclass
from urllib.parse import urlencode

import httpx
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone

from accounts.models import OAuthIdentity
from accounts.services.core import UserService
from accounts.services.verification import EmailVerificationService
from common.exceptions import Conflict

TICKET_TTL_SECONDS = 120
TICKET_CACHE_PREFIX = "oauth-ticket:"
HTTP_TIMEOUT_SECONDS = 10
# Tests swap in an httpx.MockTransport; production uses the real network.
http_transport: httpx.BaseTransport | None = None


@dataclass(frozen=True)
class ProviderConfig:
    authorize_url: str
    token_url: str
    scope: str


PROVIDERS = {
    OAuthIdentity.PROVIDER_GITHUB: ProviderConfig(
        authorize_url="https://github.com/login/oauth/authorize",
        token_url="https://github.com/login/oauth/access_token",
        scope="read:user user:email",
    ),
    OAuthIdentity.PROVIDER_GOOGLE: ProviderConfig(
        authorize_url="https://accounts.google.com/o/oauth2/v2/auth",
        token_url="https://oauth2.googleapis.com/token",
        scope="openid email profile",
    ),
}


@dataclass(frozen=True)
class ProviderProfile:
    subject: str
    email: str
    email_verified: bool
    username_hint: str


class OAuthError(Exception):
    """A failed sign-in. `code` is what the SPA shows a message for."""

    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


class OAuthService:
    @staticmethod
    def is_known(provider: str) -> bool:
        return provider in PROVIDERS

    @staticmethod
    def is_configured(provider: str) -> bool:
        credentials = settings.OAUTH_PROVIDERS.get(provider, {})
        return bool(credentials.get("client_id") and credentials.get("client_secret"))

    @staticmethod
    def callback_url(provider: str) -> str:
        return f"{settings.OAUTH_CALLBACK_BASE_URL}/auth/oauth/{provider}/callback/"

    def authorization_url(self, provider: str, state: str) -> str:
        config = PROVIDERS[provider]
        params = {
            "client_id": settings.OAUTH_PROVIDERS[provider]["client_id"],
            "redirect_uri": self.callback_url(provider),
            "scope": config.scope,
            "state": state,
            "response_type": "code",
        }
        if provider == OAuthIdentity.PROVIDER_GOOGLE:
            params["prompt"] = "select_account"
        return f"{config.authorize_url}?{urlencode(params)}"

    def fetch_profile(self, provider: str, code: str) -> ProviderProfile:
        try:
            with httpx.Client(timeout=HTTP_TIMEOUT_SECONDS, transport=http_transport) as client:
                access_token = self._exchange_code(client, provider, code)
                if provider == OAuthIdentity.PROVIDER_GITHUB:
                    return self._github_profile(client, access_token)
                return self._google_profile(client, access_token)
        except (httpx.HTTPError, KeyError, ValueError, TypeError) as exc:
            raise OAuthError("provider") from exc

    @transaction.atomic
    def resolve_user(self, provider: str, profile: ProviderProfile):
        """Return the account this provider identity signs in to, creating one if needed."""

        User = get_user_model()
        identity = (
            OAuthIdentity.objects.select_for_update()
            .select_related("user")
            .filter(provider=provider, subject=profile.subject)
            .first()
        )
        if identity is not None:
            if not identity.user.is_active:
                raise OAuthError("inactive")
            identity.email = profile.email or identity.email
            identity.last_used_at = timezone.now()
            identity.save(update_fields=["email", "last_used_at"])
            return identity.user

        # Linking or creating needs an address the provider itself has verified;
        # an unverified one could belong to someone else.
        if not profile.email or not profile.email_verified:
            raise OAuthError("email")
        email = User.objects.normalize_email(profile.email).lower()

        user = User.objects.filter(email__iexact=email).first()
        if user is not None:
            if not user.is_active:
                raise OAuthError("inactive")
            if user.is_staff or user.is_superuser:
                # Staff keep password-only sign-in; a provider account is never
                # silently attached to an administrator.
                raise OAuthError("staff")
            # The provider proved this inbox, which settles any pending sign-up code.
            EmailVerificationService.mark_verified(user)
        else:
            user = self._create_account(email=email, username_hint=profile.username_hint)

        OAuthIdentity.objects.create(
            user=user,
            provider=provider,
            subject=profile.subject,
            email=email,
            last_used_at=timezone.now(),
        )
        return user

    @staticmethod
    def issue_ticket(user) -> str:
        ticket = secrets.token_urlsafe(32)
        cache.set(_ticket_key(ticket), user.pk, timeout=TICKET_TTL_SECONDS)
        return ticket

    @staticmethod
    def redeem_ticket(ticket: str):
        """Return the ticket's active user once; any later redemption gets None."""

        key = _ticket_key(ticket)
        user_id = cache.get(key)
        # delete() reports whether this call removed the key, so two racing
        # redemptions of one ticket cannot both succeed.
        if user_id is None or not cache.delete(key):
            return None
        return get_user_model().objects.filter(pk=user_id, is_active=True).first()

    @staticmethod
    def _exchange_code(client: httpx.Client, provider: str, code: str) -> str:
        credentials = settings.OAUTH_PROVIDERS[provider]
        response = client.post(
            PROVIDERS[provider].token_url,
            data={
                "client_id": credentials["client_id"],
                "client_secret": credentials["client_secret"],
                "code": code,
                "redirect_uri": OAuthService.callback_url(provider),
                "grant_type": "authorization_code",
            },
            headers={"Accept": "application/json"},
        )
        response.raise_for_status()
        payload = response.json()
        # GitHub answers a bad or reused code with 200 and an "error" field.
        if "error" in payload or not payload.get("access_token"):
            raise ValueError(payload.get("error", "missing access_token"))
        return payload["access_token"]

    @staticmethod
    def _github_profile(client: httpx.Client, access_token: str) -> ProviderProfile:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github+json",
        }
        user_response = client.get("https://api.github.com/user", headers=headers)
        user_response.raise_for_status()
        account = user_response.json()
        emails_response = client.get("https://api.github.com/user/emails", headers=headers)
        emails_response.raise_for_status()
        emails = emails_response.json()
        primary = next(
            (item for item in emails if item.get("primary") and item.get("verified")),
            None,
        ) or next((item for item in emails if item.get("verified")), None)
        return ProviderProfile(
            subject=str(account["id"]),
            email=(primary or {}).get("email", ""),
            email_verified=primary is not None,
            username_hint=account.get("login") or "",
        )

    @staticmethod
    def _google_profile(client: httpx.Client, access_token: str) -> ProviderProfile:
        response = client.get(
            "https://openidconnect.googleapis.com/v1/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        response.raise_for_status()
        info = response.json()
        email = info.get("email", "")
        return ProviderProfile(
            subject=str(info["sub"]),
            email=email,
            email_verified=info.get("email_verified") is True,
            username_hint=info.get("given_name") or email.split("@")[0],
        )

    @staticmethod
    def _create_account(*, email: str, username_hint: str):
        base = re.sub(r"[^A-Za-z0-9._-]", "", username_hint)[:24].strip("._-")
        if len(base) < 3:
            base = "archivist"
        User = get_user_model()
        candidates = [base] + [f"{base}-{secrets.randbelow(9000) + 1000}" for _ in range(5)]
        for candidate in candidates:
            if User.objects.filter(username__iexact=candidate).exists():
                continue
            try:
                with transaction.atomic():
                    return UserService().register_account(
                        username=candidate,
                        email=email,
                        password=None,
                        verify_email=False,
                    )
            except Conflict:
                # Lost a race for this username; try the next one. Losing the
                # email instead means a parallel sign-up won, so start over.
                if User.objects.filter(email__iexact=email).exists():
                    raise OAuthError("retry") from None
        raise OAuthError("username")


def _ticket_key(ticket: str) -> str:
    return TICKET_CACHE_PREFIX + hashlib.sha256(ticket.encode()).hexdigest()
