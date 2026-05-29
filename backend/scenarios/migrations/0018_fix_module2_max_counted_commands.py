from django.db import migrations

from common.constants import DIFFICULTY_MAX_COUNTED_COMMANDS


def fix_module2_max_counted_commands(apps, schema_editor):
    CommandCountPolicy = apps.get_model("scenarios", "CommandCountPolicy")
    for difficulty, max_val in DIFFICULTY_MAX_COUNTED_COMMANDS.items():
        CommandCountPolicy.objects.filter(
            difficulty_instance__difficulty=difficulty,
        ).exclude(
            max_counted_commands=max_val,
        ).update(max_counted_commands=max_val)


class Migration(migrations.Migration):
    dependencies = [
        ("scenarios", "0017_difficulty_max_counted_commands"),
    ]

    operations = [
        migrations.RunPython(
            fix_module2_max_counted_commands,
            migrations.RunPython.noop,
        ),
    ]
