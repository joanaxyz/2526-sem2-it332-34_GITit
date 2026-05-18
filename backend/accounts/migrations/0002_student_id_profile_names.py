import re

from django.db import migrations, models

STUDENT_ID_PATTERN = re.compile(r"^\d{2}-\d{4}-\d{3}$")


def generated_student_id(index):
    return f"{index // 10_000_000:02d}-{(index // 1000) % 10_000:04d}-{index % 1000:03d}"


def normalize_student_ids(apps, schema_editor):
    StudentProfile = apps.get_model("accounts", "StudentProfile")
    seen = set()
    fallback_index = 1

    for profile in StudentProfile.objects.order_by("id"):
        raw_value = (profile.student_id or f"STUDENT-{profile.user_id}").strip().upper()
        candidate = raw_value if STUDENT_ID_PATTERN.fullmatch(raw_value) else ""
        while not candidate or candidate.lower() in seen:
            candidate = generated_student_id(fallback_index)
            fallback_index += 1

        seen.add(candidate.lower())
        profile.student_id = candidate
        profile.save(update_fields=["student_id"])


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="studentprofile",
            old_name="display_name",
            new_name="student_id",
        ),
        migrations.RunPython(normalize_student_ids, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="studentprofile",
            name="student_id",
            field=models.CharField(db_index=True, max_length=32, unique=True),
        ),
    ]
