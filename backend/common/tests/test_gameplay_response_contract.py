from __future__ import annotations

from adventures.models import AdventureRun, AdventureWave, AdventureWaveVariant
from adventures.openapi import (
    AdventureCommandResponseSerializer,
    AdventureRunResponseSerializer,
)
from challenges.models import ChallengeRun
from challenges.openapi import (
    ChallengeCommandResponseSerializer,
    ChallengeRunResponseSerializer,
)
from practice.models import CommandStep
from progress.models import (
    AdventureLevelCompletion,
    ChallengeLevelCompletion,
    ChallengeTrialCompletion,
    CoinTransaction,
    Wallet,
)
from shop.models import Entitlement
from testing.frontend_execution import diagnostic_payload, frontend_execution_payload
from testing.runtime_factories import (
    api_client_for,
    create_stage_readme_adventure_run,
    create_stage_readme_challenge_run,
)

ADVENTURE_RUN_KEYS = {
    "battle_stage",
    "chapter_id",
    "completed_at",
    "current_attempt",
    "current_level_index",
    "current_wave",
    "id",
    "is_passed",
    "library_opened",
    "mastery",
    "next_level",
    "passed",
    "progress",
    "replay",
    "results",
    "selected_level",
    "stars",
    "status",
    "story",
    "total_levels",
    "total_waves",
}
ADVENTURE_COMMAND_KEYS = {
    "command_classification",
    "command_outcome",
    "exit_code",
    "run",
    "solved",
    "stderr",
    "stdout",
    "step",
    "terminal_output",
}
ADVENTURE_STEP_KEYS = {"command_text", "id", "result_category", "terminal_output"}
CHALLENGE_RUN_KEYS = {
    "battle_stage",
    "challenge",
    "chapter",
    "completed_at",
    "completion",
    "counts",
    "difficulty",
    "expected_state",
    "failure_reason",
    "id",
    "mastery_progress",
    "next_difficulty",
    "policy",
    "replay",
    "repository_state",
    "reward_coins",
    "scaffolding",
    "scenario_context",
    "sibling_levels",
    "stars",
    "status",
    "steps",
    "story",
    "variant",
    "visualization",
}
CHALLENGE_COMMAND_KEYS = {
    "command_family",
    "command_outcome",
    "diagnostic_metadata",
    "exit_code",
    "run",
    "stderr",
    "stdout",
    "step",
}
CHALLENGE_COMMAND_BASE_RUN_KEYS = {
    "completed_at",
    "counts",
    "failure_reason",
    "id",
    "replay",
    "repository_state",
    "stars",
    "status",
    "visualization",
}
CHALLENGE_TRANSITION_RUN_KEYS = {
    "completion",
    "mastery_progress",
    "next_difficulty",
    "sibling_levels",
}
CHALLENGE_COMMAND_STEP_KEYS = {
    "command_classification",
    "command_text",
    "contextual_feedback",
    "created_at",
    "evaluation_result",
    "id",
    "result_category",
    "terminal_output",
    "visualization_snapshot",
}


def _grant_gameplay_access(fixture) -> None:
    Entitlement.objects.get_or_create(
        player=fixture.player,
        kind="companion",
        slug="blue",
    )
    Entitlement.objects.get_or_create(
        player=fixture.player,
        kind="story",
        slug=fixture.story.slug,
    )


def _assert_valid(serializer_class, payload: dict) -> None:
    serializer = serializer_class(data=payload)
    assert serializer.is_valid(), serializer.errors


def _wallet_balance(player) -> int:
    balance = Wallet.objects.filter(player=player).values_list("balance", flat=True).first()
    return balance if balance is not None else 0


def _adventure_state(fixture) -> dict:
    fixture.run.refresh_from_db()
    return {
        "status": fixture.run.status,
        "command_count": fixture.run.command_count,
        "counted_command_count": fixture.run.counted_command_count,
        "current_wave_id": fixture.run.current_wave_id,
        "repository_state": fixture.run.repository_state,
        "step_count": CommandStep.objects.filter(attempt=fixture.run).count(),
        "level_completion_count": AdventureLevelCompletion.objects.filter(
            adventure_run=fixture.run
        ).count(),
        "coin_transaction_count": CoinTransaction.objects.filter(player=fixture.player).count(),
        "wallet_balance": _wallet_balance(fixture.player),
        "run_wave_statuses": list(fixture.run.run_waves.values_list("status", flat=True)),
    }


