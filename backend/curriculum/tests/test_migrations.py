import pytest
from django.db import connection
from django.db.migrations.executor import MigrationExecutor

pytestmark = pytest.mark.django_db(transaction=True)

MIGRATE_FROM = ("curriculum", "0002_remove_unused_narrative_briefs")
MIGRATE_TO = ("curriculum", "0003_story_chapter_management_source")


def test_management_source_migration_classifies_seed_and_runtime_chapters():
    executor = MigrationExecutor(connection)
    executor.migrate([MIGRATE_FROM])
    old_apps = executor.loader.project_state([MIGRATE_FROM]).apps
    Story = old_apps.get_model("curriculum", "Story")
    Chapter = old_apps.get_model("curriculum", "Chapter")

    story = Story.objects.create(slug="seed-story", title="Seed Story")
    official = Chapter.objects.create(
        story=story,
        slug="official-chapter",
        number=1,
        title="Official",
        description="",
    )
    runtime = Chapter.objects.create(
        slug="ugc-chapter-42",
        number=900_042,
        title="Runtime",
        description="",
    )

    executor = MigrationExecutor(connection)
    executor.migrate([MIGRATE_TO])
    new_apps = executor.loader.project_state([MIGRATE_TO]).apps
    NewStory = new_apps.get_model("curriculum", "Story")
    NewChapter = new_apps.get_model("curriculum", "Chapter")

    assert NewStory.objects.get(pk=story.pk).management_source == "seed"
    assert NewChapter.objects.get(pk=official.pk).management_source == "seed"
    assert NewChapter.objects.get(pk=runtime.pk).management_source == "runtime"
