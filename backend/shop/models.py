from django.db import models

from shop.catalog import SHOP_KINDS

SHOP_KIND_CHOICES = [(kind, kind.title()) for kind in SHOP_KINDS]


class Entitlement(models.Model):
    """A story or companion the user owns.

    Default stories are implicitly owned and need no row.
    """

    player = models.ForeignKey(
        "players.Player",
        related_name="entitlements",
        on_delete=models.CASCADE,
    )
    kind = models.CharField(max_length=16, choices=SHOP_KIND_CHOICES)
    slug = models.SlugField(max_length=64)
    granted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-granted_at", "-id"]
        constraints = [
            models.UniqueConstraint(fields=["player", "kind", "slug"], name="unique_shop_entitlement"),
        ]
        indexes = [
            models.Index(fields=["player", "kind"], name="entitlement_player_kind_idx"),
        ]

    def __str__(self) -> str:
        return f"Entitlement(player={self.player_id}, {self.kind}:{self.slug})"


class PlayerLoadout(models.Model):
    """The player's equipped companion skin."""

    player = models.OneToOneField(
        "players.Player",
        related_name="loadout",
        on_delete=models.CASCADE,
    )
    # No default: nothing is equipped until the player owns a companion.
    active_companion_slug = models.SlugField(max_length=64, null=True, blank=True, default=None)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["player_id"]

    def __str__(self) -> str:
        return f"PlayerLoadout(player={self.player_id})"
