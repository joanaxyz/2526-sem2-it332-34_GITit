import json
import shutil
from copy import deepcopy
from pathlib import Path

import pytest
from django.core.management import call_command
from rest_framework.test import APIClient

from adventures.models import (
    AdventureLevel,
    AdventureLevelTier,
    AdventureLevelTierProgress,
    AdventureLevelTierRun,
    AdventureLevelTierScenario,
    AdventureLevelTierScenarioVariant,
)
from adventures.services import AdventureLevelTierRunService
from curriculum.models import Chapter, CommandForm, CommandSkill, Story
from curriculum.services.solution_replay import replay_solutions
from players.services import get_or_create_player
from progress.models import AdventureLevelTierCompletion, Wallet
from testing.frontend_execution import frontend_execution_payload


def test_git_init_completes_tier_persists_progress_and_unlocks_medium(db, django_user_model):
    user = django_user_model.objects.create_user(username="tier-init", password="pass12345")
    player = get_or_create_player(user)
    story = Story.objects.create(slug="tier-init-story", title="Tier init story")
    chapter = Chapter.objects.create(
        story=story,
        slug="tier-init-chapter",
        number=1,
        title="Module 1",
        description="",
    )
    level = AdventureLevel.objects.create(
        chapter=chapter,
        slug="initializing-a-local-repository",
        title="Initializing Repositories",
    )
    easy = AdventureLevelTier.objects.create(adventure_level=level, difficulty="easy")
    medium = AdventureLevelTier.objects.create(adventure_level=level, difficulty="medium")
    easy_scenario = AdventureLevelTierScenario.objects.create(
        tier=easy,
        slug="init-easy",
        min_counted_commands=1,
        max_counted_commands=12,
    )
    medium_scenario = AdventureLevelTierScenario.objects.create(
        tier=medium,
        slug="init-medium",
        min_counted_commands=1,
        max_counted_commands=10,
    )
    skill = CommandSkill.objects.create(
        slug="git-init",
        base_command="git init",
        title="Initialize repositories",
    )
    command_form = CommandForm.objects.create(
        command_skill=skill,
        chapter=chapter,
        slug="current",
        usage_form="git init",
        label="Initialize the current folder",
    )
    level.command_forms.add(command_form)
    easy_scenario.command_forms.add(command_form)
    medium_scenario.command_forms.add(command_form)
    initial_state = {
        "repository_initialized": False,
        "commits": [],
        "branches": {},
        "head": {"type": "branch", "name": "main"},
        "staging": {},
        "working_tree": {},
        "conflicts": [],
    }
    rules = [
        {"type": "commit_count_equals", "count": 0},
        {"type": "operation_metadata_equals", "key": "last_init_directory", "value": None},
        {
            "type": "operation_metadata_equals",
            "key": "last_init_current_directory",
            "value": True,
        },
        {
            "type": "operation_metadata_equals",
            "key": "last_init_initial_branch",
            "value": "main",
        },
        {"type": "operation_metadata_equals", "key": "last_init_quiet", "value": False},
        {
            "type": "operation_metadata_equals",
            "key": "last_init_reinitialized",
            "value": False,
        },
    ]
    variant = AdventureLevelTierScenarioVariant.objects.create(
        scenario=easy_scenario,
        slug="init-easy-current-empty",
        label="Initialize the current folder",
        initial_state=initial_state,
        evaluation_spec={
            "state_requirements": {
                "repository_initialized": True,
                "head_branch": "main",
                "staging_empty": True,
                "rules": rules,
            },
            "process_requirements": {"required_commands": [], "forbidden_commands": []},
            "completion_policy": {"mode": "rules"},
        },
        solution_commands=["git init"],
    )
    AdventureLevelTierScenarioVariant.objects.create(
        scenario=medium_scenario,
        slug="init-medium-placeholder",
        label="Initialize a named folder",
        initial_state=initial_state,
        evaluation_spec={
            "state_requirements": {"repository_initialized": True},
            "process_requirements": {"required_commands": [], "forbidden_commands": []},
            "completion_policy": {"mode": "rules"},
        },
        solution_commands=["git init project"],
    )
    run = AdventureLevelTierRunService().start_run(
        player=player,
        tier=easy,
        source_entry_point="level_page",
    )
    assert run.selected_variant_id == variant.id

    initialized = deepcopy(run.repository_state)
    initialized.update(
        {
            "repository_initialized": True,
            "repository_root": ".",
            "branches": {"main": None},
            "head": {"type": "branch", "name": "main", "target": None},
            "commits": [],
            "staging": {},
            "conflicts": [],
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

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.post(
        f"/api/adventure-tier-runs/{run.id}/submit-command/",
        {
            "command": "git init",
            "execution": frontend_execution_payload(
                "git init",
                initialized,
                client_run_revision=0,
            ),
        },
        format="json",
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["command_outcome"]["solved"] is True
    assert payload["run"]["status"] == "completed"
    assert payload["run"]["progress"] == {
        "completed": 1,
        "total": 1,
        "cleared": True,
        "next_scenario": None,
    }
    assert payload["run"]["completion"] is not None
    assert payload["run"]["next_difficulty"] == {"id": medium.id, "difficulty": "medium"}
    assert payload["run"]["rewards"] == {
        "first_level_clear": True,
        "coins_awarded": 25,
        "chapter_chests_awarded": [
            {"threshold": 25, "coins": 25},
            {"threshold": 50, "coins": 60},
            {"threshold": 75, "coins": 100},
            {"threshold": 100, "coins": 150},
        ],
        "mastery_advanced": [
            {
                "skill_slug": "git-init",
                "form_slug": "current",
                "solves": 1,
                "target": 2,
                "mastered": False,
            }
        ],
    }

    run.refresh_from_db()
    assert run.status == "completed"
    assert AdventureLevelTierProgress.objects.get(player=player, tier=easy).successful_clears == 1
    assert AdventureLevelTierCompletion.objects.filter(player=player, tier=easy).exists()
    assert Wallet.objects.get(player=player).balance == 360

    unlocked_run = AdventureLevelTierRunService().start_run(
        player=player,
        tier=medium,
        source_entry_point="level_page",
    )
    assert unlocked_run.status == "started"


@pytest.mark.skipif(
    shutil.which("node") is None
    or not (Path(__file__).resolve().parents[3] / "frontend" / "node_modules").exists(),
    reason="Requires the frontend simulator and Node for real command payloads.",
)
def test_seeded_initial_branch_task_requires_explicit_main_creation(db, django_user_model):
    from adventures.tests.test_adventure_start_access import make_player

    call_command("seed_curriculum", verbosity=0)
    tier = AdventureLevelTier.objects.get(
        adventure_level__slug="initializing-a-local-repository", difficulty="easy"
    )
    first_variant = AdventureLevelTierScenarioVariant.objects.get(case_id="init-easy-plain-notes")
    branch_variant = AdventureLevelTierScenarioVariant.objects.get(
        case_id="init-easy-current-empty"
    )
    technique = "init:initial-branch:main"
    assert branch_variant.parameter_context["required_techniques"] == [technique]
    assert first_variant.parameter_context["required_techniques"] == []
    routes = {
        "bare": (["git init"], False),
        "short": (["git init -b main"], True),
        "long-equals": (["git init --initial-branch=main"], True),
        "long-space": (["git init --initial-branch main"], True),
        "explicit-current-directory": (["git init -b main ."], True),
        "wrong-branch-then-rename": (["git init -b trunk", "git branch -m main"], False),
        "reinitialize": (["git init", "git init -b main"], False),
    }
    specs = {
        name: {
            "initial_state": branch_variant.initial_state,
            "solution_commands": commands,
            "max_counted_commands": 12,
        }
        for name, (commands, _) in routes.items()
    }
    specs["plain-lesson"] = {
        "initial_state": first_variant.initial_state,
        "solution_commands": ["git init"],
        "max_counted_commands": 12,
    }
    _, replays = replay_solutions(specs)
    evidence = []

    def submit_replay(client, run, name):
        payload = None
        for index, step in enumerate(replays[name]["steps"]):
            response = client.post(
                f"/api/adventure-tier-runs/{run.id}/submit-command/",
                {
                    "command": step["command"],
                    "execution": {
                        **step["execution"],
                        "cwd": step["cwd"],
                        "client_run_revision": index,
                    },
                },
                format="json",
            )
            assert response.status_code == 200, response.content
            payload = response.json()
            assert payload["exit_code"] == 0, payload
        return payload

    for name, (commands, solved) in routes.items():
        client, _ = make_player(django_user_model, username=f"explicit-init-{name}")
        first = client.post(
            f"/api/adventure-level-tiers/{tier.id}/runs/",
            {"source_entry_point": "level_page"},
            format="json",
        )
        assert first.status_code == 201, first.content
        first_run = AdventureLevelTierRun.objects.get(pk=first.json()["id"])
        assert first_run.selected_variant_id == first_variant.id
        assert submit_replay(client, first_run, "plain-lesson")["command_outcome"]["solved"]

        started = client.post(
            f"/api/adventure-level-tiers/{tier.id}/runs/",
            {"source_entry_point": "level_page"},
            format="json",
        )
        assert started.status_code == 201, started.content
        run = AdventureLevelTierRun.objects.get(pk=started.json()["id"])
        assert run.selected_variant_id == branch_variant.id
        assert run.required_techniques == [technique]
        assert "Required technique: git init -b main." in started.json()["scenario_context"]["task"]

        result = submit_replay(client, run, name)
        run.refresh_from_db()
        assert result["command_outcome"]["solved"] is solved, result
        assert run.status == ("completed" if solved else "started")
        assert (technique in run.verified_techniques) is solved
        assert run.repository_state["head"]["name"] == "main"
        if not solved:
            assert (
                "Use the required technique: git init -b main."
                in result["step"]["contextual_feedback"]
            )
        evidence.append(
            {
                "commands": commands,
                "exit_code": result["exit_code"],
                "solved": result["command_outcome"]["solved"],
                "status": run.status,
                "verified_techniques": run.verified_techniques,
            }
        )

    print("Initial-branch API evidence: " + json.dumps(evidence))
