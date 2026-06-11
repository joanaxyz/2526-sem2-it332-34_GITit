from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("challenges", "0002_rename_challengelevel_challengequest_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="challenge",
            old_name="module",
            new_name="storey",
        ),
        migrations.RemoveField(
            model_name="challenge",
            name="command_topics",
        ),
        migrations.RenameField(
            model_name="challengequest",
            old_name="scenario",
            new_name="challenge",
        ),
        migrations.RenameField(
            model_name="challengerun",
            old_name="module",
            new_name="storey",
        ),
        migrations.RenameField(
            model_name="challengerun",
            old_name="workflow_scenario",
            new_name="challenge",
        ),
        migrations.RenameField(
            model_name="challengerun",
            old_name="prior_session",
            new_name="prior_run",
        ),
        migrations.RenameIndex(
            model_name="challengerun",
            old_name="chal_user_level_latest_idx",
            new_name="chal_user_quest_latest_idx",
        ),
    ]
