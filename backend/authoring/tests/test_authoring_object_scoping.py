"""Another author's private rows must be invisible, not merely unwritable.

Every authoring detail route loads through the visibility selector, so a
wrong-owner id is a 404. Returning the service layer's 403 instead would confirm
the row exists and let one author enumerate another's private drafts.
"""

import pytest
from rest_framework.test import APIClient

from authoring.models import AuthoringChapter, ContentDefinition

WRITE_ROUTES = (
    "/api/authoring/content-definitions/{id}/validate/",
    "/api/authoring/content-definitions/{id}/publish/",
    "/api/authoring/content-definitions/{id}/test-run/",
)


def make_author(django_user_model, username, *, is_staff=False):
    user = django_user_model.objects.create_user(
        username=username,
        email=f"{username}@example.com",
        password="pass12345",
        is_staff=is_staff,
    )
    client = APIClient()
    client.force_authenticate(user=user)
    return user, client


@pytest.fixture
def private_draft(db, django_user_model):
    owner, _client = make_author(django_user_model, "owner")
    return ContentDefinition.objects.create(
        kind="adventure",
        owner=owner,
        slug="secret-draft",
        title="Secret draft",
        visibility="private",
        status="draft",
        definition={},
    )


def test_patch_on_another_authors_private_draft_is_not_found(db, django_user_model, private_draft):
    _stranger, client = make_author(django_user_model, "stranger")

    response = client.patch(
        f"/api/authoring/content-definitions/{private_draft.id}/",
        {"title": "Stolen"},
        format="json",
    )

    assert response.status_code == 404
    private_draft.refresh_from_db()
    assert private_draft.title == "Secret draft"


@pytest.mark.parametrize("route", WRITE_ROUTES)
def test_action_routes_on_another_authors_private_draft_are_not_found(
    db, django_user_model, private_draft, route
):
    _stranger, client = make_author(django_user_model, "stranger")

    response = client.post(route.format(id=private_draft.id))

    assert response.status_code == 404


def test_a_missing_id_and_a_hidden_id_are_indistinguishable(db, django_user_model, private_draft):
    _stranger, client = make_author(django_user_model, "stranger")
    missing_id = ContentDefinition.objects.order_by("-id").first().id + 1000

    hidden = client.post(f"/api/authoring/content-definitions/{private_draft.id}/validate/")
    missing = client.post(f"/api/authoring/content-definitions/{missing_id}/validate/")

    assert hidden.status_code == missing.status_code == 404


def test_staff_still_reach_any_content_definition(db, django_user_model, private_draft):
    _staff, client = make_author(django_user_model, "staffer", is_staff=True)

    response = client.patch(
        f"/api/authoring/content-definitions/{private_draft.id}/",
        {"title": "Moderated"},
        format="json",
    )

    assert response.status_code == 200


def test_another_authors_chapter_is_not_found(db, django_user_model):
    owner, _owner_client = make_author(django_user_model, "chapter-owner")
    chapter = AuthoringChapter.objects.create(owner=owner, slug="mine", title="Mine")
    _stranger, client = make_author(django_user_model, "chapter-stranger")

    patched = client.patch(
        f"/api/authoring/chapters/{chapter.id}/", {"title": "Yours"}, format="json"
    )
    deleted = client.delete(f"/api/authoring/chapters/{chapter.id}/")

    assert patched.status_code == 404
    assert deleted.status_code == 404
    assert AuthoringChapter.objects.filter(id=chapter.id, title="Mine").exists()


def test_staff_still_reach_any_authoring_chapter(db, django_user_model):
    owner, _owner_client = make_author(django_user_model, "chapter-owner")
    chapter = AuthoringChapter.objects.create(owner=owner, slug="mine", title="Mine")
    _staff, client = make_author(django_user_model, "chapter-staff", is_staff=True)

    response = client.patch(
        f"/api/authoring/chapters/{chapter.id}/", {"title": "Renamed"}, format="json"
    )

    assert response.status_code == 200
