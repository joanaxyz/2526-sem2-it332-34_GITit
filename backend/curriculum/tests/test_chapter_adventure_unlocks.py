from django.core.management import call_command
from django.db import connection
from django.test.utils import CaptureQueriesContext
from rest_framework.test import APIClient

from curriculum.models import Chapter
from curriculum.selectors import chapter_content_overview
from players.services import get_or_create_player


def _make_user(django_user_model, username: str = "track-student"):
    return django_user_model.objects.create_user(
        username=username,
        email=f"{username}@example.com",
        password="pass12345",
    )


def _first_seeded_chapter() -> Chapter:
    return (
        Chapter.objects.filter(is_published=True, adventure_levels__is_published=True)
        .order_by("sort_order", "number")
        .distinct()
        .first()
    )


def test_chapter_overview_marks_first_adventure_level_unlocked(db, django_user_model):
    call_command("seed_curriculum")
    user = _make_user(django_user_model)
    player = get_or_create_player(user)
    chapter = _first_seeded_chapter()

    payload = chapter_content_overview(player=player, chapter_id=chapter.id)

    assert payload["adventures"], "seeded chapter should expose adventure levels"
    first_level = payload["adventures"][0]
    assert first_level["locked"] is False
    assert first_level["lock_reason"] == ""
    assert first_level["is_passed"] is False


def test_chapter_overview_batch_loads_adventure_completions(db, django_user_model):
    call_command("seed_curriculum")
    user = _make_user(django_user_model, "track-query-student")
    player = get_or_create_player(user)
    chapter = _first_seeded_chapter()

    with CaptureQueriesContext(connection) as queries:
        chapter_content_overview(player=player, chapter_id=chapter.id)

    completion_queries = [
        query
        for query in queries.captured_queries
        if "progress_adventurelevelcompletion" in query["sql"].lower()
    ]
    assert len(completion_queries) == 1


def test_chapter_overview_api_does_not_fall_back_to_locked_placeholders(db, django_user_model):
    call_command("seed_curriculum")
    user = _make_user(django_user_model, "track-api-student")
    client = APIClient()
    client.force_authenticate(user=user)
    chapter = _first_seeded_chapter()

    response = client.get(f"/api/chapters/{chapter.id}/overview/")

    assert response.status_code == 200
    first_level = response.json()["adventures"][0]
    assert first_level["locked"] is False
    assert first_level["is_passed"] is False
