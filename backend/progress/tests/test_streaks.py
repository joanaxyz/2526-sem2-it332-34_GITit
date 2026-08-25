from datetime import datetime, timedelta

import pytest
from django.utils import timezone

from players.services import get_or_create_player
from progress.models import StreakRecord
from progress.services.streaks import StreakService

pytestmark = pytest.mark.django_db


def test_record_completion_is_idempotent_and_preserves_the_longest_streak(
    django_user_model,
):
    user = django_user_model.objects.create_user(username="streak-player")
    player = get_or_create_player(user)
    first_completion = timezone.make_aware(datetime(2026, 7, 1, 12))
    service = StreakService()

    service.record_completion(player=player, completed_at=first_completion)
    service.record_completion(
        player=player,
        completed_at=first_completion + timedelta(hours=1),
    )
    streak = StreakRecord.objects.get(player=player)
    assert (streak.current_streak, streak.longest_streak) == (1, 1)

    service.record_completion(
        player=player,
        completed_at=first_completion + timedelta(days=1),
    )
    streak.refresh_from_db()
    assert (streak.current_streak, streak.longest_streak) == (2, 2)

    service.record_completion(
        player=player,
        completed_at=first_completion + timedelta(days=3),
    )
    streak.refresh_from_db()
    assert (streak.current_streak, streak.longest_streak) == (1, 2)
