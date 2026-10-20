from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING

from adventures.models import AdventureLevel, AdventureLevelTier
from adventures.rewards import tier_reward_payload
from adventures.tier_waves import wave_progress
from common.constants import DIFFICULTY_EASY, DIFFICULTY_HARD, DIFFICULTY_MEDIUM
from drills.selectors import (
    drill_access_payload,
    drill_progress_by_level_id,
    drillable_level_ids,
)

from .access_helpers import (
    _completion_payload,
    _level_commands,
)

if TYPE_CHECKING:
    from progress.models import AdventureLevelTierCompletion


@dataclass(frozen=True)
class AdventureAccessContext:
    """User-specific state for an ordered group of Adventures.

    Adventures are a linear progression within a chapter. Completion rows are
    batch-loaded once so building the overview never issues a query per level.
    """

    completion_by_adventure_id: dict[int, AdventureLevelTierCompletion] = field(default_factory=dict)
    passed_at_by_adventure_id: dict[int, datetime] = field(default_factory=dict)
    passed_adventure_ids: set[int] = field(default_factory=set)
    locked_adventure_ids: set[int] = field(default_factory=set)
    lock_reasons: dict[int, str] = field(default_factory=dict)
    # Squire's Drill: which levels have seeded drill content, and this
    # player's row for each. Batch-loaded here so the map can mark drilled
    # levels without a query per node.
    drillable_adventure_ids: set[int] = field(default_factory=set)
    drill_progress_by_adventure_id: dict[int, object] = field(default_factory=dict)


def _build_adventure_access(
    *,
    player,
    adventures: list[AdventureLevel],
    tiers: list[AdventureLevelTier] | None = None,
    tier_access: AdventureTierAccessContext | None = None,
) -> AdventureAccessContext:
    """``tiers``/``tier_access``: a chapter caller's already-loaded published
    tiers and their access context, reused instead of re-querying completions."""
    if not adventures:
        return AdventureAccessContext()

    # A level is passed once its Easy tier is complete; that completion is
    # the level's map completion.
    completion_by_adventure_id: dict[int, AdventureLevelTierCompletion] = {}
    if tiers is not None and tier_access is not None:
        completion_by_adventure_id = {
            tier.adventure_level_id: tier_access.completions[tier.id]
            for tier in tiers
            if tier.difficulty == DIFFICULTY_EASY and tier.id in tier_access.completions
        }
    elif player is not None:
        from progress.models import AdventureLevelTierCompletion

        completion_by_adventure_id = {
            completion.tier.adventure_level_id: completion
            for completion in AdventureLevelTierCompletion.objects.filter(
                player=player,
                tier__difficulty=DIFFICULTY_EASY,
                tier__adventure_level_id__in=[adventure.id for adventure in adventures],
            ).select_related("tier")
        }
    passed_at_by_adventure_id = {
        level_id: completion.completed_at
        for level_id, completion in completion_by_adventure_id.items()
    }
    passed_adventure_ids = set(completion_by_adventure_id)

    return AdventureAccessContext(
        completion_by_adventure_id=completion_by_adventure_id,
        passed_at_by_adventure_id=passed_at_by_adventure_id,
        passed_adventure_ids=passed_adventure_ids,
        drillable_adventure_ids=drillable_level_ids(
            level_ids=[adventure.id for adventure in adventures]
        ),
        drill_progress_by_adventure_id=drill_progress_by_level_id(
            player=player, level_ids=[adventure.id for adventure in adventures]
        ),
    )


def adventure_locked(*, player, adventure: AdventureLevel) -> tuple[bool, str]:
    """Return whether the immediately preceding adventure still blocks launch."""
    adventures = list(
        AdventureLevel.objects.filter(chapter_id=adventure.chapter_id, is_published=True).order_by(
            "sort_order", "id"
        )
    )
    access = _build_adventure_access(player=player, adventures=adventures)
    return (
        adventure.id in access.locked_adventure_ids,
        access.lock_reasons.get(adventure.id, ""),
    )


def level_locked(*, player, level: AdventureLevel) -> tuple[bool, str]:
    """Return whether this adventure level is blocked by the previous level in the chapter."""
    return adventure_locked(player=player, adventure=level)


