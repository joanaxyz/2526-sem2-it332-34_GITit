from django.core.management import call_command
from rest_framework.test import APIClient

from curriculum.selectors import published_storeys, storey_book


def test_storey_book_lists_every_registered_command(db):
    call_command("seed_curriculum_v2")

    storey = next(s for s in published_storeys() if s.command_skill_count > 0)
    book = storey_book(storey_id=storey.id)

    assert book is not None
    assert book["storey_id"] == storey.id
    assert book["command_count"] == storey.command_skill_count
    assert len(book["commands"]) == storey.command_skill_count

    first = book["commands"][0]
    assert first["base_command"]
    assert first["title"]
    # The library is seeded content and is empty until that seed is wired, so the
    # book renders the synthesized summary page rather than rich library content.
    assert first["pages"]
    assert all("blocks" in page for page in first["pages"])


def test_storey_book_endpoint_ok_and_404(db, django_user_model):
    call_command("seed_curriculum_v2")
    user = django_user_model.objects.create_user(
        username="reader",
        email="reader@example.com",
        password="pass12345",
    )
    api_client = APIClient()
    api_client.force_authenticate(user=user)

    storey = next(s for s in published_storeys() if s.command_skill_count > 0)
    response = api_client.get(f"/api/storeys/{storey.id}/book/")
    assert response.status_code == 200
    assert response.json()["commands"]

    missing = api_client.get("/api/storeys/999999/book/")
    assert missing.status_code == 404


def test_command_library_seed_template_builds_pages_and_diagram():
    # The seed scaffold is the authoring home for the (currently unbaked) library.
    # Building its template through the shared helpers proves the authoring path —
    # including option/argument sub-sections and authored diagram blocks — still
    # works after the baked content was removed.
    from curriculum.command_content import _content
    from curriculum.management.commands.seed_command_library import COMMAND_LIBRARY_ENTRIES

    assert COMMAND_LIBRARY_ENTRIES, "the seed template should ship at least one example entry"

    entry = _content(**COMMAND_LIBRARY_ENTRIES[0])
    assert entry["pages"], "an authored entry should build into renderable pages"

    section_types = {page.get("section_type") for page in entry["pages"]}
    assert {"option", "argument"} <= section_types

    diagram_kinds = {
        block.get("diagram_kind")
        for page in entry["pages"]
        for block in page.get("blocks", [])
        if block.get("type") == "diagram"
    }
    assert diagram_kinds, "the template demonstrates an authored diagram block"


def test_seed_command_library_runs():
    # The management command validates the template end to end without raising.
    call_command("seed_command_library")
