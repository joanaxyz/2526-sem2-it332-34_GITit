import pytest
from rest_framework.test import APIClient

from assets.models import KIND_RELIC, Asset, RelicAsset
from archive.models import ArchiveDesign, RelicPlacement


def make_user(django_user_model, username="builder"):
    return django_user_model.objects.create_user(
        username=username, email=f"{username}@example.com", password="pass12345"
    )


def make_relic_asset(slug="official-relic"):
    asset = Asset.objects.create(kind=KIND_RELIC, slug=slug, label="Arcane Relic", is_published=True)
    RelicAsset.objects.create(asset=asset, view_box="0 0 200 120")
    return asset


@pytest.mark.django_db
def test_create_personal_archive_is_idempotent(django_user_model):
    make_relic_asset()
    user = make_user(django_user_model)
    client = APIClient()
    client.force_authenticate(user=user)

    first = client.post("/api/archive-designs/", {}, format="json")
    second = client.post("/api/archive-designs/", {}, format="json")

    assert first.status_code == 201, first.content
    assert second.status_code == 201
    assert first.json()["id"] == second.json()["id"]
    assert ArchiveDesign.objects.filter(owner=user, origin="personal").count() == 1


@pytest.mark.django_db
def test_relic_crud_round_trip(django_user_model):
    asset = make_relic_asset()
    user = make_user(django_user_model)
    client = APIClient()
    client.force_authenticate(user=user)
    design = client.post("/api/archive-designs/", {}, format="json").json()
    design_id = design["id"]

    created = client.post(
        f"/api/archive-designs/{design_id}/relics/",
        {"relic_asset_id": asset.id, "chapter_index": 2, "x": 40, "y": 80, "kind": "normal"},
        format="json",
    )
    assert created.status_code == 201, created.content
    placement_id = created.json()["id"]

    patched = client.patch(
        f"/api/archive-designs/{design_id}/relics/{placement_id}/",
        {"x": 120, "scale": 1.5},
        format="json",
    )
    assert patched.status_code == 200
    placement = RelicPlacement.objects.get(id=placement_id)
    assert placement.x == 120
    assert placement.scale == 1.5

    overview = client.get(f"/api/archive-designs/{design_id}/layout/").json()
    assert any(r["id"] == placement_id for r in overview["relic_layout"]["relics"])

    deleted = client.delete(f"/api/archive-designs/{design_id}/relics/{placement_id}/")
    assert deleted.status_code == 204
    assert not RelicPlacement.objects.filter(id=placement_id).exists()


@pytest.mark.django_db
def test_add_chapter_returns_next_index_without_creating_relics(django_user_model):
    make_relic_asset()
    user = make_user(django_user_model)
    client = APIClient()
    client.force_authenticate(user=user)
    design = client.post("/api/archive-designs/", {}, format="json").json()
    design_id = design["id"]
    before = RelicPlacement.objects.filter(archive_design_id=design_id).count()

    response = client.post(f"/api/archive-designs/{design_id}/chapters/", {}, format="json")

    assert response.status_code == 201, response.content
    # Seed put a relic on chapter 1, so the next empty tab is chapter 2.
    assert response.json()["added_chapter_index"] == 2
    assert RelicPlacement.objects.filter(archive_design_id=design_id).count() == before
