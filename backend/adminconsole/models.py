from django.db import models


class FeatureFlag(models.Model):
    """A simple admin-toggleable feature switch.

    Read by code via :func:`feature_enabled`; the admin Settings console flips
    them. Unknown keys read as off, so a flag can be referenced before it exists.
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


def feature_enabled(key: str) -> bool:
    return FeatureFlag.objects.filter(key=key, enabled=True).exists()
