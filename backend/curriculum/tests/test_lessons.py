from django.core.management import call_command
from rest_framework.test import APIClient

from curriculum.models import Chapter, ChapterLesson
from curriculum.selectors import chapter_content_overview
from players.services import get_or_create_player
from shop.models import Entitlement

LESSON_PAGES = [
    {
        "id": "intro",
        "title": "What a commit records",
        "blocks": [{"type": "paragraph", "text": "A commit is a snapshot of staged files."}],
    }
]


def authored_lesson() -> ChapterLesson:
    """A reading lesson on a module chapter, the way authored content attaches one."""
    chapter = Chapter.objects.get(story__slug="arcane-spire", number=1)
    return ChapterLesson.objects.create(
        chapter=chapter,
        slug="what-a-commit-records",
        title="What a commit records",
        pages=LESSON_PAGES,
        is_published=True,
    )


def test_published_lessons_ship_renderable_pages(db):
    call_command("seed_curriculum", verbosity=0)
    authored_lesson()

    lessons = list(ChapterLesson.objects.filter(is_published=True))
    assert lessons
    for lesson in lessons:
        assert lesson.pages, f"{lesson.slug}: a lesson must ship renderable pages"
        assert all("blocks" in page for page in lesson.pages)


def test_chapter_overview_includes_lesson_pages(db):
    call_command("seed_curriculum", verbosity=0)
    lesson = authored_lesson()
    overview = chapter_content_overview(player=None, chapter_id=lesson.chapter_id)

    assert overview["lessons"], "the authored chapter should list its lessons"
    payload = overview["lessons"][0]
    assert payload["item_type"] == "lesson"
    assert payload["pages"], "pages ship inline so the reader needs no second request"


def test_overview_endpoint_and_unauthored_chapter_is_empty(db, django_user_model):
    call_command("seed_curriculum", verbosity=0)
    user = django_user_model.objects.create_user(
        username="reader",
        email="reader@example.com",
        password="pass12345",
    )
    api_client = APIClient()
    api_client.force_authenticate(user=user)

    lesson = authored_lesson()
    Entitlement.objects.create(
        player=get_or_create_player(user),
        kind="story",
        slug=lesson.chapter.story.slug,
    )
    response = api_client.get(f"/api/chapters/{lesson.chapter_id}/overview/")
    assert response.status_code == 200
    assert response.json()["lessons"][0]["slug"] == lesson.slug

    # Chapters without an authored lesson return an empty section - the chapter book
    # renders nothing there, keeping non-authored chapters unchanged.
    from curriculum.models import Story

    story = Story.objects.get(slug="arcane-spire")
    Entitlement.objects.get_or_create(
        player=get_or_create_player(user), kind="story", slug=story.slug
    )
    bare_chapter = Chapter.objects.create(
        story=story,
        slug="bare-lesson-test",
        number=99,
        title="Bare ChapterLesson Test",
        description="No authored lessons here.",
        is_published=True,
    )
    empty = api_client.get(f"/api/chapters/{bare_chapter.id}/overview/")
    assert empty.status_code == 200
    assert empty.json()["lessons"] == []
