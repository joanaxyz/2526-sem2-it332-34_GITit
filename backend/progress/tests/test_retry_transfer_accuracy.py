"""Restored retry-based Retry Transfer Accuracy (RTA).

Every fixture here is hand-built so each expected value can be counted by eye.
Each "chain" is a failed (or completed) first run followed by the run started
from it with ``prior_run`` set, exactly as the retry/continue endpoints do.
"""

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
    SESSION_STATUS_COMPLETED,
    SESSION_STATUS_FAILED,
    SESSION_STATUS_STARTED,
)
from curriculum.models import Chapter, Story
from players.services import get_or_create_player
from progress.services import MetricsService

NO_DATA = {"value": None, "numerator": 0, "denominator": 0}

BASE_STATE = {"branches": {"main": ["c1"]}, "files": {"app.txt": "v1"}}
OTHER_STATE = {"branches": {"main": ["c1"], "feature": ["c2"]}, "files": {"lib.txt": "v2"}}
BASE_TARGET = {"branches": {"main": ["c1", "c2"]}}
OTHER_TARGET = {"branches": {"main": ["c1", "c3"]}}


def _module(story, number):
    """One module with one tier/scenario and five variants:

    - ``a``: the original
    - ``b``: different initial_state AND target_state (structurally changed)
    - ``same``: different key, identical initial_state and target_state
    - ``target``: identical initial_state, different target_state (changed)
    - ``initial``: different initial_state, identical target_state (changed)
    """
    chapter = Chapter.objects.create(
        story=story, slug=f"module-{number}", number=number, title=f"Module {number}"
    )
    level = AdventureLevel.objects.create(
        chapter=chapter, slug=f"level-{number}", title=f"Level {number}"
    )
    tier = AdventureLevelTier.objects.create(adventure_level=level, difficulty="easy")
    scenario = AdventureLevelTierScenario.objects.create(tier=tier, slug=f"scenario-{number}")
    specs = {
        "a": (BASE_STATE, BASE_TARGET),
        "b": (OTHER_STATE, OTHER_TARGET),
        "same": (BASE_STATE, BASE_TARGET),
        "target": (BASE_STATE, OTHER_TARGET),
        "initial": (OTHER_STATE, BASE_TARGET),
    }
    variants = {
        key: AdventureLevelTierScenarioVariant.objects.create(
            scenario=scenario,
            slug=f"m{number}-{key}",
            label=key,
            semantic_key=f"m{number}-{key}",
            initial_state=initial,
            target_state=target,
        )
        for key, (initial, target) in specs.items()
    }
    return tier, scenario, variants


@pytest.fixture
def modules(db):
    story = Story.objects.create(slug=MetricsService.PERFORMANCE_STORY_SLUG, title="Legacy")
    return {number: _module(story, number) for number in (1, 2, 3, 4)}


@pytest.fixture
def learner(db, django_user_model):
    user = django_user_model.objects.create_user(username="rta-learner", password="pass12345")
    return user, get_or_create_player(user)


def _run(player, module, variant_key, status, prior=None, **extra):
    tier, scenario, variants = module
    return AdventureLevelTierRun.objects.create(
        player=player,
        tier=tier,
        current_scenario=scenario,
        selected_variant=variants[variant_key],
        prior_run=prior,
        status=status,
        retry_index=(prior.retry_index + 1) if prior else 0,
        **extra,
    )


def _rta(player=None):
    service = MetricsService()
    summary = (
        service.performance_summary(player=player)
        if player
        else service.all_player_performance_summary()
    )
    return summary


