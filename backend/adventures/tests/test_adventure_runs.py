from django.core.management import call_command

from adventures.services import AdventureRunService, ordered_problems_for
from adventures.models import AdventureRun, CommandAdventure
from adventures.scoring import (
    BAND_FAILED,
    BAND_MASTERED,
    BAND_PASSED,
    AdventureScoringService,
    band_for,
)


def make_user(django_user_model, username="adventurer"):
    return django_user_model.objects.create_user(
        username=username, email=f"{username}@example.com", password="pass12345"
    )


# ---- Scoring engine -------------------------------------------------------

def test_ideal_solve_is_mastered():
    score = AdventureScoringService().score_attempt(
        solved=True, counted_commands=1, ideal_commands=1, hint_count=0
    )
    assert score.correctness_score == 100
    assert score.efficiency_score == 100
    assert score.independence_score == 100
    assert score.final_score == 100
    assert score.band == BAND_MASTERED
    assert score.passed is True
    assert score.mastery_gain == 1.0


def test_inefficient_solve_drops_to_passed_band():
    score = AdventureScoringService().score_attempt(
        solved=True, counted_commands=4, ideal_commands=1, hint_count=0
    )
    # 0.6*100 + 0.25*25 + 0.15*100 = 81
    assert score.efficiency_score == 25
    assert score.final_score == 81
    assert score.band == BAND_PASSED
    assert 0 < score.mastery_gain < 1.0


def test_unsolved_scores_zero_and_no_mastery():
    score = AdventureScoringService().score_attempt(
        solved=False, counted_commands=10, ideal_commands=1, hint_count=0
    )
    assert score.final_score == 0
    assert score.band == BAND_FAILED
    assert score.passed is False
    assert score.mastery_gain == 0.0


def test_hints_reduce_independence():
    score = AdventureScoringService().score_attempt(
        solved=True, counted_commands=1, ideal_commands=1, hint_count=1
    )
    assert score.independence_score == 75
    assert score.final_score == 96  # 60 + 25 + 11.25 -> 96


def test_band_thresholds():
    assert band_for(69) == BAND_FAILED
    assert band_for(70) == BAND_PASSED
    assert band_for(94) == "strong_pass"
    assert band_for(95) == BAND_MASTERED


def test_bare_pass_yields_partial_mastery_not_full():
    score = AdventureScoringService().score_attempt(
        solved=True, counted_commands=100, ideal_commands=1, hint_count=4
    )
    # solved but very inefficient + many hints -> low pass or fail
    assert score.mastery_gain < 0.6


# ---- Run orchestration ----------------------------------------------------

def _adventure_with_problems():
    for adventure in CommandAdventure.objects.filter(is_published=True):
        if ordered_problems_for(adventure):
            return adventure
    raise AssertionError("No published adventure with problems was seeded.")


def test_run_completes_when_all_problems_solved(db, django_user_model):
    call_command("seed_curriculum_v2")
    user = make_user(django_user_model)
    adventure = _adventure_with_problems()
    service = AdventureRunService()

    run = service.start_run(user=user, adventure=adventure)
    assert run.status == "started"

    problems = ordered_problems_for(adventure)
    for _ in problems:
        attempt = service.current_attempt(run=run)
        assert attempt is not None
        service.record_attempt_result(
            attempt=attempt,
            solved=True,
            counted_command_count=attempt.adventure_problem.ideal_counted_commands or 1,
            command_count=1,
            hint_count=0,
        )

    run.refresh_from_db()
    assert run.status == "completed"
    assert service.current_attempt(run=run) is None
    assert run.mastery_progress_gained > 0
    assert run.total_score >= 70


