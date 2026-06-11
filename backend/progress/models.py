from django.conf import settings
from django.db import models


class StudentProgress(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    first_practice_started_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Progress({self.user_id})"


class StreakRecord(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    current_streak = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)
    last_completed_on = models.DateField(null=True, blank=True)

    def __str__(self) -> str:
        return f"Streak({self.user_id}: {self.current_streak})"


class Wallet(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wallet"
    )
    balance = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Wallet({self.user_id}: {self.balance})"


class CoinTransaction(models.Model):
    """GitCoin ledger entry. ``award_key`` makes every grant idempotent: a
    reward source (first clear of a quest, passing an adventure) can be
    retried safely and never pays out twice."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="coin_transactions"
    )
    amount = models.IntegerField()
    reason = models.CharField(max_length=64)
    award_key = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        constraints = [
            models.UniqueConstraint(fields=["user", "award_key"], name="unique_award_per_user"),
        ]

    def __str__(self) -> str:
        return f"CoinTransaction({self.user_id}: {self.amount} {self.reason})"


class QuestCompletion(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    adventure_quest = models.ForeignKey(
        "adventures.AdventureQuest",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    challenge_quest = models.ForeignKey(
        "challenges.ChallengeQuest",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    challenge_run = models.OneToOneField(
        "challenges.ChallengeRun",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    first_attempt_star = models.BooleanField(default=False)
    counted_action_total = models.PositiveIntegerField(default=0)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "adventure_quest"],
                name="unique_adventure_quest_completion",
                condition=models.Q(adventure_quest__isnull=False),
            ),
            models.UniqueConstraint(
                fields=["user", "challenge_quest"],
                name="unique_challenge_quest_completion",
                condition=models.Q(challenge_quest__isnull=False),
            ),
        ]

    @property
    def quest(self):
        return self.adventure_quest or self.challenge_quest
