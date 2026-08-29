"""Authored chapter settings reach the compiled runtime chapter, and content
in the same authored chapter shares one runtime chapter."""

import pytest

from authoring.compiler import ContentRuntimeCompiler
from authoring.models import AuthoringChapter, ContentDefinition


def _playable_definition() -> dict:
    return {
        "levels": [
            {
                "slug": "s",
                "title": "S",
                "initial_state": {},
                "solution_commands": ["git status"],
                "evaluation_spec": {"completion_policy": {"mode": "state_hash"}},
            }
        ]
    }


def make_user(django_user_model, username="author"):
    return django_user_model.objects.create_user(
        username=username, email=f"{username}@example.com", password="pass12345"
    )


def make_admin(django_user_model, username="admin"):
    return django_user_model.objects.create_user(
        username=username, email=f"{username}@example.com", password="pass12345", is_staff=True
    )


@pytest.mark.django_db
def test_chapter_groups_content_into_one_runtime_chapter(django_user_model):
    user = make_admin(django_user_model)
    chapter = AuthoringChapter.objects.create(
        owner=user,
        slug="floor-1",
        title="Floor One",
    )
    adventure = ContentDefinition.objects.create(
        owner=user,
        kind="adventure",
        chapter=chapter,
        slug="adv",
        title="Adv",
        command_family="git status",
        definition=_playable_definition(),
    )
    challenge_a = ContentDefinition.objects.create(
        owner=user,
        kind="challenge",
        chapter=chapter,
        slug="cha",
        title="Cha A",
        command_family="git status",
        definition=_playable_definition(),
    )
    challenge_b = ContentDefinition.objects.create(
        owner=user,
        kind="challenge",
        chapter=chapter,
        slug="chb",
        title="Cha B",
        command_family="git status",
        definition=_playable_definition(),
    )

    compiler = ContentRuntimeCompiler()
    runtimes = [compiler.compile(content=c) for c in (adventure, challenge_a, challenge_b)]

    # A chapter holds one adventure and one challenge, all sharing ONE runtime chapter.
    chapter_ids = {r.chapter_id for r in runtimes}
    assert len(chapter_ids) == 1
    shared = runtimes[0].chapter
    # Multiple challenge definitions in the same authored chapter compile into
    # the chapter's single runtime challenge.
    assert runtimes[1].challenge.chapter_id == shared.id
    assert runtimes[2].challenge.chapter_id == shared.id


@pytest.mark.django_db
def test_chapter_summary_becomes_runtime_overview(django_user_model):
    # The authored chapter overview (summary) reaches the runtime chapter as its
    # description, which the chapter map panel displays.
    user = make_user(django_user_model)
    chapter = AuthoringChapter.objects.create(
        owner=user,
        slug="repo-foundations",
        title="Repository Foundations",
        summary="Read branch and commit-history signals before changing anything.",
    )
    content = ContentDefinition.objects.create(
        owner=user,
        kind="adventure",
        chapter=chapter,
        slug="adv-overview",
        title="Adv",
        command_family="git status",
        definition=_playable_definition(),
    )

    runtime = ContentRuntimeCompiler().compile(content=content)

    assert runtime.chapter.description == (
        "Read branch and commit-history signals before changing anything."
    )


@pytest.mark.django_db
def test_authored_battle_stage_stays_on_content_definition(django_user_model):
    # Battle-stage backdrop is content-scoped, not chapter-scoped.
    user = make_user(django_user_model)
    stage = {
        "background": "arcane-backdrop",
        "landing": {"x": 0.1, "y": 0.7, "width": 0.8, "height": 0.2},
    }
    chapter = AuthoringChapter.objects.create(
        owner=user, slug="dressed-floor", title="Dressed Floor"
    )
    content = ContentDefinition.objects.create(
        owner=user,
        kind="adventure",
        chapter=chapter,
        slug="adv-stage",
        title="Adv",
        command_family="git status",
        definition={**_playable_definition(), "battle_stage": stage},
    )

    runtime = ContentRuntimeCompiler().compile(content=content)

    assert runtime.adventure.source_content_definition.definition["battle_stage"] == stage
    assert runtime.chapter.battle_stage == {}
