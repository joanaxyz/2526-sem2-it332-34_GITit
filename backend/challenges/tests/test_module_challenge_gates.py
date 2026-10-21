"""Each module ends in a seeded Challenge Gate (docs/goals/curriculum-waves-and-repetition/PLAN.md §14)."""

import shlex

import pytest
from django.core.management import call_command

from adventures.models import AdventureLevelTier
from challenges.models import ChallengeLevel, ChallengeTrial
from challenges.payloads import next_difficulty_payload
from challenges.services.runs import ChallengeRunService
from common.constants import SESSION_STATUS_COMPLETED
from common.exceptions import Locked
from curriculum.models import Chapter
from curriculum.seed_data.scenario_bank import scenario_for_case
from curriculum.seed_data.source.challenge_gates import CHALLENGE_GATES
from curriculum.seed_data.source.wave_plan import MODULE_WAVE_PLAN
from curriculum.selectors.content import chapter_content_overview
from players.services import get_or_create_player
from progress.models import AdventureLevelTierCompletion, ChallengeTrialCompletion

MODULES = (1, 2, 3, 4)
# Read-only looks never spend the command budget (CONTENT_AUTHORING_GUIDE.md).
DIAGNOSTIC_SUBCOMMANDS = {"status", "log", "show", "reflog", "diff"}


def _module_chapter(number: int) -> Chapter:
    return Chapter.objects.get(story__slug="arcane-spire", number=number)


def _gate(number: int) -> ChallengeLevel:
    return ChallengeLevel.objects.get(chapter=_module_chapter(number), is_published=True)


def _clear_tiers(player, chapter: Chapter, difficulty: str) -> None:
    for tier in AdventureLevelTier.objects.filter(
        adventure_level__chapter=chapter, difficulty=difficulty, is_published=True
    ):
        AdventureLevelTierCompletion.objects.get_or_create(player=player, tier=tier)


def _gate_locked(player, chapter: Chapter) -> bool:
    [gate] = chapter_content_overview(player=player, chapter_id=chapter.id)["challenges"]
    return gate["locked"]


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


def test_the_gate_opens_only_once_every_tier_of_every_level_is_cleared(db, django_user_model):
    call_command("seed_curriculum", verbosity=0)
    player = get_or_create_player(
        django_user_model.objects.create_user(username="gatekeeper", password="pass12345")
    )
    chapter = _module_chapter(2)
    trials = {trial.difficulty: trial for trial in _gate(2).trials.all()}
    runs = ChallengeRunService()
    locked = {"easy": "locked", "medium": "locked", "hard": "locked"}

    for difficulty in ("easy", "medium"):
        _clear_tiers(player, chapter, difficulty)
        assert _trial_statuses(player, chapter) == locked
        assert _gate_locked(player, chapter)
        with pytest.raises(Locked):
            runs.start_run(player=player, trial=trials["easy"], source_entry_point="level_page")

    _clear_tiers(player, chapter, "hard")
    assert not _gate_locked(player, chapter)
    assert _trial_statuses(player, chapter) == {**locked, "easy": "not_started"}
    runs.start_run(player=player, trial=trials["easy"], source_entry_point="level_page")
    with pytest.raises(Locked):
        runs.start_run(player=player, trial=trials["medium"], source_entry_point="level_page")

    # Inside the open gate the trials still go Easy, Medium, Hard.
    ChallengeTrialCompletion.objects.create(player=player, challenge_trial=trials["easy"], stars=3)
    assert _trial_statuses(player, chapter) == {
        "easy": "completed",
        "medium": "not_started",
        "hard": "locked",
    }


def test_a_cleared_gate_trial_offers_the_next_trial(db, django_user_model):
    call_command("seed_curriculum", verbosity=0)
    player = get_or_create_player(
        django_user_model.objects.create_user(username="gatewalker", password="pass12345")
    )
    chapter = _module_chapter(2)
    trials = {trial.difficulty: trial for trial in _gate(2).trials.all()}
    for difficulty in ("easy", "medium", "hard"):
        _clear_tiers(player, chapter, difficulty)
    run = ChallengeRunService().start_run(
        player=player, trial=trials["easy"], source_entry_point="level_page"
    )
    run.status = SESSION_STATUS_COMPLETED
    run.save(update_fields=["status"])
    ChallengeTrialCompletion.objects.create(
        player=player, challenge_trial=trials["easy"], challenge_run=run, stars=3
    )

    assert next_difficulty_payload(run) == {"id": trials["medium"].id, "difficulty": "medium"}


def _counted_skeleton(commands: list[str]) -> tuple[str, ...]:
    """A solution's counted git commands with their options, operands dropped."""
    steps = []
    for command in commands:
        words = shlex.split(command)
        if len(words) < 2 or words[0] != "git" or words[1] in DIAGNOSTIC_SUBCOMMANDS:
            continue
        steps.append(" ".join([words[1], *(word for word in words[2:] if word.startswith("-"))]))
    return tuple(steps)


def test_every_gate_trial_is_a_module_workflow_not_an_adventure_wave():
    adventure = {
        _counted_skeleton(scenario_for_case(case_id)["solution_commands"]): case_id
        for tiers in MODULE_WAVE_PLAN.values()
        for waves in tiers.values()
        for wave in waves
        for case_id in wave.variants
    }
    for gate in CHALLENGE_GATES.values():
        for difficulty, case_ids in gate["trials"].items():
            for case_id in case_ids:
                steps = _counted_skeleton(scenario_for_case(case_id)["solution_commands"])
                assert len(steps) >= 3, f"{case_id}: a gate trial is a workflow"
                assert steps not in adventure, (
                    f"{case_id} repeats the steps of adventure wave {adventure.get(steps)}"
                )


def test_only_module_chapters_get_gates(db):
    call_command("seed_curriculum", verbosity=0)

    assert not ChallengeLevel.objects.filter(chapter=_module_chapter(0)).exists()
    assert ChallengeTrial.objects.filter(challenge_level__chapter__number__in=MODULES).count() == 12
