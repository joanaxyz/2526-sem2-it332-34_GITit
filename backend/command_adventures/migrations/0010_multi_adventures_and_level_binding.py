from django.db import migrations, models
import django.db.models.deletion


def bind_existing_levels(apps, schema_editor):
    AdventureLevel = apps.get_model("adventures", "AdventureLevel")
    CommandAdventure = apps.get_model("adventures", "CommandAdventure")
    for level in AdventureLevel.objects.select_related("command_form__command_skill__storey"):
        storey = level.command_form.command_skill.storey
        adventure = (
            CommandAdventure.objects.filter(storey=storey, is_published=True)
            .order_by("sort_order", "id")
            .first()
        )
        if adventure:
            level.command_adventure_id = adventure.id
            level.save(update_fields=["command_adventure"])


class Migration(migrations.Migration):

    dependencies = [
        ("adventures", "0009_commandadventure_source_content_definition"),
    ]

    operations = [
        migrations.AlterField(
            model_name="commandadventure",
            name="storey",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="command_adventures",
                to="curriculum.storey",
            ),
        ),
        migrations.AddField(
            model_name="adventurelevel",
            name="command_adventure",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="levels",
                to="adventures.commandadventure",
            ),
        ),
        migrations.RunPython(bind_existing_levels, migrations.RunPython.noop),
    ]
