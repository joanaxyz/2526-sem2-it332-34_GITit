import pytest
from rest_framework.test import APIClient

from curriculum.models import Chapter, Story
from curriculum.serializers import ChapterListSerializer, StorySerializer

STORY_FIELDS = {
    "id",
    "slug",
    "title",
    "summary",
    "price",
    "sort_order",
    "is_published",
    "completed",
    "owned",
    "world_slug",
    "difficulty",
    "prerequisite_story",
    "locked",
    "lock_reason",
}
CHAPTER_FIELDS = {
    "id",
    "slug",
    "number",
    "title",
    "description",
    "sort_order",
    "is_playable",
    "story",
    "locked",
    "lock_reason",
    "command_skill_count",
    "challenge_count",
    "adventure_level_count",
    "level_completion",
    "chest_schedule",
}


@pytest.fixture()
def authenticated_client(django_user_model):
    user = django_user_model.objects.create_user(
        username="catalog-reader",
        email="catalog-reader@example.com",
        password="pass12345",
    )
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def create_catalog():
    prerequisite = Story.objects.create(
        slug="foundation",
        title="Foundation",
        summary="Start here.",
        price=0,
        sort_order=1,
        world_slug="arcane-spire",
        difficulty=Story.DIFFICULTY_BEGINNER,
    )
    sequel = Story.objects.create(
        slug="summit",
        title="Summit",
        summary="Climb higher.",
        price=250,
        sort_order=2,
        world_slug="frostbound-citadel",
        difficulty=Story.DIFFICULTY_ADVANCED,
        prerequisite_story=prerequisite,
    )
    chapter = Chapter.objects.create(
        story=sequel,
        slug="summit-one",
        number=1,
        title="Summit One",
        description="Climb.",
        sort_order=4,
    )
    other_story = Story.objects.create(
        slug="elsewhere",
        title="Elsewhere",
        sort_order=3,
        world_slug="neon-backstreets",
    )
    Chapter.objects.create(
        story=other_story,
        slug="elsewhere-one",
        number=1,
        title="Elsewhere One",
        description="Not in the filtered response.",
        sort_order=5,
    )
    return prerequisite, sequel, chapter


@pytest.mark.django_db
def test_story_catalog_response_has_exact_nested_contract(authenticated_client):
    prerequisite, sequel, _ = create_catalog()

    response = authenticated_client.get("/api/stories/")

    assert response.status_code == 200
    rows = {row["slug"]: row for row in response.json()}
    assert all(set(row) == STORY_FIELDS for row in rows.values())
    assert rows[prerequisite.slug]["prerequisite_story"] is None
    assert rows[sequel.slug]["prerequisite_story"] == {
        "slug": prerequisite.slug,
        "title": prerequisite.title,
        "completed": False,
    }
    assert rows[sequel.slug]["difficulty"] == Story.DIFFICULTY_ADVANCED
    assert rows[sequel.slug]["summary"] == "Climb higher."
    assert rows[sequel.slug]["price"] == 250
    assert rows[sequel.slug] == StorySerializer(
        sequel,
        context={"player": None, "story_completed_map": {prerequisite.id: False}},
    ).data


@pytest.mark.django_db
def test_chapter_catalog_response_has_exact_nested_contract_and_filter(authenticated_client):
    _, sequel, chapter = create_catalog()

    response = authenticated_client.get("/api/chapters/?story=summit")

    assert response.status_code == 200
    assert len(response.json()) == 1
    row = response.json()[0]
    assert row["id"] == chapter.id
    assert set(row) == CHAPTER_FIELDS
    assert row["story"] == {
        "id": sequel.id,
        "slug": sequel.slug,
        "title": sequel.title,
        "world_slug": sequel.world_slug,
    }
    assert row["level_completion"] == {
        "value": 0.0,
        "numerator": 0,
        "denominator": 0,
    }
    assert row["chest_schedule"] == [
        {"threshold": 25, "coins": 25},
        {"threshold": 50, "coins": 60},
        {"threshold": 75, "coins": 100},
        {"threshold": 100, "coins": 150},
    ]
    chapter.command_skill_count = 0
    chapter.challenge_count = 0
    chapter.adventure_level_count = 0
    serializer = ChapterListSerializer(
        chapter,
        context={
            "player": None,
            "chapter_completion_count_map": {},
            "chapter_completion_denominator_map": {},
        },
    )
    assert row == serializer.data


@pytest.mark.django_db
def test_chapter_serializer_supports_declared_nullable_story():
    chapter = Chapter.objects.create(
        story=None,
        slug="unassigned-reference",
        number=99,
        title="Unassigned Reference",
        description="Not published through the catalog selector.",
        sort_order=99,
    )
    chapter.command_skill_count = 0
    chapter.challenge_count = 0
    chapter.adventure_level_count = 0

    row = ChapterListSerializer(
        chapter,
        context={
            "player": None,
            "chapter_completion_count_map": {},
            "chapter_completion_denominator_map": {},
        },
    ).data

    assert set(row) == CHAPTER_FIELDS
    assert row["story"] is None
    assert row["locked"] is False
    assert row["lock_reason"] == ""
