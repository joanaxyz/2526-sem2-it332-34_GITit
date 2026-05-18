import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command

from common.constants import (
    COMMAND_DIAGNOSTIC,
    SESSION_MODE_REVIEW,
    SESSION_STATUS_FAILED,
)
from learning.models import Lesson, OrientationProgress
from progress.models import StreakRecord, StudentProgress
from review.services import ReviewModeService
from scenarios.models import CompletionRecord, DifficultyInstance, ScenarioSession
from scenarios.services import CommandProcessingService, ScenarioSessionService


@pytest.fixture()
def seeded_content(db):
    call_command("seed_starter_content")


@pytest.fixture()
def student(db, seeded_content):
    user = get_user_model().objects.create_user(
        username="student@example.com",
        email="student@example.com",
        password="Password123!",
        first_name="Student",
    )
    StudentProgress.objects.create(user=user)
    StreakRecord.objects.create(user=user)
    for lesson in Lesson.objects.filter(unit__is_orientation=True):
        OrientationProgress.objects.create(user=user, lesson=lesson, completed_at="2026-05-18T00:00:00Z")
    return user


def test_diagnostic_commands_are_logged_but_not_counted(student):
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="first-clean-commit",
        difficulty="easy",
    )
    session = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="lesson_overview",
    )

    response = CommandProcessingService().submit_command(session=session, command="git status")

    session.refresh_from_db()
    assert response["command_classification"] == COMMAND_DIAGNOSTIC
    assert session.counted_action_total == 0
    assert session.non_counted_diagnostic_total == 1


def test_state_based_completion_creates_completion_record(student):
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="first-clean-commit",
        difficulty="easy",
    )
    session = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="lesson_overview",
    )

    CommandProcessingService().submit_command(session=session, command="git add .")
    CommandProcessingService().submit_command(session=session, command='git commit -m "starter snapshot"')

    session.refresh_from_db()
    completion = CompletionRecord.objects.get(user=student, difficulty_instance=difficulty)
    assert session.status == "completed"
    assert completion.counted_action_total == 2


def test_retry_after_failure_uses_changed_variant_when_available(student):
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="first-clean-commit",
        difficulty="easy",
    )
    prior = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="lesson_overview",
    )
    prior.status = SESSION_STATUS_FAILED
    prior.save(update_fields=["status"])

    retry = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="retry",
        prior_session=prior,
    )

    assert retry.variant_id != prior.variant_id
    assert retry.changed_variant is True
    assert retry.rta_eligible is True


def test_review_mode_logs_separately_without_new_completion(student):
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="first-clean-commit",
        difficulty="easy",
    )
    session = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="lesson_overview",
    )
    CommandProcessingService().submit_command(session=session, command="git add .")
    CommandProcessingService().submit_command(session=session, command='git commit -m "starter snapshot"')

    review_session = ReviewModeService().start_review_session(user=student, difficulty_instance=difficulty)

    assert review_session.mode == SESSION_MODE_REVIEW
    assert CompletionRecord.objects.filter(user=student, difficulty_instance=difficulty).count() == 1
    assert ScenarioSession.objects.filter(user=student, mode=SESSION_MODE_REVIEW).count() == 1
