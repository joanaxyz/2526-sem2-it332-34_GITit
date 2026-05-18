import django.db.models.deletion
from django.db import migrations, models


def migrate_difficulty_content(apps, schema_editor):
    DifficultyInstance = apps.get_model("scenarios", "DifficultyInstance")
    ScenarioVariant = apps.get_model("scenarios", "ScenarioVariant")
    ScenarioSession = apps.get_model("scenarios", "ScenarioSession")

    for difficulty in DifficultyInstance.objects.select_related("scenario").all():
        if not difficulty.task_prompt:
            difficulty.task_prompt = difficulty.scenario.task_prompt
            difficulty.save(update_fields=["task_prompt"])

    legacy_variants = list(
        ScenarioVariant.objects.filter(difficulty_instance__isnull=True).select_related("scenario")
    )
    for legacy in legacy_variants:
        difficulty_ids = set(
            DifficultyInstance.objects.filter(scenario_id=legacy.scenario_id).values_list(
                "id", flat=True
            )
        )
        difficulty_ids.update(
            ScenarioSession.objects.filter(variant_id=legacy.id).values_list(
                "difficulty_instance_id", flat=True
            )
        )

        if not difficulty_ids:
            legacy.delete()
            continue

        for difficulty_id in difficulty_ids:
            replacement, _ = ScenarioVariant.objects.update_or_create(
                difficulty_instance_id=difficulty_id,
                slug=legacy.slug,
                defaults={
                    "scenario_id": legacy.scenario_id,
                    "label": legacy.label,
                    "structure_signature": legacy.structure_signature,
                    "initial_state": legacy.initial_state,
                    "target_state": legacy.target_state,
                    "expected_state_diagram": legacy.expected_state_diagram,
                    "is_published": legacy.is_published,
                },
            )
            ScenarioSession.objects.filter(
                variant_id=legacy.id,
                difficulty_instance_id=difficulty_id,
            ).update(variant_id=replacement.id)

        if not ScenarioSession.objects.filter(variant_id=legacy.id).exists():
            legacy.delete()


def reverse_difficulty_content(apps, schema_editor):
    ScenarioVariant = apps.get_model("scenarios", "ScenarioVariant")

    seen = set()
    for variant in ScenarioVariant.objects.select_related(
        "scenario", "difficulty_instance"
    ).order_by("id"):
        key = (variant.scenario_id, variant.slug)
        if key in seen:
            variant.delete()
            continue
        seen.add(key)
        variant.difficulty_instance_id = None
        variant.save(update_fields=["difficulty_instance"])


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ("scenarios", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="difficultyinstance",
            name="task_prompt",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="scenariovariant",
            name="difficulty_instance",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="variants",
                to="scenarios.difficultyinstance",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="scenariovariant",
            unique_together=set(),
        ),
        migrations.RunPython(migrate_difficulty_content, reverse_difficulty_content),
        migrations.AlterField(
            model_name="scenariovariant",
            name="difficulty_instance",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="variants",
                to="scenarios.difficultyinstance",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="scenariovariant",
            unique_together={("difficulty_instance", "slug")},
        ),
    ]
