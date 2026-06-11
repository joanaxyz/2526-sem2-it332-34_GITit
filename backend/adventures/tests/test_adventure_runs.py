from django.core.management import call_command

from adventures.models import AdventureRun, CommandAdventure
from adventures.scheduler import pass_bar_for
from adventures.scoring import (
    BAND_FAILED,
    BAND_MASTERED,
    BAND_PASSED,
    AdventureScoringService,
    band_for,
)
from adventures.services import AdventureRunService, ordered_quests_for


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

def _adventure_with_quests():
    for adventure in CommandAdventure.objects.filter(is_published=True):
        if ordered_quests_for(adventure):
            return adventure
    raise AssertionError("No published adventure with quests was seeded.")


def _solve_current(service, run, *, solved=True) -> bool:
    """Drive the run's current attempt; returns False once the session is over."""
    attempt = service.current_attempt(run=run)
    if attempt is None:
        return False
    service.record_attempt_result(
        attempt=attempt,
        solved=solved,
        counted_command_count=attempt.adventure_quest.min_counted_commands or 1,
        command_count=1,
        hint_count=0,
    )
    return True


def test_run_completes_when_all_commands_mastered(db, django_user_model):
    call_command("seed_curriculum_v2")
    user = make_user(django_user_model)
    adventure = _adventure_with_quests()
    service = AdventureRunService()

    run = service.start_run(user=user, adventure=adventure)
    assert run.status == "started"

    # Clean solves advance Leitner boxes; the scheduler interleaves the commands
    # and the session ends only once every command reaches mastery (box N).
    for _ in range(500):
        if not _solve_current(service, run):
            break
    else:
        raise AssertionError("adventure did not reach full mastery within the cap")

    run.refresh_from_db()
    assert run.status == "completed"
    assert service.current_attempt(run=run) is None
    assert run.passed_at is not None
    assert run.session_score >= pass_bar_for(adventure)
    assert run.mastery_progress_gained == 1.0


def test_run_never_passes_while_a_command_is_unsolved(db, django_user_model):
    call_command("seed_curriculum_v2")
    user = make_user(django_user_model)
    adventure = _adventure_with_quests()
    service = AdventureRunService()

    run = service.start_run(user=user, adventure=adventure)
    first_id = ordered_quests_for(adventure)[0].id

    # Solve every command except the first, which we always fail. The per-command
    # floor (every command solved at least once) is never met, so the adventure
    # can never pass and the session never completes.
    for _ in range(200):
        attempt = service.current_attempt(run=run)
        if attempt is None:
            break
        service.record_attempt_result(
            attempt=attempt,
            solved=attempt.adventure_quest_id != first_id,
            counted_command_count=1,
            command_count=1,
            hint_count=0,
        )

    run.refresh_from_db()
    assert run.passed_at is None
    assert run.status == "started"
    assert service.current_attempt(run=run) is not None


def test_starting_again_resumes_the_active_run(db, django_user_model):
    """Re-entering an adventure with a run in progress resumes it (no lockout,
    no duplicate run), preserving the one-active-run-per-adventure invariant."""
    call_command("seed_curriculum_v2")
    user = make_user(django_user_model)
    adventure = _adventure_with_quests()
    service = AdventureRunService()
    first = service.start_run(user=user, adventure=adventure)
    second = service.start_run(user=user, adventure=adventure)

    assert second.id == first.id
    active_runs = AdventureRun.objects.filter(
        user=user, command_adventure=adventure, status="started"
    )
    assert active_runs.count() == 1


def test_replay_after_pass_is_playable_but_uncounted(db, django_user_model):
    """Once an adventure is passed, the next run is an uncounted free-play replay:
    it stays fully playable (the scheduler would otherwise have nothing left to
    serve) yet never touches mastery, the pass milestone, or the session score."""
    from adventures.models import AdventureMastery

    call_command("seed_curriculum_v2")
    user = make_user(django_user_model, "replayer")
    adventure = _adventure_with_quests()
    service = AdventureRunService()

    primary = service.start_run(user=user, adventure=adventure)
    for _ in range(500):
        if not _solve_current(service, primary):
            break
    primary.refresh_from_db()
    assert primary.mode == "primary"
    assert primary.passed_at is not None

    mastery_before = dict(
        AdventureMastery.objects.filter(user=user).values_list("id", "strength")
    )

    replay = service.start_run(user=user, adventure=adventure)
    assert replay.id != primary.id
    assert replay.mode == "replay"
    assert replay.status == "started"
    # Mastery would leave nothing to serve; the replay's linear walk still does.
    assert service.current_attempt(run=replay) is not None

    served = 0
    for _ in range(500):
        if not _solve_current(service, replay):
            break
        served += 1
    replay.refresh_from_db()
    assert replay.status == "completed"
    assert served == len(ordered_quests_for(adventure))
    # Uncounted: no pass milestone, no session score, no mastery progress.
    assert replay.passed_at is None
    assert replay.session_score == 0
    assert replay.mastery_progress_gained == 0.0
    # Replay never writes mastery rows.
    mastery_after = dict(
        AdventureMastery.objects.filter(user=user).values_list("id", "strength")
    )
    assert mastery_after == mastery_before


def test_terminal_run_does_not_block_a_replay(db, django_user_model):
    """A terminal (abandoned/completed) run never blocks a new one; resume only
    applies to an in-progress run."""
    call_command("seed_curriculum_v2")
    user = make_user(django_user_model)
    adventure = _adventure_with_quests()
    service = AdventureRunService()

    first = service.start_run(user=user, adventure=adventure)
    service.abandon(run=first)
    first.refresh_from_db()
    assert first.status == "abandoned"

    replay = service.start_run(user=user, adventure=adventure)
    assert replay.id != first.id
    assert replay.status == "started"


