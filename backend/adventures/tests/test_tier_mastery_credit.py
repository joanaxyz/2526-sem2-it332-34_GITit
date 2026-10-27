"""A cleared scenario credits only the command forms the learner actually typed.

Crediting every form attached to a level used to mark unused forms as
practised.
"""

from copy import deepcopy

from rest_framework.test import APIClient

from adventures.models import (
    AdventureLevel,
    AdventureLevelTier,
    AdventureLevelTierRun,
    AdventureLevelTierScenario,
    AdventureLevelTierScenarioVariant,
    SkillMastery,
)
from adventures.services import AdventureLevelTierRunService
from adventures.services.tier_command_processing import _processed_commands
from curriculum.models import Chapter, CommandForm, CommandSkill, Story
from players.services import get_or_create_player
from practice.models import CommandStep
from testing.frontend_execution import frontend_execution_payload

INITIAL = {
    "repository_initialized": False,
    "commits": [],
    "branches": {},
    "head": {"type": "branch", "name": "main"},
    "staging": {},
    "working_tree": {},
    "conflicts": [],
}


def _init_level(player_name: str, django_user_model):
    user = django_user_model.objects.create_user(username=player_name, password="pass12345")
    player = get_or_create_player(user)
    story = Story.objects.create(slug=f"{player_name}-story", title="Story")
    chapter = Chapter.objects.create(
        story=story, slug=f"{player_name}-chapter", number=1, title="Module 1", description=""
    )
    level = AdventureLevel.objects.create(
        chapter=chapter, slug="initializing-a-local-repository", title="Initializing"
    )
    tier = AdventureLevelTier.objects.create(adventure_level=level, difficulty="easy")
    scenario = AdventureLevelTierScenario.objects.create(
        tier=tier,
        slug="init-easy",
        min_counted_commands=1,
        max_counted_commands=12,
    )
    skill = CommandSkill.objects.create(slug="git-init", base_command="git init", title="Init")
    forms = {
        slug: CommandForm.objects.create(
            command_skill=skill, chapter=chapter, slug=slug, usage_form=usage, label=slug
        )
        for slug, usage in [
            ("current", "git init"),
            ("named", "git init <directory>"),
            ("initial-branch", "git init -b <branch> [<directory>]"),
        ]
    }
    level.command_forms.set(forms.values())
    scenario.command_forms.set(forms.values())
    AdventureLevelTierScenarioVariant.objects.create(
        scenario=scenario,
        slug="init-easy-current",
        label="Initialize the current folder",
        initial_state=INITIAL,
        evaluation_spec={
            "state_requirements": {"repository_initialized": True, "head_branch": "main"},
            "process_requirements": {"required_commands": [], "forbidden_commands": []},
            "completion_policy": {"mode": "rules"},
        },
        solution_commands=["git init"],
    )
    return user, player, tier, scenario, forms


def _initialized(state: dict) -> dict:
    initialized = deepcopy(state)
    initialized.update(
        {
            "repository_initialized": True,
            "repository_root": ".",
            "branches": {"main": None},
            "head": {"type": "branch", "name": "main", "target": None},
            "remotes": {},
            "remote_branches": {},
            "upstream_tracking": {},
        }
    )
    metadata = {
        "last_init_branch": "main",
        "last_init_initial_branch": "main",
        "last_init_directory": None,
        "last_init_current_directory": True,
        "last_init_quiet": False,
        "last_init_reinitialized": False,
        "repository_reinitialized": False,
    }
    initialized["operation_metadata"] = metadata
    initialized.update(metadata)
    return initialized


def test_a_cleared_scenario_credits_only_the_forms_the_learner_typed(db, django_user_model):
    user, player, tier, _, _ = _init_level("credit-used", django_user_model)
    run = AdventureLevelTierRunService().start_run(
        player=player, tier=tier, source_entry_point="level_page"
    )
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(
        f"/api/adventure-tier-runs/{run.id}/submit-command/",
        {
            "command": "git init",
            "execution": frontend_execution_payload(
                "git init", _initialized(run.repository_state), client_run_revision=0
            ),
        },
        format="json",
    )

    assert response.status_code == 200
    advanced = response.json()["run"]["rewards"]["mastery_advanced"]
    assert [item["form_slug"] for item in advanced] == ["current"]
    assert set(
        SkillMastery.objects.filter(player=player).values_list("command_form__slug", flat=True)
    ) == {"current"}


def test_a_scenario_clear_credits_only_the_clearing_runs_processed_commands(db, django_user_model):
    _, player, tier, scenario, _ = _init_level("credit-union", django_user_model)
    service = AdventureLevelTierRunService()

    def step(run, command: str, *, processable: bool = True) -> None:
        CommandStep.objects.create(
            adventure_tier_run=run,
            player=player,
            command_text=command,
            normalized_command=command,
            result_category="target_matched" if processable else "unprocessable",
            command_classification="counted",
            attempt_number=1,
            was_processable=processable,
        )

    failed = service.start_run(player=player, tier=tier, source_entry_point="level_page")
    step(failed, "git init -q")
    AdventureLevelTierRun.objects.filter(id=failed.id).update(status="failed")
    current = service.start_run(player=player, tier=tier, source_entry_point="level_page")
    step(current, "git init")
    step(current, "git start", processable=False)

    assert current.current_scenario_id == scenario.id
    assert _processed_commands(current) == ["git init"]