def adventure_summary_payload(
    *,
    player,
    adventure: AdventureLevel,
    access: AdventureAccessContext | None = None,
    knowledge: list[dict] | None = None,
    tiers: list[AdventureLevelTier] | None = None,
    tier_access: AdventureTierAccessContext | None = None,
) -> dict:
    if access is None:
        chapter_adventures = list(
            AdventureLevel.objects.filter(
                chapter_id=adventure.chapter_id, is_published=True
            ).order_by("sort_order", "id")
        )
        access = _build_adventure_access(player=player, adventures=chapter_adventures)

    completion = access.completion_by_adventure_id.get(adventure.id)
    is_passed = adventure.id in access.passed_adventure_ids
    # Callers rendering a whole chapter pass prefetched published tiers and one
    # tier access context built for all of them, so the map costs a fixed
    # number of queries instead of several per node.
    if tiers is None:
        tiers = list(adventure.tiers.filter(is_published=True)) if adventure.id else []
    if tier_access is None:
        tier_access = _build_adventure_tier_access(player=player, tiers=tiers)

    return {
        "item_type": "adventure",
        "id": adventure.id,
        "slug": adventure.slug,
        "title": adventure.title,
        "description": adventure.description,
        "command": ", ".join(_level_commands(adventure)),
        "knowledge": knowledge or [],
        "is_passed": is_passed,
        "locked": adventure.id in access.locked_adventure_ids,
        "lock_reason": access.lock_reasons.get(adventure.id, ""),
        "completion": _completion_payload(completion),
        "passed_at": access.passed_at_by_adventure_id.get(adventure.id),
        "drill": drill_access_payload(
            available=adventure.id in access.drillable_adventure_ids,
            progress=access.drill_progress_by_adventure_id.get(adventure.id),
        ),
        "tiers": [
            adventure_level_tier_payload(tier=tier, access=tier_access)
            for tier in _ordered_adventure_tiers(tiers)
        ],
    }


# ---------------------------------------------------------------------------
# Per-node difficulty tiers (AdventureLevelTier)
#
# Mirrors the ChallengeLevel -> ChallengeTrial access pattern in
# challenge_access.py: Easy unlocks with the level itself, Medium unlocks once
# Easy has a completion row, Hard unlocks once Medium does. "Complete" means
# every wave in the tier is cleared - tracked via AdventureLevelTierCompletion,
# written once (mirrors ChallengeTrialCompletion), not re-derived per request.
# ---------------------------------------------------------------------------

_TIER_DIFFICULTY_ORDER = {DIFFICULTY_EASY: 0, DIFFICULTY_MEDIUM: 1, DIFFICULTY_HARD: 2}


def _ordered_adventure_tiers(tiers: list[AdventureLevelTier]) -> list[AdventureLevelTier]:
    return sorted(tiers, key=lambda tier: _TIER_DIFFICULTY_ORDER.get(tier.difficulty, 99))


@dataclass(frozen=True)
class AdventureTierAccessContext:
    """Batch-loaded per-tier facts: completion rows, each tier's wave (holding
    required_successful_attempts), and the player's current run (holding
    successful_clears) - so building a level's tier payloads costs a fixed
    handful of queries.

    A tier is an ordered set of waves; "progress" counts the learner's cleared
    waves (adventures/services/tier_waves.py), each wave counting its
    required clears."""

    completions: dict[int, object] = field(default_factory=dict)
    waves: dict[int, list] = field(default_factory=dict)
    progress_rows: dict[int, object] = field(default_factory=dict)
    # (adventure_level_id, difficulty) -> published tier id, so unlock checks
    # find the previous difficulty without re-querying each level's tiers.
    tier_ids_by_level_difficulty: dict[tuple[int, str], int] = field(default_factory=dict)
    # Award keys of the tier rewards this player has been paid (adventures/rewards.py).
    claimed_reward_keys: set[str] = field(default_factory=set)


def _build_adventure_tier_access(
    *, player, tiers: list[AdventureLevelTier]
) -> AdventureTierAccessContext:
    if not tiers:
        return AdventureTierAccessContext()

    from adventures.models import AdventureLevelTierWave

    tier_ids = [tier.id for tier in tiers]
    waves: dict[int, list] = {}
    for wave in (
        AdventureLevelTierWave.objects.filter(tier_id__in=tier_ids, is_published=True)
        .only("id", "tier_id", "slug", "title", "sort_order", "required_successful_attempts")
        .order_by("sort_order", "id")
    ):
        waves.setdefault(wave.tier_id, []).append(wave)

    completions: dict[int, object] = {}
    progress_rows: dict[int, object] = {}
    if player is not None:
        from adventures.models import AdventureLevelTierProgress
        from progress.models import AdventureLevelTierCompletion

        completions = {
            completion.tier_id: completion
            for completion in AdventureLevelTierCompletion.objects.filter(
                player=player, tier_id__in=tier_ids
            )
        }
        # AdventureLevelTierProgress is the per-(player, tier) rollup that
        # persists across attempts - each AdventureLevelTierRun ends on its
        # own, so a run field can't hold it (see its docstring).
        progress_rows = {
            row.tier_id: row
            for row in AdventureLevelTierProgress.objects.filter(
                player=player, tier_id__in=tier_ids
            ).only("id", "tier_id", "successful_clears", "cleared_wave_slugs")
        }

    from adventures.rewards import claimed_tier_reward_keys

    return AdventureTierAccessContext(
        completions=completions,
        waves=waves,
        progress_rows=progress_rows,
        claimed_reward_keys=claimed_tier_reward_keys(player=player, tiers=tiers),
        tier_ids_by_level_difficulty={
            (tier.adventure_level_id, tier.difficulty): tier.id
            for tier in tiers
            if tier.is_published
        },
    )


