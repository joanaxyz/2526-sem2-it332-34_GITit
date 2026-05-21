# Generated for latency-sensitive dashboard, module, and terminal queries.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("scenarios", "0005_difficultyinstance_completion_type_and_more"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="scenariosession",
            index=models.Index(
                fields=["user", "mode", "status"],
                name="sess_user_mode_status_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="scenariosession",
            index=models.Index(
                fields=["user", "difficulty_instance", "status", "mode"],
                name="sess_user_diff_state_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="scenariosession",
            index=models.Index(
                fields=["user", "difficulty_instance", "-id"],
                name="sess_user_diff_latest_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="steplog",
            index=models.Index(fields=["session", "id"], name="steplog_session_id_idx"),
        ),
    ]
