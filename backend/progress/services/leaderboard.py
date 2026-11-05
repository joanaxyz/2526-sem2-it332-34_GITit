"""The learner leaderboard: one all-time ranking per category.

Only public usernames and equipped companion slugs leave this module. KPIs and
checkpoint results are deliberately not categories: ranking them would invite
gaming the evaluation and show who failed a checkpoint.
"""

from __future__ import annotations

from django.db.models import Count, Max, Sum

from players.models import Player, PlayerPreferences
from progress.models import (
    AdventureLevelTierCompletion,
    ChallengeTrialCompletion,
    XpTransaction,
)

from .metrics import MetricsService

CATEGORIES = ("xp", "perfect_clears", "gates")
DEFAULT_CATEGORY = "xp"
TOP_ENTRIES = 10

STORY_SLUG = MetricsService.LEARNER_CURRICULUM_STORY_SLUG


def _listed_player_ids() -> set[int]:
    return set(
        Player.objects.filter(user__is_staff=False, user__is_active=True)
        .exclude(preferences__leaderboard_visible=False)
        .values_list("id", flat=True)
    )


def _xp_scores(player_ids) -> dict[int, tuple[float, float]]:
    rows = (
        XpTransaction.objects.filter(player_id__in=player_ids)
        .values("player_id")
        .annotate(value=Sum("amount"), reached=Max("created_at"))
    )
    # Whoever reached the total first ranks higher, so XP has no shared ranks.
    return {row["player_id"]: (row["value"], row["reached"].timestamp()) for row in rows}


def _perfect_clear_scores(player_ids) -> dict[int, tuple[float, float]]:
    rows = (
        AdventureLevelTierCompletion.objects.filter(
            player_id__in=player_ids,
            stars=3,
            tier__adventure_level__chapter__story__slug=STORY_SLUG,
        )
        .values("player_id")
        .annotate(value=Count("id"))
    )
    return {row["player_id"]: (row["value"], 0) for row in rows}


def _gate_scores(player_ids) -> dict[int, tuple[float, float]]:
    rows = (
        ChallengeTrialCompletion.objects.filter(
            player_id__in=player_ids,
            challenge_trial__challenge_level__chapter__story__slug=STORY_SLUG,
        )
        .values("player_id")
        .annotate(value=Count("id"))
    )
    return {row["player_id"]: (row["value"], 0) for row in rows}


SCORES = {
    "xp": _xp_scores,
    "perfect_clears": _perfect_clear_scores,
    "gates": _gate_scores,
}


def _ranked(scores: dict[int, tuple[float, float]]) -> list[tuple[int, int, float]]:
    """(rank, player_id, value), best first; equal scores share a rank."""
    ordered = sorted(
        ((value, tiebreak, player_id) for player_id, (value, tiebreak) in scores.items() if value),
        key=lambda row: (-row[0], row[1], row[2]),
    )
    ranked = []
    previous = None
    for position, (value, tiebreak, player_id) in enumerate(ordered, start=1):
        rank = ranked[-1][0] if (value, tiebreak) == previous else position
        ranked.append((rank, player_id, value))
        previous = (value, tiebreak)
    return ranked


def leaderboard(*, player, category: str = DEFAULT_CATEGORY) -> dict:
    """The top entries plus the requester's own place, listed or not."""
    listed = _listed_player_ids()
    scores = SCORES[category](listed | {player.id})
    own_value = scores.get(player.id, (0, 0))[0]
    ranked = _ranked({key: score for key, score in scores.items() if key in listed})
    players = {
        player_id: (username, companion_slug)
        for player_id, username, companion_slug in Player.objects.filter(
            id__in=[row[1] for row in ranked[:TOP_ENTRIES]]
        ).values_list("id", "user__username", "loadout__active_companion_slug")
    }
    return {
        "category": category,
        "entries": [
            {
                "rank": rank,
                "username": players[player_id][0],
                "companion_slug": players[player_id][1],
                "value": value,
                "is_you": player_id == player.id,
            }
            for rank, player_id, value in ranked[:TOP_ENTRIES]
        ],
        "you": {
            "rank": next((row[0] for row in ranked if row[1] == player.id), None),
            "value": own_value,
            "hidden": PlayerPreferences.objects.filter(
                player=player, leaderboard_visible=False
            ).exists(),
        },
    }
