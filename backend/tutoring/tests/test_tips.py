from rest_framework.test import APIClient

from tutoring.models import PlayerCommandIntroduction


def dismiss(client, key):
    return client.post("/api/tutoring/tips/dismiss/", {"key": key}, format="json")


def run_tips(client, run):
    response = client.get(f"/api/adventure-tier-runs/{run.id}/")
    assert response.status_code == 200, response.data
    return [tip["key"] for tip in response.data["tips"]]


def test_a_dismissed_tip_stays_dismissed(client, teaching_run):
    assert run_tips(client, teaching_run) == ["concept:commands", "concept:repository"]

    for _ in range(2):
        response = dismiss(client, "concept:commands")
        assert response.status_code == 200, response.data
        assert response.data == {"key": "concept:commands"}

    assert run_tips(client, teaching_run) == ["concept:repository"]
    assert PlayerCommandIntroduction.objects.get().teaching_key == "concept:commands"


def test_only_known_tips_can_be_dismissed(client, teaching_run):
    # A guide is finished by completing it, never by dismissing it as a tip.
    for key in ["concept:nonsense", "git-init/current-directory", "form:git init"]:
        assert dismiss(client, key).status_code == 400
    assert not PlayerCommandIntroduction.objects.exists()


def test_dismissing_needs_a_signed_in_player(teaching_run):
    assert dismiss(APIClient(), "concept:commands").status_code in {401, 403}
