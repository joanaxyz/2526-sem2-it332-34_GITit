from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "progress",
            "0003_cointransaction_coin_transaction_amount_nonzero_and_more",
        ),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="streakrecord",
            constraint=models.CheckConstraint(
                condition=models.Q(("longest_streak__gte", models.F("current_streak"))),
                name="streak_longest_gte_current",
            ),
        ),
    ]