# ---- HTTP integration -----------------------------------------------------

def test_adventure_run_http_flow_solves_a_quest(db, django_user_model):
    from rest_framework.test import APIClient

    call_command("seed_curriculum_v2")
    user = make_user(django_user_model, "httpadv")
    adventure = _adventure_with_quests()
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
    # Drive the authored solution for the first quest's selected variant.
    from adventures.models import AdventureQuestAttempt

    attempt_obj = AdventureQuestAttempt.objects.get(id=attempt["id"])
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


def test_objective_checklist_ticks_off_as_state_reaches_target(db, django_user_model):
    """The adventure brief exposes a live objective checklist; each check flips to
    satisfied once the repository state meets its server-side requirement."""
    from adventures.serializers import attempt_payload

    call_command("seed_curriculum_v2")
    user = make_user(django_user_model, "checklist")
    adventure = _adventure_with_quests()
    service = AdventureRunService()
    run = service.start_run(user=user, adventure=adventure)
    attempt = service.current_attempt(run=run)

    payload = attempt_payload(attempt)
    checks = payload["objective_checks"]
    assert checks, "adventure attempt should expose an objective checklist"
    assert all({"label", "satisfied"} <= set(check) for check in checks)
    # The checklist is a dedicated payload field; the scenario brief stays pure.
    assert "objective" not in payload["scenario_context"]

    # The build step guarantees the solution's target state satisfies every
    # authored check, so the checklist reads all-green at the target state.
    attempt.repository_state = attempt.selected_variant.target_state
    attempt.save(update_fields=["repository_state"])
    solved_checks = attempt_payload(attempt)["objective_checks"]
    assert solved_checks and all(check["satisfied"] for check in solved_checks)


def test_use_hint_endpoint_increments_hint_count(db, django_user_model):
    from rest_framework.test import APIClient

    call_command("seed_curriculum_v2")
    user = make_user(django_user_model, "hinter")
    adventure = _adventure_with_quests()
    client = APIClient()
    client.force_authenticate(user=user)

    run_id = client.post(f"/api/command-adventures/{adventure.slug}/runs/").json()["id"]
    resp = client.post(f"/api/adventure-runs/{run_id}/use-hint/")
    assert resp.status_code == 200
    body = resp.json()
    assert body["run"]["current_attempt"]["counts"]["hint_count"] == 1
    assert body["hint_number"] == 1
    assert isinstance(body["hint"], str) and body["hint"]


def test_workspace_file_endpoint_creates_and_edits_files(db, django_user_model):
    from rest_framework.test import APIClient

    call_command("seed_curriculum_v2")
    user = make_user(django_user_model, "filer")
    adventure = _adventure_with_quests()
    client = APIClient()
    client.force_authenticate(user=user)

    run_id = client.post(f"/api/command-adventures/{adventure.slug}/runs/").json()["id"]

    created = client.post(
        f"/api/adventure-runs/{run_id}/files/",
        {"path": "notes/todo.txt", "content": "first draft"},
        format="json",
    )
    assert created.status_code == 200
    working_tree = created.json()["current_attempt"]["repository_state"]["working_tree"]
    assert working_tree["notes/todo.txt"]["content"] == "first draft"

    edited = client.patch(
        f"/api/adventure-runs/{run_id}/files/",
        {"path": "notes/todo.txt", "content": "second draft"},
        format="json",
    )
    assert edited.status_code == 200
    working_tree = edited.json()["current_attempt"]["repository_state"]["working_tree"]
    assert working_tree["notes/todo.txt"]["content"] == "second draft"

    duplicate = client.post(
        f"/api/adventure-runs/{run_id}/files/",
        {"path": "notes/todo.txt", "content": ""},
        format="json",
    )
    assert duplicate.status_code == 400


def test_authored_hint_set_is_served_in_order(db, django_user_model):
    from adventures.services import AdventureRunService

    call_command("seed_curriculum_v2")
    user = make_user(django_user_model, "authoredhints")
    adventure = _adventure_with_quests()
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


def test_submit_returns_step_and_run_payload_carries_terminal_history(db, django_user_model):
    """The submit response returns the persisted step (symmetric to challenges)
    and the run detail payload carries the live attempt's terminal history, so
    the frontend can render an optimistic placeholder and rehydrate on refresh."""
    from rest_framework.test import APIClient

    call_command("seed_curriculum_v2")
    user = make_user(django_user_model, "stephistory")
    adventure = _adventure_with_quests()
    client = APIClient()
    client.force_authenticate(user=user)

    start = client.post(f"/api/command-adventures/{adventure.slug}/runs/")
    run_id = start.json()["id"]
    # A fresh attempt has no terminal history yet.
    assert start.json()["current_attempt"]["steps"] == []

    # A diagnostic command keeps the attempt in progress (not solved / not over
    # budget), so the same attempt accumulates the step.
    resp = client.post(
        f"/api/adventure-runs/{run_id}/submit-command/",
        {"command": "git status"},
        format="json",
    )
    assert resp.status_code == 200
    step = resp.json()["step"]
    assert {"id", "command_text", "terminal_output", "result_category"} <= set(step)
    assert step["command_text"] == "git status"

    detail = client.get(f"/api/adventure-runs/{run_id}/")
    steps = detail.json()["current_attempt"]["steps"]
    assert [s["command_text"] for s in steps] == ["git status"]
    assert steps[0]["id"] == step["id"]
