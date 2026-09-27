from copy import deepcopy

import pytest
from rest_framework.test import APIClient

from adventures.models import (
    AdventureLevel,
    AdventureLevelTier,
    AdventureLevelTierRun,
    AdventureLevelTierWave,
    AdventureLevelTierWaveVariant,
)
from common.git.repository_state import VariantTargetStateHashCache
from curriculum.models import Chapter, CommandForm, CommandSkill, Story
from evaluation.compiler import CompiledEvaluationSpecCache
from players.services import get_or_create_player
from simulator.services import RepositoryStateSimulator
from simulator.trajectory import build_solution_trajectory

SOLUTION = ["git init", "git add README.md", "git add app.py", "git commit -m 'Save work'"]


@pytest.fixture(autouse=True)
def isolate_authored_variant_caches():
    # These fixtures reuse database IDs and edit objectives without generating
    # seed semantic keys. Do not leak their compiled objectives into other tests.
    CompiledEvaluationSpecCache._cache.clear()
    VariantTargetStateHashCache._cache.clear()
    yield
    CompiledEvaluationSpecCache._cache.clear()
    VariantTargetStateHashCache._cache.clear()


def initialized_state(state, branch="main", directory=None):
    state = deepcopy(state)
    state.update(repository_initialized=True, branches={branch: None},
                 head={"type": "branch", "name": branch, "target": None})
    metadata = {"last_init_branch": branch, "last_init_initial_branch": branch,
                "last_init_directory": directory, "last_init_current_directory": directory is None,
                "last_init_quiet": False, "last_init_reinitialized": False,
                "repository_reinitialized": False}
    state["operation_metadata"] = metadata
    state.update(metadata)
    return state


def staged(state, path):
    state = deepcopy(state)
    state["staging"][path] = state["working_tree"].pop(path)
    return state


def committed(state, message="Save work"):
    state = deepcopy(state)
    tree = {path: "ready" for path in state["staging"]}
    state["commits"] = [{"id": "c0", "parents": [], "tree": tree, "message": message}]
    state["branches"]["main"] = "c0"
    state["head"]["target"] = "c0"
    state["staging"] = {}
    return state


def solution_states(initial):
    """The repository in front of every SOLUTION command, then the final state."""

    first = initialized_state(initial)
    readme = staged(first, "README.md")
    both = staged(readme, "app.py")
    return [initial, first, readme, both], committed(both)


def trajectory_for(commands, states, final):
    return build_solution_trajectory({
        "steps": [
            {"command": command, "diagnostic": command.split()[1] in {"status", "log"}, "ready": state}
            for command, state in zip(commands, states, strict=True)
        ],
        "final": final,
    })


@pytest.fixture
def teaching_run(db, django_user_model):
    user = django_user_model.objects.create_user(username="learner", password="test-pass")
    player = get_or_create_player(user)
    story = Story.objects.create(slug="teaching", title="Teaching")
    chapter = Chapter.objects.create(story=story, slug="teaching", number=1, title="Teaching")
    level = AdventureLevel.objects.create(chapter=chapter, slug="teaching", title="Teaching")
    tier = AdventureLevelTier.objects.create(adventure_level=level, difficulty="easy")
    wave = AdventureLevelTierWave.objects.create(
        tier=tier, slug="teaching", max_counted_commands=12, required_successful_attempts=2,
    )
    for slug, form, usage_form, label in [
        ("git-init", "current-directory", "git init", "Start a repository here"),
        ("git-add", "file", "git add <file>", "Stage one file"),
        ("git-commit", "message", "git commit -m <message>", "Commit with a message"),
    ]:
        skill = CommandSkill.objects.create(slug=slug, title=slug, base_command=slug.replace("-", " "))
        wave.command_forms.add(CommandForm.objects.create(
            command_skill=skill, chapter=chapter, slug=form, usage_form=usage_form,
            label=label,
        ))
    state = RepositoryStateSimulator().normalize_state({
        "repository_initialized": False, "head": {"type": "branch", "name": "main"},
        "working_tree": {"README.md": "ready", "app.py": "ready", "draft.txt": "unfinished"},
    })
    states, final = solution_states(state)
    variant = AdventureLevelTierWaveVariant.objects.create(
        wave=wave, slug="first", label="First", initial_state=state,
        solution_commands=SOLUTION,
        solution_trajectory=trajectory_for(SOLUTION, states, final),
        target_state=final,
        evaluation_spec={
            "state_requirements": {"repository_initialized": True,
                "latest_commit": {"branch": "main", "contains_paths": ["README.md", "app.py"],
                                  "message_contains": ["Save work"]},
                "working_tree_contains": ["draft.txt"], "staging_empty": True},
            "completion_policy": {"mode": "rules"},
        },
    )
    return AdventureLevelTierRun.objects.create(
        player=player, tier=tier, current_wave=wave, selected_variant=variant,
        repository_state=state, max_counted_commands=12,
    )


@pytest.fixture
def client(teaching_run):
    client = APIClient()
    client.force_authenticate(teaching_run.player.user)
    return client
