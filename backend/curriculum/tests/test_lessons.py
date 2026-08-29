from django.core.management import call_command
from rest_framework.test import APIClient

from curriculum.models import ChapterLesson
from curriculum.selectors import chapter_content_overview


def test_seed_creates_published_lessons_with_pages(db):
    call_command("seed_curriculum")

    lessons = list(ChapterLesson.objects.filter(is_published=True))
    assert lessons, "the seed should author at least one published lesson"
    for lesson in lessons:
        assert lesson.pages, f"{lesson.slug}: a lesson must ship renderable pages"
        assert all("blocks" in page for page in lesson.pages)


def test_chapter_overview_includes_lesson_pages(db):
    call_command("seed_curriculum")

    lesson = ChapterLesson.objects.filter(is_published=True).select_related("chapter").first()
    overview = chapter_content_overview(player=None, chapter_id=lesson.chapter_id)

    assert overview["lessons"], "the authored chapter should list its lessons"
    payload = overview["lessons"][0]
    assert payload["item_type"] == "lesson"
    assert payload["pages"], "pages ship inline so the reader needs no second request"


def test_overview_endpoint_and_unauthored_chapter_is_empty(db, django_user_model):
    call_command("seed_curriculum")
    user = django_user_model.objects.create_user(
        username="reader",
        email="reader@example.com",
        password="pass12345",
    )
    api_client = APIClient()
    api_client.force_authenticate(user=user)

    lesson = ChapterLesson.objects.filter(is_published=True).first()
    response = api_client.get(f"/api/chapters/{lesson.chapter_id}/overview/")
    assert response.status_code == 200
    assert response.json()["lessons"][0]["slug"] == lesson.slug

    # Chapters without an authored lesson return an empty section - the chapter book
    # renders nothing there, keeping non-authored chapters unchanged.
    from curriculum.models import Chapter, Story

    story = Story.objects.get(slug="arcane-spire")
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
