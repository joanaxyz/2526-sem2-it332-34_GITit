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

    # The getting-started journey walks Stories -> Shop -> Home. It is stored
    # per account (not in browser storage) so a returning player is never
    # re-onboarded on a new device, and so a half-finished journey resumes.
    ONBOARDING_DONE = "done"
    ONBOARDING_START = "stories"
    ONBOARDING_CHOICES = [
        (ONBOARDING_START, "Stories"),
        ("shop", "Shop"),
        ("purchase", "Purchase"),
        ("home", "Home"),
        ("equip", "Equip"),
        (ONBOARDING_DONE, "Done"),
    ]

    player = models.OneToOneField(
        Player,
        related_name="preferences",
        on_delete=models.CASCADE,
    )
    motion_mode = models.CharField(max_length=16, choices=MOTION_CHOICES, default=MOTION_SYSTEM)
    # Defaults to "done": only registration opts an account in, so accounts that
    # predate the journey (and lazily created preference rows) stay untouched.
    onboarding_phase = models.CharField(
        max_length=16, choices=ONBOARDING_CHOICES, default=ONBOARDING_DONE
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"PlayerPreferences(player={self.player_id})"
