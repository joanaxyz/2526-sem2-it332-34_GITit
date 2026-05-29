import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.utils import timezone

from common.constants import (
    SESSION_STATUS_ABANDONED,
    SESSION_STATUS_COMPLETED,
    SESSION_STATUS_FAILED,
    SESSION_STATUS_STARTED,
)
from learning.models import Lesson, OrientationProgress
from progress.models import StreakRecord, StudentProgress
from scenarios.models import DifficultyInstance
from scenarios.selectors import (
    command_accuracy_rate,
    latest_attempt_payload_from_session,
    minimum_counted_for_session,
    scenario_status_payload,
    session_meets_progress_threshold,
)
from scenarios.services import CommandProcessingService, ScenarioSessionService


@pytest.mark.parametrize(
    ("status", "counted", "minimum", "expected"),
    [
        (SESSION_STATUS_STARTED, 0, 2, None),
        (SESSION_STATUS_STARTED, 5, 2, None),
        (SESSION_STATUS_FAILED, 3, 2, 0),
        (SESSION_STATUS_ABANDONED, 1, 2, 0),
        (SESSION_STATUS_COMPLETED, 2, 2, 100),
        (SESSION_STATUS_COMPLETED, 1, 2, 100),
        (SESSION_STATUS_COMPLETED, 3, 2, 67),
        (SESSION_STATUS_COMPLETED, 4, 2, 50),
        (SESSION_STATUS_COMPLETED, 5, 0, 0),
    ],
)
def test_command_accuracy_rate_parametric(status, counted, minimum, expected):
    assert (
        command_accuracy_rate(
            status=status,
            counted_action_total=counted,
            minimum_counted_commands=minimum,
        )
        == expected
    )


@pytest.fixture()
def module3_content(db):
    call_command("seed_module3_scenarios", "--reset", "--confirm", "--validate-build")


@pytest.fixture()
def module3_student(db, module3_content):
    user = get_user_model().objects.create_user(
        username="m3-student@example.com",
        email="m3-student@example.com",
        password="Password123!",
        first_name="Module3",
    )
    StudentProgress.objects.create(user=user)
    StreakRecord.objects.create(user=user)
    for lesson in Lesson.objects.filter(unit__is_orientation=True):
        OrientationProgress.objects.create(
            user=user, lesson=lesson, completed_at="2026-05-18T00:00:00Z"
        )
    return user


def test_published_difficulty_policies_are_valid(db, module3_content):
    for instance in DifficultyInstance.objects.filter(is_published=True).select_related(
        "command_policy"
    ):
        policy = instance.command_policy
        assert policy.min_counted_commands <= policy.max_counted_commands
        assert policy.min_counted_commands >= 0
        assert policy.max_counted_commands >= 1


def test_minimum_counted_for_session_prefers_snapshot(module3_student):
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="accept-conflict-side",
        difficulty="easy",
    )
    session = ScenarioSessionService().start_session(
        user=module3_student,
        difficulty_instance=difficulty,
        source_entry_point="module_card",
    )
    live_min = difficulty.command_policy.min_counted_commands
    session.command_policy_snapshot = {
        **session.command_policy_snapshot,
        "min_counted_commands": live_min + 2,
    }
    session.status = SESSION_STATUS_COMPLETED
    session.counted_action_total = live_min + 1
    session.completed_at = timezone.now()
    session.ended_at = session.completed_at
    session.save(
        update_fields=[
            "command_policy_snapshot",
            "status",
            "counted_action_total",
            "completed_at",
            "ended_at",
        ]
    )

    assert minimum_counted_for_session(session=session, difficulty_instance=difficulty) == live_min + 2
    payload = latest_attempt_payload_from_session(
        session=session,
        difficulty_instance=difficulty,
    )
    assert payload["accuracy_rate"] == 100


