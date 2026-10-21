"""Drop what the retired level editor's ``authoring`` app left in the database.

The app and its references were removed from the migration history, so a fresh
database never creates them and every step below is a no-op. Databases migrated
before the removal still hold the authoring tables, the
``source_content_definition_id`` columns that pointed at them, and the
unpublished ``runtime`` chapters the compiler parked player content in; this
migration drops whatever of that exists.
"""

from django.db import migrations, models
from django.db.migrations.recorder import MigrationRecorder

# Referencing tables first.
AUTHORING_TABLES = (
    "authoring_publishedcontentruntime",
    "authoring_contentdefinition",
    "authoring_authoringchapter",
)
SOURCE_COLUMN = "source_content_definition_id"
SOURCE_COLUMN_MODELS = (
    ("adventures", "AdventureLevel"),
    ("challenges", "ChallengeLevel"),
    ("curriculum", "ChapterLesson"),
    ("curriculum", "CommandSkill"),
)
RUNTIME_MANAGEMENT_SOURCE = "runtime"


def _table_columns(connection, table: str) -> set[str]:
    with connection.cursor() as cursor:
        return {
            column.name
            for column in connection.introspection.get_table_description(cursor, table)
        }


def drop_authoring_leftovers(apps, schema_editor):
    connection = schema_editor.connection
    tables = set(connection.introspection.table_names())

    for table in AUTHORING_TABLES:
        if table in tables:
            cascade = " CASCADE" if connection.vendor == "postgresql" else ""
            schema_editor.execute(f"DROP TABLE {schema_editor.quote_name(table)}{cascade}")

    # Runtime chapters only ever held editor content, which is unreachable now.
    apps.get_model("curriculum", "Chapter").objects.filter(
        management_source=RUNTIME_MANAGEMENT_SOURCE
    ).delete()
    if connection.vendor == "postgresql":
        # Fire the deferred FK checks the deletes queued, so the ALTER TABLEs
        # below do not trip over pending trigger events.
        connection.check_constraints()

    for app_label, model_name in SOURCE_COLUMN_MODELS:
        model = apps.get_model(app_label, model_name)
        table = model._meta.db_table
        if table not in tables or SOURCE_COLUMN not in _table_columns(connection, table):
            continue
        # The column is no longer in the migration state; give the historical
        # model a stand-in field so the schema editor can drop it portably.
        stand_in = models.BigIntegerField(null=True, db_index=True)
        stand_in.contribute_to_class(model, SOURCE_COLUMN)
        schema_editor.remove_field(model, stand_in)

    MigrationRecorder(connection).migration_qs.filter(app="authoring").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("adventures", "0017_rename_waves_to_scenarios"),
        ("challenges", "0005_alter_challengetrialvariant_label"),
        ("curriculum", "0005_alter_chapter_management_source"),
        ("drills", "0002_leveldrill_drillrun_leveldrillcard"),
        ("practice", "0004_remove_legacy_adventure_attempt"),
        ("progress", "0004_delete_adventurelevelcompletion"),
        ("tutoring", "0002_pendingcommandintroduction"),
    ]

    operations = [
        migrations.RunPython(drop_authoring_leftovers, migrations.RunPython.noop),
    ]
