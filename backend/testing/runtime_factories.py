from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from uuid import uuid4

from rest_framework.test import APIClient

from adventures.models import (
    AdventureLevel,
    AdventureRun,
    AdventureRunWave,
    AdventureWave,
    AdventureWaveVariant,
)
from challenges.models import ChallengeLevel, ChallengeRun, ChallengeTrial, ChallengeTrialVariant
from common.constants import DIFFICULTY_EASY
from curriculum.models import Chapter, Story
from players.services import get_or_create_player
from simulator.services import RepositoryStateSimulator


@dataclass(frozen=True)
class SimpleRepositoryStates:
    initial: dict
    target: dict


@dataclass(frozen=True)
class ChallengeRunFixture:
    user: object
    player: object
    story: Story
    chapter: Chapter
    level: ChallengeLevel
    trial: ChallengeTrial
    variant: ChallengeTrialVariant
    run: ChallengeRun
    states: SimpleRepositoryStates


@dataclass(frozen=True)
class AdventureRunFixture:
    user: object
    player: object
    story: Story
    chapter: Chapter
    level: AdventureLevel
    wave: AdventureWave
    variant: AdventureWaveVariant
    run: AdventureRun
    states: SimpleRepositoryStates


def unique_suffix() -> str:
    return uuid4().hex[:8]


def make_user(django_user_model, username: str = "student"):
    suffix = unique_suffix()
    return django_user_model.objects.create_user(
        username=f"{username}-{suffix}",
        email=f"{username}-{suffix}@example.com",
        password="pass12345",
    )


def api_client_for(user) -> APIClient:
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def stage_readme_states() -> SimpleRepositoryStates:
    tools = RepositoryStateSimulator()
    initial = tools.normalize_state(
        {
            "branches": {"main": None},
            "head": {"type": "branch", "name": "main"},
            "working_tree": {"README.md": {"status": "untracked", "content": "hello"}},
        }
    )
    target = deepcopy(initial)
    target["staging"] = {"README.md": {"status": "untracked", "content": "hello"}}
    target["working_tree"] = {}
    return SimpleRepositoryStates(
        initial=tools.normalize_state(initial),
        target=tools.normalize_state(target),
    )


def create_test_chapter(*, suffix: str, number_base: int = 920000) -> tuple[Story, Chapter]:
    story = Story.objects.create(slug=f"test-story-{suffix}", title="Test Story")
    chapter = Chapter.objects.create(
        story=story,
        slug=f"test-chapter-{suffix}",
        number=number_base + Story.objects.count(),
        title="Test Chapter",
        description="Runtime test chapter",
    )
    return story, chapter


def create_stage_readme_challenge_run(
    django_user_model,
    *,
    username: str = "challenge-runtime",
    reward_coins: int = 0,
) -> ChallengeRunFixture:
    user = make_user(django_user_model, username=username)
    player = get_or_create_player(user)
    suffix = unique_suffix()
    story, chapter = create_test_chapter(suffix=f"challenge-{suffix}")
    level = ChallengeLevel.objects.create(
        chapter=chapter,
        slug=f"stage-readme-challenge-{suffix}",
        title="Stage README Challenge",
        is_published=True,
    )
    trial = ChallengeTrial.objects.create(
        challenge_level=level,
        difficulty=DIFFICULTY_EASY,
        min_counted_commands=1,
        max_counted_commands=3,
        reward_coins=reward_coins,
        is_published=True,
    )
    states = stage_readme_states()
    variant = ChallengeTrialVariant.objects.create(
        trial=trial,
        slug=f"stage-readme-{suffix}",
        label="Stage README",
        initial_state=states.initial,
        target_state=states.target,
        evaluation_spec={"completion_policy": {"mode": "state_hash"}},
        solution_commands=["git add README.md"],
        semantic_key=f"stage-readme:{suffix}",
        is_published=True,
    )
    run = ChallengeRun.objects.create(
        player=player,
        challenge_trial=trial,
        selected_variant=variant,
        source_entry_point="runtime_test",
        min_counted_commands=trial.min_counted_commands,
        max_counted_commands=trial.max_counted_commands,
        repository_state=states.initial,
    )
    return ChallengeRunFixture(
        user=user,
        player=player,
        story=story,
        chapter=chapter,
        level=level,
        trial=trial,
        variant=variant,
        run=run,
        states=states,
    )


def create_stage_readme_adventure_run(
    django_user_model,
    *,
    username: str = "adventure-runtime",
    reward_coins: int = 0,
) -> AdventureRunFixture:
    user = make_user(django_user_model, username=username)
    player = get_or_create_player(user)
    suffix = unique_suffix()
    story, chapter = create_test_chapter(suffix=f"adventure-{suffix}")
    level = AdventureLevel.objects.create(
        chapter=chapter,
        slug=f"stage-readme-adventure-{suffix}",
        title="Stage README Adventure",
        is_required=True,
        is_published=True,
        reward_coins=reward_coins,
    )
    wave = AdventureWave.objects.create(
        level=level,
        slug=f"stage-readme-wave-{suffix}",
        title="Stage README",
        min_counted_commands=1,
        max_counted_commands=3,
        is_published=True,
    )
    states = stage_readme_states()
    variant = AdventureWaveVariant.objects.create(
        wave=wave,
        slug=f"stage-readme-{suffix}",
        label="Stage README",
        initial_state=states.initial,
        target_state=states.target,
        evaluation_spec={"completion_policy": {"mode": "state_hash"}},
        solution_commands=["git add README.md"],
        semantic_key=f"stage-readme:{suffix}",
        is_published=True,
    )
    run = AdventureRun.objects.create(
        player=player,
        level=level,
        current_wave=wave,
        selected_variant=variant,
        repository_state=states.initial,
    )
    AdventureRunWave.objects.create(run=run, wave=wave, selected_variant=variant)
    return AdventureRunFixture(
        user=user,
        player=player,
        story=story,
        chapter=chapter,
        level=level,
        wave=wave,
        variant=variant,
        run=run,
        states=states,
    )
