from importlib import import_module

import pytest
from django.apps import apps

from curriculum.models import Chapter, Story

cutover = import_module(
    "curriculum.migrations.0004_collapse_story_records_to_arcane_spire"
).collapse_to_arcane_spire


def _story(*, slug: str, title: str, prerequisite_story=None) -> Story:
    return Story.objects.create(
        slug=slug,
        title=title,
        world_slug=slug,
        prerequisite_story=prerequisite_story,
    )


@pytest.mark.django_db
def test_cutover_preserves_runebound_identity_and_deletes_retired_trees():
    survivor = _story(slug="git-it-legacy", title="The Runebound Turret")
    survivor_chapter = Chapter.objects.create(
        story=survivor,
        slug="module-0-orientation",
        number=0,
        title="Module 0",
        description="Preserved content",
    )
    old_arcane = _story(slug="arcane-spire", title="Old Arcane")
    frost = _story(
        slug="frostbound-citadel",
        title="Frostbound Citadel",
        prerequisite_story=old_arcane,
    )
    neon = _story(
        slug="neon-backstreets",
        title="Neon Backstreets",
        prerequisite_story=frost,
    )
    retired_chapter_ids = [
        Chapter.objects.create(
            story=story,
            slug=f"retired-{story.slug}",
            number=index,
            title="Retired",
            description="Delete me",
        ).id
        for index, story in enumerate((old_arcane, frost, neon), start=1)
    ]

    cutover(apps, schema_editor=None)

    renamed = Story.objects.get()
    assert renamed.id == survivor.id
    assert renamed.slug == "arcane-spire"
    assert renamed.title == "The Arcane Spire"
    assert renamed.world_slug == "arcane-spire"
    assert Chapter.objects.get(id=survivor_chapter.id).story_id == survivor.id
    assert not Chapter.objects.filter(id__in=retired_chapter_ids).exists()


@pytest.mark.django_db
def test_cutover_refuses_to_delete_retired_stories_without_the_survivor():
    _story(slug="arcane-spire", title="Old Arcane")

    with pytest.raises(RuntimeError, match="Runebound curriculum"):
        cutover(apps, schema_editor=None)

    assert Story.objects.filter(slug="arcane-spire").exists()
