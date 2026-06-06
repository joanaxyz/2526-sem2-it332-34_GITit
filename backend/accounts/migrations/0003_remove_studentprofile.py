from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_student_id_profile_names"),
    ]

    operations = [
        migrations.DeleteModel(
            name="StudentProfile",
        ),
    ]
