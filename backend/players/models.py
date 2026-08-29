from django.conf import settings
from django.db import models


class Player(models.Model):
    """The player's identity: every other app's player-owned data (wallet, XP,
    entitlements, mastery, runs, completions) FKs to this instead of to the
    auth user directly, so "the player" has one canonical home separate from
    auth/session concerns."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="player"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Player({self.user_id})"


class PlayerPreferences(models.Model):
    MOTION_SYSTEM = "system"
    MOTION_REDUCED = "reduced"
    MOTION_FULL = "full"
    MOTION_CHOICES = [
        (MOTION_SYSTEM, "Follow system"),
        (MOTION_REDUCED, "Reduced"),
        (MOTION_FULL, "Full"),
    ]

    player = models.OneToOneField(
        Player,
        related_name="preferences",
        on_delete=models.CASCADE,
    )
    motion_mode = models.CharField(max_length=16, choices=MOTION_CHOICES, default=MOTION_SYSTEM)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"PlayerPreferences(player={self.player_id})"
