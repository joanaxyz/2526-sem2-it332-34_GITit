from datetime import date

from rest_framework.test import APIClient

from curriculum.models import CommandSkill
from progress.serializers import StatsSummaryResponseSerializer

SUMMARY_KEYS = {"skill_profile", "activity_trend", "headline"}
SKILL_AXIS_KEYS = {"key", "label", "hint", "value", "command"}
TREND_POINT_KEYS = {"date", "levels_completed", "commands_run"}
HEADLINE_KEYS = {
    "levels_completed",
    "finish_rate",
    "accuracy",
    "boss_floors",
    "comebacks",
    "perfect_clears",
    "day_streak",
    "longest_streak",
    "gitcoins",
    "commands_run",
}


def test_authenticated_stats_summary_matches_documented_contract(db, django_user_model):
    CommandSkill.objects.create(
        slug="status",
        base_command="git status",
        title="Status",
        summary="Inspect the working tree.",
        sort_order=1,
    )
    user = django_user_model.objects.create_user(
        username="stats-contract",
        email="stats-contract@example.com",
        password="pass12345",
    )
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.get("/api/progress/stats/")

    assert response.status_code == 200
    payload = response.json()
    assert set(payload) == SUMMARY_KEYS

    assert {
        "key": "status",
        "label": "Status",
        "hint": "Inspect the working tree.",
        "value": None,
        "command": "git status",
    } in payload["skill_profile"]
    assert all(set(axis) == SKILL_AXIS_KEYS for axis in payload["skill_profile"])
    assert all(
        type(axis["key"]) is str
        and type(axis["label"]) is str
        and type(axis["hint"]) is str
        and (type(axis["value"]) is float or axis["value"] is None)
        and type(axis["command"]) is str
        for axis in payload["skill_profile"]
    )

    assert len(payload["activity_trend"]) == 14
    assert all(set(point) == TREND_POINT_KEYS for point in payload["activity_trend"])
    assert all(
        type(point["date"]) is str
        and type(point["levels_completed"]) is int
        and type(point["commands_run"]) is int
        for point in payload["activity_trend"]
    )
    assert all(date.fromisoformat(point["date"]) for point in payload["activity_trend"])

    assert set(payload["headline"]) == HEADLINE_KEYS
    finish_rate = payload["headline"]["finish_rate"]
    assert finish_rate == {
        "value": None,
        "numerator": 0,
        "denominator": 0,
    }
    assert set(finish_rate) == {
        "value",
        "numerator",
        "denominator",
    }
    assert finish_rate["value"] is None
    assert type(finish_rate["numerator"]) is int
    assert type(finish_rate["denominator"]) is int
    assert payload["headline"]["accuracy"] is None
    for field_name in ("boss_floors", "comebacks"):
        scoped_count = payload["headline"][field_name]
        assert set(scoped_count) == {"value", "scope"}
        assert type(scoped_count["value"]) is int
        assert type(scoped_count["scope"]) is str
    for field_name in (
        "levels_completed",
        "perfect_clears",
        "day_streak",
        "longest_streak",
        "gitcoins",
        "commands_run",
    ):
        assert type(payload["headline"][field_name]) is int
    assert "activity" not in payload
    assert "headlines" not in payload
    assert "totals" not in payload

    documented = StatsSummaryResponseSerializer(data=payload)
    assert documented.is_valid(), documented.errors


def test_stats_contract_rejects_the_displaced_openapi_shape():
    serializer = StatsSummaryResponseSerializer(
        data={
            "skill_profile": [],
            "activity": [],
            "headlines": {},
            "totals": {},
        }
    )

    assert set(serializer.fields) == SUMMARY_KEYS
    assert serializer.is_valid() is False
    assert set(serializer.errors) == {"activity_trend", "headline"}
