from django.core.management import call_command

from adventures.models import AdventureLevel, AdventureWave, AdventureWaveVariant
from challenges.models import ChallengeLevel, ChallengeTrial, ChallengeTrialVariant
from curriculum.models import Chapter, ChapterLesson, CommandForm, CommandSkill, Story


def _counts() -> dict[str, int]:
    return {
        "stories": Story.objects.count(),
        "chapters": Chapter.objects.count(),
        "lessons": ChapterLesson.objects.count(),
        "skills": CommandSkill.objects.count(),
        "forms": CommandForm.objects.count(),
        "adventure_levels": AdventureLevel.objects.count(),
        "adventure_waves": AdventureWave.objects.count(),
        "adventure_variants": AdventureWaveVariant.objects.count(),
        "challenge_levels": ChallengeLevel.objects.count(),
        "challenge_trials": ChallengeTrial.objects.count(),
        "challenge_variants": ChallengeTrialVariant.objects.count(),
    }


def _identity_snapshot() -> dict[str, list[str]]:
    return {
        "stories": list(Story.objects.order_by("slug").values_list("slug", flat=True)),
        "chapters": list(Chapter.objects.order_by("slug").values_list("slug", flat=True)),
        "adventure_levels": list(AdventureLevel.objects.order_by("slug").values_list("slug", flat=True)),
        "adventure_waves": list(AdventureWave.objects.order_by("slug").values_list("slug", flat=True)),
        "challenge_levels": list(ChallengeLevel.objects.order_by("slug").values_list("slug", flat=True)),
        "challenge_variants": list(ChallengeTrialVariant.objects.order_by("case_id").values_list("case_id", flat=True)),
    }


def test_seed_curriculum_is_idempotent_without_reset(db):
    call_command("seed_curriculum")
    first_counts = _counts()
    first_identity = _identity_snapshot()

    call_command("seed_curriculum")

    assert _counts() == first_counts
    assert _identity_snapshot() == first_identity
