from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("learning", "0002_rename_lesson_overview_html"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="lesson",
            name="kind",
        ),
    ]
