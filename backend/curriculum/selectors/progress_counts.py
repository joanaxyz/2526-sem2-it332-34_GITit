from __future__ import annotations

from adventures.models import AdventureLevel
from challenges.models import ChallengeTrial


def chapter_completion_count_map(*, player, chapter_ids: list[int]) -> dict[int, int]:
    if player is None or not chapter_ids:
        return {}

    completion_by_chapter = {chapter_id: 0 for chapter_id in chapter_ids}
    from progress.models import AdventureLevelCompletion, ChallengeTrialCompletion

    for chapter_id, _level_id in (
        AdventureLevelCompletion.objects.filter(
            player=player,
            adventure_level__is_published=True,
            adventure_level__chapter_id__in=chapter_ids,
        )
        .values_list("adventure_level__chapter_id", "adventure_level_id")
        .distinct()
    ):
        completion_by_chapter[chapter_id] += 1

    for chapter_id, _trial_id in (
        ChallengeTrialCompletion.objects.filter(
            player=player,
            challenge_trial__is_published=True,
            challenge_trial__challenge_level__is_published=True,
            challenge_trial__challenge_level__chapter_id__in=chapter_ids,
        )
        .values_list("challenge_trial__challenge_level__chapter_id", "challenge_trial_id")
        .distinct()
    ):
        completion_by_chapter[chapter_id] += 1
    return completion_by_chapter


def chapter_completion_denominator_map(*, chapter_ids: list[int]) -> dict[int, int]:
    if not chapter_ids:
        return {}

    denominator_by_chapter = {chapter_id: 0 for chapter_id in chapter_ids}
    for chapter_id in (
        AdventureLevel.objects.filter(
            is_published=True,
            chapter_id__in=chapter_ids,
        )
        .values_list("chapter_id", flat=True)
    ):
        denominator_by_chapter[chapter_id] += 1

    for chapter_id in ChallengeTrial.objects.filter(
        is_published=True,
        challenge_level__is_published=True,
        challenge_level__chapter_id__in=chapter_ids,
    ).values_list("challenge_level__chapter_id", flat=True):
        denominator_by_chapter[chapter_id] += 1
    return denominator_by_chapter
