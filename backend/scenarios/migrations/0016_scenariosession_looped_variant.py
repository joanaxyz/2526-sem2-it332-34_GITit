from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("scenarios", "0015_delete_targetstaterule"),
    ]

    operations = [
        migrations.AddField(
            model_name="scenariosession",
            name="looped_variant",
            field=models.BooleanField(default=False),
        ),
    ]