def _challenge_state(fixture) -> dict:
    fixture.run.refresh_from_db()
    return {
        "status": fixture.run.status,
        "counted_action_total": fixture.run.counted_action_total,
        "non_counted_diagnostic_total": fixture.run.non_counted_diagnostic_total,
        "total_attempts": fixture.run.total_attempts,
        "repository_state": fixture.run.repository_state,
        "step_count": CommandStep.objects.filter(challenge_run=fixture.run).count(),
        "trial_completion_count": ChallengeTrialCompletion.objects.filter(
            challenge_run=fixture.run
        ).count(),
        "level_completion_count": ChallengeLevelCompletion.objects.filter(
            player=fixture.player,
            challenge_level=fixture.level,
        ).count(),
        "coin_transaction_count": CoinTransaction.objects.filter(player=fixture.player).count(),
        "wallet_balance": _wallet_balance(fixture.player),
    }


def _assert_adventure_command_shape(payload: dict, run_keys: set[str]) -> None:
    assert set(payload) == ADVENTURE_COMMAND_KEYS
    assert set(payload["run"]) == run_keys
    assert set(payload["step"]) == ADVENTURE_STEP_KEYS


def _submit_adventure_command(fixture, *, diagnostic: bool = False):
    command = "git status" if diagnostic else "git add README.md"
    execution = (
        diagnostic_payload(command, fixture.states.initial, output="status clean")
        if diagnostic
        else frontend_execution_payload(command, fixture.states.target)
    )
    execution["client_run_revision"] = 0
    return api_client_for(fixture.user).post(
        f"/api/adventure-runs/{fixture.run.id}/submit-command/",
        {"command": command, "execution": execution},
        format="json",
    )


def _submit_challenge_command(fixture, *, diagnostic: bool = False):
    command = "git status" if diagnostic else "git add README.md"
    execution = (
        diagnostic_payload(command, fixture.states.initial, output="status clean")
        if diagnostic
        else frontend_execution_payload(command, fixture.states.target)
    )
    execution["client_run_revision"] = 0
    return api_client_for(fixture.user).post(
        f"/api/challenge-runs/{fixture.run.id}/submit-command/",
        {"command": command, "execution": execution},
        format="json",
    )


def test_adventure_full_success_endpoints_match_the_domain_schema(db, django_user_model):
    fixture = create_stage_readme_adventure_run(
        django_user_model,
        username="adventure-response-full",
    )
    _grant_gameplay_access(fixture)
    fixture.run.delete()
    client = api_client_for(fixture.user)

    start = client.post(f"/api/adventure-levels/{fixture.level.id}/runs/", format="json")
    assert start.status_code == 201
    run_id = start.json()["id"]
    detail = client.get(f"/api/adventure-runs/{run_id}/")
    workspace = client.post(
        f"/api/adventure-runs/{run_id}/files/",
        {"path": "NOTES.md", "content": "response contract"},
        format="json",
    )

    for response in (start, detail, workspace):
        assert set(response.json()) == ADVENTURE_RUN_KEYS
        assert response.json()["passed"] == response.json()["is_passed"]
        _assert_valid(AdventureRunResponseSerializer, response.json())
    assert "NOTES.md" in AdventureRun.objects.get(id=run_id).repository_state["working_tree"]


