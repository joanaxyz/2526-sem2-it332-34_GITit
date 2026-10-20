"""Reseeding the live curriculum changes nothing (it runs on every deploy)."""

from django.core.management import call_command

from adventures.models import (
    AdventureLevel,
    AdventureLevelTier,
    AdventureLevelTierWave,
    AdventureLevelTierWaveVariant,
)
from challenges.models import ChallengeLevel, ChallengeTrial, ChallengeTrialVariant
from curriculum.models import Chapter, CommandForm, CommandSkill, Story


def _snapshot() -> dict[str, list]:
    def slugs(model, *fields):
        return list(model.objects.order_by(*fields, "id").values_list(*fields, "is_published"))

    return {
        "stories": slugs(Story, "slug"),
        "chapters": slugs(Chapter, "slug"),
        "skills": list(CommandSkill.objects.order_by("slug").values_list("slug", flat=True)),
        "forms": slugs(CommandForm, "slug"),
        "levels": slugs(AdventureLevel, "slug"),
        "tiers": slugs(AdventureLevelTier, "adventure_level__slug", "difficulty"),
        "waves": slugs(AdventureLevelTierWave, "slug"),
        "variants": slugs(AdventureLevelTierWaveVariant, "slug"),
        "gates": slugs(ChallengeLevel, "slug"),
        "trials": slugs(ChallengeTrial, "challenge_level__slug", "difficulty"),
        "trial_variants": slugs(ChallengeTrialVariant, "slug"),
    }


def test_seeding_the_curriculum_twice_is_idempotent(db):
    call_command("seed_curriculum", verbosity=0)
    first = _snapshot()

    call_command("seed_curriculum", verbosity=0)

    assert _snapshot() == first
    assert first["levels"] and first["waves"] and first["trial_variants"]
