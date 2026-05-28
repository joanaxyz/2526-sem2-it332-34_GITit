import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from learning.management.commands.seed_module0_orientation import STATUS_DEMO_STATE
from learning.models import LearningUnit, Lesson, OrientationLessonSession


@pytest.fixture()
def api_client():
    return APIClient()


@pytest.fixture()
def student(db):
    return get_user_model().objects.create_user(
        username="reset-student@example.com",
        email="reset-student@example.com",
        password="Password123!",
    )


@pytest.fixture()
def status_lesson(db):
    unit = LearningUnit.objects.create(
        slug="orientation-reset",
        number=99,
        title="Reset test",
        description="",
        is_orientation=True,
        is_published=True,
        sort_order=99,
    )
    return Lesson.objects.create(
        unit=unit,
        slug="status-step",
        title="Status",
        subtitle="",
        content_html="",
        interaction_steps=[
            {
                "id": "run-status",
                "kind": "git_command",
                "title": "Status",
                "prompt": "git status",
                "accept_prefixes": ["git status"],
                "initial_state": STATUS_DEMO_STATE,
            }
        ],
        is_published=True,
        sort_order=1,
    )


def test_reset_session_applies_step_initial_state(student, api_client, status_lesson):
    session = OrientationLessonSession.objects.create(
        user=student,
        lesson=status_lesson,
        repository_state={"commits": [], "branches": {}, "head": {"type": "none"}},
    )
    api_client.force_authenticate(student)

    response = api_client.post(
        f"/api/learning/orientation/sessions/{session.id}/reset/",
        {"step_id": "run-status"},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    session.refresh_from_db()
    assert session.repository_state["branches"]["main"] == "c0"
    assert "app.txt" in session.repository_state["working_tree"]