def test_adventure_command_response_validates_partial_and_full_branches(db, django_user_model):
    partial = create_stage_readme_adventure_run(
        django_user_model,
        username="adventure-response-partial",
    )
    assert _adventure_state(partial) == {
        "status": "started",
        "command_count": 0,
        "counted_command_count": 0,
        "current_wave_id": partial.wave.id,
        "repository_state": partial.states.initial,
        "step_count": 0,
        "level_completion_count": 0,
        "coin_transaction_count": 0,
        "wallet_balance": 0,
        "run_wave_statuses": ["started"],
    }
    partial_response = _submit_adventure_command(partial, diagnostic=True)
    partial_payload = partial_response.json()

    assert partial_response.status_code == 200
    _assert_adventure_command_shape(partial_payload, {"partial", "id", "status", "current_attempt"})
    assert partial_payload["run"]["partial"] is True
    assert isinstance(partial_payload["run"]["current_attempt"], dict)
    _assert_valid(AdventureCommandResponseSerializer, partial_payload)
    assert _adventure_state(partial) == {
        "status": "started",
        "command_count": 1,
        "counted_command_count": 0,
        "current_wave_id": partial.wave.id,
        "repository_state": partial.states.initial,
        "step_count": 1,
        "level_completion_count": 0,
        "coin_transaction_count": 0,
        "wallet_balance": 0,
        "run_wave_statuses": ["started"],
    }

    transition = create_stage_readme_adventure_run(
        django_user_model,
        username="adventure-response-transition",
    )
    next_wave = AdventureWave.objects.create(
        level=transition.level,
        slug="response-contract-second-wave",
        title="Second Wave",
        sort_order=1,
        min_counted_commands=1,
        max_counted_commands=3,
        is_published=True,
    )
    AdventureWaveVariant.objects.create(
        wave=next_wave,
        slug="response-contract-second-variant",
        label="Second Variant",
        initial_state=transition.states.initial,
        target_state=transition.states.target,
        evaluation_spec={"completion_policy": {"mode": "state_hash"}},
        solution_commands=["git add README.md"],
        semantic_key="response-contract-second-wave",
        is_published=True,
    )
    assert _adventure_state(transition) == {
        "status": "started",
        "command_count": 0,
        "counted_command_count": 0,
        "current_wave_id": transition.wave.id,
        "repository_state": transition.states.initial,
        "step_count": 0,
        "level_completion_count": 0,
        "coin_transaction_count": 0,
        "wallet_balance": 0,
        "run_wave_statuses": ["started"],
    }
    transition_response = _submit_adventure_command(transition)
    transition_payload = transition_response.json()

    assert transition_response.status_code == 200
    _assert_adventure_command_shape(transition_payload, ADVENTURE_RUN_KEYS)
    assert "partial" not in transition_payload["run"]
    _assert_valid(AdventureCommandResponseSerializer, transition_payload)
    assert _adventure_state(transition) == {
        "status": "started",
        "command_count": 0,
        "counted_command_count": 0,
        "current_wave_id": next_wave.id,
        "repository_state": transition.states.initial,
        "step_count": 1,
        "level_completion_count": 0,
        "coin_transaction_count": 0,
        "wallet_balance": 0,
        "run_wave_statuses": ["completed", "started"],
    }

    terminal = create_stage_readme_adventure_run(
        django_user_model,
        username="adventure-response-terminal",
        reward_coins=7,
    )
    assert _adventure_state(terminal) == {
        "status": "started",
        "command_count": 0,
        "counted_command_count": 0,
        "current_wave_id": terminal.wave.id,
        "repository_state": terminal.states.initial,
        "step_count": 0,
        "level_completion_count": 0,
        "coin_transaction_count": 0,
        "wallet_balance": 0,
        "run_wave_statuses": ["started"],
    }
    terminal_response = _submit_adventure_command(terminal)
    terminal_payload = terminal_response.json()

    assert terminal_response.status_code == 200
    _assert_adventure_command_shape(terminal_payload, ADVENTURE_RUN_KEYS)
    assert "partial" not in terminal_payload["run"]
    _assert_valid(AdventureCommandResponseSerializer, terminal_payload)
    assert _adventure_state(terminal) == {
        "status": "completed",
        "command_count": 1,
        "counted_command_count": 1,
        "current_wave_id": terminal.wave.id,
        "repository_state": terminal.states.target,
        "step_count": 1,
        "level_completion_count": 1,
        "coin_transaction_count": 5,
        "wallet_balance": 342,
        "run_wave_statuses": ["completed"],
    }


