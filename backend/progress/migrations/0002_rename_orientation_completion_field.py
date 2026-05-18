from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("progress", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="studentprogress",
            old_name="orientation_gate_satisfied_at_first_start",
            new_name="orientation_complete_at_first_start",
        ),
    ]
