from django.core.management import call_command
from rest_framework.test import APIClient

from curriculum.models import Chapter, Story
from curriculum.selectors import story_locked
from players.services import get_or_create_player


def make_user(django_user_model, username: str = "climber"):
    return django_user_model.objects.create_user(
        username=username,
        email=f"{username}@example.com",
        password="pass12345",
    )


def test_story_without_a_prerequisite_is_never_locked(db, django_user_model):
    call_command("seed_curriculum")
    user = make_user(django_user_model)
    player = get_or_create_player(user)
    story = Story.objects.get(slug="git-it-legacy")

    locked, _ = story_locked(player=player, story=story)

    assert locked is False


def test_story_is_gated_only_by_its_prerequisite(db, django_user_model):
    """Stories are not sold, so mastery of the prerequisite is the whole gate."""
    user = make_user(django_user_model)
    player = get_or_create_player(user)
    prerequisite = Story.objects.create(
        slug="opening-story",
        title="Opening Story",
        world_slug="opening-story",
    )
    sequel = Story.objects.create(
        slug="sequel-story",
        title="Sequel Story",
        world_slug="sequel-story",
        prerequisite_story=prerequisite,
    )

    locked, reason = story_locked(player=player, story=sequel)
    assert locked is True
    assert reason == "Master every command in Opening Story before entering Sequel Story."

    # The prerequisite reports completed - nothing else stands in the way.
    locked, reason = story_locked(
        player=player, story=sequel, completed_map={prerequisite.id: True}
    )
    assert locked is False
    assert reason == ""


def test_story_list_api_reports_lock_state_without_pricing(db, django_user_model):
    call_command("seed_curriculum")
    user = make_user(django_user_model)
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.get("/api/stories/")

    assert response.status_code == 200
    by_slug = {row["slug"]: row for row in response.json()}
    assert by_slug["git-it-legacy"]["locked"] is False
    # No prerequisite, so an unsold story opens immediately.
    assert by_slug["arcane-spire"]["locked"] is False
    assert by_slug["arcane-spire"]["world_slug"] == "arcane-spire"
    # Frostbound sits behind Arcane Spire mastery.
    assert by_slug["frostbound-citadel"]["locked"] is True
    assert "price" not in by_slug["arcane-spire"]
    assert "owned" not in by_slug["arcane-spire"]


def test_chapters_of_an_ungated_story_are_open(db, django_user_model):
    story = Story.objects.create(
        slug="open-story",
        title="Open Story",
        world_slug="open-story",
        is_published=True,
    )
    chapter = Chapter.objects.create(
        story=story,
        slug="open-basics",
        number=900001,
        title="Open Basics",
        description="Learn in the open story.",
        is_published=True,
    )
    user = make_user(django_user_model)
    client = APIClient()
    client.force_authenticate(user=user)

    chapters = client.get("/api/chapters/?story=open-story")

    assert chapters.status_code == 200
    assert chapters.json()[0]["id"] == chapter.id
    assert chapters.json()[0]["locked"] is False
