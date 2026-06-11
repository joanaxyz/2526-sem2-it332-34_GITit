from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("progress", "0003_remove_problemcompletion_unique_adventure_problem_completion_and_more"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="ProblemCompletion",
            new_name="QuestCompletion",
        ),
    ]
