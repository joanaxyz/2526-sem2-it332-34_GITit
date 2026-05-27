import pytest
from django.contrib.auth import get_user_model

from common.constants import (
    DIFFICULTY_EASY,
    DIFFICULTY_HARD,
    SESSION_MODE_PRIMARY,
    SESSION_STATUS_COMPLETED,
    SESSION_STATUS_FAILED,
)
from learning.models import LearningUnit, Lesson
from progress.services import MetricsService
from scenarios.models import DifficultyInstance, ScenarioSession, ScenarioSkillFocus, ScenarioVariant


def _module_content(*, number: int, slug: str):
    unit = LearningUnit.objects.create(
        slug=f"module-{number}-{slug}",
        number=number,
        title=f"Module {number}",
        description=f"Module {number} tests",
        is_published=True,
    )
    lesson = Lesson.objects.create(
        unit=unit,
        slug=f"lesson-{slug}",
        title=f"Lesson {slug}",
        content_html="<p>Test</p>",
        is_published=True,
    )
    scenario = ScenarioSkillFocus.objects.create(
        learning_unit=unit,
        lesson=lesson,
        slug=f"scenario-{slug}",
        title=f"Scenario {slug}",
        focus="focus",
        is_published=True,
    )
    hard_difficulty = DifficultyInstance.objects.create(
        scenario=scenario,
        difficulty=DIFFICULTY_HARD,
        required_successful_attempts=1,
        is_published=True,
    )
    easy_difficulty = DifficultyInstance.objects.create(
        scenario=scenario,
        difficulty=DIFFICULTY_EASY,
        required_successful_attempts=1,
        is_published=True,
    )
    hard_variant = ScenarioVariant.objects.create(
        scenario=scenario,
        difficulty_instance=hard_difficulty,
        slug=f"hard-{slug}",
        label=f"Hard {slug}",
        structure_signature=f"hard-{slug}",
        initial_state={"branches": {}, "commits": []},
        target_rule={},
        target_state={"branches": {}, "commits": []},
        expected_state_diagram={},
        case_id=f"hard-{slug}",
        semantic_key=f"hard-{slug}",
    )
    easy_variant = ScenarioVariant.objects.create(
        scenario=scenario,
        difficulty_instance=easy_difficulty,
        slug=f"easy-{slug}",
        label=f"Easy {slug}",
        structure_signature=f"easy-{slug}",
        initial_state={"branches": {}, "commits": []},
        target_rule={},
        target_state={"branches": {}, "commits": []},
        expected_state_diagram={},
        case_id=f"easy-{slug}",
        semantic_key=f"easy-{slug}",
    )
    return unit, scenario, hard_difficulty, easy_difficulty, hard_variant, easy_variant


def _session(*, user, unit, scenario, difficulty, variant, status, rta_eligible=False, rta_success=False):
    return ScenarioSession.objects.create(
        user=user,
        learning_unit=unit,
        scenario=scenario,
        difficulty_instance=difficulty,
        variant=variant,
        source_entry_point="module_card",
        mode=SESSION_MODE_PRIMARY,
        status=status,
        rta_eligible=rta_eligible,
        rta_success=rta_success,
        command_policy_snapshot={},
        repository_state=variant.initial_state,
    )


@pytest.mark.django_db
def test_dashboard_summary_includes_stable_module_kpi_keys():
    user = get_user_model().objects.create_user(
        username="module-kpi-empty@example.com",
        email="module-kpi-empty@example.com",
        password="Password123!",
    )

    summary = MetricsService().dashboard_summary(user=user)

    assert set(summary["module_kpis"].keys()) == {"1", "2", "3", "4"}
    for module_data in summary["module_kpis"].values():
        assert module_data["hlcr"] == {"value": None, "numerator": 0, "denominator": 0}
        assert module_data["rta"] == {"value": None, "numerator": 0, "denominator": 0}


@pytest.mark.django_db
def test_dashboard_summary_calculates_module_rates_without_changing_overall_kpis():
    user = get_user_model().objects.create_user(
        username="module-kpi-rates@example.com",
        email="module-kpi-rates@example.com",
        password="Password123!",
    )
    (
        module_1,
        scenario_1,
        hard_1,
        easy_1,
        hard_variant_1,
        easy_variant_1,
    ) = _module_content(number=1, slug="m1")
    (
        module_2,
        scenario_2,
        hard_2,
        _easy_2,
        hard_variant_2,
        _easy_variant_2,
    ) = _module_content(number=2, slug="m2")

    _session(
        user=user,
        unit=module_1,
        scenario=scenario_1,
        difficulty=hard_1,
        variant=hard_variant_1,
        status=SESSION_STATUS_COMPLETED,
        rta_eligible=True,
        rta_success=True,
    )
    _session(
        user=user,
        unit=module_1,
        scenario=scenario_1,
        difficulty=hard_1,
        variant=hard_variant_1,
        status=SESSION_STATUS_COMPLETED,
        rta_eligible=True,
        rta_success=False,
    )
    _session(
        user=user,
        unit=module_1,
        scenario=scenario_1,
        difficulty=hard_1,
        variant=hard_variant_1,
        status=SESSION_STATUS_FAILED,
    )
    _session(
        user=user,
        unit=module_1,
        scenario=scenario_1,
        difficulty=easy_1,
        variant=easy_variant_1,
        status=SESSION_STATUS_COMPLETED,
    )
    _session(
        user=user,
        unit=module_2,
        scenario=scenario_2,
        difficulty=hard_2,
        variant=hard_variant_2,
        status=SESSION_STATUS_COMPLETED,
        rta_eligible=True,
        rta_success=False,
    )

    summary = MetricsService().dashboard_summary(user=user)

    assert summary["module_kpis"]["1"]["hlcr"] == {
        "value": 66.7,
        "numerator": 2,
        "denominator": 3,
    }
    assert summary["module_kpis"]["1"]["rta"] == {
        "value": 50.0,
        "numerator": 1,
        "denominator": 2,
    }
    assert summary["module_kpis"]["2"]["hlcr"] == {
        "value": 100.0,
        "numerator": 1,
        "denominator": 1,
    }
    assert summary["module_kpis"]["2"]["rta"] == {
        "value": 0.0,
        "numerator": 0,
        "denominator": 1,
    }
    assert summary["module_kpis"]["3"]["hlcr"]["value"] is None
    assert summary["module_kpis"]["4"]["rta"]["value"] is None

    assert summary["kpis"]["hlcr"] == {"value": 75.0, "numerator": 3, "denominator": 4}
    assert summary["kpis"]["rta"] == {"value": 33.3, "numerator": 1, "denominator": 3}
