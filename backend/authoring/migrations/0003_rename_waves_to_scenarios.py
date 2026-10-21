from django.db import migrations


def _levels(definition):
    if not isinstance(definition, dict):
        return []
    levels = definition.get("levels")
    if isinstance(levels, list):
        return [level for level in levels if isinstance(level, dict)]
    level = definition.get("level")
    return [level] if isinstance(level, dict) else []


def _rename_key(apps, old, new):
    ContentDefinition = apps.get_model("authoring", "ContentDefinition")
    for content in ContentDefinition.objects.only("id", "definition").iterator():
        changed = False
        for level in _levels(content.definition):
            if old in level and new not in level:
                level[new] = level.pop(old)
                changed = True
        if changed:
            content.save(update_fields=["definition"])


def forwards(apps, schema_editor):
    _rename_key(apps, "waves", "scenarios")


def backwards(apps, schema_editor):
    _rename_key(apps, "scenarios", "waves")


class Migration(migrations.Migration):
    """Authored adventure levels nest their problems under ``scenarios``."""

    dependencies = [
        ("authoring", "0002_initial"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
