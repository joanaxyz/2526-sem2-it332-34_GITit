"""Admin KPI scope: staff accounts are excluded, and an optional date range in
Philippine time (Asia/Manila, UTC+8) limits runs by started_at."""

from datetime import UTC, date, datetime

import pytest
from rest_framework.test import APIClient

from adventures.models import (
    AdventureLevel,
    AdventureLevelTier,
    AdventureLevelTierRun,
    AdventureLevelTierScenario,
    AdventureLevelTierScenarioVariant,
)
from common.constants import (
    DIFFICULTY_HARD,
    SESSION_STATUS_COMPLETED,
    SESSION_STATUS_FAILED,
    SESSION_STATUS_STARTED,
)
from curriculum.models import Chapter, Story
from players.services import get_or_create_player
from practice.models import CommandStep
from progress.services import MetricsService
from progress.services.kpi_range import ALL_TIME, KpiRange

OCT_1_TO_10 = KpiRange(start_date=date(2026, 10, 1), end_date=date(2026, 10, 10))


def utc(*args):
    return datetime(*args, tzinfo=UTC)


@pytest.fixture
def tier(db):
    """Module 3 hard tier (mapped to SO 3.1) with two structurally different variants."""
    story = Story.objects.create(slug=MetricsService.PERFORMANCE_STORY_SLUG, title="Legacy")
    chapter = Chapter.objects.create(story=story, slug="m3", number=3, title="Module 3")
    level = AdventureLevel.objects.create(
        chapter=chapter, slug="resolving-conflicts-manually", title="Level"
    )
    hard = AdventureLevelTier.objects.create(adventure_level=level, difficulty=DIFFICULTY_HARD)
    scenario = AdventureLevelTierScenario.objects.create(tier=hard, slug="m3-hard")
    variants = {
        key: AdventureLevelTierScenarioVariant.objects.create(
            scenario=scenario,
            slug=f"scope-{key}",
            label=key,
            semantic_key=f"scope-{key}",
            initial_state={"files": {f"{key}.txt": key}},
            target_state={"files": {f"{key}.txt": "done"}},
        )
        for key in ("a", "b")
    }
    return hard, scenario, variants


def _player(django_user_model, username, *, staff=False):
    user = django_user_model.objects.create_user(
        username=username, password="pass12345", is_staff=staff
    )
    return user, get_or_create_player(user)


def _run(player, bundle, variant, status, *, prior=None, started_at=None, steps=(True,)):
    tier, scenario, variants = bundle
    run = AdventureLevelTierRun.objects.create(
        player=player,
        tier=tier,
        current_scenario=scenario,
        selected_variant=variants[variant],
        prior_run=prior,
        status=status,
        retry_index=(prior.retry_index + 1) if prior else 0,
    )
    if started_at is not None:
        # started_at is auto_now_add, so it is set after creation. A concluded
        # run ends when it starts here, as the runtime always stamps ended_at.
        AdventureLevelTierRun.objects.filter(pk=run.pk).update(
            started_at=started_at,
            ended_at=None if status == SESSION_STATUS_STARTED else started_at,
        )
        run.refresh_from_db()
    for index, ok in enumerate(steps, start=1):
        CommandStep.objects.create(
            adventure_tier_run=run,
            command_text="git status" if ok else "git nonsense",
            normalized_command="git status" if ok else "git nonsense",
            result_category=(
                CommandStep.ResultCategory.TARGET_MATCHED
                if ok
                else CommandStep.ResultCategory.INVALID
            ),
            command_classification=(
                CommandStep.CommandClassification.DIAGNOSTIC
                if ok
                else CommandStep.CommandClassification.UNPROCESSABLE
            ),
            was_processable=ok,
            attempt_number=index,
        )
    return run


def _staff_client(django_user_model):
    staff, _ = _player(django_user_model, "scope-admin", staff=True)
    client = APIClient()
    client.force_authenticate(user=staff)
    return client


def test_range_converts_manila_days_to_utc():
    assert OCT_1_TO_10.start_at.astimezone(UTC) == utc(2026, 9, 30, 16)
    assert OCT_1_TO_10.end_before.astimezone(UTC) == utc(2026, 10, 10, 16)
    assert ALL_TIME.is_bounded is False
    assert ALL_TIME.start_at is None and ALL_TIME.end_before is None


