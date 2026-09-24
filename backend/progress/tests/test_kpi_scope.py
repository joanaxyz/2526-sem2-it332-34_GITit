"""Admin KPI scope: staff accounts are excluded, and an optional date range in
Philippine time (Asia/Manila, UTC+8) limits runs by started_at."""

from datetime import UTC, date, datetime

import pytest
from rest_framework.test import APIClient

from adventures.models import (
    AdventureLevel,
    AdventureLevelTier,
    AdventureLevelTierRun,
    AdventureLevelTierWave,
    AdventureLevelTierWaveVariant,
)
from common.constants import (
    DIFFICULTY_HARD,
    SESSION_STATUS_ABANDONED,
    SESSION_STATUS_COMPLETED,
    SESSION_STATUS_FAILED,
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
    wave = AdventureLevelTierWave.objects.create(tier=hard, slug="m3-hard")
    variants = {
        key: AdventureLevelTierWaveVariant.objects.create(
            wave=wave,
            slug=f"scope-{key}",
            label=key,
            semantic_key=f"scope-{key}",
            initial_state={"files": {f"{key}.txt": key}},
            target_state={"files": {f"{key}.txt": "done"}},
        )
        for key in ("a", "b")
    }
    return hard, wave, variants


def _player(django_user_model, username, *, staff=False):
    user = django_user_model.objects.create_user(
        username=username, password="pass12345", is_staff=staff
    )
    return user, get_or_create_player(user)


def _run(player, bundle, variant, status, *, prior=None, started_at=None, steps=(True,)):
    tier, wave, variants = bundle
    run = AdventureLevelTierRun.objects.create(
        player=player,
        tier=tier,
        current_wave=wave,
        selected_variant=variants[variant],
        prior_run=prior,
        status=status,
        retry_index=(prior.retry_index + 1) if prior else 0,
    )
    if started_at is not None:
        # started_at is auto_now_add, so it is set after creation.
        AdventureLevelTierRun.objects.filter(pk=run.pk).update(started_at=started_at)
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


# ------------------------------------------------------------ staff ---


def test_staff_runs_change_no_admin_kpi(tier, django_user_model):
    learner_user, learner = _player(django_user_model, "scope-learner")
    failed = _run(learner, tier, "a", SESSION_STATUS_FAILED)
    _run(learner, tier, "b", SESSION_STATUS_COMPLETED, prior=failed)
    service = MetricsService()
    before = (service.all_player_performance_summary(), service.all_player_objective_car())

    # A teammate play-tests with a staff account: every kind of run.
    tester_user, tester = _player(django_user_model, "scope-tester", staff=True)
    t_failed = _run(tester, tier, "a", SESSION_STATUS_FAILED, steps=(False, False))
    _run(tester, tier, "b", SESSION_STATUS_ABANDONED, prior=t_failed, steps=(False,))
    _run(tester, tier, "a", SESSION_STATUS_COMPLETED)
    _run(tester, tier, "a", SESSION_STATUS_FAILED, steps=(False,))

    after = (service.all_player_performance_summary(), service.all_player_objective_car())
    assert after == before

    client = _staff_client(django_user_model)
    body = client.get("/api/admin/analytics/").json()
    assert body["runebound_performance"] == before[0]
    assert body["objectives"] == before[1]
    # The sessions counter is the SCR denominator: the learner's 2 runs only.
    assert body["runebound_performance"]["kpis"]["scr"]["denominator"] == 2

    tester_panel = client.get(f"/api/admin/users/{tester_user.id}/kpis/").json()
    assert tester_panel["has_data"] is False
    assert tester_panel["kpis"]["scr"]["denominator"] == 0
    learner_panel = client.get(f"/api/admin/users/{learner_user.id}/kpis/").json()
    assert learner_panel["kpis"]["scr"] == before[0]["kpis"]["scr"]


def test_learner_performance_page_still_includes_a_staff_players_own_runs(tier, django_user_model):
    _, tester = _player(django_user_model, "scope-self", staff=True)
    _run(tester, tier, "a", SESSION_STATUS_COMPLETED)

    own = MetricsService().performance_summary(player=tester)

    assert own["kpis"]["scr"] == {"value": 100.0, "numerator": 1, "denominator": 1}


# ------------------------------------------------------- date range ---


def test_range_converts_manila_days_to_utc():
    assert OCT_1_TO_10.start_at.astimezone(UTC) == utc(2026, 9, 30, 16)
    assert OCT_1_TO_10.end_before.astimezone(UTC) == utc(2026, 10, 10, 16)
    assert ALL_TIME.is_bounded is False
    assert ALL_TIME.start_at is None and ALL_TIME.end_before is None


def test_range_includes_whole_local_days_and_late_night_sessions(tier, django_user_model):
    _, learner = _player(django_user_model, "scope-dates")
    # Oct 1 00:00 Manila (inside, first instant).
    _run(learner, tier, "a", SESSION_STATUS_COMPLETED, started_at=utc(2026, 9, 30, 16, 0))
    # Oct 10 23:30 Manila, late at night on the last day (inside).
    _run(learner, tier, "a", SESSION_STATUS_FAILED, started_at=utc(2026, 10, 10, 15, 30))
    # Sep 30 23:59 Manila (outside, the day before).
    _run(learner, tier, "a", SESSION_STATUS_COMPLETED, started_at=utc(2026, 9, 30, 15, 59))
    # Oct 11 00:00 Manila (outside, the day after).
    _run(learner, tier, "a", SESSION_STATUS_COMPLETED, started_at=utc(2026, 10, 10, 16, 0))

    ranged = MetricsService().all_player_performance_summary(kpi_range=OCT_1_TO_10)
    everything = MetricsService().all_player_performance_summary()

    assert ranged["kpis"]["scr"] == {"value": 50.0, "numerator": 1, "denominator": 2}
    assert ranged["kpis"]["car"]["denominator"] == 2
    assert everything["kpis"]["scr"] == {"value": 75.0, "numerator": 3, "denominator": 4}
    # One-sided ranges work too.
    from_oct_1 = KpiRange(start_date=date(2026, 10, 1))
    assert (
        MetricsService().all_player_performance_summary(kpi_range=from_oct_1)["kpis"]["scr"][
            "denominator"
        ]
        == 3
    )


def test_per_so_car_honours_the_range(tier, django_user_model):
    _, learner = _player(django_user_model, "scope-car")
    _run(learner, tier, "a", SESSION_STATUS_COMPLETED, started_at=utc(2026, 10, 5), steps=(True,))
    _run(learner, tier, "a", SESSION_STATUS_FAILED, started_at=utc(2026, 11, 5), steps=(False,))

    ranged = MetricsService().all_player_objective_car(kpi_range=OCT_1_TO_10)

    assert ranged["SO 3.1"] == {"value": 100.0, "numerator": 1, "denominator": 1}


def test_rta_counts_a_retry_only_when_its_failure_is_also_in_range(tier, django_user_model):
    _, learner = _player(django_user_model, "scope-rta")
    # Failure before the range, retry inside it: not counted.
    old_failure = _run(learner, tier, "a", SESSION_STATUS_FAILED, started_at=utc(2026, 9, 25))
    _run(
        learner,
        tier,
        "b",
        SESSION_STATUS_COMPLETED,
        prior=old_failure,
        started_at=utc(2026, 10, 2),
    )
    # Failure and retry both inside: counted (a failed retry).
    failure = _run(learner, tier, "a", SESSION_STATUS_FAILED, started_at=utc(2026, 10, 3))
    _run(learner, tier, "b", SESSION_STATUS_FAILED, prior=failure, started_at=utc(2026, 10, 3, 1))

    ranged = MetricsService().all_player_performance_summary(kpi_range=OCT_1_TO_10)
    everything = MetricsService().all_player_performance_summary()

    assert ranged["kpis"]["rta"] == {"value": 0.0, "numerator": 0, "denominator": 1}
    assert everything["kpis"]["rta"] == {"value": 50.0, "numerator": 1, "denominator": 2}


def test_no_range_is_the_current_behaviour(tier, django_user_model):
    _, learner = _player(django_user_model, "scope-none")
    _run(learner, tier, "a", SESSION_STATUS_COMPLETED, started_at=utc(2020, 1, 1))
    _run(learner, tier, "a", SESSION_STATUS_FAILED, started_at=utc(2030, 1, 1))
    service = MetricsService()

    assert service.all_player_performance_summary() == service.all_player_performance_summary(
        kpi_range=ALL_TIME
    )
    assert service.all_player_performance_summary()["kpis"]["scr"]["denominator"] == 2


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
    assert unbounded["runebound_performance"]["kpis"]["scr"]["denominator"] == 2


@pytest.mark.parametrize(
    "query",
    ["?start_date=2026-10-10&end_date=2026-10-01", "?start_date=not-a-date"],
)
def test_endpoints_reject_an_invalid_range(db, django_user_model, query):
    client = _staff_client(django_user_model)

    assert client.get(f"/api/admin/analytics/{query}").status_code == 400