def test_accept_conflict_side_easy_completed_at_minimum_is_100_percent(module3_student):
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="accept-conflict-side",
        difficulty="easy",
    )
    session = ScenarioSessionService().start_session(
        user=module3_student,
        difficulty_instance=difficulty,
        source_entry_point="module_card",
    )
    for command in session.variant.solution_commands:
        CommandProcessingService().submit_command(session=session, command=command)
        session.refresh_from_db()
        if session.status == SESSION_STATUS_COMPLETED:
            break

    assert session.status == SESSION_STATUS_COMPLETED
    payload = scenario_status_payload(user=module3_student, scenario=difficulty.scenario)
    easy = next(item for item in payload["difficulties"] if item["difficulty"] == "easy")
    assert easy["latest_attempt"]["accuracy_rate"] == 100


def test_accept_conflict_side_easy_completed_over_minimum_is_proportional(module3_student):
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="accept-conflict-side",
        difficulty="easy",
    )
    min_counted = difficulty.command_policy.min_counted_commands
    session = ScenarioSessionService().start_session(
        user=module3_student,
        difficulty_instance=difficulty,
        source_entry_point="module_card",
    )
    session.status = SESSION_STATUS_COMPLETED
    session.counted_action_total = min_counted + 1
    session.completed_at = timezone.now()
    session.ended_at = session.completed_at
    session.save(
        update_fields=["status", "counted_action_total", "completed_at", "ended_at"]
    )

    payload = scenario_status_payload(user=module3_student, scenario=difficulty.scenario)
    easy = next(item for item in payload["difficulties"] if item["difficulty"] == "easy")
    expected = round((min_counted / (min_counted + 1)) * 100)
    assert easy["latest_attempt"]["accuracy_rate"] == expected


def test_accept_conflict_side_easy_failed_latest_shows_zero(module3_student):
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="accept-conflict-side",
        difficulty="easy",
    )
    session = ScenarioSessionService().start_session(
        user=module3_student,
        difficulty_instance=difficulty,
        source_entry_point="module_card",
    )
    session.status = SESSION_STATUS_FAILED
    session.ended_at = timezone.now()
    session.save(update_fields=["status", "ended_at"])

    payload = scenario_status_payload(user=module3_student, scenario=difficulty.scenario)
    easy = next(item for item in payload["difficulties"] if item["difficulty"] == "easy")
    assert easy["latest_attempt"]["accuracy_rate"] == 0


@pytest.mark.parametrize(
    ("counted", "minimum", "expected"),
    [
        (4, 3, True),
        (3, 3, True),
        (2, 2, True),
        (4, 2, False),
        (3, 2, False),
    ],
)
def test_session_meets_progress_threshold(module3_student, counted, minimum, expected):
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="accept-conflict-side",
        difficulty="easy",
    )
    session = ScenarioSessionService().start_session(
        user=module3_student,
        difficulty_instance=difficulty,
        source_entry_point="module_card",
    )
    session.status = SESSION_STATUS_COMPLETED
    session.counted_action_total = counted
    session.command_policy_snapshot = {
        **session.command_policy_snapshot,
        "min_counted_commands": minimum,
    }
    session.completed_at = timezone.now()
    session.ended_at = session.completed_at
    session.save(
        update_fields=[
            "status",
            "counted_action_total",
            "command_policy_snapshot",
            "completed_at",
            "ended_at",
        ]
    )

    assert (
        session_meets_progress_threshold(session=session, difficulty_instance=difficulty)
        is expected
    )


def test_accept_conflict_side_easy_abandoned_latest_shows_zero(module3_student):
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="accept-conflict-side",
        difficulty="easy",
    )
    session = ScenarioSessionService().start_session(
        user=module3_student,
        difficulty_instance=difficulty,
        source_entry_point="module_card",
    )
    ScenarioSessionService().abandon(session=session)

    payload = scenario_status_payload(user=module3_student, scenario=difficulty.scenario)
    easy = next(item for item in payload["difficulties"] if item["difficulty"] == "easy")
    assert easy["latest_attempt"]["accuracy_rate"] == 0
