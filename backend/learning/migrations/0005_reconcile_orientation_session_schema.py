from django.db import migrations

_SQL = """
DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = current_schema()
          AND table_name = 'learning_orientationlessonsession'
          AND column_name = 'command_history'
    ) THEN
        EXECUTE 'ALTER TABLE learning_orientationlessonsession RENAME COLUMN command_history TO command_log';
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = current_schema()
          AND table_name = 'learning_orientationlessonsession'
          AND column_name = 'command_log'
    ) THEN
        EXECUTE 'ALTER TABLE learning_orientationlessonsession ADD COLUMN command_log jsonb NOT NULL DEFAULT ''[]''::jsonb';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = current_schema()
          AND table_name = 'learning_orientationlessonsession'
          AND column_name = 'started_at'
    ) THEN
        EXECUTE 'ALTER TABLE learning_orientationlessonsession RENAME COLUMN started_at TO created_at';
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = current_schema()
          AND table_name = 'learning_orientationlessonsession'
          AND column_name = 'created_at'
    ) THEN
        EXECUTE 'ALTER TABLE learning_orientationlessonsession ADD COLUMN created_at timestamp with time zone NOT NULL DEFAULT NOW()';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = current_schema()
          AND table_name = 'learning_orientationlessonsession'
          AND column_name = 'status'
    ) THEN
        EXECUTE 'ALTER TABLE learning_orientationlessonsession DROP COLUMN status';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = current_schema()
          AND table_name = 'learning_orientationlessonsession'
          AND column_name = 'current_topic_index'
    ) THEN
        EXECUTE 'ALTER TABLE learning_orientationlessonsession DROP COLUMN current_topic_index';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = current_schema()
          AND table_name = 'learning_orientationlessonsession'
          AND column_name = 'completed_at'
    ) THEN
        EXECUTE 'ALTER TABLE learning_orientationlessonsession DROP COLUMN completed_at';
    END IF;
END $$;
"""


def _reconcile_schema(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    schema_editor.execute(_SQL)


class Migration(migrations.Migration):
    dependencies = [
        ("learning", "0004_orientationlessonsession"),
    ]

    operations = [
        migrations.RunPython(_reconcile_schema, migrations.RunPython.noop),
    ]