def test_run_fails_when_required_problem_unsolved(db, django_user_model):
    call_command("seed_curriculum_v2")
    user = make_user(django_user_model)
    adventure = _adventure_with_problems()
    service = AdventureRunService()

    run = service.start_run(user=user, adventure=adventure)
    problems = ordered_problems_for(adventure)
    for index, _ in enumerate(problems):
        attempt = service.current_attempt(run=run)
        service.record_attempt_result(
            attempt=attempt,
            solved=index != 0,  # fail the first (required) problem
            counted_command_count=1,
            command_count=1,
            hint_count=0,
        )

    run.refresh_from_db()
    assert run.status == "failed"


def test_cannot_start_two_active_runs(db, django_user_model):
    call_command("seed_curriculum_v2")
    user = make_user(django_user_model)
    adventure = _adventure_with_problems()
    service = AdventureRunService()
    service.start_run(user=user, adventure=adventure)
    try:
        service.start_run(user=user, adventure=adventure)
        raise AssertionError("Expected Locked when starting a second active run.")
    except Exception as exc:  # Locked
        assert "active run" in str(exc)


# ---- HTTP integration -----------------------------------------------------

def test_adventure_run_http_flow_solves_a_problem(db, django_user_model):
    from rest_framework.test import APIClient

    call_command("seed_curriculum_v2")
    user = make_user(django_user_model, "httpadv")
    adventure = _adventure_with_problems()
    client = APIClient()
    client.force_authenticate(user=user)

    start = client.post(f"/api/command-adventures/{adventure.slug}/runs/")
    assert start.status_code == 201
    body = start.json()
    assert body["status"] == "started"
    attempt = body["current_attempt"]
    assert attempt is not None
    # Adventure scaffolding must not leak the answer.
    assert attempt["scaffolding"]["expected_state"] is False
    assert attempt["scaffolding"]["hints"] is True

    run_id = body["id"]
    # Drive the authored solution for the first problem's selected variant.
    from adventures.models import AdventureProblemAttempt

    attempt_obj = AdventureProblemAttempt.objects.get(id=attempt["id"])
    solution = attempt_obj.selected_variant.solution_commands
    assert solution, "seed variant should have an official solution"

    last = None
    for command in solution:
        last = client.post(
            f"/api/adventure-runs/{run_id}/submit-command/",
            {"command": command},
            format="json",
        )
        assert last.status_code == 200
    assert last.json()["solved"] is True

    attempt_obj.refresh_from_db()
    assert attempt_obj.status == "completed"
    assert attempt_obj.final_score >= 70


def test_use_hint_endpoint_increments_hint_count(db, django_user_model):
    from rest_framework.test import APIClient

    call_command("seed_curriculum_v2")
    user = make_user(django_user_model, "hinter")
    adventure = _adventure_with_problems()
    client = APIClient()
    client.force_authenticate(user=user)

    run_id = client.post(f"/api/command-adventures/{adventure.slug}/runs/").json()["id"]
    resp = client.post(f"/api/adventure-runs/{run_id}/use-hint/")
    assert resp.status_code == 200
    body = resp.json()
    assert body["run"]["current_attempt"]["counts"]["hint_count"] == 1
    assert body["hint_number"] == 1
    assert isinstance(body["hint"], str) and body["hint"]


def test_authored_hint_set_is_served_in_order(db, django_user_model):
    from adventures.services import AdventureRunService

    call_command("seed_curriculum_v2")
    user = make_user(django_user_model, "authoredhints")
    adventure = _adventure_with_problems()
    service = AdventureRunService()
    run = service.start_run(user=user, adventure=adventure)
    attempt = service.current_attempt(run=run)
    attempt.selected_variant.hint_set = ["First nudge", "Second nudge"]
    attempt.selected_variant.save(update_fields=["hint_set"])

    first = service.use_hint(attempt=attempt)
    second = service.use_hint(attempt=attempt)
    third = service.use_hint(attempt=attempt)  # exhausted -> generic fallback

    assert first["hint"] == "First nudge"
    assert second["hint"] == "Second nudge"
    assert third["hint"] not in {"First nudge", "Second nudge"}
    attempt.refresh_from_db()
    assert attempt.hint_count == 3
