import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    """Rename ChallengeQuest → ChallengeLevel (the difficulty unit) plus the FK
    fields on ChallengeVariant and ChallengeRun. Pure renames.

    chal_user_quest_latest_idx is dropped before the challenge_quest field
    rename and re-created after (RenameField doesn't rewrite Index field refs; on
    SQLite a remake would otherwise build a stale index). The index keeps its
    name."""

    dependencies = [
        ("challenges", "0006_remove_challengevariant_sabotage_script"),
    ]

    operations = [
        migrations.RemoveIndex(model_name="challengerun", name="chal_user_quest_latest_idx"),
        migrations.RenameModel(old_name="ChallengeQuest", new_name="ChallengeLevel"),
        migrations.RenameField(
            model_name="challengevariant", old_name="challenge_quest", new_name="challenge_level"
        ),
        migrations.RenameField(
            model_name="challengerun", old_name="challenge_quest", new_name="challenge_level"
        ),
        migrations.AddIndex(
            model_name="challengerun",
            index=models.Index(
                fields=["user", "challenge_level", "-id"], name="chal_user_level_latest_idx"
            ),
        ),
        migrations.AlterField(
            model_name="challengelevel",
            name="challenge",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="challenge_levels",
                to="challenges.challenge",
            ),
        ),
        migrations.AlterModelOptions(
            name="challengevariant",
            options={"ordering": ["challenge_level_id", "semantic_key", "id"]},
        ),
    ]
