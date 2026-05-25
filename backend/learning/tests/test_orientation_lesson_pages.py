import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from learning.models import LearningUnit, Lesson, OrientationProgress


@pytest.fixture()
def api_client():
    return APIClient()


@pytest.fixture()
def student(db):
    return get_user_model().objects.create_user(
        username="lesson-student@example.com",
        email="lesson-student@example.com",
        password="Password123!",
    )


@pytest.fixture()
def lesson_units(db):
    orientation = LearningUnit.objects.create(
        slug="orientation",
        number=0,
        title="Orientation",
        description="Start here.",
        is_orientation=True,
        is_published=True,
        sort_order=0,
    )
    practice = LearningUnit.objects.create(
        slug="practice-module",
        number=1,
        title="Practice Module",
        description="Practice with scenarios.",
        is_orientation=False,
        is_published=True,
        sort_order=1,
    )
    orientation_lesson = Lesson.objects.create(
        unit=orientation,
        slug="welcome",
        title="Welcome",
        subtitle="Read first.",
        content_html="<h1>Welcome</h1>",
        sort_order=1,
    )
    internal_lesson = Lesson.objects.create(
        unit=practice,
        slug="internal-anchor",
        title="Internal Anchor",
        subtitle="Orders scenario cards.",
        content_html="<h1>Internal only</h1>",
        sort_order=1,
    )
    return orientation, practice, orientation_lesson, internal_lesson


def test_orientation_lesson_detail_opens_without_kind(student, api_client, lesson_units):
    _, _, orientation_lesson, _ = lesson_units
    api_client.force_authenticate(student)

    response = api_client.get(f"/api/learning/lessons/{orientation_lesson.id}/")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == orientation_lesson.id
    assert response.data["module"]["is_orientation"] is True
    assert "kind" not in response.data


def test_non_orientation_lesson_detail_is_not_student_facing(student, api_client, lesson_units):
    _, _, _, internal_lesson = lesson_units
    api_client.force_authenticate(student)

    response = api_client.get(f"/api/learning/lessons/{internal_lesson.id}/")

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_orientation_mark_read_creates_progress(student, api_client, lesson_units):
    _, _, orientation_lesson, _ = lesson_units
    api_client.force_authenticate(student)

    response = api_client.post(
        f"/api/learning/orientation/{orientation_lesson.id}/complete/",
        {"highest_step_seen": 2},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    progress = OrientationProgress.objects.get(user=student, lesson=orientation_lesson)
    assert progress.completed_at is not None
    assert response.data["is_complete"] is True
    assert response.data["highest_step_seen"] == 2


def test_non_orientation_lesson_cannot_be_marked_read(student, api_client, lesson_units):
    _, _, _, internal_lesson = lesson_units
    api_client.force_authenticate(student)

    response = api_client.post(
        f"/api/learning/orientation/{internal_lesson.id}/complete/",
        {"highest_step_seen": 1},
        format="json",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert not OrientationProgress.objects.filter(user=student, lesson=internal_lesson).exists()


def test_module_list_exposes_lessons_only_for_orientation_units(student, api_client, lesson_units):
    orientation, practice, orientation_lesson, _ = lesson_units
    api_client.force_authenticate(student)

    response = api_client.get("/api/learning/modules/")

    assert response.status_code == status.HTTP_200_OK
    orientation_payload = next(item for item in response.data if item["id"] == orientation.id)
    practice_payload = next(item for item in response.data if item["id"] == practice.id)
    assert orientation_payload["lesson_count"] == 1
    assert orientation_payload["lessons"][0]["id"] == orientation_lesson.id
    assert "kind" not in orientation_payload["lessons"][0]
    assert practice_payload["lesson_count"] == 0
    assert practice_payload["lessons"] == []
