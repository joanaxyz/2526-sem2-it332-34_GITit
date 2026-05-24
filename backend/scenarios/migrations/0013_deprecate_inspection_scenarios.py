from django.db import migrations, models


def deprecate_inspection_difficulties(apps, schema_editor):
    DifficultyInstance = apps.get_model("scenarios", "DifficultyInstance")
    DifficultyInstance.objects.filter(completion_type="inspection").update(
        completion_type="state_based",
        is_published=False,
    )


class Migration(migrations.Migration):
    dependencies = [
        ("scenarios", "0012_gitcommandcontent_sections"),
    ]

    operations = [
        migrations.RunPython(deprecate_inspection_difficulties, migrations.RunPython.noop),
        migrations.RenameField(
            model_name="scenarioskillfocus",
            old_name="supporting_inspection_commands",
            new_name="supporting_diagnostic_commands",
        ),
        migrations.RemoveField(
            model_name="scenariogenerationblueprint",
            name="expected_observations_template",
        ),
        migrations.RemoveField(
            model_name="scenariovariant",
            name="expected_observations",
        ),
        migrations.RemoveField(
            model_name="scenariosession",
            name="inspection_answer",
        ),
        migrations.AlterField(
            model_name="difficultyinstance",
            name="completion_type",
            field=models.CharField(
                choices=[
                    ("state_based", "State based"),
                    (
                        "expanded_state_based",
                        "State based with detailed target rules",
                    ),
                ],
                default="state_based",
                max_length=32,
            ),
        ),
    ]
