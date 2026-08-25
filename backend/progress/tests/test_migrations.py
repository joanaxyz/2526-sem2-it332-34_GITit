import pytest
from django.db import connection
from django.db.migrations.executor import MigrationExecutor

pytestmark = pytest.mark.django_db(transaction=True)

MIGRATE_FROM = (
    "progress",
    "0002_adventurelevelcompletion_adventure_completion_stars_lte_3_and_more",
)
MIGRATE_TO = (
    "progress",
    "0005_remove_studentprogress",
)


def test_legacy_progress_rows_are_normalized_and_dead_progress_table_is_removed():
    executor = MigrationExecutor(connection)
    executor.migrate([MIGRATE_FROM])
    old_apps = executor.loader.project_state([MIGRATE_FROM]).apps
    User = old_apps.get_model("auth", "User")
    Player = old_apps.get_model("players", "Player")
    OldCoinTransaction = old_apps.get_model("progress", "CoinTransaction")
    OldStudentProgress = old_apps.get_model("progress", "StudentProgress")
    OldStreakRecord = old_apps.get_model("progress", "StreakRecord")

    user = User.objects.create(username="legacy-progress-player")
    player = Player.objects.create(user_id=user.pk)
    streak = OldStreakRecord.objects.create(
        player_id=player.pk,
        current_streak=3,
        longest_streak=1,
    )
    transaction = OldCoinTransaction.objects.create(
        player_id=player.pk,
        amount=0,
        reason="legacy_zero_value",
        award_key="legacy-zero-value",
    )
    OldStudentProgress.objects.create(player_id=player.pk)

    executor = MigrationExecutor(connection)
    executor.migrate([MIGRATE_TO])
    new_apps = executor.loader.project_state([MIGRATE_TO]).apps
    NewCoinTransaction = new_apps.get_model("progress", "CoinTransaction")
    NewStreakRecord = new_apps.get_model("progress", "StreakRecord")

    assert NewStreakRecord.objects.get(pk=streak.pk).longest_streak == 3
    assert not NewCoinTransaction.objects.filter(pk=transaction.pk).exists()
    with connection.cursor() as cursor:
        assert (
            "progress_studentprogress"
            not in connection.introspection.table_names(cursor)
        )
