from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("adventures", "0004_rename_adventureproblem_adventurequest_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="commandadventure",
            old_name="module",
            new_name="storey",
        ),
        migrations.RenameField(
            model_name="adventurequest",
            old_name="usage",
            new_name="command_form",
        ),
        migrations.RenameField(
            model_name="adventurerun",
            old_name="current_problem_index",
            new_name="current_quest_index",
        ),
        migrations.RenameIndex(
            model_name="adventuremastery",
            old_name="advmastery_user_problem_idx",
            new_name="advmastery_user_quest_idx",
        ),
    ]