def _adventure_tier_unlocked(
    *, tier: AdventureLevelTier, access: AdventureTierAccessContext
) -> bool:
    if tier.difficulty == DIFFICULTY_EASY:
        return True
    previous_difficulty = (
        DIFFICULTY_EASY if tier.difficulty == DIFFICULTY_MEDIUM else DIFFICULTY_MEDIUM
    )
    previous_tier_id = access.tier_ids_by_level_difficulty.get(
        (tier.adventure_level_id, previous_difficulty)
    )
    return previous_tier_id is not None and previous_tier_id in access.completions


def adventure_level_tier_payload(
    *, tier: AdventureLevelTier, access: AdventureTierAccessContext
) -> dict:
    completion = access.completions.get(tier.id)
    progress = wave_progress(
        access.waves.get(tier.id, []),
        access.progress_rows.get(tier.id),
        tier_completed=completion is not None,
    )
    completed, total = progress["completed"], progress["total"]
    return {
        "id": tier.id,
        "difficulty": tier.difficulty,
        "locked": not _adventure_tier_unlocked(tier=tier, access=access),
        "wave_progress": {"completed": completed, "total": total},
        "completion": _completion_payload(completion),
        "reward": tier_reward_payload(tier, claimed_keys=access.claimed_reward_keys),
    }


def cleared_tier_difficulties(*, player, chapter_id: int) -> set[str] | None:
    """Difficulties whose tier every required level of the chapter has cleared.

    This is the Challenge Gate rule for tier-based chapters: a gate trial of
    difficulty *d* opens once every level's *d* tier is complete. Returns
    None for chapters without tiers, which keep their own rule.
    """
    from progress.models import AdventureLevelTierCompletion

    tiers = list(
        AdventureLevelTier.objects.filter(
            adventure_level__chapter_id=chapter_id,
            adventure_level__is_published=True,
            adventure_level__is_required=True,
            is_published=True,
        ).values_list("id", "adventure_level_id", "difficulty")
    )
    if not tiers:
        return None
    if player is None:
        return set()
    completed = set(
        AdventureLevelTierCompletion.objects.filter(
            player=player, tier_id__in=[tier_id for tier_id, _, _ in tiers]
        ).values_list("tier_id", flat=True)
    )
    return cleared_difficulties(tiers, completed)


def cleared_difficulties(tiers, completed_tier_ids) -> set[str]:
    """``tiers``: (tier id, level id, difficulty) for a chapter's required levels."""
    level_ids = {level_id for _, level_id, _ in tiers}
    cleared = set()
    for difficulty in (DIFFICULTY_EASY, DIFFICULTY_MEDIUM, DIFFICULTY_HARD):
        done = {
            level_id
            for tier_id, level_id, tier_difficulty in tiers
            if tier_difficulty == difficulty and tier_id in completed_tier_ids
        }
        if done == level_ids:
            cleared.add(difficulty)
    return cleared


def _adventure_passed(*, player, chapter_id: int) -> bool:
    """Every required level of the chapter has cleared its Easy tier."""
    from progress.models import AdventureLevelTierCompletion

    required_level_ids = set(
        AdventureLevel.objects.filter(
            chapter_id=chapter_id,
            is_published=True,
            is_required=True,
        ).values_list("id", flat=True)
    )
    if not required_level_ids:
        return True
    if player is None:
        return False
    passed = set(
        AdventureLevelTierCompletion.objects.filter(
            player=player,
            tier__difficulty=DIFFICULTY_EASY,
            tier__adventure_level_id__in=required_level_ids,
        ).values_list("tier__adventure_level_id", flat=True)
    )
    return required_level_ids <= passed