def test_challenge_full_success_endpoints_match_the_domain_schema(db, django_user_model):
    fixture = create_stage_readme_challenge_run(
        django_user_model,
        username="challenge-response-full",
    )
    _grant_gameplay_access(fixture)
    fixture.run.delete()
    client = api_client_for(fixture.user)

    start = client.post(
        f"/api/challenge-trials/{fixture.trial.id}/runs/",
        {"source_entry_point": "level_page"},
        format="json",
    )
    assert start.status_code == 201
    run_id = start.json()["id"]
    detail = client.get(f"/api/challenge-runs/{run_id}/")
    workspace = client.post(
        f"/api/challenge-runs/{run_id}/files/",
        {"path": "NOTES.md", "content": "response contract"},
        format="json",
    )
    run = ChallengeRun.objects.get(id=run_id)
    run.status = "failed"
    run.ended_at = run.started_at
    run.save(update_fields=["status", "ended_at"])
    retry = client.post(f"/api/challenge-runs/{run_id}/retry/", format="json")

    for response in (start, detail, workspace, retry):
        assert set(response.json()) == CHALLENGE_RUN_KEYS
        assert "story" in response.json()
        _assert_valid(ChallengeRunResponseSerializer, response.json())
    assert "NOTES.md" in run.repository_state["working_tree"]


def test_challenge_command_response_validates_started_and_terminal_updates(
    db,
    django_user_model,
):
    started = create_stage_readme_challenge_run(
        django_user_model,
        username="challenge-response-started",
    )
    assert _challenge_state(started) == {
        "status": "started",
        "counted_action_total": 0,
        "non_counted_diagnostic_total": 0,
        "total_attempts": 0,
        "repository_state": started.states.initial,
        "step_count": 0,
        "trial_completion_count": 0,
        "level_completion_count": 0,
        "coin_transaction_count": 0,
        "wallet_balance": 0,
    }
    started_response = _submit_challenge_command(started, diagnostic=True)
    started_payload = started_response.json()

    assert started_response.status_code == 200
    assert set(started_payload) == CHALLENGE_COMMAND_KEYS
    assert set(started_payload["run"]) == CHALLENGE_COMMAND_BASE_RUN_KEYS
    assert set(started_payload["step"]) == CHALLENGE_COMMAND_STEP_KEYS
    _assert_valid(ChallengeCommandResponseSerializer, started_payload)
    assert _challenge_state(started) == {
        "status": "started",
        "counted_action_total": 0,
        "non_counted_diagnostic_total": 1,
        "total_attempts": 1,
        "repository_state": started.states.initial,
        "step_count": 1,
        "trial_completion_count": 0,
        "level_completion_count": 0,
        "coin_transaction_count": 0,
        "wallet_balance": 0,
    }

    terminal = create_stage_readme_challenge_run(
        django_user_model,
        username="challenge-response-terminal",
        reward_coins=5,
    )
    assert _challenge_state(terminal) == {
        "status": "started",
        "counted_action_total": 0,
        "non_counted_diagnostic_total": 0,
        "total_attempts": 0,
        "repository_state": terminal.states.initial,
        "step_count": 0,
        "trial_completion_count": 0,
        "level_completion_count": 0,
        "coin_transaction_count": 0,
        "wallet_balance": 0,
    }
    terminal_response = _submit_challenge_command(terminal)
    terminal_payload = terminal_response.json()

    assert terminal_response.status_code == 200
    assert set(terminal_payload) == CHALLENGE_COMMAND_KEYS
    assert set(terminal_payload["run"]) == (
        CHALLENGE_COMMAND_BASE_RUN_KEYS | CHALLENGE_TRANSITION_RUN_KEYS
    )
    assert set(terminal_payload["step"]) == CHALLENGE_COMMAND_STEP_KEYS
    assert terminal_payload["run"]["mastery_progress"] is not None
    assert isinstance(terminal_payload["run"]["sibling_levels"], list)
    assert "completion" in terminal_payload["run"]
    assert "next_difficulty" in terminal_payload["run"]
    _assert_valid(ChallengeCommandResponseSerializer, terminal_payload)
    assert _challenge_state(terminal) == {
        "status": "completed",
        "counted_action_total": 1,
        "non_counted_diagnostic_total": 0,
        "total_attempts": 1,
        "repository_state": terminal.states.target,
        "step_count": 1,
        "trial_completion_count": 1,
        "level_completion_count": 1,
        "coin_transaction_count": 5,
        "wallet_balance": 340,
    }
