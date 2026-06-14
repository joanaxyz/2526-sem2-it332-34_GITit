from django.core.management import call_command
from rest_framework.test import APIClient

from command_adventures.models import (
    AdventureLevel,
    AdventureLevelAttempt,
    AdventureMastery,
    AdventureRun,
    CommandAdventure,
)
from practice.models import CommandStep
from progress.models import LevelCompletion
from progress.services import TREND_DAYS


def make_user(django_user_model, username: str = "student"):
    return django_user_model.objects.create_user(
        username=username,
        email=f"{username}@example.com",
        password="pass12345",
    )


def axis(body: dict, key: str) -> dict:
    return next(item for item in body["skill_profile"] if item["key"] == key)


def test_stats_empty_user_is_graceful(db, django_user_model):
    user = make_user(django_user_model)
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.get("/api/progress/stats/")

    assert response.status_code == 200
    body = response.json()

    # All six axes present, each null (no data) - never NaN or a misleading 0.
    assert [item["key"] for item in body["skill_profile"]] == [
        "accuracy",
        "efficiency",
        "independence",
        "consistency",
        "mastery",
        "coverage",
    ]
    assert all(item["value"] is None for item in body["skill_profile"])
    assert all(item["label"] and item["hint"] for item in body["skill_profile"])

    # Trend is zero-filled for the whole window.
    assert len(body["activity_trend"]) == TREND_DAYS
    assert all(point["levels_completed"] == 0 and point["commands_run"] == 0 for point in body["activity_trend"])

    headline = body["headline"]
    assert headline["levels_completed"] == 0
    assert headline["commands_run"] == 0
    assert headline["gitcoins"] == 0
    assert headline["day_streak"] == 0
    assert headline["boss_floors"] == {"value": 0, "scope": "challenge"}
    assert headline["comebacks"] == {"value": 0, "scope": "challenge"}


def test_stats_adventure_only_user_gets_full_radar(db, django_user_model):
    """An adventure-only learner (no challenges) still gets non-null Accuracy,
    Efficiency, Independence, Mastery, and Coverage - the whole point of the
    rework is that adventures are first-class in the metrics."""
    call_command("seed_curriculum_v2")
    user = make_user(django_user_model)

    adventure = CommandAdventure.objects.filter(is_published=True).first()
    level = (
        AdventureLevel.objects.filter(
            command_form__command_skill__storey=adventure.storey, adventure_variants__isnull=False
        )
        .distinct()
        .first()
    )
    variant = level.adventure_variants.first()

    run = AdventureRun.objects.create(user=user, command_adventure=adventure, mode="primary")
    attempt = AdventureLevelAttempt.objects.create(
        run=run,
        adventure_level=level,
        selected_variant=variant,
        status="completed",
        correctness_score=100,
        efficiency_score=80,
        independence_score=100,
        final_score=90,
        mastery_gain=1.0,
        command_count=3,
        counted_command_count=2,
    )
    # One clean command, one invalid - accuracy should be 50%.
    CommandStep.objects.create(
        attempt=attempt,
        command_text="git status",
        result_category="TargetMatched",
        command_classification="counted_action",
        attempt_number=1,
    )
    CommandStep.objects.create(
        attempt=attempt,
        command_text="git oops",
        result_category="Invalid",
        command_classification="counted_action",
        attempt_number=2,
    )
    AdventureMastery.objects.create(
        user=user,
        adventure_level=level,
        strength=level.required_successful_attempts,
        introduced=True,
    )
    LevelCompletion.objects.create(
        user=user, adventure_level=level, first_attempt_star=True, counted_action_total=2
    )

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.get("/api/progress/stats/")

    assert response.status_code == 200
    body = response.json()

    assert axis(body, "accuracy")["value"] == 50.0
    assert axis(body, "efficiency")["value"] == 80.0
    assert axis(body, "independence")["value"] == 100.0
    assert axis(body, "mastery")["value"] == 100.0
    assert axis(body, "coverage")["value"] is not None and axis(body, "coverage")["value"] > 0
    assert axis(body, "consistency")["value"] is not None

    headline = body["headline"]
    assert headline["levels_completed"] == 1
    assert headline["perfect_clears"] == 1
    assert headline["commands_run"] == 2
    # Challenge-scoped numbers stay zero (and flagged), never faked from command_adventures.
    assert headline["boss_floors"] == {"value": 0, "scope": "challenge"}
    assert headline["comebacks"] == {"value": 0, "scope": "challenge"}

    # Today registered as an active day in the trend.
    assert body["activity_trend"][-1]["commands_run"] == 2
    assert body["activity_trend"][-1]["levels_completed"] == 1
