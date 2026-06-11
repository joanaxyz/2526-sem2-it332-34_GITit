from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("practice", "0002_commandstep_cmdstep_attempt_id_idx"),
    ]

    operations = [
        # The old index references the field being renamed; drop it first and
        # re-add it under the new name afterwards (RenameField does not rewrite
        # index field references in migration state).
        migrations.RemoveIndex(
            model_name="commandstep",
            name="cmdstep_session_id_idx",
        ),
        migrations.RenameField(
            model_name="commandstep",
            old_name="session",
            new_name="challenge_run",
        ),
        migrations.RenameField(
            model_name="commandlog",
            old_name="step_log",
            new_name="step",
        ),
        migrations.AddIndex(
            model_name="commandstep",
            index=models.Index(fields=["challenge_run", "id"], name="cmdstep_run_id_idx"),
        ),
    ]
