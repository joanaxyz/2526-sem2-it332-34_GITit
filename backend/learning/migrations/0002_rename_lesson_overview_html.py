from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("learning", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="lesson",
            old_name="overview_html",
            new_name="content_html",
        ),
    ]