def _build_all_cases(player, modules):
    m1, m3, m4 = modules[1], modules[3], modules[4]

    # 1. Module 3: fail -> first retry on a structurally changed variant that
    #    completes. Eligible, success.
    failed = _run(player, m3, "a", SESSION_STATUS_FAILED)
    _run(player, m3, "b", SESSION_STATUS_COMPLETED, prior=failed)

    # 2. Module 3: fail -> changed retry that fails (eligible, not a success)
    #    -> later retry that completes. The later retry follows a failed retry,
    #    so it is not a new eligible session and not a success.
    failed = _run(player, m3, "a", SESSION_STATUS_FAILED)
    failed_retry = _run(player, m3, "b", SESSION_STATUS_FAILED, prior=failed)
    _run(player, m3, "target", SESSION_STATUS_COMPLETED, prior=failed_retry)

    # 3. Module 3: fail -> retry on a different key with the same structure.
    #    Excluded.
    failed = _run(player, m3, "a", SESSION_STATUS_FAILED)
    _run(player, m3, "same", SESSION_STATUS_COMPLETED, prior=failed)

    # 4. Module 3: complete -> "continue" run on a changed variant. The prior
    #    run succeeded, so this is not a retry session. Excluded.
    cleared = _run(player, m3, "a", SESSION_STATUS_COMPLETED)
    _run(player, m3, "b", SESSION_STATUS_COMPLETED, prior=cleared)

    # 5. Module 1: fail -> changed retry that completes. Outside Modules 3-4.
    #    Excluded.
    failed = _run(player, m1, "a", SESSION_STATUS_FAILED)
    _run(player, m1, "b", SESSION_STATUS_COMPLETED, prior=failed)

    # 6. Module 4: fail -> retry whose target_state alone differs, completes.
    #    Structurally changed (target differs). Eligible, success.
    failed = _run(player, m4, "a", SESSION_STATUS_FAILED)
    _run(player, m4, "target", SESSION_STATUS_COMPLETED, prior=failed)

    # 7. Module 4: fail -> changed retry still in progress. No outcome yet.
    #    Excluded.
    failed = _run(player, m4, "a", SESSION_STATUS_FAILED)
    _run(player, m4, "b", SESSION_STATUS_STARTED, prior=failed)

    # 8. Module 4: replay retry. Replays are excluded from every KPI.
    failed = _run(player, m4, "a", SESSION_STATUS_FAILED, is_replay=True)
    _run(player, m4, "b", SESSION_STATUS_COMPLETED, prior=failed, is_replay=True)


def test_rta_counts_only_first_changed_retries_after_failure(modules, learner):
    _, player = learner
    _build_all_cases(player, modules)

    summary = _rta(player)

    # Eligible: case 1 (success), case 2 first retry (fail), case 6 (success).
    assert summary["kpis"]["rta"] == {"value": 66.7, "numerator": 2, "denominator": 3}
    by_module = {module["number"]: module["rta"] for module in summary["modules"]}
    assert by_module == {
        1: NO_DATA,
        2: NO_DATA,
        3: {"value": 50.0, "numerator": 1, "denominator": 2},
        4: {"value": 100.0, "numerator": 1, "denominator": 1},
    }


@pytest.mark.parametrize(
    "case",
    ["success", "failure", "later_success", "same_structure", "continue", "module_one"],
)
def test_rta_single_case(modules, learner, case):
    """Each edge case alone, so a regression names the rule it broke."""
    _, player = learner
    m1, m3 = modules[1], modules[3]
    if case == "success":
        _run(player, m3, "b", SESSION_STATUS_COMPLETED, prior=_run(player, m3, "a", "failed"))
        expected = {"value": 100.0, "numerator": 1, "denominator": 1}
    elif case == "failure":
        _run(player, m3, "b", SESSION_STATUS_FAILED, prior=_run(player, m3, "a", "failed"))
        expected = {"value": 0.0, "numerator": 0, "denominator": 1}
    elif case == "later_success":
        first_retry = _run(
            player, m3, "b", SESSION_STATUS_FAILED, prior=_run(player, m3, "a", "failed")
        )
        _run(player, m3, "target", SESSION_STATUS_COMPLETED, prior=first_retry)
        # Only the first retry is a session, and it failed.
        expected = {"value": 0.0, "numerator": 0, "denominator": 1}
    elif case == "same_structure":
        _run(player, m3, "same", SESSION_STATUS_COMPLETED, prior=_run(player, m3, "a", "failed"))
        expected = NO_DATA
    elif case == "continue":
        _run(player, m3, "b", SESSION_STATUS_COMPLETED, prior=_run(player, m3, "a", "completed"))
        expected = NO_DATA
    else:
        _run(player, m1, "b", SESSION_STATUS_COMPLETED, prior=_run(player, m1, "a", "failed"))
        expected = NO_DATA

    assert _rta(player)["kpis"]["rta"] == expected


