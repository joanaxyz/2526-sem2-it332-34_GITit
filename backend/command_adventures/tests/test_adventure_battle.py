"""Battle layer on the adventure submit path: authoritative roster on the
attempt, ordered events per command, defeat = the existing budget exhaustion."""

from django.core.management import call_command
from rest_framework.test import APIClient

from adventures.models import AdventureLevelAttempt, CommandAdventure
from adventures.services import ordered_levels_for
from battle.state import _target_hp


def _client(django_user_model, username="battler"):
    user = django_user_model.objects.create_user(
        username=username, email=f"{username}@example.com", password="pass12345"
    )
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def _adventure():
    for adventure in CommandAdventure.objects.order_by("sort_order", "id"):
        if ordered_levels_for(adventure):
            return adventure
    raise AssertionError("seed should provide an adventure with levels")


def _start(client, adventure):
    response = client.post(f"/api/command-adventures/{adventure.slug}/runs/")
    assert response.status_code == 201
    return response.json()


def test_attempt_payload_carries_an_initial_roster(db, django_user_model):
    call_command("seed_curriculum_v2")
    body = _start(_client(django_user_model), _adventure())

    battle = body["current_attempt"]["battle"]
    assert battle is not None
    assert battle["events"] == []
    monsters = battle["monsters"]
    assert monsters, "every encounter fields at least one monster"
    assert all(m["alive"] and m["hp"] == m["max_hp"] for m in monsters)
    # Total roster HP equals the variant's rule count (distance to target).
    attempt = AdventureLevelAttempt.objects.get(id=body["current_attempt"]["id"])
    assert sum(m["hp"] for m in monsters) == _target_hp(attempt.selected_variant.evaluation_spec)


def test_miss_triggers_a_monster_attack_event(db, django_user_model):
    call_command("seed_curriculum_v2")
    client = _client(django_user_model)
    body = _start(client, _adventure())

    # A counted-but-failing git command: syntactically git, no progress.
    response = client.post(
        f"/api/adventure-runs/{body['id']}/submit-command/",
        {"command": "git nonsense-subcommand"},
        format="json",
    )
    assert response.status_code == 200
    events = response.json()["battle"]["events"]
    assert [e["type"] for e in events] == ["monster_attack"]
    assert events[0]["cause"] == "miss"


def test_solving_lands_the_finishing_blow(db, django_user_model):
    call_command("seed_curriculum_v2")
    client = _client(django_user_model)
    body = _start(client, _adventure())

    attempt = AdventureLevelAttempt.objects.get(id=body["current_attempt"]["id"])
    solution = attempt.selected_variant.solution_commands
    assert solution

    last = None
    for command in solution:
        last = client.post(
            f"/api/adventure-runs/{body['id']}/submit-command/",
            {"command": command},
            format="json",
        )
        assert last.status_code == 200
    payload = last.json()
    assert payload["solved"] is True

    battle = payload["battle"]
    types = [e["type"] for e in battle["events"]]
    assert "encounter_cleared" in types
    assert "monster_attack" not in types, "a solve is never a miss"
    assert all(not m["alive"] for m in battle["monsters"])
    # The transition run carries the NEXT encounter's fresh roster.
    next_attempt = payload["run"]["current_attempt"]
    if next_attempt is not None:
        assert all(m["alive"] for m in next_attempt["battle"]["monsters"])


def test_budget_exhaustion_emits_player_defeat(db, django_user_model):
    call_command("seed_curriculum_v2")
    client = _client(django_user_model)
    body = _start(client, _adventure())

    attempt = AdventureLevelAttempt.objects.get(id=body["current_attempt"]["id"])
    budget = attempt.adventure_level.max_counted_commands

    last = None
    for _ in range(budget):
        last = client.post(
            f"/api/adventure-runs/{body['id']}/submit-command/",
            {"command": "git nonsense-subcommand"},
            format="json",
        )
        assert last.status_code == 200
    payload = last.json()
    assert payload["solved"] is False
    types = [e["type"] for e in payload["battle"]["events"]]
    assert types[-1] == "player_defeat"
    # Defeat is the existing failure path: the attempt failed, the run goes on.
    attempt.refresh_from_db()
    assert attempt.status == "failed"
