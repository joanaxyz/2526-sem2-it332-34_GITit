from django.db import models
from django.utils import timezone


class PlayerCommandIntroduction(models.Model):
    """A completed introduction, independent of problem variants and mastery."""

    player = models.ForeignKey("players.Player", on_delete=models.CASCADE)
    teaching_key = models.CharField(max_length=160)
    completed_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["player", "teaching_key"], name="unique_player_command_introduction"
            ),
        ]


class PendingCommandIntroduction(models.Model):
    """Feedback from a real terminal command, resumable until acknowledged."""

    run = models.OneToOneField("adventures.AdventureLevelTierRun", on_delete=models.CASCADE)
    teaching_key = models.CharField(max_length=160)
    revision = models.PositiveIntegerField()
    context_hash = models.CharField(max_length=64)
    payload = models.JSONField(default=dict)
