import pytest
from django.contrib.auth.models import AnonymousUser
from django.db import connection
from django.db.migrations.executor import MigrationExecutor

from authoring.models import ContentDefinition
from authoring.selectors import visible_content_definitions
from shop.access import can_launch

pytestmark = pytest.mark.django_db(transaction=True)

MIGRATE_FROM = ("authoring", "0003_contentdefinition_unique_system_content_slug_per_kind_and_more")
MIGRATE_TO = ("authoring", "0005_contentdefinition_official_chapter")


def test_store_visibility_is_preserved_as_public_during_migration():
    executor = MigrationExecutor(connection)
    executor.migrate([MIGRATE_FROM])
    old_apps = executor.loader.project_state([MIGRATE_FROM]).apps
    OldContentDefinition = old_apps.get_model("authoring", "ContentDefinition")
    content = OldContentDefinition.objects.create(
        owner=None,
        kind="lesson",
        slug="legacy-store-lesson",
        title="Legacy store lesson",
        visibility="store",
        status="published",
    )

    executor = MigrationExecutor(connection)
    executor.migrate([MIGRATE_TO])
    new_apps = executor.loader.project_state([MIGRATE_TO]).apps
    NewContentDefinition = new_apps.get_model("authoring", "ContentDefinition")

    assert NewContentDefinition.objects.get(pk=content.pk).visibility == "public"

    migrated = ContentDefinition.objects.get(pk=content.pk)
    anonymous = AnonymousUser()
    assert visible_content_definitions(user=anonymous).filter(pk=migrated.pk).exists()
    assert can_launch(user=anonymous, content_definition=migrated)
