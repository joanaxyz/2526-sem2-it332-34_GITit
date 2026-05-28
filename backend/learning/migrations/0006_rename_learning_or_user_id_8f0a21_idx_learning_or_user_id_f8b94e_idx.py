from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("learning", "0005_reconcile_orientation_session_schema"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RenameIndex(
                    model_name="orientationlessonsession",
                    old_name="learning_or_user_id_8f0a21_idx",
                    new_name="learning_or_user_id_f8b94e_idx",
                ),
            ],
            database_operations=[
                migrations.RunSQL(
                    sql="""
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE indexname = 'learning_or_user_id_8f0a21_idx'
    ) THEN
        ALTER INDEX learning_or_user_id_8f0a21_idx
            RENAME TO learning_or_user_id_f8b94e_idx;
    ELSIF NOT EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE indexname = 'learning_or_user_id_f8b94e_idx'
    ) THEN
        CREATE INDEX learning_or_user_id_f8b94e_idx
            ON learning_orientationlessonsession (user_id, lesson_id, updated_at DESC);
    END IF;
END $$;
""",
                    reverse_sql=migrations.RunSQL.noop,
                ),
            ],
        ),
    ]
