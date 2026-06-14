import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    """Rename the per-task unit from "quest" to "level" (AdventureQuest →
    AdventureLevel, AdventureQuestAttempt → AdventureLevelAttempt) plus the FK
    fields and AdventureRun.current_quest_index. Pure renames — no data moves.

    The advmastery_user_quest_idx index is dropped before the field rename and
    re-created after: RenameField does not rewrite an Index's field refs, and on
    SQLite the next table remake would then build a stale index. The index keeps
    its name (it only identifies the object)."""

    dependencies = [
        ("adventures", "0007_adventurequest_encounter_spec_and_more"),
    ]

    operations = [
        migrations.RemoveIndex(model_name="adventuremastery", name="advmastery_user_quest_idx"),
        migrations.RenameModel(old_name="AdventureQuest", new_name="AdventureLevel"),
        migrations.RenameModel(old_name="AdventureQuestAttempt", new_name="AdventureLevelAttempt"),
        migrations.RenameField(
            model_name="adventurevariant", old_name="adventure_quest", new_name="adventure_level"
        ),
        migrations.RenameField(
            model_name="adventurelevelattempt", old_name="adventure_quest", new_name="adventure_level"
        ),
        migrations.RenameField(
            model_name="adventuremastery", old_name="adventure_quest", new_name="adventure_level"
        ),
        migrations.RenameField(
            model_name="adventurerun", old_name="current_quest_index", new_name="current_level_index"
        ),
        migrations.AddIndex(
            model_name="adventuremastery",
            index=models.Index(fields=["user", "adventure_level"], name="advmastery_user_level_idx"),
        ),
        migrations.AlterField(
            model_name="adventurelevel",
            name="command_form",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="adventure_levels",
                to="curriculum.commandform",
            ),
        ),
        migrations.AlterModelOptions(
            name="adventurevariant",
            options={"ordering": ["adventure_level_id", "semantic_key", "id"]},
        ),
    ]
