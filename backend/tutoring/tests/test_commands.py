from copy import deepcopy

from adventures.models import SkillMastery
from testing.frontend_execution import frontend_execution_payload
from tutoring.models import PlayerCommandIntroduction
from tutoring.payloads import tutor_payload
from tutoring.tests.conftest import initialized_state, solution_states, staged


def submit(client, run, command, state, **kwargs):
    response = client.post(f"/api/adventure-tier-runs/{run.id}/submit-command/", {
        "command": command,
        "execution": frontend_execution_payload(command, state, client_run_revision=run.total_attempts,
                                                **kwargs),
    }, format="json")
    run.refresh_from_db()
    return response


def complete(client, run, token):
    return client.post(f"/api/adventure-tier-runs/{run.id}/introduction/complete/",
                       {"token": token}, format="json")


def test_wrong_terminal_command_reveals_and_keeps_normal_penalty(client, teaching_run):
    before = deepcopy(teaching_run.repository_state)
    response = submit(client, teaching_run, "git start", before, processed=False, exit_code=129)
    assert response.status_code == 200, response.data
    tutor = response.data["run"]["tutor"]
    assert tutor["phase"] == "feedback"
    assert tutor["verdict"] == "incorrect"
    assert tutor["example_command"] == "git init"
    assert teaching_run.repository_state == before
    assert teaching_run.total_attempts == teaching_run.counted_action_total == 1
    assert teaching_run.steps.count() == 1
    assert not SkillMastery.objects.exists()
    assert not PlayerCommandIntroduction.objects.exists()
    assert tutor_payload(teaching_run)["example_command"] == "git init"  # reload resumes
    for _ in range(2):
        result = complete(client, teaching_run, tutor["completion_token"])
        assert result.status_code == 200, result.data
        assert result.data["tutor"] is None
    keys = set(PlayerCommandIntroduction.objects.values_list("teaching_key", flat=True))
    # The guide, plus the beginner concepts it explained (never shown again).
    assert keys == {"git-init/current-directory", "concept:commands", "concept:repository"}


def test_successful_init_explains_the_change_then_introduces_the_next_form(client, teaching_run):
    response = submit(client, teaching_run, "git init", initialized_state(teaching_run.repository_state))
    assert response.status_code == 200, response.data
    tutor = response.data["run"]["tutor"]
    assert tutor["verdict"] == "correct"
    assert tutor["explanation"] == "That's the right command."
    assert tutor["changes"][0]["text"] == "The folder becomes a Git repository."
    assert tutor["changes"][0]["action"] == "create"
    result = complete(client, teaching_run, tutor["completion_token"])
    assert result.status_code == 200
    assert result.data["tutor"]["teaching_key"] == "form:git add <path>..."
    assert result.data["tutor"]["command_form"]["usage_form"] == "git add <path>..."


def at_first_add(run):
    states, _ = solution_states(run.selected_variant.initial_state)
    run.repository_state = states[1]
    run.save(update_fields=["repository_state"])
    return states


def test_same_form_on_another_route_is_praised_without_claiming_the_route(client, teaching_run):
    states = at_first_add(teaching_run)
    after = staged(staged(states[1], "app.py"), "draft.txt")
    response = submit(client, teaching_run, "git add app.py draft.txt", after)
    assert response.status_code == 200, response.data
    tutor = response.data["run"]["tutor"]
    assert tutor["verdict"] == "correct"
    assert tutor["explanation"].startswith("That worked.")
    assert {"kind": "staging", "text": "app.py and draft.txt are staged.", "action": "add",
            "subjects": ["app.py", "draft.txt"]} in tutor["changes"]


def test_the_combined_command_completes_both_steps(client, teaching_run):
    states = at_first_add(teaching_run)
    response = submit(client, teaching_run, "git add README.md app.py", states[3])
    assert response.status_code == 200, response.data
    tutor = response.data["run"]["tutor"]
    assert tutor["verdict"] == "correct"
    assert tutor["explanation"] == "That's the right command."


def test_a_miss_reveals_the_combined_command(client, teaching_run):
    at_first_add(teaching_run)
    response = submit(client, teaching_run, "git ad README.md", teaching_run.repository_state,
                      processed=False, exit_code=1)
    assert response.data["run"]["tutor"]["example_command"] == "git add README.md app.py"


