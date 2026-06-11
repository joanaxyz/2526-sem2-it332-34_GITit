from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("curriculum", "0002_storey_chest_rewards"),
    ]

    operations = [
        migrations.RenameField(
            model_name="commandskill",
            old_name="module",
            new_name="storey",
        ),
        migrations.RenameField(
            model_name="commandform",
            old_name="topic",
            new_name="command_skill",
        ),
    ]
