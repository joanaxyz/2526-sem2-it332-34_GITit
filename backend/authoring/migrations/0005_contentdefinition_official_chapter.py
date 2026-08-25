import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("authoring", "0004_alter_contentdefinition_visibility_and_more"),
        ("curriculum", "0003_story_chapter_management_source"),
    ]

    operations = [
        migrations.AddField(
            model_name="contentdefinition",
            name="official_chapter",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="official_content_definitions",
                to="curriculum.chapter",
            ),
        ),
        migrations.AddConstraint(
            model_name="contentdefinition",
            constraint=models.CheckConstraint(
                condition=(
                    models.Q(("chapter__isnull", True))
                    | models.Q(("official_chapter__isnull", True))
                ),
                name="authoring_content_one_chapter_type",
            ),
        ),
    ]
