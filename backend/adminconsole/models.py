from django.conf import settings
from django.db import models


class FeatureFlag(models.Model):
    """A simple admin-toggleable feature switch.

    Read by code via :func:`adminconsole.flags.feature_enabled`; the admin
    Settings console flips them. Unknown keys read as off, so a flag can be
    referenced before it exists.
    """

    key = models.SlugField(unique=True)
    label = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    enabled = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["key"]

    def __str__(self) -> str:
        return f"FeatureFlag({self.key}={'on' if self.enabled else 'off'})"


class AdminActionLog(models.Model):
    """Append-only record of a material action taken through the SPA console."""

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name="admin_action_logs",
        on_delete=models.SET_NULL,
    )
    action = models.CharField(max_length=64)
    target_type = models.CharField(max_length=80)
    target_id = models.CharField(max_length=80, blank=True)
    target_label = models.CharField(max_length=255, blank=True)
    before = models.JSONField(default=dict, blank=True)
    after = models.JSONField(default=dict, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    request_id = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [
            models.Index(fields=["action", "-created_at"], name="admin_action_kind_idx"),
            models.Index(fields=["target_type", "target_id"], name="admin_action_target_idx"),
        ]

    def __str__(self) -> str:
        return f"AdminActionLog({self.action} -> {self.target_type}:{self.target_id})"
