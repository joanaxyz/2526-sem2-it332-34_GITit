"""Staff-only admin console API: access gating + key data actions."""

import pytest
from rest_framework.test import APIClient

from players.services import get_or_create_player
from progress.wallet import WalletService


def make_user(django_user_model, username="player", *, is_staff=False):
    return django_user_model.objects.create_user(
        username=username, email=f"{username}@example.com", password="pass12345", is_staff=is_staff
    )


@pytest.mark.django_db
def test_overview_requires_staff(django_user_model):
    student = make_user(django_user_model, "student")
    client = APIClient()
    client.force_authenticate(user=student)
    assert client.get("/api/admin/overview/").status_code == 403


@pytest.mark.django_db
def test_staff_overview_returns_metrics(django_user_model):
    staff = make_user(django_user_model, "admin", is_staff=True)
    client = APIClient()
    client.force_authenticate(user=staff)

    response = client.get("/api/admin/overview/")
    assert response.status_code == 200
    body = response.json()
    assert set(body) >= {"users", "economy"}
    assert body["users"]["total"] >= 1


@pytest.mark.django_db
def test_staff_economy_adjust(django_user_model):
    staff = make_user(django_user_model, "admin", is_staff=True)
    target = make_user(django_user_model, "target")
    client = APIClient()
    client.force_authenticate(user=staff)

    response = client.post(
        "/api/admin/economy/adjust/",
        {"user_id": target.id, "amount": 250, "reason": "goodwill"},
        format="json",
    )
    assert response.status_code == 200
    assert response.json()["wallet"]["balance"] == 250


@pytest.mark.django_db
def test_non_staff_cannot_adjust_coins(django_user_model):
    student = make_user(django_user_model, "student")
    target = make_user(django_user_model, "target")
    client = APIClient()
    client.force_authenticate(user=student)

    response = client.post(
        "/api/admin/economy/adjust/",
        {"user_id": target.id, "amount": 250},
        format="json",
    )
    assert response.status_code == 403
    assert WalletService().summary(player=get_or_create_player(target))["balance"] == 0


@pytest.mark.django_db
def test_staff_can_create_and_edit_story(django_user_model):
    from curriculum.models import Story

    staff = make_user(django_user_model, "admin", is_staff=True)
    client = APIClient()
    client.force_authenticate(user=staff)

    created = client.post(
        "/api/admin/stories/",
        {"slug": "new-spire", "title": "New Spire"},
        format="json",
    )
    assert created.status_code == 201
    story_id = created.json()["id"]

    patched = client.patch(
        f"/api/admin/stories/{story_id}/",
        {"is_published": False},
        format="json",
    )
    assert patched.status_code == 200
    story = Story.objects.get(id=story_id)
    assert story.is_published is False


@pytest.mark.django_db
def test_staff_settings_toggle_feature_flag(django_user_model):
    from adminconsole.models import feature_enabled

    staff = make_user(django_user_model, "admin", is_staff=True)
    client = APIClient()
    client.force_authenticate(user=staff)

    assert feature_enabled("beta-thing") is False
    response = client.post(
        "/api/admin/settings/",
        {"key": "beta-thing", "label": "Beta Thing", "enabled": True},
        format="json",
    )
    assert response.status_code == 200
    assert feature_enabled("beta-thing") is True

    settings_body = client.get("/api/admin/settings/").json()
    assert any(flag["key"] == "beta-thing" for flag in settings_body["feature_flags"])


@pytest.mark.django_db
def test_staff_moderation_unpublishes_content(django_user_model):
    from authoring.models import STATUS_PUBLISHED, ContentDefinition

    staff = make_user(django_user_model, "admin", is_staff=True)
    author = make_user(django_user_model, "author")
    content = ContentDefinition.objects.create(
        owner=author,
        kind="challenge",
        slug="shared-content",
        title="Shared Content",
        status=STATUS_PUBLISHED,
        visibility="public",
    )
    client = APIClient()
    client.force_authenticate(user=staff)

    listed = client.get("/api/admin/moderation/").json()
    assert any(c["id"] == content.id for c in listed["content"])

    response = client.post(
        "/api/admin/moderation/unpublish/",
        {"kind": "content", "id": content.id},
        format="json",
    )
    assert response.status_code == 200
    content.refresh_from_db()
    assert content.visibility == "private"
    assert content.status == "draft"


@pytest.mark.django_db
def test_staff_analytics_returns_shape(django_user_model):
    staff = make_user(django_user_model, "admin", is_staff=True)
    client = APIClient()
    client.force_authenticate(user=staff)

    body = client.get("/api/admin/analytics/").json()
    assert set(body) >= {"runs", "completions", "active_learners_30d", "per_story"}
