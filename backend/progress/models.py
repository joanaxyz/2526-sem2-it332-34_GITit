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


class ProblemCompletion(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    adventure_problem = models.ForeignKey(
        "adventures.AdventureProblem",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    challenge_level = models.ForeignKey(
        "challenges.ChallengeLevel",
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
                fields=["user", "adventure_problem"],
                name="unique_adventure_problem_completion",
                condition=models.Q(adventure_problem__isnull=False),
            ),
            models.UniqueConstraint(
                fields=["user", "challenge_level"],
                name="unique_challenge_level_completion",
                condition=models.Q(challenge_level__isnull=False),
            ),
        ]

    @property
    def problem(self):
        return self.adventure_problem or self.challenge_level
