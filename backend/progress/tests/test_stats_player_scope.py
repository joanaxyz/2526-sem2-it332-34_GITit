from datetime import datetime, time, timedelta

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.utils import timezone
from rest_framework.test import APIClient

from adventures.models import (
    AdventureLevel,
    AdventureLevelTier,
    AdventureLevelTierRun,
    AdventureLevelTierWave,
    AdventureLevelTierWaveVariant,
    AdventureRun,
    AdventureWave,
    AdventureWaveVariant,
)
from challenges.models import ChallengeLevel, ChallengeRun, ChallengeTrial, ChallengeTrialVariant
from curriculum.models import Chapter, Story
from players.services import get_or_create_player
from practice.models import CommandStep
from progress.models import AdventureLevelCompletion, ChallengeTrialCompletion
from progress.services import MetricsService


@pytest.fixture
def stats_players(db, django_user_model):
    story = Story.objects.create(slug="stats", title="Stats")
    chapter = Chapter.objects.create(story=story, slug="stats", number=1, title="Stats")
    level = AdventureLevel.objects.create(chapter=chapter, slug="stats", title="Stats")
    wave = AdventureWave.objects.create(level=level, slug="stats")
    variant = AdventureWaveVariant.objects.create(wave=wave, slug="stats")
    tier = AdventureLevelTier.objects.create(adventure_level=level, difficulty="easy")
    tier_wave = AdventureLevelTierWave.objects.create(tier=tier, slug="stats")
    tier_variant = AdventureLevelTierWaveVariant.objects.create(wave=tier_wave, slug="stats")
    challenge = ChallengeLevel.objects.create(chapter=chapter, slug="stats", title="Stats")
    trial = ChallengeTrial.objects.create(challenge_level=challenge, difficulty="easy")
    trial_variant = ChallengeTrialVariant.objects.create(trial=trial, slug="stats")
    players = []
    for username in ("stats-learner", "stats-other"):
        user = django_user_model.objects.create_user(username=username)
        player = get_or_create_player(user)
        runs = {
            "attempt": AdventureRun.objects.create(
                player=player,
                level=level,
                current_wave=wave,
                selected_variant=variant,
                status="completed",
            ),
            "challenge_run": ChallengeRun.objects.create(
                player=player,
                challenge_trial=trial,
                selected_variant=trial_variant,
                status="completed",
            ),
            "adventure_tier_run": AdventureLevelTierRun.objects.create(
                player=player,
                tier=tier,
                current_wave=tier_wave,
                selected_variant=tier_variant,
                status="completed",
            ),
        }
        players.append((user, player, runs))
    return players


def _step(runs, parent, *, number, days_ago=0, valid=True):
    step = CommandStep.objects.create(
        **{parent: runs[parent]},
        command_text="git status" if valid else "git unknown",
        result_category=CommandStep.ResultCategory.TARGET_NOT_YET_MATCHED
        if valid
        else CommandStep.ResultCategory.INVALID,
        command_classification=CommandStep.CommandClassification.DIAGNOSTIC
        if valid
        else CommandStep.CommandClassification.UNPROCESSABLE,
        attempt_number=number,
        was_processable=valid,
    )
    day = timezone.localdate() - timedelta(days=days_ago)
    CommandStep.objects.filter(pk=step.pk).update(
        created_at=timezone.make_aware(datetime.combine(day, time(12)))
    )


@pytest.mark.parametrize("window,buckets", [("week", 7), ("month", 30), ("year", 12)])
def test_stats_include_every_command_parent_without_leaking_other_players(
    stats_players, window, buckets
):
    (user, player, runs), (_, _, other_runs) = stats_players
    _step(runs, "challenge_run", number=1, days_ago=2)
    _step(runs, "attempt", number=1, days_ago=1, valid=False)
    _step(runs, "adventure_tier_run", number=1)
    _step(runs, "adventure_tier_run", number=2, valid=False)
    # Headline accuracy and volume stay all-time even outside every trend window.
    _step(runs, "adventure_tier_run", number=3, days_ago=400)
    _step(runs, "adventure_tier_run", number=4, days_ago=400, valid=False)
    for parent in other_runs:
        _step(other_runs, parent, number=1, days_ago=3, valid=False)

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.get("/api/progress/stats/", {"window": window})

    assert response.status_code == 200
    payload = response.json()
    assert payload["headline"]["commands_run"] == 6
    assert payload["headline"]["accuracy"] == 50.0
    assert len(payload["activity_trend"]) == buckets
    assert sum(point["commands_run"] for point in payload["activity_trend"]) == 4
    if window != "year":
        assert payload["activity_trend"][-1]["commands_run"] == 2
    today = timezone.localdate()
    since = timezone.make_aware(datetime.combine(today - timedelta(days=6), time.min))
    assert MetricsService()._active_days(player=player, since=since) == {
        today,
        today - timedelta(days=1),
        today - timedelta(days=2),
    }


def test_stats_count_mixed_star_completions_in_two_queries(stats_players):
    (_, player, runs), (_, other_player, _) = stats_players
    level = runs["attempt"].level
    trial = runs["challenge_run"].challenge_trial
    other_level = AdventureLevel.objects.create(
        chapter=level.chapter, slug="another", title="Another"
    )
    other_trial = ChallengeTrial.objects.create(
        challenge_level=trial.challenge_level, difficulty="medium"
    )
    for owner, completed_level, stars in (
        (player, level, 3),
        (player, other_level, 2),
        (other_player, level, 3),
    ):
        AdventureLevelCompletion.objects.create(
            player=owner, adventure_level=completed_level, stars=stars
        )
    for owner, completed_trial, stars in (
        (player, trial, 3),
        (player, other_trial, 1),
        (other_player, trial, 3),
    ):
        ChallengeTrialCompletion.objects.create(
            player=owner, challenge_trial=completed_trial, stars=stars
        )

    with CaptureQueriesContext(connection) as captured:
        summary = MetricsService().stats_summary(player=player)

    assert summary["headline"]["levels_completed"] == 4
    assert summary["headline"]["perfect_clears"] == 2
    # Exclude the dated GROUP BY queries used to draw activity; the two headline
    # aggregates each return total and perfect counts in one database round trip.
    completion_count_queries = [
        query["sql"]
        for query in captured
        if "COUNT(" in query["sql"]
        and "GROUP BY" not in query["sql"]
        and any(
            table in query["sql"]
            for table in (
                AdventureLevelCompletion._meta.db_table,
                ChallengeTrialCompletion._meta.db_table,
            )
        )
    ]
    assert len(completion_count_queries) == 2
