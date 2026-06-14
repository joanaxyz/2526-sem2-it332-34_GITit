from django.core.management import call_command
from rest_framework.test import APIClient

from curriculum.models import Tome
from curriculum.selectors import storey_content_page


def test_seed_creates_published_tomes_with_pages(db):
    call_command("seed_curriculum_v2")

    tomes = list(Tome.objects.filter(is_published=True))
    assert tomes, "the seed should author at least one published tome"
    for tome in tomes:
        assert tome.pages, f"{tome.slug}: a tome must ship renderable pages"
        assert all("blocks" in page for page in tome.pages)
        assert tome.placement in {"above_adventure", "below_adventure", "below_challenges"}


def test_storey_content_tomes_section(db):
    call_command("seed_curriculum_v2")

    tome = Tome.objects.filter(is_published=True).select_related("storey").first()
    page = storey_content_page(user=None, storey_id=tome.storey_id, section="tomes")

    assert page["section"] == "tomes"
    assert page["next_cursor"] is None
    assert page["results"], "the authored storey should list its tomes"
    payload = page["results"][0]
    assert payload["item_type"] == "tome"
    assert payload["placement"]
    assert payload["pages"], "pages ship inline so the reader needs no second request"


def test_tomes_endpoint_and_unauthored_storey_is_empty(db, django_user_model):
    call_command("seed_curriculum_v2")
    user = django_user_model.objects.create_user(
        username="reader",
        email="reader@example.com",
        password="pass12345",
    )
    api_client = APIClient()
    api_client.force_authenticate(user=user)

    tome = Tome.objects.filter(is_published=True).first()
    response = api_client.get(f"/api/storeys/{tome.storey_id}/content/", {"section": "tomes"})
    assert response.status_code == 200
    assert response.json()["results"][0]["slug"] == tome.slug

    # Storeys without an authored tome return an empty section - the tower
    # renders nothing there, keeping non-authored storeys unchanged.
    from curriculum.models import Storey

    bare_storey = Storey.objects.exclude(id=tome.storey_id).first()
    empty = api_client.get(f"/api/storeys/{bare_storey.id}/content/", {"section": "tomes"})
    assert empty.status_code == 200
    assert empty.json()["results"] == []
