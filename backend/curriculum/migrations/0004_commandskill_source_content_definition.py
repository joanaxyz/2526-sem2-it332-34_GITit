import re

import django.db.models.deletion
from django.db import migrations, models

AUTHORED_SKILL_RE = re.compile(r"-ugc-(\d+)$")


def backfill_authored_command_skills(apps, schema_editor):
    CommandSkill = apps.get_model("curriculum", "CommandSkill")
    ContentDefinition = apps.get_model("authoring", "ContentDefinition")
    content_ids = set(ContentDefinition.objects.values_list("id", flat=True))
    changed = []
    for skill in CommandSkill.objects.filter(source_content_definition__isnull=True):
        match = AUTHORED_SKILL_RE.search(skill.slug)
        if match and int(match.group(1)) in content_ids:
            skill.source_content_definition_id = int(match.group(1))
            changed.append(skill)
    if changed:
        CommandSkill.objects.bulk_update(changed, ["source_content_definition"])


class Migration(migrations.Migration):
    dependencies = [
        ("authoring", "0005_contentdefinition_official_chapter"),
        ("curriculum", "0003_story_chapter_management_source"),
    ]

    operations = [
        migrations.AddField(
            model_name="commandskill",
            name="source_content_definition",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="runtime_command_skills",
                to="authoring.contentdefinition",
            ),
        ),
        migrations.RunPython(backfill_authored_command_skills, migrations.RunPython.noop),
    ]
