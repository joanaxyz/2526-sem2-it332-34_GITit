from django.core.management import call_command
from rest_framework.test import APIClient

from curriculum.selectors import published_chapters


def test_chapters_have_command_skill_and_challenge_counts(db):
    call_command("seed_curriculum_v2")

    chapters = list(published_chapters())

    assert chapters
    assert chapters[0].command_skill_count > 0
    assert any(chapter.challenge_count > 0 for chapter in chapters)


def test_chapters_endpoint_uses_chapter_language_and_progress_payload(db, django_user_model):
    call_command("seed_curriculum_v2")
    user = django_user_model.objects.create_user(
        username="student",
        email="student@example.com",
        password="pass12345",
    )
    api_client = APIClient()
    api_client.force_authenticate(user=user)

    chapters = list(published_chapters())
    response = api_client.get("/api/chapters/")

    assert response.status_code == 200
    assert len(response.json()) == len(chapters)
    assert response.json()[0]["level_completion"]["denominator"] > 0
