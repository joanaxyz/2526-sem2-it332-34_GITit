from django.db import migrations, models


def delete_story_entitlements(apps, schema_editor):
    """Stories are no longer sold, so every kind="story" row is dead weight.

    Story access is now decided purely by prerequisite mastery, so dropping
    these rows takes nothing away from the players who hold them.
    """
    apps.get_model("shop", "Entitlement").objects.filter(kind="story").delete()


class Migration(migrations.Migration):
    dependencies = [
        ("shop", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(delete_story_entitlements, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="entitlement",
            name="kind",
            field=models.CharField(choices=[("companion", "Companion")], max_length=16),
        ),
    ]
