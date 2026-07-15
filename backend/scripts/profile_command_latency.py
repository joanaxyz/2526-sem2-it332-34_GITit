"""Ad-hoc latency profile for the adventure/challenge submit-command endpoints.

Run with: pytest scripts/profile_command_latency.py -s
Counts SQL queries and wall time per request through the real API views.
"""

import time

from django.core.management import call_command
from django.db import connection
from django.test.utils import CaptureQueriesContext
from rest_framework.test import APIClient

from adventures.models import AdventureLevel, AdventureRun
from challenges.models import ChallengeTrial
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
    call_command("seed_curriculum")
    user = make_user(django_user_model)
    client = APIClient()
    client.force_authenticate(user=user)

    level = AdventureLevel.objects.filter(is_published=True).first()
    start = client.post(f"/api/adventure-levels/{level.id}/runs/")
    assert start.status_code == 201
    run_id = start.json()["id"]

    url = f"/api/adventure-runs/{run_id}/submit-command/"
    _timed_post(client, url, {"command": "git status"}, "adventure: diagnostic cmd")
    _timed_post(client, url, {"command": "git branch tmp"}, "adventure: counted cmd (mid-attempt)")

    # Solve the current problem to capture a transition submit.
    run = AdventureRun.objects.get(id=run_id)
    solution = run.selected_variant.solution_commands
    for idx, command in enumerate(solution):
        _timed_post(client, url, {"command": command}, f"adventure: solution {idx + 1}/{len(solution)}")


def test_profile_challenge_submit(db, django_user_model):
    call_command("seed_curriculum")
    user = make_user(django_user_model)
    client = APIClient()
    client.force_authenticate(user=user)

    trial = ChallengeTrial.objects.get(
        challenge_level__slug="compose-clean-history",
        difficulty="easy",
    )
    # Challenges are gated on passing EVERY published adventure in the chapter,
    # so satisfy the gate for all of them (not just the first).
    from django.utils import timezone

    from players.services import get_or_create_player
    from progress.models import AdventureLevelCompletion

    player = get_or_create_player(user)
    for level in AdventureLevel.objects.filter(
        chapter=trial.challenge_level.chapter,
        is_published=True,
        is_required=True,
    ):
        run = AdventureRun.objects.create(
            player=player,
            level=level,
            selected_variant=level.variants.filter(is_published=True).first(),
            passed_at=timezone.now(),
        )
        AdventureLevelCompletion.objects.create(
            player=player,
            adventure_level=level,
            adventure_run=run,
        )
    run = ChallengeRunService().start_run(user=user, trial=trial, source_entry_point="level_page")

    url = f"/api/challenge-runs/{run.id}/submit-command/"
    _timed_post(client, url, {"command": "git status"}, "challenge: diagnostic cmd")
    solution = run.variant.solution_commands
    for idx, command in enumerate(solution):
        _timed_post(client, url, {"command": command}, f"challenge: solution {idx + 1}/{len(solution)}")
