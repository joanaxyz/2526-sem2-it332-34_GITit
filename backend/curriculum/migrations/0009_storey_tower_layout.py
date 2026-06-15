from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("curriculum", "0008_storey_battle_stage"),
    ]

    operations = [
        migrations.AddField(
            model_name="storey",
            name="tower_layout",
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
