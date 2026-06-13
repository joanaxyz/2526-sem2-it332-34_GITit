import pytest
from rest_framework.test import APIClient

from authoring.models import ContentDefinition, PublishedContentRuntime


def make_user(django_user_model, username="student"):
    return django_user_model.objects.create_user(
        username=username,
        email=f"{username}@example.com",
        password="pass12345",
    )


def adventure_definition():
    return {
        "levels": [
            {
                "slug": "status-check",
                "title": "Check status",
                "initial_state": {},
                "solution_commands": ["git status"],
                "evaluation_spec": {"completion_policy": {"mode": "state_hash"}},
                "scenario_context": {"schema_version": 3, "story": "Inspect the repo."},
            }
        ]
    }


@pytest.mark.django_db
def test_user_can_create_validate_and_test_run_adventure_definition(django_user_model):
    user = make_user(django_user_model)
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(
        "/api/authoring/content-definitions/",
        {
            "kind": "adventure",
            "slug": "my-adventure",
            "title": "My Adventure",
            "summary": "Practice status.",
            "command_family": "git status",
            "definition": adventure_definition(),
        },
        format="json",
    )

    assert response.status_code == 201
    definition_id = response.json()["id"]

    validate = client.post(f"/api/authoring/content-definitions/{definition_id}/validate/")
    assert validate.status_code == 200
    assert validate.json()["valid"] is True

    test_run = client.post(f"/api/authoring/content-definitions/{definition_id}/test-run/")
    assert test_run.status_code == 200
    assert test_run.json()["kind"] == "adventure"
    assert test_run.json()["start_path"].startswith("/command-adventures/")

    content = ContentDefinition.objects.get(id=definition_id)
    assert content.status == "testable"
    assert PublishedContentRuntime.objects.filter(content_definition=content).exists()


@pytest.mark.django_db
def test_private_content_is_hidden_from_other_users(django_user_model):
    owner = make_user(django_user_model, "owner")
    other = make_user(django_user_model, "other")
    content = ContentDefinition.objects.create(
        owner=owner,
        kind="tome",
        slug="private-tome",
        title="Private Tome",
        definition={"pages": [{"title": "Only mine", "blocks": []}]},
    )
    client = APIClient()
    client.force_authenticate(user=other)

    response = client.get(f"/api/authoring/content-definitions/{content.id}/")

    assert response.status_code == 404

