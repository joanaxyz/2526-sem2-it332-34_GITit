from copy import deepcopy

import pytest
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.core.management.base import CommandError

from progress.services.references import ref_hash, valid_ref, validate_refs
from testing.kpi_fixtures import bundle, routes


@pytest.mark.django_db
def test_reservation_batch_must_leave_ordinary_practice(django_user_model):
    _, _, _, variants = bundle(django_user_model)
    with pytest.raises(CommandError, match="ordinary practice"):
        call_command(
            "kpi_refs", cases=[v.slug for v in variants], reserve=True, reason="Reviewed difference"
        )
    variants[0].refresh_from_db()
    assert not variants[0].is_transfer


@pytest.mark.django_db
def test_diagnostic_assessment_uses_one_shared_reference_policy(django_user_model, monkeypatch):
    _, _, _, variants = bundle(django_user_model)
    variant = variants[0]
    state = routes()[2]["practice"]["steps"][1]["ready"]
    variant.initial_state = variant.target_state = state
    variant.solution_commands = ["git status"]
    variant.save()
    key = str(variant.id)
    replay = {"steps": [{"command": "git status", "diagnostic": True}], "final": state}
    monkeypatch.setattr(
        "progress.services.references.replay_solutions", lambda cases: ({key: state}, {key: replay})
    )
    with pytest.raises(ValidationError, match="no counted commands"):
        validate_refs([variant])
    assert validate_refs([variant], allow_unscored=True) == {}
    variant.assess_diag = True
    assert validate_refs([variant]) == {variant.id: 1}


@pytest.mark.django_db
def test_real_solution_replay_validates_reference_independently_of_star_budget(django_user_model):
    _, _, scenario, variants = bundle(django_user_model)
    scenario.min_counted_commands = 7
    scenario.save()
    assert validate_refs(variants) == {v.id: 3 for v in variants}
    assert valid_ref(variants[0]) == 3
    variants[0].solution_commands = ["git status"]
    assert valid_ref(variants[0]) is None


@pytest.mark.django_db
def test_processable_but_unsolved_reference_is_rejected(django_user_model, monkeypatch):
    _, _, _, variants = bundle(django_user_model)
    variant = variants[0]
    _, _, replays = routes()
    wrong = deepcopy(replays["practice"])
    wrong["final"] = wrong["steps"][0]["ready"]
    monkeypatch.setattr(
        "progress.services.references.replay_solutions",
        lambda cases: (
            {str(variant.id): wrong["final"]},
            {str(variant.id): wrong},
        ),
    )
    with pytest.raises(ValidationError, match="does not solve"):
        validate_refs([variant])


@pytest.mark.django_db
def test_reference_hash_covers_goal_workspace_and_diagnostic_policy(django_user_model):
    _, _, _, variants = bundle(django_user_model)
    variant = variants[0]
    original = ref_hash(variant)
    variant.assess_diag = True
    assert ref_hash(variant) != original
    variant.assess_diag = False
    variant.solution_workspace_files = [{"path": "note.txt", "content": "changed"}]
    assert ref_hash(variant) != original
