from copy import deepcopy

import pytest

from common.serializers import (
    CommandSubmitSerializer,
    WorkspaceFilePathSerializer,
    WorkspaceFileRenameSerializer,
    WorkspaceFileSerializer,
)
from testing.runtime_factories import (
    api_client_for,
    create_stage_readme_adventure_run,
    create_stage_readme_challenge_run,
)


@pytest.mark.parametrize(
    "serializer_class, expected_fields",
    [
        (CommandSubmitSerializer, {"command", "execution"}),
        (WorkspaceFileSerializer, {"path", "content"}),
        (WorkspaceFilePathSerializer, {"path"}),
        (WorkspaceFileRenameSerializer, {"path", "new_path"}),
    ],
)
def test_gameplay_mutation_serializers_have_one_common_owner(serializer_class, expected_fields):
    assert serializer_class.__module__ == "common.serializers"
    assert set(serializer_class().fields) == expected_fields


def test_workspace_file_contract_preserves_limits_defaults_and_whitespace():
    serializer = WorkspaceFileSerializer(data={"path": " notes.txt "})

    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data == {"path": "notes.txt", "content": ""}
    assert serializer.fields["path"].max_length == 240
    assert serializer.fields["content"].max_length == 20_000
    assert serializer.fields["content"].trim_whitespace is False

    with_whitespace = WorkspaceFileSerializer(data={"path": "notes.txt", "content": "  keep me  "})
    assert with_whitespace.is_valid(), with_whitespace.errors
    assert with_whitespace.validated_data["content"] == "  keep me  "


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("factory", "route_prefix"),
    [
        (create_stage_readme_adventure_run, "adventure-runs"),
        (create_stage_readme_challenge_run, "challenge-runs"),
    ],
)
def test_workspace_mutations_follow_the_same_real_http_contract(
    django_user_model, factory, route_prefix
):
    fixture = factory(django_user_model, username=f"{route_prefix}-workspace-contract")
    client = api_client_for(fixture.user)
    endpoint = f"/api/{route_prefix}/{fixture.run.id}/files/"

    created = client.post(
        endpoint,
        {"path": "notes.txt", "content": "first"},
        format="json",
    )
    assert created.status_code == 200, created.data

    written = client.patch(
        endpoint,
        {"path": "notes.txt", "content": "second"},
        format="json",
    )
    assert written.status_code == 200, written.data

    renamed = client.put(
        endpoint,
        {"path": "notes.txt", "new_path": "docs/notes.txt"},
        format="json",
    )
    assert renamed.status_code == 200, renamed.data

    fixture.run.refresh_from_db()
    assert fixture.run.repository_state["working_tree"]["docs/notes.txt"] == {
        "status": "untracked",
        "content": "second",
    }
    assert "notes.txt" not in fixture.run.repository_state["working_tree"]

    deleted = client.delete(f"{endpoint}?path=docs%2Fnotes.txt")
    assert deleted.status_code == 200, deleted.data

    fixture.run.refresh_from_db()
    assert "docs/notes.txt" not in fixture.run.repository_state["working_tree"]

    recreated = client.post(
        endpoint,
        {"path": "body-delete.txt", "content": "compatibility"},
        format="json",
    )
    assert recreated.status_code == 200, recreated.data

    deleted_from_body = client.delete(
        endpoint,
        {"path": "body-delete.txt"},
        format="json",
    )
    assert deleted_from_body.status_code == 200, deleted_from_body.data

    fixture.run.refresh_from_db()
    assert "body-delete.txt" not in fixture.run.repository_state["working_tree"]


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("factory", "route_prefix"),
    [
        (create_stage_readme_adventure_run, "adventure-runs"),
        (create_stage_readme_challenge_run, "challenge-runs"),
    ],
)
def test_invalid_workspace_patch_is_rejected_before_run_mutation(
    django_user_model, factory, route_prefix
):
    fixture = factory(django_user_model, username=f"{route_prefix}-workspace-invalid")
    before = deepcopy(fixture.run.repository_state)
    response = api_client_for(fixture.user).patch(
        f"/api/{route_prefix}/{fixture.run.id}/files/",
        {"content": "missing file identity"},
        format="json",
    )

    assert response.status_code == 400
    assert "path" in response.data
    fixture.run.refresh_from_db()
    assert fixture.run.repository_state == before


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("factory", "route_prefix"),
    [
        (create_stage_readme_adventure_run, "adventure-runs"),
        (create_stage_readme_challenge_run, "challenge-runs"),
    ],
)
@pytest.mark.parametrize(
    ("method", "route_suffix", "payload", "missing_field"),
    [
        ("post", "files/", {}, "path"),
        ("put", "files/", {"path": "README.md"}, "new_path"),
        ("delete", "files/", {}, "path"),
        ("post", "submit-command/", {"command": "git status"}, "execution"),
    ],
)
def test_malformed_gameplay_mutations_stop_before_repository_changes(
    django_user_model,
    factory,
    route_prefix,
    method,
    route_suffix,
    payload,
    missing_field,
):
    fixture = factory(
        django_user_model,
        username=f"{route_prefix}-{method}-{missing_field}-invalid",
    )
    before = deepcopy(fixture.run.repository_state)
    client = api_client_for(fixture.user)

    response = getattr(client, method)(
        f"/api/{route_prefix}/{fixture.run.id}/{route_suffix}",
        payload,
        format="json",
    )

    assert response.status_code == 400
    assert missing_field in response.data
    fixture.run.refresh_from_db()
    assert fixture.run.repository_state == before
