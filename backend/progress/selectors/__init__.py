"""Read-only queries over progress' completion ledger for other apps.

progress owns the AdventureLevelCompletion/ChallengeTrialCompletion tables;
callers outside this app should go through here rather than importing
progress.models directly, so the ledger's read shape can change without a
cross-app grep.
"""

from progress.models import AdventureLevelCompletion, ChallengeTrialCompletion


def total_adventure_level_completions() -> int:
    return AdventureLevelCompletion.objects.count()


def total_challenge_trial_completions() -> int:
    return ChallengeTrialCompletion.objects.count()


def completed_adventure_level_count(*, player_id: int, adventure_level_ids) -> int:
    return AdventureLevelCompletion.objects.filter(
        player_id=player_id,
        adventure_level_id__in=adventure_level_ids,
    ).count()
