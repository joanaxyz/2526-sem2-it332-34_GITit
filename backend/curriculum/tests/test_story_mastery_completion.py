"""Story completion is mastery-based.

A story counts as completed only when the player has mastered every published
playable command form taught by the story's required published adventure
levels. Challenge completions alone no longer complete a story.
"""

import pytest

from adventures.models import AdventureLevel, SkillMastery
from challenges.models import ChallengeLevel
from curriculum.models import Chapter, CommandForm, CommandSkill, Story
from curriculum.selectors import stories_completed_map, story_completed, story_locked
from players.services import get_or_create_player
from progress.models import ChallengeLevelCompletion
from shop.models import Entitlement

pytestmark = pytest.mark.django_db


@pytest.fixture
def player(django_user_model):
    user = django_user_model.objects.create_user(
        username="mastery-reader",
        email="mastery-reader@example.com",
        password="pass12345",
    )
    return get_or_create_player(user)


def _story(slug: str, *, sort_order: int = 1, prerequisite=None) -> Story:
    return Story.objects.create(
        slug=slug,
        title=slug.replace("-", " ").title(),
        world_slug=slug,
        sort_order=sort_order,
        is_published=True,
        prerequisite_story=prerequisite,
    )


def _chapter(story: Story, slug: str, number: int = 1) -> Chapter:
    return Chapter.objects.create(
        story=story,
        slug=slug,
        number=number,
        sort_order=number,
        title=slug,
        description="test chapter",
        is_published=True,
        is_playable=True,
    )


def _form(chapter: Chapter, slug: str, **overrides) -> CommandForm:
    skill, _ = CommandSkill.objects.get_or_create(
        slug=f"skill-{slug}",
        defaults={"base_command": f"git {slug}", "title": f"git {slug}"},
    )
    fields = {
        "command_skill": skill,
        "chapter": chapter,
        "slug": slug,
        "usage_form": f"git {slug}",
        "label": f"Use git {slug}",
        "is_published": True,
        "is_playable": True,
    }
    fields.update(overrides)
    return CommandForm.objects.create(**fields)


def _level(chapter: Chapter, slug: str, forms, **overrides) -> AdventureLevel:
    fields = {
        "chapter": chapter,
        "slug": slug,
        "title": slug,
        "is_published": True,
        "is_required": True,
    }
    fields.update(overrides)
    level = AdventureLevel.objects.create(**fields)
    level.command_forms.set(forms)
    return level


def _master(player, form: CommandForm) -> None:
    SkillMastery.objects.create(player=player, command_form=form, solves=8, mastered=True)


def test_story_completes_only_when_every_taught_form_is_mastered(player):
    story = _story("mastery-story")
    chapter = _chapter(story, "mastery-chapter")
    form_a = _form(chapter, "alpha")
    form_b = _form(chapter, "beta")
    _level(chapter, "level-1", [form_a, form_b])

    assert story_completed(player=player, story=story) is False

    _master(player, form_a)
    assert story_completed(player=player, story=story) is False

    _master(player, form_b)
    assert story_completed(player=player, story=story) is True


def test_unplayable_unpublished_and_optional_forms_are_ignored(player):
    story = _story("mastery-story")
    chapter = _chapter(story, "mastery-chapter")
    taught = _form(chapter, "alpha")
    reference_only = _form(chapter, "ref-only", is_playable=False)
    unpublished = _form(chapter, "retired", is_published=False)
    optional_form = _form(chapter, "optional")
    _level(chapter, "level-1", [taught, reference_only, unpublished])
    # Forms taught only by optional or unpublished levels stay out of the
    # completion denominator.
    _level(chapter, "level-optional", [optional_form], is_required=False)

    _master(player, taught)

    assert story_completed(player=player, story=story) is True


def test_challenge_completions_alone_do_not_complete_a_story(player):
    story = _story("mastery-story")
    chapter = _chapter(story, "mastery-chapter")
    form = _form(chapter, "alpha")
    _level(chapter, "level-1", [form])
    challenge = ChallengeLevel.objects.create(
        chapter=chapter,
        slug="mastery-challenge",
        title="Challenge",
        is_published=True,
    )
    ChallengeLevelCompletion.objects.create(player=player, challenge_level=challenge)

    assert story_completed(player=player, story=story) is False

    _master(player, form)
    assert story_completed(player=player, story=story) is True


def test_story_without_taught_forms_is_never_completed(player):
    story = _story("empty-story")
    _chapter(story, "empty-chapter")

    assert story_completed(player=player, story=story) is False


def test_batched_map_matches_per_story_selector(player):
    first = _story("first-story", sort_order=1)
    second = _story("second-story", sort_order=2, prerequisite=first)
    first_chapter = _chapter(first, "first-chapter")
    second_chapter = _chapter(second, "second-chapter", number=2)
    first_form = _form(first_chapter, "alpha")
    second_form = _form(second_chapter, "beta")
    _level(first_chapter, "level-1", [first_form])
    _level(second_chapter, "level-2", [second_form])
    _master(player, first_form)

    batched = stories_completed_map(player=player, stories=[first, second])

    assert batched == {
        first.id: story_completed(player=player, story=first),
        second.id: story_completed(player=player, story=second),
    }
    assert batched[first.id] is True
    assert batched[second.id] is False


def test_prerequisite_gate_uses_mastery_and_truthful_copy(player):
    first = _story("first-story", sort_order=1)
    second = _story("second-story", sort_order=2, prerequisite=first)
    chapter = _chapter(first, "first-chapter")
    form = _form(chapter, "alpha")
    _level(chapter, "level-1", [form])
    Entitlement.objects.create(player=player, kind="story", slug=second.slug)

    locked, reason = story_locked(player=player, story=second)
    assert locked is True
    assert reason == "Master every command in First Story before entering Second Story."

    _master(player, form)
    locked, reason = story_locked(player=player, story=second)
    assert locked is False
    assert reason == ""

    # A prebuilt map short-circuits the per-story query.
    locked, _ = story_locked(
        player=player, story=second, completed_map={first.id: False}
    )
    assert locked is True
