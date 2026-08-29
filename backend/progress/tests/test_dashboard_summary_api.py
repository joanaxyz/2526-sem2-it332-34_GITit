from datetime import date

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from challenges.models import ChallengeRun
from common.constants import SESSION_STATUS_COMPLETED, SESSION_STATUS_FAILED
from progress.models import StreakRecord
from progress.serializers import DashboardSummaryResponseSerializer
from testing.runtime_factories import create_stage_readme_challenge_run

SUMMARY_KEYS = {
    "kpis",
    "chapter_kpis",
    "counts",
    "completed_story_slug",
    "completed_stories",
    "streak",
    "perfect_clears",
    "mastery",
    "retry_trends",
}
KPI_KEYS = {"scr", "arc", "hlcr"}
RATE_KEYS = {"value", "numerator", "denominator"}
COUNT_KEYS = {"started", "completed", "failed", "abandoned"}
STREAK_KEYS = {"current", "longest", "last_completed_on"}
RETRY_KEYS = {"level_title", "attempts", "retries", "label"}


def assert_rate_metric(metric):
    assert set(metric) == RATE_KEYS
    assert metric["value"] is None or type(metric["value"]) in {int, float}
    assert type(metric["numerator"]) is int
    assert type(metric["denominator"]) is int


def assert_dashboard_wire_shape(payload):
    assert set(payload) == SUMMARY_KEYS
    assert set(payload["kpis"]) == KPI_KEYS
    for metric in payload["kpis"].values():
        assert_rate_metric(metric)

    assert type(payload["chapter_kpis"]) is dict
    for chapter_number, kpis in payload["chapter_kpis"].items():
        assert type(chapter_number) is str
        assert set(kpis) == KPI_KEYS
        for metric in kpis.values():
            assert_rate_metric(metric)

    assert set(payload["counts"]) == COUNT_KEYS
    assert all(type(value) is int for value in payload["counts"].values())
    assert payload["completed_story_slug"] is None or type(payload["completed_story_slug"]) is str
    assert type(payload["completed_stories"]) is list
    assert all(type(slug) is str for slug in payload["completed_stories"])

    streak = payload["streak"]
    assert set(streak) == STREAK_KEYS
    assert type(streak["current"]) is int
    assert type(streak["longest"]) is int
    if streak["last_completed_on"] is not None:
        assert date.fromisoformat(streak["last_completed_on"])

    assert type(payload["perfect_clears"]) is int
    assert type(payload["mastery"]) in {int, float}
    assert type(payload["retry_trends"]) is list
    for row in payload["retry_trends"]:
        assert set(row) == RETRY_KEYS
        assert type(row["level_title"]) is str
        assert type(row["attempts"]) is int
        assert type(row["retries"]) is int
        assert type(row["label"]) is str


def test_authenticated_empty_dashboard_matches_exact_documented_contract(db, django_user_model):
    user = django_user_model.objects.create_user(
        username="dashboard-contract-empty",
        email="dashboard-contract-empty@example.com",
        password="pass12345",
    )
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.get("/api/progress/dashboard/")

    assert response.status_code == 200
    payload = response.json()
    assert_dashboard_wire_shape(payload)
    assert payload["chapter_kpis"] == {}
    assert payload["counts"] == {
        "started": 0,
        "completed": 0,
        "failed": 0,
        "abandoned": 0,
    }
    assert payload["completed_story_slug"] is None
    assert payload["completed_stories"] == []
    assert payload["streak"] == {
        "current": 0,
        "longest": 0,
        "last_completed_on": None,
    }
    assert payload["retry_trends"] == []

    documented = DashboardSummaryResponseSerializer(data=payload)
    assert documented.is_valid(), documented.errors

    displaced = dict(payload)
    displaced.pop("completed_story_slug")
    displaced["retry_trends"] = {}
    rejected = DashboardSummaryResponseSerializer(data=displaced)
    assert rejected.is_valid() is False
    assert set(rejected.errors) == {"completed_story_slug", "retry_trends"}


def test_authenticated_dashboard_exposes_typed_chapter_and_retry_rows(db):
    fixture = create_stage_readme_challenge_run(
        get_user_model(), username="dashboard-contract-seeded"
    )
    fixture.run.status = SESSION_STATUS_COMPLETED
    fixture.run.retry_index = 0
    fixture.run.save(update_fields=["status", "retry_index"])
    ChallengeRun.objects.create(
        player=fixture.player,
        challenge_trial=fixture.trial,
        selected_variant=fixture.variant,
        prior_run=fixture.run,
        source_entry_point="runtime_test",
        status=SESSION_STATUS_FAILED,
        retry_index=1,
        min_counted_commands=fixture.trial.min_counted_commands,
        max_counted_commands=fixture.trial.max_counted_commands,
        repository_state=fixture.states.initial,
    )
    StreakRecord.objects.create(
        player=fixture.player,
        current_streak=3,
        longest_streak=5,
        last_completed_on=date(2026, 8, 9),
    )
    client = APIClient()
    client.force_authenticate(user=fixture.user)

    response = client.get("/api/progress/dashboard/")

    assert response.status_code == 200
    payload = response.json()
    assert_dashboard_wire_shape(payload)
    assert payload["counts"] == {
        "started": 2,
        "completed": 1,
        "failed": 1,
        "abandoned": 0,
    }
    assert payload["kpis"]["scr"] == {
        "value": 50.0,
        "numerator": 1,
        "denominator": 2,
    }
    chapter_kpis = payload["chapter_kpis"][str(fixture.chapter.number)]
    assert chapter_kpis["scr"] == payload["kpis"]["scr"]
    assert payload["streak"] == {
        "current": 3,
        "longest": 5,
        "last_completed_on": "2026-08-09",
    }
    assert payload["retry_trends"] == [
        {
            "level_title": "Stage README Challenge",
            "attempts": 2,
            "retries": 1,
            "label": "1 retry runs",
        }
    ]
    assert "completed_story_slug" in payload
    assert "completed_stories" in payload

    documented = DashboardSummaryResponseSerializer(data=payload)
    assert documented.is_valid(), documented.errors
