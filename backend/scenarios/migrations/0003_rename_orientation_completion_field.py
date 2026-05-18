from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("scenarios", "0002_difficulty_owned_variants"),
    ]

    operations = [
        migrations.RenameField(
            model_name="scenariosession",
            old_name="ocg_satisfied_at_start",
            new_name="orientation_complete_at_start",
        ),
    ]
