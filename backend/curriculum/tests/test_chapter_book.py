from django.core.management import call_command
from rest_framework.test import APIClient

from curriculum.selectors import published_chapters, chapter_book


def test_chapter_book_lists_every_registered_command(db):
    call_command("seed_curriculum_v2")

    chapter = next(s for s in published_chapters() if s.command_skill_count > 0)
    book = chapter_book(chapter_id=chapter.id)

    assert book is not None
    assert book["chapter_id"] == chapter.id
    assert book["command_count"] == chapter.command_skill_count
    assert len(book["commands"]) == chapter.command_skill_count

    first = book["commands"][0]
    assert first["base_command"]
    assert first["title"]
    # Without seeded library entries the book falls back to the synthesized
    # summary page, so a registered command never renders empty.
    assert first["pages"]
    assert all("blocks" in page for page in first["pages"])


def test_chapter_book_prefers_seeded_library_entries(db):
    call_command("seed_curriculum_v2")
    call_command("seed_command_library")

    from curriculum.library import library_key_for_command
    from curriculum.models import LibraryEntry

    chapter = next(s for s in published_chapters() if s.command_skill_count > 0)
    book = chapter_book(chapter_id=chapter.id)
    seeded_keys = set(
        LibraryEntry.objects.filter(is_published=True).values_list("command_key", flat=True)
    )
    assert seeded_keys, "seed_command_library should persist at least one entry"

    seeded_commands = [
        command
        for command in book["commands"]
        if library_key_for_command(command["base_command"]) in seeded_keys
    ]
    assert seeded_commands, "chapter 1 registers git init, which ships a library entry"
    for command in seeded_commands:
        # Seeded entries carry rich multi-page content, not the one-page fallback.
        assert len(command["pages"]) > 1
        assert command["tags"]

    # Unpublishing the entry drops the book back to the synthesized fallback.
    LibraryEntry.objects.update(is_published=False)
    book = chapter_book(chapter_id=chapter.id)
    refreshed = next(c for c in book["commands"] if c["id"] == seeded_commands[0]["id"])
    assert len(refreshed["pages"]) == 1
    assert refreshed["tags"] == []


def test_chapter_book_endpoint_ok_and_404(db, django_user_model):
    call_command("seed_curriculum_v2")
    user = django_user_model.objects.create_user(
        username="reader",
        email="reader@example.com",
        password="pass12345",
    )
    api_client = APIClient()
    api_client.force_authenticate(user=user)

    chapter = next(s for s in published_chapters() if s.command_skill_count > 0)
    response = api_client.get(f"/api/chapters/{chapter.id}/book/")
    assert response.status_code == 200
    assert response.json()["commands"]

    missing = api_client.get("/api/chapters/999999/book/")
    assert missing.status_code == 404


def test_command_library_entries_build_pages_and_diagram():
    # Authored library entries live in library.py. Building them through the
    # shared helpers proves the authoring path - including option/argument
    # sub-sections and authored diagram blocks - end to end.
    from curriculum.library import LIBRARY_ENTRIES, _content

    assert LIBRARY_ENTRIES, "the library should ship at least one authored entry"

    entry = _content(**LIBRARY_ENTRIES[0])
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


def test_seed_command_library_persists_entries(db):
    from curriculum.models import LibraryEntry

    call_command("seed_command_library")

    entry = LibraryEntry.objects.get(command_key="git-init")
    assert entry.is_published
    assert entry.pages
    assert entry.tags
