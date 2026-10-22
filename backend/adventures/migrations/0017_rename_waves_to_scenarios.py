from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):
    """Rename the tier stage from "wave" to "scenario"; rows and data are kept."""

    dependencies = [
        ("adventures", "0016_retire_required_successful_attempts"),
        ("curriculum", "0001_initial"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="adventureleveltierwave",
            name="unique_adv_level_tier_wave_slug",
        ),
        migrations.RemoveConstraint(
            model_name="adventureleveltierwave",
            name="adv_level_tier_wave_valid_command_budget",
        ),
        migrations.RemoveConstraint(
            model_name="adventureleveltierwavevariant",
            name="unique_adv_level_tier_wave_variant_slug",
        ),
        migrations.RenameModel(
            old_name="AdventureLevelTierWave",
            new_name="AdventureLevelTierScenario",
        ),
        migrations.RenameModel(
            old_name="AdventureLevelTierWaveVariant",
            new_name="AdventureLevelTierScenarioVariant",
        ),
        migrations.RenameField(
            model_name="adventureleveltierscenariovariant",
            old_name="wave",
            new_name="scenario",
        ),
        migrations.RenameField(
            model_name="adventureleveltierrun",
            old_name="current_wave",
            new_name="current_scenario",
        ),
        migrations.RenameField(
            model_name="adventureleveltierprogress",
            old_name="cleared_wave_slugs",
            new_name="cleared_scenario_slugs",
        ),
        migrations.AlterField(
            model_name="adventureleveltierscenario",
            name="tier",
            field=models.ForeignKey(
                on_delete=models.deletion.CASCADE,
                related_name="scenarios",
                to="adventures.adventureleveltier",
            ),
        ),
        migrations.AlterField(
            model_name="adventureleveltierscenario",
            name="command_forms",
            field=models.ManyToManyField(
                blank=True,
                related_name="adventure_level_tier_scenarios",
                to="curriculum.commandform",
            ),
        ),
        migrations.AlterModelOptions(
            name="adventureleveltierscenariovariant",
            options={"ordering": ["scenario_id", "sort_order", "semantic_key", "id"]},
        ),
        migrations.RenameIndex(
            model_name="adventureleveltierscenario",
            new_name="adv_lvl_tier_scenario_slot_idx",
            old_name="adv_lvl_tier_wave_slot_idx",
        ),
        migrations.AddConstraint(
            model_name="adventureleveltierscenario",
            constraint=models.UniqueConstraint(
                fields=("tier", "slug"), name="unique_adv_level_tier_scenario_slug"
            ),
        ),
        migrations.AddConstraint(
            model_name="adventureleveltierscenario",
            constraint=models.CheckConstraint(
                condition=Q(min_counted_commands__gte=0)
                & Q(max_counted_commands__gte=models.F("min_counted_commands")),
                name="adv_level_tier_scenario_valid_command_budget",
            ),
        ),
        migrations.AddConstraint(
            model_name="adventureleveltierscenariovariant",
            constraint=models.UniqueConstraint(
                fields=("scenario", "slug"),
                name="unique_adv_level_tier_scenario_variant_slug",
            ),
        ),
    ]
