from django.db import migrations, models


class Migration(migrations.Migration):
    """Rename QuestCompletion → LevelCompletion and its adventure_quest /
    challenge_quest FKs. The two partial-unique constraints reference those
    fields in their condition, so they are dropped before the rename and
    re-added (with the new names) after — RenameField can't rewrite a
    constraint's condition in place."""

    dependencies = [
        ("progress", "0004_rename_problemcompletion_questcompletion"),
        ("adventures", "0008_rename_quest_to_level"),
        ("challenges", "0007_rename_quest_to_level"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="questcompletion", name="unique_adventure_quest_completion"
        ),
        migrations.RemoveConstraint(
            model_name="questcompletion", name="unique_challenge_quest_completion"
        ),
        migrations.RenameModel(old_name="QuestCompletion", new_name="LevelCompletion"),
        migrations.RenameField(
            model_name="levelcompletion", old_name="adventure_quest", new_name="adventure_level"
        ),
        migrations.RenameField(
            model_name="levelcompletion", old_name="challenge_quest", new_name="challenge_level"
        ),
        migrations.AddConstraint(
            model_name="levelcompletion",
            constraint=models.UniqueConstraint(
                fields=["user", "adventure_level"],
                name="unique_adventure_level_completion",
                condition=models.Q(adventure_level__isnull=False),
            ),
        ),
        migrations.AddConstraint(
            model_name="levelcompletion",
            constraint=models.UniqueConstraint(
                fields=["user", "challenge_level"],
                name="unique_challenge_level_completion",
                condition=models.Q(challenge_level__isnull=False),
            ),
        ),
    ]
