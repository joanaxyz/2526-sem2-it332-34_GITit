from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("adventures", "0002_initial"),
    ]

    operations = [
        migrations.RemoveField(model_name="adventurelevel", name="brief"),
        migrations.RemoveField(model_name="adventurelevel", name="description"),
        migrations.RemoveField(model_name="adventurelevel", name="level_type"),
        migrations.RemoveField(model_name="adventurelevel", name="narrative_brief"),
    ]
