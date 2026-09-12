from django.db import migrations, models


def move_story_starts_to_welcome(apps, schema_editor):
    PlayerPreferences = apps.get_model("players", "PlayerPreferences")
    PlayerPreferences.objects.filter(onboarding_phase="stories").update(
        onboarding_phase="welcome"
    )


def restore_story_starts(apps, schema_editor):
    PlayerPreferences = apps.get_model("players", "PlayerPreferences")
    PlayerPreferences.objects.filter(onboarding_phase="welcome").update(
        onboarding_phase="stories"
    )


class Migration(migrations.Migration):

    dependencies = [
        ("players", "0002_playerpreferences_onboarding_phase"),
    ]

    operations = [
        migrations.RunPython(move_story_starts_to_welcome, restore_story_starts),
        migrations.AlterField(
            model_name="playerpreferences",
            name="onboarding_phase",
            field=models.CharField(
                choices=[
                    ("welcome", "Welcome"),
                    ("orientation", "Orientation"),
                    ("stories", "Stories"),
                    ("shop", "Shop"),
                    ("purchase", "Purchase"),
                    ("home", "Home"),
                    ("equip", "Equip"),
                    ("done", "Done"),
                ],
                default="done",
                max_length=16,
            ),
        ),
    ]
