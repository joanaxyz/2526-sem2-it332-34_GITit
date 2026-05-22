from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("scenarios", "0008_generation_blueprints"),
    ]

    operations = [
        migrations.AddField(
            model_name="scenariosession",
            name="inspection_answer",
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
