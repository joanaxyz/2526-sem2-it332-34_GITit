from django.core.management import call_command

from curriculum.models import Chapter, CommandForm
from curriculum.selectors import chapter_book, published_chapters


EXPECTED_COMMANDS = {
    1: {"git init", "git clone", "git add", "git commit", "git restore"},
    2: {
        "git branch",
        "git commit",
        "git fetch",
        "git merge",
        "git pull",
        "git push",
        "git stash",
        "git switch",
    },
    3: {"git add", "git cherry-pick", "git commit", "git merge"},
    4: {
        "git log",
        "git push",
        "git rebase",
        "git reflog",
        "git revert",
        "git show",
        "git switch",
    },
}


def _legacy_chapters():
    return {
        chapter.number: chapter
        for chapter in Chapter.objects.filter(story__slug="git-it-legacy").order_by("number")
    }


def test_legacy_modules_seed_complete_rich_field_guides(db):
    call_command("seed_legacy_modules", verbosity=0)
    call_command("seed_command_library", verbosity=0)

    chapters = _legacy_chapters()
    listed_counts = {
        chapter.number: chapter.command_skill_count
        for chapter in published_chapters(story_slug="git-it-legacy")
    }

    assert chapter_book(chapter_id=chapters[0].id)["command_count"] == 0
    for module_number, expected_commands in EXPECTED_COMMANDS.items():
        book = chapter_book(chapter_id=chapters[module_number].id)
        actual_commands = {command["base_command"] for command in book["commands"]}

        assert actual_commands == expected_commands
        assert book["command_count"] == len(expected_commands)
        assert listed_counts[module_number] == book["command_count"]
        assert all(command["forms"] for command in book["commands"])
        assert all(
            form["is_playable"]
            for command in book["commands"]
            for form in command["forms"]
        )
        assert all(command["tags"] for command in book["commands"])
        assert all(len(command["pages"]) > 1 for command in book["commands"])


def test_legacy_field_guide_seed_is_idempotent(db):
    call_command("seed_legacy_modules", verbosity=0)
    first = list(
        CommandForm.objects.filter(chapter__story__slug="git-it-legacy")
        .order_by("command_skill__slug", "slug")
        .values_list("id", "command_skill__slug", "slug", "chapter__number")
    )

    call_command("seed_legacy_modules", verbosity=0)
    second = list(
        CommandForm.objects.filter(chapter__story__slug="git-it-legacy")
        .order_by("command_skill__slug", "slug")
        .values_list("id", "command_skill__slug", "slug", "chapter__number")
    )

    assert second == first


def test_canonical_reseed_preserves_legacy_field_guides(db):
    call_command("seed_legacy_modules", verbosity=0)
    call_command("seed_curriculum", verbosity=0)

    chapters = _legacy_chapters()
    assert all(chapter.is_published for chapter in chapters.values())
    for module_number, expected_commands in EXPECTED_COMMANDS.items():
        book = chapter_book(chapter_id=chapters[module_number].id)
        assert {command["base_command"] for command in book["commands"]} == expected_commands