def test_one_file_at_a_time_is_left_alone(client, teaching_run):
    states = at_first_add(teaching_run)
    response = submit(client, teaching_run, "git add README.md", states[2])
    assert response.status_code == 200, response.data
    # Not the technique being introduced, and the remaining single add is a
    # command the learner just used - no guide either way.
    assert response.data["run"]["tutor"] is None


def test_mutating_wrong_route_never_reveals_an_obsolete_example(client, teaching_run):
    response = submit(client, teaching_run, "git init -b wrong",
                      initialized_state(teaching_run.repository_state, branch="wrong"))
    assert response.status_code == 200, response.data
    assert response.data["run"]["tutor"] is None
    assert not PlayerCommandIntroduction.objects.exists()


def test_looking_around_is_not_a_mistake(client, teaching_run):
    response = submit(client, teaching_run, "git status", teaching_run.repository_state,
                      diagnostic=True)
    assert response.status_code == 200, response.data
    assert response.data["run"]["tutor"]["phase"] == "introduction"


def test_next_terminal_command_preserves_unacknowledged_feedback(client, teaching_run):
    response = submit(client, teaching_run, "git init", initialized_state(teaching_run.repository_state))
    old_token = response.data["run"]["tutor"]["completion_token"]
    response = submit(client, teaching_run, "git status", teaching_run.repository_state,
                      diagnostic=True)
    assert response.status_code == 200, response.data
    tutor = response.data["run"]["tutor"]
    assert tutor["teaching_key"] == "git-init/current-directory"
    assert tutor["verdict"] == "correct"
    assert complete(client, teaching_run, old_token).status_code == 409
    result = complete(client, teaching_run, tutor["completion_token"])
    assert result.status_code == 200
    assert result.data["tutor"]["teaching_key"] == "form:git add <path>..."


def test_terminal_correction_updates_pending_wrong_feedback(client, teaching_run):
    submit(client, teaching_run, "git start", teaching_run.repository_state,
           processed=False, exit_code=129)
    response = submit(client, teaching_run, "git init", initialized_state(teaching_run.repository_state))
    assert response.status_code == 200, response.data
    assert response.data["run"]["tutor"]["verdict"] == "correct"
    assert teaching_run.counted_action_total == 2


def test_forgery_is_rejected_before_command_accounting(client, teaching_run):
    teaching_run.repository_state = initialized_state(teaching_run.repository_state)
    teaching_run.save(update_fields=["repository_state"])
    state = deepcopy(teaching_run.repository_state)
    state["staging"]["invented"] = "forged"
    response = submit(client, teaching_run, "git add README.md", state)
    assert response.status_code == 400
    assert teaching_run.total_attempts == 0
    assert not teaching_run.steps.exists()


def test_ack_rejects_other_player_and_file_changes(client, teaching_run, django_user_model):
    response = submit(client, teaching_run, "git start", teaching_run.repository_state,
                      processed=False, exit_code=129)
    token = response.data["run"]["tutor"]["completion_token"]
    owner = teaching_run.player.user
    client.force_authenticate(django_user_model.objects.create_user(username="intruder"))
    assert complete(client, teaching_run, token).status_code == 404
    client.force_authenticate(owner)
    teaching_run.repository_state["working_tree"]["new.txt"] = "new"
    teaching_run.save(update_fields=["repository_state"])
    assert complete(client, teaching_run, token).status_code == 409


def test_successful_final_command_keeps_feedback_available_before_outcome(client, teaching_run):
    variant = teaching_run.selected_variant
    variant.evaluation_spec = {"state_requirements": {"repository_initialized": True},
                               "completion_policy": {"mode": "rules"}}
    variant.save()
    response = submit(client, teaching_run, "git init", initialized_state(teaching_run.repository_state))
    assert response.status_code == 200, response.data
    assert teaching_run.status == "completed"
    tutor = response.data["run"]["tutor"]
    assert tutor["verdict"] == "correct"
    result = complete(client, teaching_run, tutor["completion_token"])
    assert result.status_code == 200
    assert result.data["tutor"] is None
