from django.db.models import Q

from challenges.models import ChallengeRun, ChallengeTrial


def minimum_counted_for_run(*, run: ChallengeRun) -> int:
    return run.min_counted_commands


def get_challenge_trial(trial_id: int) -> ChallengeTrial:
    return (
        ChallengeTrial.objects.select_related(
            "challenge_level",
            "challenge_level__source_content_definition",
            "challenge_level__chapter",
            "challenge_level__chapter__story",
        )
        .prefetch_related("variants")
        .filter(
            Q(challenge_level__chapter__is_published=True)
            | Q(challenge_level__source_content_definition__isnull=False)
        )
        .get(
            id=trial_id,
            is_published=True,
            challenge_level__is_published=True,
        )
    )
