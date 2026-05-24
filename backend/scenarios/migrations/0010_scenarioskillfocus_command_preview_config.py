from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("scenarios", "0009_scenariosession_inspection_answer"),
    ]

    operations = [
        migrations.AddField(
            model_name="scenarioskillfocus",
            name="command_preview_config",
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
