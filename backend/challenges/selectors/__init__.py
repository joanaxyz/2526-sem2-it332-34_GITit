from challenges.models import ChallengeTrial


def get_challenge_trial(trial_id: int) -> ChallengeTrial:
    return (
        ChallengeTrial.objects.select_related(
            "challenge_level",
            "challenge_level__chapter",
            "challenge_level__chapter__story",
        )
        .prefetch_related("variants")
        .get(
            id=trial_id,
            is_published=True,
            challenge_level__is_published=True,
            challenge_level__chapter__is_published=True,
        )
    )
