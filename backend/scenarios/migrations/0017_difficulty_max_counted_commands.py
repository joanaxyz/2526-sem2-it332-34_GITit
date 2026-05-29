from django.db import migrations

DIFFICULTY_MAX_COUNTED_COMMANDS = {
    "easy": 12,
    "medium": 10,
    "hard": 8,
}


def apply_difficulty_max_counted_commands(apps, schema_editor):
    CommandCountPolicy = apps.get_model("scenarios", "CommandCountPolicy")
    for difficulty, max_val in DIFFICULTY_MAX_COUNTED_COMMANDS.items():
        CommandCountPolicy.objects.filter(
            difficulty_instance__difficulty=difficulty,
        ).update(max_counted_commands=max_val)


class Migration(migrations.Migration):
    dependencies = [
        ("scenarios", "0016_scenariosession_looped_variant"),
    ]

    operations = [
        migrations.RunPython(
            apply_difficulty_max_counted_commands,
            migrations.RunPython.noop,
        ),
    ]
