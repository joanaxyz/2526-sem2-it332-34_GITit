from common.constants import SESSION_STATUS_COMPLETED, SESSION_STATUS_FAILED
from progress.models import ChallengeTrialCompletion, CoinTransaction
from testing.frontend_execution import frontend_execution_payload
from testing.runtime_factories import api_client_for, create_stage_readme_challenge_run


def _submit(*, fixture, command: str, next_state: dict, processed: bool = True, output: str | None = None):
    return api_client_for(fixture.user).post(
        f"/api/challenge-runs/{fixture.run.id}/submit-command/",
        {
            "command": command,
            "execution": frontend_execution_payload(
                command,
                next_state,
                processed=processed,
                output=output or ("ok" if processed else "git: invalid command"),
                exit_code=0 if processed else 129,
                client_run_revision=fixture.run.total_attempts,
            ),
        },
        format="json",
    )


def test_challenge_budget_exhaustion_fails_without_completion_or_reward(db, django_user_model):
    fixture = create_stage_readme_challenge_run(
        django_user_model,
        username="challenge-budget-fail",
        reward_coins=25,
    )
    fixture.run.counted_action_total = fixture.run.max_counted_commands - 1
    fixture.run.total_attempts = fixture.run.counted_action_total
    fixture.run.save(update_fields=["counted_action_total", "total_attempts"])

    response = _submit(
        fixture=fixture,
        command="git nope",
        next_state=fixture.run.repository_state,
        processed=False,
        output="git: 'nope' is not a git command.",
    )

    assert response.status_code == 200
    fixture.run.refresh_from_db()
    assert fixture.run.status == SESSION_STATUS_FAILED
    assert fixture.run.failure_reason == "You ran out of counted commands before reaching the target repository state."
    assert not ChallengeTrialCompletion.objects.filter(challenge_run=fixture.run).exists()
    assert not CoinTransaction.objects.filter(player=fixture.player, award_key=f"trial-reward:{fixture.trial.id}").exists()


def test_challenge_can_complete_on_last_allowed_counted_command(db, django_user_model):
    fixture = create_stage_readme_challenge_run(
        django_user_model,
        username="challenge-last-command",
        reward_coins=25,
    )
    fixture.run.counted_action_total = fixture.run.max_counted_commands - 1
    fixture.run.total_attempts = fixture.run.counted_action_total
    fixture.run.save(update_fields=["counted_action_total", "total_attempts"])

    response = _submit(
        fixture=fixture,
        command="git add README.md",
        next_state=fixture.states.target,
    )

    assert response.status_code == 200
    fixture.run.refresh_from_db()
    assert fixture.run.status == SESSION_STATUS_COMPLETED
    assert ChallengeTrialCompletion.objects.filter(challenge_run=fixture.run).exists()
    assert CoinTransaction.objects.filter(player=fixture.player, award_key=f"trial-reward:{fixture.trial.id}").count() == 1
