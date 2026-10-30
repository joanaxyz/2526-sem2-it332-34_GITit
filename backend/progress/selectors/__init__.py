"""Read-only queries over progress' completion ledger for other apps.

progress owns the AdventureLevelTierCompletion/ChallengeTrialCompletion tables;
callers outside this app should go through here rather than importing
progress.models directly, so the ledger's read shape can change without a
cross-app grep.
"""

from progress.models import AdventureLevelTierCompletion, ChallengeTrialCompletion


def total_adventure_tier_completions() -> int:
    return AdventureLevelTierCompletion.objects.count()


def total_challenge_trial_completions() -> int:
    return ChallengeTrialCompletion.objects.count()
