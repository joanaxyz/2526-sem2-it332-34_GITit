from django.core.management import call_command
from rest_framework.test import APIClient

from curriculum.selectors import published_storeys


def test_storeys_have_command_skill_and_challenge_counts(db):
    call_command("seed_curriculum_v2")

    storeys = list(published_storeys())

    assert storeys
    assert storeys[0].command_skill_count > 0
    assert any(storey.challenge_count > 0 for storey in storeys)


def test_storeys_endpoint_uses_storey_language_and_progress_payload(db, django_user_model):
    call_command("seed_curriculum_v2")
    user = django_user_model.objects.create_user(
        username="student",
        email="student@example.com",
        password="pass12345",
    )
    api_client = APIClient()
    api_client.force_authenticate(user=user)

    storeys = list(published_storeys())
    response = api_client.get("/api/storeys/")

    assert response.status_code == 200
    assert len(response.json()) == len(storeys)
    assert response.json()[0]["level_completion"]["denominator"] > 0
