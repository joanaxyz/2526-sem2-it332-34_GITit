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
    AdventureLevelTierScenario,
    AdventureLevelTierScenarioVariant,
)
from challenges.models import ChallengeLevel, ChallengeRun, ChallengeTrial, ChallengeTrialVariant
from curriculum.models import Chapter, Story
from players.services import get_or_create_player
from practice.models import CommandStep
from progress.models import AdventureLevelTierCompletion
from progress.services import MetricsService


@pytest.fixture
def stats_players(db, django_user_model):
    story = Story.objects.create(slug="arcane-spire", title="The Arcane Spire")
    chapter = Chapter.objects.create(story=story, slug="stats", number=1, title="Stats")
    level = AdventureLevel.objects.create(chapter=chapter, slug="stats", title="Stats")
    tier = AdventureLevelTier.objects.create(adventure_level=level, difficulty="easy")
    tier_scenario = AdventureLevelTierScenario.objects.create(tier=tier, slug="stats")
    tier_variant = AdventureLevelTierScenarioVariant.objects.create(
        scenario=tier_scenario, slug="stats"
    )
    challenge = ChallengeLevel.objects.create(chapter=chapter, slug="stats", title="Stats")
    trial = ChallengeTrial.objects.create(challenge_level=challenge, difficulty="easy")
    trial_variant = ChallengeTrialVariant.objects.create(trial=trial, slug="stats")
    players = []
    for username in ("stats-learner", "stats-other"):
        user = django_user_model.objects.create_user(username=username)
        player = get_or_create_player(user)
        runs = {
            "challenge_run": ChallengeRun.objects.create(
                player=player,
                challenge_trial=trial,
                selected_variant=trial_variant,
                status="completed",
            ),
            "adventure_tier_run": AdventureLevelTierRun.objects.create(
                player=player,
                tier=tier,
                current_scenario=tier_scenario,
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
    return step


def _completed_tier_run(player, *, story_slug: str, suffix: str, chapter_number: int):
    story = Story.objects.create(slug=story_slug, title=suffix)
    chapter = Chapter.objects.create(
        story=story,
        slug=f"{suffix}-chapter",
        number=chapter_number,
        title=f"{suffix} chapter",
    )
    level = AdventureLevel.objects.create(
        chapter=chapter,
        slug=f"{suffix}-level",
        title=f"{suffix} level",
    )
    tier = AdventureLevelTier.objects.create(adventure_level=level, difficulty="easy")
    scenario = AdventureLevelTierScenario.objects.create(tier=tier, slug=f"{suffix}-scenario")
    variant = AdventureLevelTierScenarioVariant.objects.create(
        scenario=scenario,
        slug=f"{suffix}-variant",
    )
    run = AdventureLevelTierRun.objects.create(
        player=player,
        tier=tier,
        current_scenario=scenario,
        selected_variant=variant,
        status="completed",
    )
    return run


def test_player_steps_use_the_direct_owner_without_parent_joins(stats_players):
    (_, player, runs), (_, other_player, other_runs) = stats_players
    own_steps = [_step(runs, parent, number=1) for parent in runs]
    _step(other_runs, "adventure_tier_run", number=1)

    queryset = MetricsService()._player_steps(player=player)
    sql = str(queryset.query)

    assert set(queryset) == set(own_steps)
    assert all(step.player_id == player.id for step in own_steps)
    assert other_player.id != player.id
    assert '"practice_commandstep"."player_id"' in sql
    assert " JOIN " not in sql


@pytest.mark.parametrize("window,buckets", [("week", 7), ("month", 30), ("year", 12)])
def test_stats_include_only_runebound_tier_commands_without_leaking_other_players(
    stats_players, window, buckets
):
    (user, player, runs), (_, _, other_runs) = stats_players
    _step(runs, "challenge_run", number=1, days_ago=2)
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
    assert payload["headline"]["commands_run"] == 4
    assert payload["headline"]["accuracy"] == 50.0
    assert len(payload["activity_trend"]) == buckets
    assert sum(point["commands_run"] for point in payload["activity_trend"]) == 2
    if window != "year":
        assert payload["activity_trend"][-1]["commands_run"] == 2
    today = timezone.localdate()
    since = timezone.make_aware(datetime.combine(today - timedelta(days=6), time.min))
    assert MetricsService()._active_days(player=player, since=since) == {today}


def test_stats_count_runebound_tier_completions_in_one_query(stats_players):
    (_, player, runs), (_, other_player, _) = stats_players
    level = runs["adventure_tier_run"].tier.adventure_level
    other_level = AdventureLevel.objects.create(
        chapter=level.chapter, slug="another", title="Another"
    )
    other_tier = AdventureLevelTier.objects.create(adventure_level=other_level, difficulty="easy")
    for owner, completed_tier, stars in (
        (player, runs["adventure_tier_run"].tier, 3),
        (player, other_tier, 2),
        (other_player, runs["adventure_tier_run"].tier, 3),
    ):
        AdventureLevelTierCompletion.objects.create(player=owner, tier=completed_tier, stars=stars)

    with CaptureQueriesContext(connection) as captured:
        summary = MetricsService().stats_summary(player=player)

    assert summary["headline"]["levels_completed"] == 2
    assert summary["headline"]["perfect_clears"] == 1
    # Exclude the dated GROUP BY query used to draw activity; the headline
    # aggregate returns total, perfect, and hard counts in one round trip.
    completion_count_queries = [
        query["sql"]
        for query in captured
        if "COUNT(" in query["sql"]
        and "GROUP BY" not in query["sql"]
        and AdventureLevelTierCompletion._meta.db_table in query["sql"]
    ]
    assert len(completion_count_queries) == 1


def test_learner_progress_ignores_every_non_runebound_story(stats_players):
    (user, player, runs), _ = stats_players
    _step(runs, "adventure_tier_run", number=1)
    AdventureLevelTierCompletion.objects.create(
        player=player,
        tier=runs["adventure_tier_run"].tier,
        stars=3,
    )

    for number, slug in enumerate(
        ("retired-arcane-campaign", "frostbound-citadel", "neon-backstreets"),
        start=7,
    ):
        run = _completed_tier_run(
            player,
            story_slug=slug,
            suffix=f"retired-{number}",
            chapter_number=number,
        )
        _step({"adventure_tier_run": run}, "adventure_tier_run", number=1)
        AdventureLevelTierCompletion.objects.create(
            player=player,
            tier=run.tier,
            stars=3,
        )

    client = APIClient()
    client.force_authenticate(user=user)
    stats = client.get("/api/progress/stats/").json()
    dashboard = client.get("/api/progress/dashboard/").json()

    assert stats["headline"]["commands_run"] == 1
    assert stats["headline"]["levels_completed"] == 1
    assert stats["headline"]["perfect_clears"] == 1
    assert dashboard["counts"] == {
        "started": 1,
        "completed": 1,
        "failed": 0,
        "abandoned": 0,
    }
    assert set(dashboard["chapter_kpis"]) == {"1"}
    assert dashboard["perfect_clears"] == 1
    assert dashboard["completed_stories"] == []
