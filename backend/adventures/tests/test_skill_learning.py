from types import SimpleNamespace

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from adventures.models import (
    AdventureLevel,
    AdventureLevelTier,
    AdventureLevelTierWave,
    AdventureLevelTierWaveVariant,
    AdventureWave,
    AdventureWaveVariant,
    SkillMastery,
)
from adventures.services import AdventureLevelTierRunService, AdventureRunService
from adventures.services.skill_learning import learn_from_command
from curriculum.models import Chapter, CommandForm, CommandSkill, Story
from curriculum.selectors.command_skills import learned_command_skills
from players.services import get_or_create_player
from testing.frontend_execution import frontend_execution_payload


@pytest.fixture
def learner(db, django_user_model):
    return get_or_create_player(django_user_model.objects.create_user(username="skill-learner"))


def form(command, usage=None, slug="basic", **kwargs):
    skill, _ = CommandSkill.objects.get_or_create(
        slug=command.replace(" ", "-"), defaults={"base_command": command, "title": command}
    )
    return CommandForm.objects.create(
        command_skill=skill, slug=slug, usage_form=usage or command, label=command, **kwargs
    )


def result(command, *, processed=True, exit_code=0):
    return SimpleNamespace(normalized_command=command, processed=processed, exit_code=exit_code)


@pytest.mark.parametrize("processed,exit_code", [(False, 0), (False, 129), (True, 1)])
def test_failed_or_unprocessed_command_does_not_teach(learner, processed, exit_code):
    form("git add", "git add <file>")
    assert (
        learn_from_command(
            player=learner,
            result=result("git add readme.md", processed=processed, exit_code=exit_code),
        )
        == []
    )
    assert not SkillMastery.objects.filter(player=learner).exists()


def test_success_teaches_only_exercised_forms_and_notifies_once_per_skill(learner):
    single = form("git add", "git add <file>")
    multiple = form("git add", "git add <path>...", slug="multiple")
    all_files = form("git add", "git add -A", slug="all")
    unused = form("git commit", "git commit -m <message>")

    learned = learn_from_command(player=learner, result=result("git add readme.md"))
    assert [skill["id"] for skill in learned] == [single.command_skill_id]
    row = SkillMastery.objects.get(player=learner, command_form=single)
    assert row.learned_at is not None
    assert row.solves == 0 and row.mastered is False
    first_learned_at = row.learned_at
    assert SkillMastery.objects.get(player=learner, command_form=multiple).learned_at is not None
    assert not SkillMastery.objects.filter(
        player=learner, command_form__in=[all_files, unused]
    ).exists()

    assert learn_from_command(player=learner, result=result("git add readme.md")) == []
    row.refresh_from_db()
    assert row.learned_at == first_learned_at
    assert learn_from_command(player=learner, result=result("git add --all")) == []
    assert SkillMastery.objects.get(player=learner, command_form=all_files).learned_at is not None
    assert len(learned_command_skills(player=learner)) == 1


def test_single_path_use_teaches_a_catalog_authored_with_one_or_more_paths(learner):
    add = form("git add", "git add <path>...")
    learned = learn_from_command(player=learner, result=result("git add src/auth/"))
    assert [skill["id"] for skill in learned] == [add.command_skill_id]
    assert SkillMastery.objects.get(player=learner, command_form=add).solves == 0


def test_unpublished_or_unplayable_forms_do_not_teach(learner):
    form("git status", is_published=False)
    form("git status", slug="reference", is_playable=False)
    assert learn_from_command(player=learner, result=result("git status")) == []
    assert learned_command_skills(player=learner) == []