def test_rta_with_no_eligible_sessions_is_null_not_zero(modules, learner, django_user_model):
    user, player = learner
    # Only first runs: nothing is a retry session.
    _run(player, modules[3], "a", SESSION_STATUS_FAILED)
    _run(player, modules[4], "a", SESSION_STATUS_COMPLETED)

    assert _rta(player)["kpis"]["rta"] == NO_DATA
    assert _rta()["kpis"]["rta"] == {**NO_DATA, "unit": "participants"}

    staff = django_user_model.objects.create_user(
        username="rta-staff", password="pass12345", is_staff=True
    )
    client = APIClient()
    client.force_authenticate(user=staff)
    user_kpis = client.get(f"/api/admin/users/{user.id}/kpis/")
    analytics = client.get("/api/admin/analytics/")
    assert user_kpis.status_code == 200
    assert analytics.status_code == 200
    assert user_kpis.json()["kpis"]["rta"] == NO_DATA
    assert analytics.json()["runebound_performance"]["kpis"]["rta"] == {
        **NO_DATA,
        "unit": "participants",
    }


def test_both_admin_endpoints_report_the_same_rta(modules, learner, django_user_model):
    user, player = learner
    _build_all_cases(player, modules)
    staff = django_user_model.objects.create_user(
        username="rta-staff", password="pass12345", is_staff=True
    )
    client = APIClient()
    client.force_authenticate(user=staff)

    user_body = client.get(f"/api/admin/users/{user.id}/kpis/").json()
    dashboard_body = client.get("/api/admin/analytics/").json()["runebound_performance"]

    expected = {"value": 66.7, "numerator": 2, "denominator": 3}
    assert user_body["kpis"]["rta"] == expected
    assert dashboard_body["kpis"]["rta"] == {
        "value": 66.7,
        "numerator": 66.7,
        "denominator": 1,
        "unit": "participants",
    }
    assert [m["rta"]["value"] for m in user_body["modules"]] == [
        m["rta"]["value"] for m in dashboard_body["modules"]
    ]
    assert user_body["has_data"] is True


def test_initial_state_change_alone_qualifies(modules, learner):
    _, player = learner
    failed = _run(player, modules[3], "a", SESSION_STATUS_FAILED)
    _run(player, modules[3], "initial", SESSION_STATUS_COMPLETED, prior=failed)
    assert _rta(player)["kpis"]["rta"] == {"value": 100, "numerator": 1, "denominator": 1}


@pytest.mark.parametrize("module", [1, 2])
def test_changed_retries_in_other_modules_are_excluded(modules, learner, module):
    _, player = learner
    failed = _run(player, modules[module], "a", SESSION_STATUS_FAILED)
    _run(player, modules[module], "b", SESSION_STATUS_COMPLETED, prior=failed)
    assert _rta(player)["kpis"]["rta"] == NO_DATA


@pytest.mark.parametrize("status", ["started", "abandoned"])
def test_unfinished_or_abandoned_first_retries_are_excluded(modules, learner, status):
    _, player = learner
    failed = _run(player, modules[3], "a", SESSION_STATUS_FAILED)
    _run(player, modules[3], "b", status, prior=failed)
    assert _rta(player)["kpis"]["rta"] == NO_DATA
