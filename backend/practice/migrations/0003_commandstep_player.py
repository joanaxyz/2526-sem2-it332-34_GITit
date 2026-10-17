import django.db.models.deletion
from django.db import migrations, models
from django.db.models import Case, OuterRef, Subquery, When


def backfill_step_players(apps, schema_editor):
    CommandStep = apps.get_model("practice", "CommandStep")
    ChallengeRun = apps.get_model("challenges", "ChallengeRun")
    AdventureRun = apps.get_model("adventures", "AdventureRun")
    AdventureLevelTierRun = apps.get_model("adventures", "AdventureLevelTierRun")

    challenge_player = ChallengeRun.objects.filter(pk=OuterRef("challenge_run_id")).values(
        "player_id"
    )[:1]
    adventure_player = AdventureRun.objects.filter(pk=OuterRef("attempt_id")).values(
        "player_id"
    )[:1]
    tier_player = AdventureLevelTierRun.objects.filter(
        pk=OuterRef("adventure_tier_run_id")
    ).values("player_id")[:1]

    CommandStep.objects.update(
        player_id=Case(
            When(challenge_run_id__isnull=False, then=Subquery(challenge_player)),
            When(attempt_id__isnull=False, then=Subquery(adventure_player)),
            When(adventure_tier_run_id__isnull=False, then=Subquery(tier_player)),
        )
    )


class Migration(migrations.Migration):
    dependencies = [
        ("practice", "0002_remove_commandstep_command_step_exactly_one_parent_and_more"),
        ("players", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="commandstep",
            name="player",
            field=models.ForeignKey(
                editable=False,
                null=True,
                db_index=False,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="command_steps",
                to="players.player",
            ),
        ),
        migrations.RunPython(backfill_step_players, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="commandstep",
            name="player",
            field=models.ForeignKey(
                editable=False,
                db_index=False,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="command_steps",
                to="players.player",
            ),
        ),
        migrations.AddIndex(
            model_name="commandstep",
            index=models.Index(
                fields=["player", "created_at"], name="cmdstep_player_created_idx"
            ),
        ),
    ]
