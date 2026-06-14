from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adventures', '0002_adventureproblem_prerequisites_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='adventurerun',
            name='mode',
            field=models.CharField(
                choices=[('primary', 'Primary'), ('replay', 'Replay')],
                default='primary',
                max_length=16,
            ),
        ),
    ]
