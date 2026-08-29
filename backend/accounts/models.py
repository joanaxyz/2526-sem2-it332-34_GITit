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
