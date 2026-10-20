"""Each module ends in a seeded Challenge Gate (docs/goals/curriculum-waves-and-repetition/PLAN.md §14)."""

import pytest
from django.core.management import call_command

from adventures.models import AdventureLevelTier
from challenges.models import ChallengeLevel, ChallengeTrial
from challenges.services.runs import ChallengeRunService
from common.exceptions import Locked
from curriculum.models import Chapter
from curriculum.selectors.content import chapter_content_overview
from players.services import get_or_create_player
from progress.models import AdventureLevelTierCompletion, ChallengeTrialCompletion

MODULES = (1, 2, 3, 4)


def _module_chapter(number: int) -> Chapter:
    return Chapter.objects.get(story__slug="arcane-spire", number=number)


def _gate(number: int) -> ChallengeLevel:
    return ChallengeLevel.objects.get(chapter=_module_chapter(number), is_published=True)


def _clear_tiers(player, chapter: Chapter, difficulty: str) -> None:
    for tier in AdventureLevelTier.objects.filter(
        adventure_level__chapter=chapter, difficulty=difficulty, is_published=True
    ):
        AdventureLevelTierCompletion.objects.get_or_create(player=player, tier=tier)


def _trial_statuses(player, chapter: Chapter) -> dict[str, str]:
    overview = chapter_content_overview(player=player, chapter_id=chapter.id)
    [gate] = overview["challenges"]
    return {trial["difficulty"]: trial["status"] for trial in gate["trials"]}


def test_every_module_gets_a_three_trial_gate_with_two_workflow_variants(db):
    call_command("seed_curriculum", verbosity=0)
    call_command("seed_curriculum", verbosity=0)  # idempotent

    for number in MODULES:
        gate = _gate(number)
        trials = {trial.difficulty: trial for trial in gate.trials.filter(is_published=True)}
        assert set(trials) == {"easy", "medium", "hard"}
        assert gate.command_forms.exists()
        assert {difficulty: trial.reward_coins for difficulty, trial in trials.items()} == {
            "easy": 50,
            "medium": 75,
            "hard": 100,
        }
        assert {difficulty: trial.max_counted_commands for difficulty, trial in trials.items()} == {
            "easy": 12,
            "medium": 10,
            "hard": 8,
        }
        for trial in trials.values():
            variants = list(trial.variants.filter(is_published=True))
            assert len(variants) == 2
            assert all(variant.target_state for variant in variants)
            assert all(variant.solution_trajectory for variant in variants)
            # A workflow, not a single command.
            assert all(len(variant.solution_commands) >= 3 for variant in variants)
    assert ChallengeLevel.objects.filter(chapter__story__slug="arcane-spire").count() == 4


def test_gate_trials_open_as_each_difficulty_is_cleared_on_every_level(db, django_user_model):
    call_command("seed_curriculum", verbosity=0)
    player = get_or_create_player(
        django_user_model.objects.create_user(username="gatekeeper", password="pass12345")
    )
    chapter = _module_chapter(2)
    trials = {trial.difficulty: trial for trial in _gate(2).trials.all()}
    runs = ChallengeRunService()

    assert _trial_statuses(player, chapter) == {
        "easy": "locked",
        "medium": "locked",
        "hard": "locked",
    }
    with pytest.raises(Locked):
        runs.start_run(player=player, trial=trials["easy"], source_entry_point="level_page")

    _clear_tiers(player, chapter, "easy")
    assert _trial_statuses(player, chapter)["easy"] == "not_started"
    runs.start_run(player=player, trial=trials["easy"], source_entry_point="level_page")

    # The Medium trial needs every Medium tier, even after the Easy trial is cleared.
    ChallengeTrialCompletion.objects.create(player=player, challenge_trial=trials["easy"], stars=3)
    assert _trial_statuses(player, chapter)["medium"] == "locked"
    with pytest.raises(Locked):
        runs.start_run(player=player, trial=trials["medium"], source_entry_point="level_page")

    _clear_tiers(player, chapter, "medium")
    assert _trial_statuses(player, chapter)["medium"] == "not_started"
    assert _trial_statuses(player, chapter)["hard"] == "locked"


def test_only_module_chapters_get_gates(db):
    call_command("seed_curriculum", verbosity=0)

    assert not ChallengeLevel.objects.filter(chapter=_module_chapter(0)).exists()
    assert ChallengeTrial.objects.filter(challenge_level__chapter__number__in=MODULES).count() == 12
