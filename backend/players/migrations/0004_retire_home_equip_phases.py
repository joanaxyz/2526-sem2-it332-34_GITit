from django.db import migrations


def advance_home_equip_to_done(apps, schema_editor):
    """
    The `home` and `equip` onboarding phases are retired. Any account that
    stalled in either phase skipped the now-removed Home tour; advance them
    to `done` so the frontend shows no further onboarding UI.
    """
    PlayerPreferences = apps.get_model("players", "PlayerPreferences")
    PlayerPreferences.objects.filter(
        onboarding_phase__in=["home", "equip"]
    ).update(onboarding_phase="done")


def restore_home_equip_phases(apps, schema_editor):
    # There is no safe reverse: we cannot know whether a `done` account was
    # originally in `home` or `equip`. This migration is intentionally
    # irreversible — reverting it would require manual data recovery.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("players", "0003_alter_playerpreferences_onboarding_phase"),
    ]

    operations = [
        migrations.RunPython(advance_home_equip_to_done, restore_home_equip_phases),
    ]
