"""Chapter CRUD + content assignment via the authoring API."""

import pytest
from rest_framework.test import APIClient

from authoring.models import AuthoringChapter, ContentDefinition


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
    assert chapter.json()["chest_rewards"]  # defaults applied

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
        {"chest_rewards": [{"threshold": 100, "coins": 999}], "pass_bar_fraction": 0.9},
        format="json",
    )
    assert response.status_code == 200
    chapter.refresh_from_db()
    assert chapter.chest_rewards == [{"threshold": 100, "coins": 999}]
    assert chapter.pass_bar_fraction == 0.9


@pytest.mark.django_db
def test_cannot_assign_another_users_chapter(django_user_model):
    owner = make_user(django_user_model, "owner")
    other = make_user(django_user_model, "other")
    chapter = AuthoringChapter.objects.create(owner=owner, slug="f1", title="F1")

    client = APIClient()
    client.force_authenticate(user=other)
    response = client.post(
        "/api/authoring/content-definitions/",
        {"kind": "tome", "slug": "t1", "title": "T1", "chapter": chapter.id, "definition": {"pages": []}},
        format="json",
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_add_chapter_reserves_empty_tab(django_user_model):
    user = make_user(django_user_model)
    from assets.models import KIND_RELIC, Asset, RelicAsset
    from archive.models import RelicPlacement

    asset = Asset.objects.create(kind=KIND_RELIC, slug="official-relic", label="Relic")
    RelicAsset.objects.create(asset=asset, view_box="0 0 200 120")

    client = APIClient()
    client.force_authenticate(user=user)
    design_id = client.post("/api/archive-designs/", {"slug": "t", "title": "T"}, format="json").json()["id"]
    before_count = RelicPlacement.objects.filter(archive_design_id=design_id).count()

    response = client.post(f"/api/archive-designs/{design_id}/chapters/")
    assert response.status_code == 201
    # The seed put a relic on chapter 1, so the next empty tab is chapter 2.
    assert response.json()["added_chapter_index"] == 2
    # Reserving a tab creates no relics (no repeating structures).
    assert RelicPlacement.objects.filter(archive_design_id=design_id).count() == before_count
