from __future__ import annotations

from copy import deepcopy

from common.constants import SESSION_STATUS_COMPLETED, SESSION_STATUS_STARTED
from practice.models import CommandStep
from progress.models import ChallengeTrialCompletion
from testing.frontend_execution import frontend_execution_payload
from testing.runtime_factories import api_client_for, create_stage_readme_challenge_run


def test_challenge_submit_rejects_forged_next_state_at_api_boundary(db, django_user_model):
    fixture = create_stage_readme_challenge_run(django_user_model, username="challenge-integrity")
    run = fixture.run
    forged = deepcopy(fixture.states.target)
    forged["commits"] = [
        {
            "id": "c0",
            "message": "forged",
            "parents": [],
            "tree": {"README.md": "hello"},
            "changes": {"README.md": {"change_type": "added", "before": None, "after": "hello"}},
            "files": {"README.md": "added"},
        }
    ]
    forged["branches"] = {"main": "c0"}
    forged["head"] = {"type": "branch", "name": "main", "target": "c0"}

    response = api_client_for(fixture.user).post(
        f"/api/challenge-runs/{run.id}/submit-command/",
        {
            "command": "git add README.md",
            "execution": frontend_execution_payload(
                "git add README.md",
                forged,
                client_run_revision=0,
            ),
        },
        format="json",
    )

    assert response.status_code == 400
    run.refresh_from_db()
    assert run.status == SESSION_STATUS_STARTED
    assert run.total_attempts == 0
    assert not CommandStep.objects.filter(challenge_run=run).exists()
    assert not ChallengeTrialCompletion.objects.filter(challenge_run=run).exists()


def test_challenge_submit_rejects_stale_client_revision_at_api_boundary(db, django_user_model):
    fixture = create_stage_readme_challenge_run(django_user_model, username="challenge-stale")
    run = fixture.run

    response = api_client_for(fixture.user).post(
        f"/api/challenge-runs/{run.id}/submit-command/",
        {
            "command": "git add README.md",
            "execution": frontend_execution_payload(
                "git add README.md",
                fixture.states.target,
                client_run_revision=1,
            ),
        },
        format="json",
    )

    assert response.status_code == 400
    run.refresh_from_db()
    assert run.status == SESSION_STATUS_STARTED
    assert run.total_attempts == 0


def test_challenge_submit_accepts_verified_transition_and_completes(db, django_user_model):
    fixture = create_stage_readme_challenge_run(django_user_model, username="challenge-valid")
    run = fixture.run

    response = api_client_for(fixture.user).post(
        f"/api/challenge-runs/{run.id}/submit-command/",
        {
            "command": "git add README.md",
            "execution": frontend_execution_payload(
                "git add README.md",
                fixture.states.target,
                client_run_revision=0,
            ),
        },
        format="json",
    )

    assert response.status_code == 200
    run.refresh_from_db()
    assert run.status == SESSION_STATUS_COMPLETED
    assert run.total_attempts == 1
    assert ChallengeTrialCompletion.objects.filter(challenge_run=run).exists()
