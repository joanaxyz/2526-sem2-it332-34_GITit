from django.conf import settings
from django.db import models


class AccountIdentity(models.Model):
    """Case-insensitive registration keys protected by database uniqueness."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="account_identity",
    )
    username_key = models.CharField(max_length=191, unique=True)
    email_key = models.CharField(max_length=254, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.username_key}:{self.email_key}"


class AccountSecurity(models.Model):
    """Security version used to invalidate every JWT after sensitive changes."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="account_security",
    )
    auth_version = models.PositiveIntegerField(default=1)
    password_changed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"AccountSecurity(user={self.user_id}, version={self.auth_version})"


class SessionRecord(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    refresh_jti = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True, db_index=True)
    user_agent = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.user_id}:{self.refresh_jti}"


class EmailVerification(models.Model):
    """Sign-up email confirmation by one-time code.

    Only self-service registration creates a row. Accounts without one (staff
    made in the admin, accounts from before verification shipped) count as
    verified, so nobody existing is locked out.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="email_verification",
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    # HMAC of the current code; the code itself is never stored.
    code_hash = models.CharField(max_length=64, blank=True)
    code_expires_at = models.DateTimeField(null=True, blank=True)
    failed_attempts = models.PositiveSmallIntegerField(default=0)
    last_sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        state = "verified" if self.verified_at else "pending"
        return f"EmailVerification(user={self.user_id}, {state})"


class OAuthIdentity(models.Model):
    """A GitHub or Google account linked to a GIT it! account."""

    PROVIDER_GITHUB = "github"
    PROVIDER_GOOGLE = "google"
    PROVIDER_CHOICES = [(PROVIDER_GITHUB, "GitHub"), (PROVIDER_GOOGLE, "Google")]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="oauth_identities",
    )
    provider = models.CharField(max_length=16, choices=PROVIDER_CHOICES)
    # The provider's stable account id; emails can change, this cannot.
    subject = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["provider", "subject"], name="unique_oauth_provider_subject"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.provider}:{self.subject} -> {self.user_id}"
