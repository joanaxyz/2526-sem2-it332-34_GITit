"""What makes a transfer checkpoint worth measuring; see KPI_METHODOLOGY.md."""

from __future__ import annotations

import shlex

import pytest
from django.core.management import call_command

from adventures.models import AdventureLevelTierScenarioVariant
from adventures.services.tier_variants import TierVariantSelectionService
from curriculum.seed_data.scenario_bank import extension_scenario_bank, scenario_bank
from curriculum.seed_data.source.scenario_plan import MODULE_SCENARIO_PLAN
from curriculum.seed_data.source.transfer_checkpoints import TRANSFER_CHECKPOINTS
from progress.services.references import state_key, valid_ref

LEVEL_NUMBERS = {
    "resolving-conflicts-manually": "3.1",
    "using-a-merge-tool": "3.2",
    "cherry-picking-commits": "3.3",
    "recovering-from-hard-resets": "4.1",
    "reversing-pushed-commits-safely": "4.2",
    "completing-rebase-recovery-sequences": "4.3",
}


def _bank() -> dict[str, dict]:
    return scenario_bank() | extension_scenario_bank()


def _moves(commands: list[str]) -> list[tuple[str, ...]]:
    """Each command as its Git subcommand and flags, without its names and values."""
    moves = []
    for command in commands:
        words = shlex.split(command)
        moves.append((words[1], *(word for word in words[2:] if word.startswith("-"))))
    return moves


def _practice_ids(level: str) -> list[str]:
    return [
        case_id
        for scenarios in MODULE_SCENARIO_PLAN[level].values()
        for scenario in scenarios
        for case_id in scenario.variants
    ]


def test_every_module_3_and_4_level_closes_with_a_hard_checkpoint():
    assert set(TRANSFER_CHECKPOINTS) == set(LEVEL_NUMBERS)
    for level, checkpoint in TRANSFER_CHECKPOINTS.items():
        authored = _bank()[checkpoint["case_id"]]
        assert authored["difficulty"] == "hard"
        assert authored["scenario_number"].rsplit(".", 1)[0] == LEVEL_NUMBERS[level]
        assert checkpoint["note"].strip()
        assert checkpoint["case_id"] not in _practice_ids(level)


@pytest.mark.parametrize("level", sorted(LEVEL_NUMBERS))
def test_a_checkpoint_route_is_not_one_the_level_practises(level):
    """A reskin of a practice variant would measure recall, not transfer."""
    route = _moves(_bank()[TRANSFER_CHECKPOINTS[level]["case_id"]]["solution_commands"])
    practised = [_moves(_bank()[case_id]["solution_commands"]) for case_id in _practice_ids(level)]
    assert route not in practised


@pytest.mark.parametrize("level", sorted(LEVEL_NUMBERS))
def test_a_checkpoint_only_asks_for_moves_already_practised(level):
    """It composes what was taught: nothing in it is new to the learner."""
    practice_ids = {
        case_id for plan_level in MODULE_SCENARIO_PLAN for case_id in _practice_ids(plan_level)
    }
    taught = {
        move for case_id in practice_ids for move in _moves(_bank()[case_id]["solution_commands"])
    }
    route = _moves(_bank()[TRANSFER_CHECKPOINTS[level]["case_id"]]["solution_commands"])
    assert sorted(set(route) - taught) == []


@pytest.mark.django_db
def test_seed_reserves_checkpoints_apart_from_practice():
    call_command("seed_curriculum", verbosity=0)
    reserved = AdventureLevelTierScenarioVariant.objects.filter(
        is_transfer=True, is_published=True
    ).select_related("scenario__tier__adventure_level")
    assert {v.slug for v in reserved} == {c["case_id"] for c in TRANSFER_CHECKPOINTS.values()}
    selector = TierVariantSelectionService()
    for variant in reserved:
        scenario = variant.scenario
        level = scenario.tier.adventure_level.slug
        assert scenario.tier.difficulty == "hard"
        assert scenario.slug == MODULE_SCENARIO_PLAN[level]["hard"][0].slug
        assert variant.transfer_note == TRANSFER_CHECKPOINTS[level]["note"]
        assert valid_ref(variant)
        practice = selector._published_variants(scenario)
        assert variant not in practice and practice
        assert state_key(variant) not in {state_key(v) for v in practice}
