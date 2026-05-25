import pytest
from django.contrib.auth import get_user_model

from common.constants import COMPLETION_STATE_BASED, SESSION_STATUS_COMPLETED
from learning.models import LearningUnit, Lesson
from learning.selectors import (
    practice_completion_count_map,
    practice_completion_denominator_map,
)
from scenarios.models import (
    CommandCountPolicy,
    DifficultyInstance,
    ScenarioSession,
    ScenarioSkillFocus,
    ScenarioVariant,
)


@pytest.fixture()
def progress_unit(db):
    unit = LearningUnit.objects.create(
        slug="progress-unit",
        number=20,
        title="Progress Unit",
        description="Progress test unit.",
        is_orientation=False,
        is_published=True,
    )
    diagnostic_lesson = Lesson.objects.create(
        unit=unit,
        slug="diagnostic-preview",
        title="Diagnostic Preview",
        content_html="",
        sort_order=1,
    )
    ScenarioSkillFocus.objects.create(
        learning_unit=unit,
        lesson=diagnostic_lesson,
        slug="diagnostic-preview",
        title="Diagnostic preview",
        focus="diagnostic commands",
        summary="Preview only.",
        is_published=True,
    )
    lesson = Lesson.objects.create(
        unit=unit,
        slug="playable",
        title="Playable",
        content_html="",
        sort_order=2,
    )
    scenario = ScenarioSkillFocus.objects.create(
        learning_unit=unit,
        lesson=lesson,
        slug="playable-scenario",
        title="Playable scenario",
        focus="git commit",
        summary="Playable.",
        primary_focus_commands=["git commit"],
        is_published=True,
    )
    difficulties = [
        _difficulty(scenario, "easy", required=1, min_count=1),
        _difficulty(scenario, "medium", required=2, min_count=2),
        _difficulty(scenario, "extra_hard", required=4, min_count=3),
    ]
    return unit, scenario, difficulties


def _difficulty(scenario, difficulty: str, *, required: int, min_count: int):
    instance = DifficultyInstance.objects.create(
        scenario=scenario,
        difficulty=difficulty,
        completion_type=COMPLETION_STATE_BASED,
        required_successful_attempts=required,
        narrative=f"{difficulty} narrative",
        is_published=True,
    )
    CommandCountPolicy.objects.create(
        difficulty_instance=instance,
        min_counted_commands=min_count,
        max_counted_commands=min_count + 3,
        non_counted_patterns=["git status"],
    )
    variant = ScenarioVariant.objects.create(
        scenario=scenario,
        difficulty_instance=instance,
        slug=f"{difficulty}-variant",
        label=f"{difficulty} variant",
        structure_signature=difficulty,
        initial_state={"commits": [], "branches": {}, "head": {"type": "branch", "name": "main"}},
        target_state={"commits": [], "branches": {}, "head": {"type": "branch", "name": "main"}},
        target_rule={"required_commands": ["git commit"]},
        expected_state_diagram={"commits": [], "branches": {}, "head": {"type": "branch", "name": "main"}},
        parameter_context={"case_id": difficulty, "index": 1},
        student_context={"story": f"{difficulty} story"},
        case_id=difficulty,
        semantic_key=f"{difficulty}:progress:{difficulty}",
        is_published=True,
    )
    return instance, variant


def _completed_session(*, user, unit, scenario, difficulty, variant, counted_total: int):
    return ScenarioSession.objects.create(
        user=user,
        learning_unit=unit,
        scenario=scenario,
        difficulty_instance=difficulty,
        variant=variant,
        source_entry_point="module_card",
        status=SESSION_STATUS_COMPLETED,
        counted_action_total=counted_total,
        command_policy_snapshot=difficulty.command_policy.snapshot(),
        repository_state=variant.target_state,
    )


def test_practice_denominator_uses_published_playable_requirements(progress_unit):
    unit, _, _ = progress_unit

    denominator = practice_completion_denominator_map(unit_ids=[unit.id])

    assert denominator[unit.id] == 7


def test_practice_completion_excludes_preview_only_lessons_and_caps_requirements(progress_unit):
    unit, scenario, difficulties = progress_unit
    user = get_user_model().objects.create_user(
        username="progress@example.com",
        email="progress@example.com",
        password="Password123!",
    )
    easy, easy_variant = difficulties[0]
    medium, medium_variant = difficulties[1]
    extra_hard, extra_hard_variant = difficulties[2]

    _completed_session(
        user=user,
        unit=unit,
        scenario=scenario,
        difficulty=easy,
        variant=easy_variant,
        counted_total=1,
    )
    for _ in range(3):
        _completed_session(
            user=user,
            unit=unit,
            scenario=scenario,
            difficulty=medium,
            variant=medium_variant,
            counted_total=2,
        )
    _completed_session(
        user=user,
        unit=unit,
        scenario=scenario,
        difficulty=extra_hard,
        variant=extra_hard_variant,
        counted_total=4,
    )

    numerator = practice_completion_count_map(user=user, unit_ids=[unit.id])
    denominator = practice_completion_denominator_map(unit_ids=[unit.id])

    assert numerator[unit.id] == 3
    assert denominator[unit.id] == 7
