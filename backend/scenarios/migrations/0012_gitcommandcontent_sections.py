from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("scenarios", "0011_gitcommandcontent"),
    ]

    operations = [
        migrations.AddField(
            model_name="gitcommandcontent",
            name="base_command",
            field=models.CharField(blank=True, max_length=120),
        ),
        migrations.AddField(
            model_name="gitcommandcontent",
            name="sections",
            field=models.JSONField(blank=True, default=list),
        ),
    ]