@pytest.mark.parametrize("lane", ["adventure", "tier"])
def test_verified_command_teaches_before_completion_and_survives_discard(learner, lane):
    story = Story.objects.create(slug="learning-story", title="Learning")
    chapter = Chapter.objects.create(story=story, slug="learning", number=1, title="Learning")
    status_form = form("git status", chapter=chapter)
    commit_form = form("git commit", "git commit -m <message>", chapter=chapter)
    level = AdventureLevel.objects.create(chapter=chapter, slug="learning", title="Learning")
    level.command_forms.add(status_form, commit_form)
    initial_state = {
        "repository_initialized": True,
        "commits": [],
        "branches": {"main": None},
        "head": {"type": "branch", "name": "main"},
        "working_tree": {},
        "staging": {},
    }
    variant_fields = {
        "slug": "learning",
        "initial_state": initial_state,
        "evaluation_spec": {
            "state_requirements": {"rules": [{"type": "commit_count_equals", "count": 1}]},
            "completion_policy": {"mode": "rules"},
        },
        "solution_commands": ['git commit -m "First"'],
    }
    if lane == "adventure":
        wave = AdventureWave.objects.create(level=level, slug="learning")
        AdventureWaveVariant.objects.create(wave=wave, **variant_fields)
        run_service = AdventureRunService()
        run = run_service.start_run(player=learner, level=level)
        endpoint = f"/api/adventure-runs/{run.id}/submit-command/"
    else:
        tier = AdventureLevelTier.objects.create(adventure_level=level, difficulty="easy")
        wave = AdventureLevelTierWave.objects.create(tier=tier, slug="learning")
        AdventureLevelTierWaveVariant.objects.create(wave=wave, **variant_fields)
        run_service = AdventureLevelTierRunService()
        run = run_service.start_run(player=learner, tier=tier, source_entry_point="level_page")
        endpoint = f"/api/adventure-tier-runs/{run.id}/submit-command/"
    wave.command_forms.add(status_form, commit_form)
    client = APIClient()
    client.force_authenticate(user=learner.user)

    failed = client.post(
        endpoint,
        {
            "command": 'git commit -m "First"',
            "execution": frontend_execution_payload(
                'git commit -m "First"',
                run.repository_state,
                processed=False,
                exit_code=1,
                client_run_revision=0,
            ),
        },
        format="json",
    )
    assert failed.status_code == 200, failed.data
    assert failed.data["learned_skills"] == []
    assert not SkillMastery.objects.filter(player=learner).exists()

    response = client.post(
        endpoint,
        {
            "command": "git status",
            "execution": frontend_execution_payload(
                "git status",
                run.repository_state,
                diagnostic=True,
                client_run_revision=1,
                diagnostic_metadata=["inspected_status"],
            ),
        },
        format="json",
    )
    assert response.status_code == 200, response.data
    assert response.data["run"]["status"] == "started"
    assert response.data["learned_skills"][0]["id"] == status_form.command_skill_id
    assert response.data["command_outcome"]["solved"] is False
    row = SkillMastery.objects.get(player=learner, command_form=status_form)
    assert row.learned_at is not None and row.solves == 0
    assert not SkillMastery.objects.filter(player=learner, command_form=commit_form).exists()

    repeat = client.post(
        endpoint,
        {
            "command": "git status",
            "execution": frontend_execution_payload(
                "git status",
                run.repository_state,
                diagnostic=True,
                client_run_revision=2,
                diagnostic_metadata=["inspected_status"],
            ),
        },
        format="json",
    )
    assert repeat.status_code == 200, repeat.data
    assert repeat.data["learned_skills"] == []

    # A failed/abandoned run cannot revoke already demonstrated command use.
    run.refresh_from_db()
    run_service.discard(run=run)
    assert [skill["id"] for skill in learned_command_skills(player=learner)] == [
        status_form.command_skill_id
    ]


def test_completion_without_command_use_cannot_populate_spellbook(learner):
    story = Story.objects.create(slug="completion-story", title="Completion")
    chapter = Chapter.objects.create(story=story, slug="completion", number=1, title="Completion")
    unused = form("git status", chapter=chapter)
    level = AdventureLevel.objects.create(chapter=chapter, slug="completion", title="Completion")
    level.command_forms.add(unused)
    wave = AdventureWave.objects.create(level=level, slug="completion")
    wave.command_forms.add(unused)
    AdventureWaveVariant.objects.create(wave=wave, slug="completion")
    service = AdventureRunService()
    run = service.start_run(player=learner, level=level)
    run.passed_at = timezone.now()
    run.save(update_fields=["passed_at"])
    service._credit_mastery(player=learner, level=level)

    assert learned_command_skills(player=learner) == []
    assert SkillMastery.objects.get(player=learner, command_form=unused).solves == 1