def test_endpoints_accept_and_echo_the_range(tier, django_user_model):
    learner_user, learner = _player(django_user_model, "scope-api")
    _run(learner, tier, "a", SESSION_STATUS_COMPLETED, started_at=utc(2026, 10, 10, 15, 30))
    _run(learner, tier, "a", SESSION_STATUS_COMPLETED, started_at=utc(2026, 10, 10, 16, 0))
    client = _staff_client(django_user_model)
    params = "?start_date=2026-10-01&end_date=2026-10-10"

    analytics = client.get(f"/api/admin/analytics/{params}").json()
    panel = client.get(f"/api/admin/users/{learner_user.id}/kpis/{params}").json()
    unbounded = client.get("/api/admin/analytics/").json()

    assert analytics["kpi_range"] == {
        "start_date": "2026-10-01",
        "end_date": "2026-10-10",
        "timezone": "Asia/Manila",
    }
    assert analytics["runebound_performance"]["kpis"]["scr"]["denominator"] == 1
    assert panel["kpis"]["scr"]["denominator"] == 1
    assert unbounded["kpi_range"] == {
        "start_date": None,
        "end_date": None,
        "timezone": "Asia/Manila",
    }
    assert unbounded["runebound_performance"]["kpis"]["scr"]["denominator"] == 1


@pytest.mark.parametrize(
    "query",
    ["?start_date=2026-10-10&end_date=2026-10-01", "?start_date=not-a-date"],
)
def test_endpoints_reject_an_invalid_range(db, django_user_model, query):
    client = _staff_client(django_user_model)

    assert client.get(f"/api/admin/analytics/{query}").status_code == 400


# -------------------------------------------- supplementary retry rate ---


def test_staff_accounts_do_not_change_cohort_means(tier, django_user_model):
    _, learner = _player(django_user_model, "learner")
    _run(learner, tier, "a", SESSION_STATUS_FAILED)
    service = MetricsService()
    before = service.all_player_performance_summary()
    _, staff = _player(django_user_model, "staff", staff=True)
    _run(staff, tier, "a", SESSION_STATUS_COMPLETED)
    assert service.all_player_performance_summary() == before
    assert service.admin_player_performance_summary(player=staff)["samples"]["attempted_tiers"] == 0
    assert service.performance_summary(player=staff)["samples"]["attempted_tiers"] == 1


def test_failed_only_activity_is_data_and_retries_do_not_expand_tiers(tier, django_user_model):
    user, player = _player(django_user_model, "failed")
    first = _run(player, tier, "a", SESSION_STATUS_FAILED)
    _run(player, tier, "b", SESSION_STATUS_FAILED, prior=first)
    report = MetricsService().performance_summary(player=player)
    assert report["kpis"]["scr"] == {"value": 0, "numerator": 0, "denominator": 1}
    assert report["kpis"]["arc"]["value"] is None
    client = _staff_client(django_user_model)
    assert client.get(f"/api/admin/users/{user.id}/kpis/").json()["has_data"] is True


def test_range_selects_starts_but_excludes_assessments_ending_after_cutoff(tier, django_user_model):
    from progress.models import AdventureLevelTierCompletion, KpiCheckpoint

    _, player = _player(django_user_model, "date")
    run = _run(player, tier, "a", SESSION_STATUS_COMPLETED, started_at=utc(2026, 10, 1))
    completion = AdventureLevelTierCompletion.objects.create(
        player=player, tier=tier[0], tier_run=run
    )
    AdventureLevelTierCompletion.objects.filter(pk=completion.pk).update(
        completed_at=utc(2026, 10, 11)
    )
    point = KpiCheckpoint.objects.create(
        player=player,
        tier=tier[0],
        kind="car",
        run=run,
        passed=True,
        ref_count=3,
        actual=4,
        ended_at=utc(2026, 10, 11),
    )
    KpiCheckpoint.objects.filter(pk=point.pk).update(assigned_at=utc(2026, 10, 1))
    ranged = MetricsService().admin_player_performance_summary(player=player, kpi_range=OCT_1_TO_10)
    assert ranged["kpis"]["scr"]["value"] == 0
    assert ranged["kpis"]["car"]["value"] is None
    all_time = MetricsService().admin_player_performance_summary(player=player)
    assert all_time["kpis"]["scr"]["value"] == 100
    assert all_time["kpis"]["car"]["value"] == 75


def test_learner_and_all_time_admin_player_report_are_identical(tier, django_user_model):
    _, player = _player(django_user_model, "parity")
    _run(player, tier, "a", SESSION_STATUS_FAILED)
    service = MetricsService()
    assert service.performance_summary(player=player) == service.admin_player_performance_summary(
        player=player
    )
