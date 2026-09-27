import pytest

from common.exceptions import BadRequest, Conflict
from tutoring.models import PlayerCommandIntroduction
from tutoring.payloads import tutor_payload
from tutoring.services.introductions import complete_introduction, issue_token


def test_reads_do_not_complete_or_allow_question_ack(teaching_run):
    first = tutor_payload(teaching_run)
    assert first["teaching_key"] == "git-init/current-directory"
    assert first["phase"] == "introduction"
    assert first["completion_token"] is None
    assert tutor_payload(teaching_run)["context_id"] == first["context_id"]
    assert not PlayerCommandIntroduction.objects.exists()
    with pytest.raises(BadRequest):
        complete_introduction(teaching_run, issue_token(teaching_run, first["teaching_key"], "question"))
    with pytest.raises(BadRequest):
        complete_introduction(teaching_run, issue_token(teaching_run, first["teaching_key"], "feedback"))


def test_completion_survives_run_and_form_deletion(teaching_run):
    key = tutor_payload(teaching_run)["teaching_key"]
    PlayerCommandIntroduction.objects.create(player=teaching_run.player, teaching_key=key)
    teaching_run.current_wave.command_forms.all().delete()
    teaching_run.delete()
    assert PlayerCommandIntroduction.objects.get().teaching_key == key


def test_file_edits_invalidate_ack_and_ended_runs_get_no_new_lesson(teaching_run):
    token = issue_token(teaching_run, "git-init/current-directory", "feedback")
    teaching_run.repository_state["working_tree"]["new.txt"] = "new content"
    with pytest.raises(Conflict):
        complete_introduction(teaching_run, token)
    teaching_run.status = "completed"
    assert tutor_payload(teaching_run) is None
    assert not PlayerCommandIntroduction.objects.exists()


def test_identity_survives_variants_but_is_per_player(teaching_run, django_user_model):
    from adventures.models import AdventureLevelTierWaveVariant
    from players.services import get_or_create_player

    PlayerCommandIntroduction.objects.create(player=teaching_run.player, teaching_key="git-init/current-directory")
    original = teaching_run.selected_variant
    teaching_run.selected_variant = AdventureLevelTierWaveVariant.objects.create(
        wave=teaching_run.current_wave, slug="second", label="Second",
        initial_state=original.initial_state, evaluation_spec=original.evaluation_spec,
        solution_trajectory=original.solution_trajectory,
    )
    assert tutor_payload(teaching_run) is None
    teaching_run.player = get_or_create_player(django_user_model.objects.create_user(username="other"))
    assert tutor_payload(teaching_run)["teaching_key"] == "git-init/current-directory"
