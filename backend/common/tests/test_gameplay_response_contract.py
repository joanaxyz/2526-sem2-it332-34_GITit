from __future__ import annotations

from adventures.models import AdventureLevel, AdventureLevelTierRun
from adventures.openapi import (
    AdventureLevelTierCommandResponseSerializer,
    AdventureLevelTierRunResponseSerializer,
)
from adventures.tier_payloads import tier_run_payload
from challenges.models import ChallengeRun
from challenges.openapi import (
    ChallengeCommandResponseSerializer,
    ChallengeRunResponseSerializer,
)
from practice.models import CommandStep
from progress.models import (
    ChallengeLevelCompletion,
    ChallengeTrialCompletion,
    CoinTransaction,
    Wallet,
)
from shop.models import Entitlement
from testing.frontend_execution import diagnostic_payload, frontend_execution_payload
from testing.runtime_factories import (
    api_client_for,
    create_stage_readme_challenge_run,
    create_stage_readme_tier_run,
)

CHALLENGE_RUN_KEYS = {
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
    "star_breakdown",
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
    "star_breakdown",
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


def _submit_tier_command(fixture, *, diagnostic: bool = False):
    command = "git status" if diagnostic else "git add README.md"
    execution = (
        diagnostic_payload(command, fixture.states.initial, output="status clean")
        if diagnostic
        else frontend_execution_payload(command, fixture.states.target)
    )
    execution["client_run_revision"] = 0
    return api_client_for(fixture.user).post(
        f"/api/adventure-tier-runs/{fixture.run.id}/submit-command/",
        {"command": command, "execution": execution},
        format="json",
    )


def test_result_level_number_matches_published_chapter_order(db, django_user_model):
    fixture = create_stage_readme_tier_run(django_user_model, username="result-level-number")
    fixture.level.sort_order = 5
    fixture.level.save(update_fields=["sort_order"])
    for slug, sort_order, published in (
        ("earlier", 1, True),
        ("draft", 2, False),
        ("later-tie", 5, True),
        ("later", 8, True),
    ):
        AdventureLevel.objects.create(
            chapter=fixture.chapter,
            slug=slug,
            title=slug,
            sort_order=sort_order,
            is_published=published,
        )
    # Later IDs at the same sort order follow this level on the map.
    fixture.chapter.adventure_levels.filter(slug="earlier").update(sort_order=5)

    tier = tier_run_payload(fixture.run)["tier"]
    assert tier["adventure_level_number"] == 1
    assert tier["adventure_level_title"] == fixture.level.title

    fixture.chapter.adventure_levels.filter(slug="earlier").update(sort_order=1)
    assert tier_run_payload(fixture.run)["tier"]["adventure_level_number"] == 2


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


def test_adventure_tier_full_success_endpoints_match_the_domain_schema(db, django_user_model):
    fixture = create_stage_readme_tier_run(django_user_model, username="tier-response-full")
    _grant_gameplay_access(fixture)
    fixture.run.delete()
    client = api_client_for(fixture.user)

    start = client.post(
        f"/api/adventure-level-tiers/{fixture.tier.id}/runs/",
        {"source_entry_point": "level_page"},
        format="json",
    )
    assert start.status_code == 201
    run_id = start.json()["id"]
    detail = client.get(f"/api/adventure-tier-runs/{run_id}/")
    workspace = client.post(
        f"/api/adventure-tier-runs/{run_id}/files/",
        {"path": "NOTES.md", "content": "response contract"},
        format="json",
    )

    for response in (start, detail, workspace):
        _assert_valid(AdventureLevelTierRunResponseSerializer, response.json())
        assert response.json()["scenario"] == {"index": 1, "total": 1, "title": "Stage README"}
        assert response.json()["reward"] == {"coins": 25, "claimed": False}
        # The outcome modal names the level as the story map numbers it.
        assert response.json()["tier"]["adventure_level_number"] == 1
    run = AdventureLevelTierRun.objects.get(id=run_id)
    assert "NOTES.md" in run.repository_state["working_tree"]


def test_adventure_tier_command_response_validates_started_and_terminal_updates(
    db, django_user_model
):
    started = create_stage_readme_tier_run(django_user_model, username="tier-response-started")
    started_response = _submit_tier_command(started, diagnostic=True)
    started_payload = started_response.json()

    assert started_response.status_code == 200
    _assert_valid(AdventureLevelTierCommandResponseSerializer, started_payload)
    assert started_payload["run"]["status"] == "started"
    assert "progress" not in started_payload["run"]
    assert CommandStep.objects.filter(adventure_tier_run=started.run).count() == 1

    terminal = create_stage_readme_tier_run(django_user_model, username="tier-response-terminal")
    terminal_response = _submit_tier_command(terminal)
    terminal_payload = terminal_response.json()

    assert terminal_response.status_code == 200
    _assert_valid(AdventureLevelTierCommandResponseSerializer, terminal_payload)
    assert terminal_payload["run"]["status"] == "completed"
    assert terminal_payload["run"]["progress"] == {
        "completed": 1,
        "total": 1,
        "cleared": True,
        "next_scenario": None,
    }
    assert terminal_payload["run"]["rewards"]["coins_awarded"] == 25
    assert (
        CoinTransaction.objects.filter(
            player=terminal.player, award_key=f"adventure-level-reward:{terminal.level.id}"
        ).count()
        == 1
    )


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
