"""Storey CRUD + content assignment via the authoring API."""

import pytest
from rest_framework.test import APIClient

from authoring.models import AuthoringStorey, ContentDefinition


def make_user(django_user_model, username="author"):
    return django_user_model.objects.create_user(
        username=username, email=f"{username}@example.com", password="pass12345"
    )


@pytest.mark.django_db
def test_create_storey_and_assign_content(django_user_model):
    user = make_user(django_user_model)
    client = APIClient()
    client.force_authenticate(user=user)

    storey = client.post("/api/authoring/storeys/", {"title": "Floor One"}, format="json")
    assert storey.status_code == 201
    storey_id = storey.json()["id"]
    assert storey.json()["chest_rewards"]  # defaults applied

    content = client.post(
        "/api/authoring/content-definitions/",
        {"kind": "challenge", "slug": "c1", "title": "C1", "storey": storey_id, "definition": {"levels": []}},
        format="json",
    )
    assert content.status_code == 201
    assert content.json()["storey_id"] == storey_id


@pytest.mark.django_db
def test_update_storey_settings(django_user_model):
    user = make_user(django_user_model)
    storey = AuthoringStorey.objects.create(owner=user, slug="f1", title="F1")
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.patch(
        f"/api/authoring/storeys/{storey.id}/",
        {"chest_rewards": [{"threshold": 100, "coins": 999}], "pass_bar_fraction": 0.9},
        format="json",
    )
    assert response.status_code == 200
    storey.refresh_from_db()
    assert storey.chest_rewards == [{"threshold": 100, "coins": 999}]
    assert storey.pass_bar_fraction == 0.9


@pytest.mark.django_db
def test_cannot_assign_another_users_storey(django_user_model):
    owner = make_user(django_user_model, "owner")
    other = make_user(django_user_model, "other")
    storey = AuthoringStorey.objects.create(owner=owner, slug="f1", title="F1")

    client = APIClient()
    client.force_authenticate(user=other)
    response = client.post(
        "/api/authoring/content-definitions/",
        {"kind": "tome", "slug": "t1", "title": "T1", "storey": storey.id, "definition": {"pages": []}},
        format="json",
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_add_storey_keeps_single_visual_template(django_user_model):
    user = make_user(django_user_model)
    from assets.models import KIND_TOWER_PIECE, Asset, TowerPieceAsset
    from tower_designs.models import STOREY_TEMPLATE_INDEX, TowerPieceInstance

    for slug, ptype in [
        ("official-hall-section", "section"),
        ("official-landing", "landing"),
    ]:
        asset = Asset.objects.create(kind=KIND_TOWER_PIECE, slug=slug, label=slug)
        TowerPieceAsset.objects.create(asset=asset, piece_type=ptype)

    client = APIClient()
    client.force_authenticate(user=user)
    design_id = client.post("/api/tower-designs/", {"slug": "t", "title": "T"}, format="json").json()["id"]
    before_count = TowerPieceInstance.objects.filter(tower_design_id=design_id).count()

    response = client.post(f"/api/tower-designs/{design_id}/storeys/")
    assert response.status_code == 201
    assert response.json()["added_storey_index"] == STOREY_TEMPLATE_INDEX
    assert TowerPieceInstance.objects.filter(tower_design_id=design_id).count() == before_count
    indices = {p["storeyIndex"] for p in response.json()["tower_layout"]["pieces"]}
    assert indices == {STOREY_TEMPLATE_INDEX}
