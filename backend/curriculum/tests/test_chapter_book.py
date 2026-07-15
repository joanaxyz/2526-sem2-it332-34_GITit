from django.core.management import call_command
from rest_framework.test import APIClient

from curriculum.models import ChapterLesson
from curriculum.selectors import chapter_book, published_chapters


def test_chapter_book_lists_every_registered_command(db):
    call_command("seed_curriculum")

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


def test_chapter_book_includes_authored_lessons(db):
    call_command("seed_curriculum")

    lesson = ChapterLesson.objects.filter(is_published=True).select_related("chapter").first()
    book = chapter_book(chapter_id=lesson.chapter_id)

    assert book is not None
    assert book["lesson_count"] >= 1
    payload = next(item for item in book["lessons"] if item["slug"] == lesson.slug)
    assert payload["item_type"] == "lesson"
    assert payload["pages"], "lesson pages should render inside the chapter book"


def test_chapter_book_prefers_seeded_library_entries(db):
    call_command("seed_curriculum")
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
    call_command("seed_curriculum")
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


def test_beginner_command_library_entries_are_educationally_rich():
    from curriculum.library import LIBRARY_ENTRIES, _content
    from curriculum.library_education import BEGINNER_COMMAND_KEYS

    specs_by_key = {entry["key"]: entry for entry in LIBRARY_ENTRIES}
    missing = BEGINNER_COMMAND_KEYS - set(specs_by_key)
    assert not missing, f"beginner command library entries are missing: {sorted(missing)}"

    required_section_types = {"overview", "checklist", "comparison", "scenario", "quiz", "mistake"}
    required_block_types = {"state_flow", "before_after", "comparison_table", "scenario", "quiz", "do_dont"}

    for key in sorted(BEGINNER_COMMAND_KEYS):
        content = _content(**specs_by_key[key])
        section_types = {page.get("section_type") for page in content["pages"]}
        block_types = {
            block.get("type")
            for page in content["pages"]
            for block in page.get("blocks", [])
        }

        assert required_section_types <= section_types, key
        assert required_block_types <= block_types, key


def test_command_library_terminal_outputs_use_realistic_transcripts():
    from curriculum.library_preview_outputs import _sample_output_for_syntax
    from curriculum.seed_data.command_catalog import COMMAND_CATALOG

    placeholder_tokens = ("<file>", "<path>", "<branch>", "<url>", "<commit>", "<name>", "<directory>", "<folder>")
    comment_tokens = ("# output depends", "# no output")
    for spec in COMMAND_CATALOG:
        for usage in spec["usages"]:
            transcript = _sample_output_for_syntax(usage["usage_form"])
            first_line = transcript.splitlines()[0]
            assert first_line.startswith("student@git-it:~/quest$ "), usage["usage_form"]
            assert not any(token in first_line for token in placeholder_tokens), usage["usage_form"]
            assert not any(token in transcript for token in comment_tokens), usage["usage_form"]

    assert "Cloning into 'arcane-spire'" in _sample_output_for_syntax("git clone <url>")
    assert "diff --git" in _sample_output_for_syntax("git diff")
    assert "Changes to be committed:" in _sample_output_for_syntax("git status")
    assert _sample_output_for_syntax("git add <file>").strip().endswith("git add README.md")
