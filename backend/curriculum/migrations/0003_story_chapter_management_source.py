from django.db import migrations, models


def classify_runtime_chapters(apps, schema_editor):
    Chapter = apps.get_model("curriculum", "Chapter")
    Chapter.objects.filter(slug__startswith="ugc-").update(management_source="runtime")


def restore_seed_ownership(apps, schema_editor):
    Chapter = apps.get_model("curriculum", "Chapter")
    Chapter.objects.filter(management_source="runtime").update(management_source="seed")


class Migration(migrations.Migration):
    dependencies = [
        ("curriculum", "0002_remove_unused_narrative_briefs"),
    ]

    operations = [
        migrations.AddField(
            model_name="story",
            name="management_source",
            field=models.CharField(
                choices=[("seed", "Seed"), ("admin", "Admin")],
                default="seed",
                max_length=8,
            ),
        ),
        migrations.AddField(
            model_name="chapter",
            name="management_source",
            field=models.CharField(
                choices=[("seed", "Seed"), ("admin", "Admin"), ("runtime", "Runtime")],
                default="seed",
                max_length=8,
            ),
        ),
        migrations.RunPython(classify_runtime_chapters, restore_seed_ownership),
    ]
