from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("challenges", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(model_name="challengelevel", name="brief"),
    ]
