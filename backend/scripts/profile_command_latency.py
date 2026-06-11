"""Ad-hoc latency profile for the adventure/challenge submit-command endpoints.

Run with: pytest scripts/profile_command_latency.py -s
Counts SQL queries and wall time per request through the real API views.
"""

import time

from django.core.management import call_command
from django.db import connection
from django.test.utils import CaptureQueriesContext
from rest_framework.test import APIClient

from adventures.models import AdventureRun, CommandAdventure
from challenges.models import ChallengeQuest
from challenges.services import ChallengeRunService


def make_user(django_user_model, username="profiler"):
    return django_user_model.objects.create_user(
        username=username, email=f"{username}@example.com", password="pass12345"
    )


def _timed_post(client, url, body, label):
    with CaptureQueriesContext(connection) as ctx:
        start = time.perf_counter()
        response = client.post(url, body, format="json")
        elapsed = (time.perf_counter() - start) * 1000
    assert response.status_code == 200, response.content
    print(f"\n=== {label}: {elapsed:.1f}ms CPU, {len(ctx.captured_queries)} queries ===")
    for q in ctx.captured_queries:
        sql = q["sql"]
        print(f"  [{q['time']}] {sql[:140]}")
    return response


def test_profile_adventure_submit(db, django_user_model):
    call_command("seed_curriculum_v2")
    user = make_user(django_user_model)
    client = APIClient()
    client.force_authenticate(user=user)

    adventure = CommandAdventure.objects.filter(is_published=True).first()
    start = client.post(f"/api/command-adventures/{adventure.slug}/runs/")
    assert start.status_code == 201
    run_id = start.json()["id"]

    url = f"/api/adventure-runs/{run_id}/submit-command/"
    _timed_post(client, url, {"command": "git status"}, "adventure: diagnostic cmd")
    _timed_post(client, url, {"command": "git branch tmp"}, "adventure: counted cmd (mid-attempt)")

    # Solve the current problem to capture a transition submit.
    run = AdventureRun.objects.get(id=run_id)
    attempt = run.attempts.filter(status="started").order_by("order").first()
    solution = attempt.selected_variant.solution_commands
    for idx, command in enumerate(solution):
        _timed_post(client, url, {"command": command}, f"adventure: solution {idx + 1}/{len(solution)}")


def test_profile_challenge_submit(db, django_user_model):
    call_command("seed_curriculum_v2")
    user = make_user(django_user_model)
    client = APIClient()
    client.force_authenticate(user=user)

    quest = ChallengeQuest.objects.get(challenge__slug="stage-commit-switch", difficulty="easy")
    adventure = CommandAdventure.objects.filter(
        storey=quest.challenge.storey, is_published=True
    ).first()
    if adventure is not None:
        from django.utils import timezone

        AdventureRun.objects.create(user=user, command_adventure=adventure, passed_at=timezone.now())
    run = ChallengeRunService().start_run(user=user, quest=quest, source_entry_point="tower_page")

    url = f"/api/challenge-runs/{run.id}/submit-command/"
    _timed_post(client, url, {"command": "git status"}, "challenge: diagnostic cmd")
    solution = run.variant.solution_commands
    for idx, command in enumerate(solution):
        _timed_post(client, url, {"command": command}, f"challenge: solution {idx + 1}/{len(solution)}")
