from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("scenarios", "0010_scenarioskillfocus_command_preview_config"),
    ]

    operations = [
        migrations.CreateModel(
            name="GitCommandContent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("key", models.SlugField(unique=True)),
                ("display_name", models.CharField(max_length=120)),
                ("canonical_command", models.CharField(max_length=160)),
                ("aliases", models.JSONField(blank=True, default=list)),
                ("summary", models.TextField(blank=True)),
                ("tags", models.JSONField(blank=True, default=list)),
                ("pages", models.JSONField(blank=True, default=list)),
                ("is_active", models.BooleanField(default=True)),
                ("version", models.PositiveIntegerField(default=1)),
                ("sort_order", models.PositiveIntegerField(default=0)),
            ],
            options={
                "ordering": ["sort_order", "key"],
            },
        ),
    ]
