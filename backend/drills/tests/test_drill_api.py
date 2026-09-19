"""The drill endpoints: access, recording, and what they refuse to store."""

from django.core.management import call_command
from rest_framework.test import APIClient

from adventures.models import AdventureLevel
from drills.models import DrillProgress, DrillRun
from drills.selectors import drill_card_keys
from players.services import get_or_create_player


def make_client(django_user_model, username="squire"):
    user = django_user_model.objects.create_user(
        username=username,
        email=f"{username}@example.com",
        password="pass12345",
    )
    player = get_or_create_player(user)
    client = APIClient()
    client.force_authenticate(user=user)
    return client, player


def first_drillable_level() -> AdventureLevel:
    """A level with seeded drill content - seeding is what creates it."""
    return (
        AdventureLevel.objects.filter(is_published=True, drill__cards__isnull=False)
        .select_related("chapter")
        .order_by("chapter__sort_order", "sort_order", "id")
        .distinct()
        .first()
    )


def result_body(**overrides) -> dict:
    return {
        "answers_total": 10,
        "answers_correct": 8,
        "completed": True,
        "shaky_form_keys": [],
        **overrides,
    }


def test_plan_returns_cards_and_a_zeroed_progress_row(db, django_user_model):
    call_command("seed_curriculum")
    call_command("seed_drills")
    client, _player = make_client(django_user_model)
    level = first_drillable_level()

    response = client.get(f"/api/adventure-levels/{level.id}/drill/")

    assert response.status_code == 200
    payload = response.json()
    assert payload["available"] is True
    assert payload["level"]["id"] == level.id
    assert payload["cards"]
    # Never null, so the client renders one readout rather than branching.
    assert payload["progress"]["cleared"] is False
    assert payload["progress"]["sessions"] == 0


def test_drill_does_not_require_a_companion(db, django_user_model):
    """Unlike an adventure run: a drill is recall practice on text, not a
    battle, so the companion gate would only lock beginners out of the rung
    that exists to help them."""
    call_command("seed_curriculum")
    call_command("seed_drills")
    client, player = make_client(django_user_model)
    level = first_drillable_level()

    response = client.get(f"/api/adventure-levels/{level.id}/drill/")

    assert not player.entitlements.filter(kind="companion").exists()
    assert response.status_code == 200


def test_recording_a_cleared_session_marks_the_level_drilled(db, django_user_model):
    call_command("seed_curriculum")
    call_command("seed_drills")
    client, player = make_client(django_user_model)
    level = first_drillable_level()

    response = client.post(
        f"/api/adventure-levels/{level.id}/drill/results/",
        result_body(),
        format="json",
    )

    assert response.status_code == 200
    progress = response.json()["progress"]
    assert progress["cleared"] is True
    assert progress["clears"] == 1
    assert progress["sessions"] == 1
    assert progress["best_accuracy"] == 80
    row = DrillProgress.objects.get(player=player, adventure_level=level)
    assert row.first_cleared_at is not None


def test_best_accuracy_keeps_the_high_water_mark(db, django_user_model):
    call_command("seed_curriculum")
    call_command("seed_drills")
    client, _player = make_client(django_user_model)
    level = first_drillable_level()
    url = f"/api/adventure-levels/{level.id}/drill/results/"

    client.post(url, result_body(answers_total=10, answers_correct=9), format="json")
    response = client.post(
        url, result_body(answers_total=10, answers_correct=4), format="json"
    )

    progress = response.json()["progress"]
    assert progress["best_accuracy"] == 90
    assert progress["last_accuracy"] == 40
    assert progress["sessions"] == 2
    assert progress["clears"] == 2


def test_an_abandoned_session_counts_but_does_not_clear(db, django_user_model):
    call_command("seed_curriculum")
    call_command("seed_drills")
    client, _player = make_client(django_user_model)
    level = first_drillable_level()

    response = client.post(
        f"/api/adventure-levels/{level.id}/drill/results/",
        result_body(completed=False),
        format="json",
    )

    progress = response.json()["progress"]
    assert progress["sessions"] == 1
    assert progress["clears"] == 0
    assert progress["cleared"] is False
    assert progress["first_cleared_at"] is None


def test_reported_weak_spots_are_intersected_with_the_levels_real_forms(db, django_user_model):
    """Stored vocabulary stays authored: a client cannot write arbitrary
    strings into the practice readout."""
    call_command("seed_curriculum")
    call_command("seed_drills")
    client, _player = make_client(django_user_model)
    level = first_drillable_level()
    real_key = sorted(drill_card_keys(level_id=level.id))[0]

    response = client.post(
        f"/api/adventure-levels/{level.id}/drill/results/",
        result_body(shaky_form_keys=[real_key, "git-not-a-command/made-up", real_key]),
        format="json",
    )

    assert response.json()["progress"]["shaky_form_keys"] == [real_key]


def test_more_correct_than_answered_is_rejected(db, django_user_model):
    call_command("seed_curriculum")
    call_command("seed_drills")
    client, _player = make_client(django_user_model)
    level = first_drillable_level()

    response = client.post(
        f"/api/adventure-levels/{level.id}/drill/results/",
        result_body(answers_total=3, answers_correct=9),
        format="json",
    )

    assert response.status_code == 400
    assert not DrillProgress.objects.exists()


def test_a_locked_level_cannot_be_drilled(db, django_user_model):
    call_command("seed_curriculum")
    call_command("seed_legacy_modules")
    call_command("seed_drills")
    client, _player = make_client(django_user_model)
    locked = (
        AdventureLevel.objects.filter(is_published=True, chapter__story__isnull=False)
        .exclude(chapter__story__prerequisite_story__isnull=True)
        .order_by("chapter__sort_order", "sort_order")
        .first()
    )
    if locked is None:
        return

    response = client.get(f"/api/adventure-levels/{locked.id}/drill/")

    assert response.status_code == 423


def test_an_unknown_level_is_a_404(db, django_user_model):
    call_command("seed_curriculum")
    call_command("seed_drills")
    client, _player = make_client(django_user_model)

    assert client.get("/api/adventure-levels/99999/drill/").status_code == 404


def test_the_chapter_overview_reports_drill_state_per_level(db, django_user_model):
    call_command("seed_curriculum")
    call_command("seed_drills")
    client, _player = make_client(django_user_model)
    level = first_drillable_level()
    client.post(
        f"/api/adventure-levels/{level.id}/drill/results/", result_body(), format="json"
    )

    overview = client.get(f"/api/chapters/{level.chapter_id}/overview/").json()

    entry = next(item for item in overview["adventures"] if item["id"] == level.id)
    assert entry["drill"] == {"available": True, "cleared": True, "best_accuracy": 80}
