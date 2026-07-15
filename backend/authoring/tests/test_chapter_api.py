"""Chapter CRUD + content assignment via the authoring API."""

import pytest
from rest_framework.test import APIClient

from authoring.models import AuthoringChapter


def make_user(django_user_model, username="author"):
    return django_user_model.objects.create_user(
        username=username, email=f"{username}@example.com", password="pass12345"
    )


@pytest.mark.django_db
def test_create_chapter_and_assign_content(django_user_model):
    user = make_user(django_user_model)
    client = APIClient()
    client.force_authenticate(user=user)

    chapter = client.post("/api/authoring/chapters/", {"title": "Floor One"}, format="json")
    assert chapter.status_code == 201
    chapter_id = chapter.json()["id"]

    content = client.post(
        "/api/authoring/content-definitions/",
        {"kind": "challenge", "slug": "c1", "title": "C1", "chapter": chapter_id, "definition": {"levels": []}},
        format="json",
    )
    assert content.status_code == 201
    assert content.json()["chapter_id"] == chapter_id


@pytest.mark.django_db
def test_update_chapter_settings(django_user_model):
    user = make_user(django_user_model)
    chapter = AuthoringChapter.objects.create(owner=user, slug="f1", title="F1")
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.patch(
        f"/api/authoring/chapters/{chapter.id}/",
        {"summary": "Updated summary."},
        format="json",
    )
    assert response.status_code == 200
    chapter.refresh_from_db()
    assert chapter.summary == "Updated summary."


@pytest.mark.django_db
def test_cannot_assign_another_users_chapter(django_user_model):
    owner = make_user(django_user_model, "owner")
    other = make_user(django_user_model, "other")
    chapter = AuthoringChapter.objects.create(owner=owner, slug="f1", title="F1")

    client = APIClient()
    client.force_authenticate(user=other)
    response = client.post(
        "/api/authoring/content-definitions/",
        {"kind": "lesson", "slug": "t1", "title": "T1", "chapter": chapter.id, "definition": {"pages": []}},
        format="json",
    )
    assert response.status_code == 400


# (Map-design authoring was removed — track maps are code-rendered now.)
