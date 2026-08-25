from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("curriculum", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="chapter",
            name="narrative_brief",
        ),
        migrations.RemoveField(
            model_name="story",
            name="narrative_brief",
        ),
    ]
