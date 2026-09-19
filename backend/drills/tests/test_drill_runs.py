"""Resuming a drill.

A drill is a several-minute queue that re-asks what you missed, so losing
it to a refresh costs the whole ladder. These pin that the checkpoint
survives, that it stays inside the level's own vocabulary, and that it
retires when the session does.
"""

from django.core.management import call_command
from rest_framework.test import APIClient

from adventures.models import AdventureLevel
from common.constants import SESSION_STATUS_ABANDONED, SESSION_STATUS_COMPLETED
from drills.models import DrillRun
from drills.selectors import drill_card_keys
from players.services import get_or_create_player


def make_client(django_user_model, username="squire-resume"):
    user = django_user_model.objects.create_user(
        username=username, email=f"{username}@example.com", password="pass12345"
    )
    player = get_or_create_player(user)
    client = APIClient()
    client.force_authenticate(user=user)
    return client, player


def seeded_level() -> AdventureLevel:
    return (
        AdventureLevel.objects.filter(is_published=True, drill__cards__isnull=False)
        .order_by("chapter__sort_order", "sort_order", "id")
        .distinct()
        .first()
    )


def state_for(level, *, extra_keys=()):
    keys = sorted(drill_card_keys(level_id=level.id))
    cards = {
        key: {"key": key, "ladder": ["recognise"], "rung": 0, "cleared": 1, "asks": 1, "missed": False, "retired": False}
        for key in list(keys) + list(extra_keys)
    }
    return {
        "cards": cards,
        "queue": list(cards),
        "sequence_pending": False,
        "answered": 3,
        "correct": 2,
    }


def seed(db_marker=None):
    call_command("seed_curriculum")
    call_command("seed_drills")


def test_a_checkpoint_comes_back_on_the_next_visit(db, django_user_model):
    seed()
    client, _player = make_client(django_user_model)
    level = seeded_level()

    saved = client.put(
        f"/api/adventure-levels/{level.id}/drill/run/", state_for(level), format="json"
    )
    assert saved.status_code == 200

    plan = client.get(f"/api/adventure-levels/{level.id}/drill/").json()

    assert plan["resume"] is not None
    assert plan["resume"]["answered"] == 3
    assert plan["resume"]["correct"] == 2
    assert plan["resume"]["queue_state"]["queue"]


def test_a_fresh_level_has_nothing_to_resume(db, django_user_model):
    seed()
    client, _player = make_client(django_user_model)
    level = seeded_level()

    assert client.get(f"/api/adventure-levels/{level.id}/drill/").json()["resume"] is None


def test_saving_twice_updates_the_one_active_run(db, django_user_model):
    seed()
    client, player = make_client(django_user_model)
    level = seeded_level()
    url = f"/api/adventure-levels/{level.id}/drill/run/"

    client.put(url, state_for(level), format="json")
    second = state_for(level)
    second["answered"] = 9
    second["correct"] = 7
    client.put(url, second, format="json")

    runs = DrillRun.objects.filter(player=player, adventure_level=level)
    assert runs.count() == 1
    assert runs.first().answered == 9


def test_a_card_the_level_does_not_teach_is_dropped(db, django_user_model):
    """The resumed queue decides which questions appear, so a stale or
    hand-edited key must not survive into the next session."""
    seed()
    client, player = make_client(django_user_model)
    level = seeded_level()

    client.put(
        f"/api/adventure-levels/{level.id}/drill/run/",
        state_for(level, extra_keys=["git-elsewhere/not-here"]),
        format="json",
    )

    stored = DrillRun.objects.get(player=player, adventure_level=level).queue_state
    assert "git-elsewhere/not-here" not in stored["cards"]
    assert "git-elsewhere/not-here" not in stored["queue"]
    assert set(stored["cards"]) == drill_card_keys(level_id=level.id)


def test_more_correct_than_answered_is_refused(db, django_user_model):
    seed()
    client, _player = make_client(django_user_model)
    level = seeded_level()
    state = state_for(level)
    state["correct"] = 99

    response = client.put(
        f"/api/adventure-levels/{level.id}/drill/run/", state, format="json"
    )

    assert response.status_code == 400
    assert not DrillRun.objects.exists()


def test_reporting_a_result_retires_the_run(db, django_user_model):
    seed()
    client, player = make_client(django_user_model)
    level = seeded_level()
    client.put(f"/api/adventure-levels/{level.id}/drill/run/", state_for(level), format="json")

    client.post(
        f"/api/adventure-levels/{level.id}/drill/results/",
        {"answers_total": 9, "answers_correct": 9, "completed": True, "shaky_form_keys": []},
        format="json",
    )

    run = DrillRun.objects.get(player=player, adventure_level=level)
    assert run.status == SESSION_STATUS_COMPLETED
    assert client.get(f"/api/adventure-levels/{level.id}/drill/").json()["resume"] is None


def test_starting_over_discards_the_checkpoint(db, django_user_model):
    seed()
    client, player = make_client(django_user_model)
    level = seeded_level()
    client.put(f"/api/adventure-levels/{level.id}/drill/run/", state_for(level), format="json")

    response = client.delete(f"/api/adventure-levels/{level.id}/drill/run/")

    assert response.status_code == 200
    assert response.json()["resume"] is None
    assert (
        DrillRun.objects.get(player=player, adventure_level=level).status
        == SESSION_STATUS_ABANDONED
    )


def test_one_players_checkpoint_is_not_another_players(db, django_user_model):
    seed()
    level = seeded_level()
    first, _ = make_client(django_user_model, "squire-one")
    second, _ = make_client(django_user_model, "squire-two")
    first.put(f"/api/adventure-levels/{level.id}/drill/run/", state_for(level), format="json")

    assert second.get(f"/api/adventure-levels/{level.id}/drill/").json()["resume"] is None
