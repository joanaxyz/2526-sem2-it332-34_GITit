from django.core.management import call_command, get_commands

from adventures.models import AdventureLevel, AdventureLevelTier
from adventures.rewards import tier_reward_coins
from curriculum.models import Chapter, CommandForm, Story
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
    3: {"git add", "git cherry-pick", "git commit", "git config", "git merge", "git mergetool"},
    4: {
        "git log",
        "git push",
        "git rebase",
        "git reflog",
        "git reset",
        "git revert",
        "git show",
        "git switch",
    },
}


def _curriculum_chapters():
    return {
        chapter.number: chapter
        for chapter in Chapter.objects.filter(story__slug="arcane-spire").order_by("number")
    }


def test_canonical_curriculum_uses_arcane_spire_identity_and_visual_assets(db):
    call_command("seed_curriculum", verbosity=0)

    story = Story.objects.get(slug="arcane-spire")

    assert story.title == "The Arcane Spire"
    assert story.world_slug == "arcane-spire"


def test_only_the_live_curriculum_seed_command_is_registered():
    commands = get_commands()
    assert commands["seed_curriculum"] == "curriculum"
    assert "seed_curriculum_fixture" not in commands
    assert "seed_legacy_modules" not in commands


def test_canonical_seed_creates_only_the_unchanged_module_tree(db):
    call_command("seed_curriculum", verbosity=0)
    call_command("seed_curriculum", verbosity=0)

    assert list(Story.objects.values_list("slug", "title", "world_slug")) == [
        ("arcane-spire", "The Arcane Spire", "arcane-spire")
    ]
    assert Chapter.objects.filter(story__slug="arcane-spire").count() == 5
    assert AdventureLevel.objects.filter(chapter__story__slug="arcane-spire").count() == 21
    assert (
        AdventureLevelTier.objects.filter(
            adventure_level__chapter__story__slug="arcane-spire"
        ).count()
        == 63
    )


def test_curriculum_modules_seed_complete_rich_field_guides(db):
    call_command("seed_curriculum", verbosity=0)
    call_command("seed_command_library", verbosity=0)

    chapters = _curriculum_chapters()
    listed_counts = {
        chapter.number: chapter.command_skill_count
        for chapter in published_chapters(story_slug="arcane-spire")
    }

    assert chapter_book(chapter_id=chapters[0].id)["command_count"] == 0
    for module_number, expected_commands in EXPECTED_COMMANDS.items():
        book = chapter_book(chapter_id=chapters[module_number].id)
        actual_commands = {command["base_command"] for command in book["commands"]}

        assert actual_commands == expected_commands
        assert book["command_count"] == len(expected_commands)
        assert listed_counts[module_number] == book["command_count"]
        assert all(command["forms"] for command in book["commands"])
        assert all(form["is_playable"] for command in book["commands"] for form in command["forms"])
        assert all(command["tags"] for command in book["commands"])
        assert all(len(command["pages"]) > 1 for command in book["commands"])


def test_curriculum_field_guide_seed_is_idempotent(db):
    call_command("seed_curriculum", verbosity=0)
    first = list(
        CommandForm.objects.filter(chapter__story__slug="arcane-spire")
        .order_by("command_skill__slug", "slug")
        .values_list("id", "command_skill__slug", "slug", "chapter__number")
    )

    call_command("seed_curriculum", verbosity=0)
    second = list(
        CommandForm.objects.filter(chapter__story__slug="arcane-spire")
        .order_by("command_skill__slug", "slug")
        .values_list("id", "command_skill__slug", "slug", "chapter__number")
    )

    assert second == first


def test_curriculum_levels_seed_gamification_rewards_and_skill_forms(db):
    call_command("seed_curriculum", verbosity=0)

    levels = list(
        AdventureLevel.objects.filter(chapter__story__slug="arcane-spire")
        .exclude(chapter__number=0)
        .prefetch_related("command_forms", "tiers__scenarios__command_forms")
    )

    assert levels
    # Every level pays the difficulty ladder once per tier (adventures/rewards.py).
    assert all(
        {tier.difficulty: tier_reward_coins(tier) for tier in level.tiers.all()}
        == {"easy": 25, "medium": 35, "hard": 50}
        for level in levels
    )
    assert all(level.command_forms.exists() for level in levels)
    # A scenario attaches the level forms every one of its variants types: they
    # are the mastery targets' denominator, so a learner can always reach
    # them. A pool whose variants each teach a different form attaches none.
    for level in levels:
        level_forms = {form.id for form in level.command_forms.all()}
        for tier in level.tiers.all():
            for scenario in tier.scenarios.all():
                assert {form.id for form in scenario.command_forms.all()} <= level_forms
