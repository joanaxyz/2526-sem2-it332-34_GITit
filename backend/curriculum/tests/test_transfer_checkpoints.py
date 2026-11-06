"""What makes a transfer checkpoint worth measuring; see KPI_METHODOLOGY.md."""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from django.core.management import call_command

from adventures.models import AdventureLevelTierScenarioVariant
from adventures.services.tier_variants import TierVariantSelectionService
from challenges.models import ChallengeTrialVariant
from curriculum.seed_data.scenario_bank import extension_scenario_bank, scenario_bank
from curriculum.seed_data.source.challenge_gates import CHALLENGE_GATES
from curriculum.seed_data.source.scenario_plan import MODULE_SCENARIO_PLAN
from curriculum.seed_data.source.transfer_checkpoints import (
    RETIRED_TRANSFER_CHECKPOINTS,
    TRANSFER_CHECKPOINTS,
)
from progress.services.references import state_key, valid_ref

LEVEL_NUMBERS = {
    "unstaging-and-discarding-changes": "1.6",
    "branch-naming-and-housekeeping": "2.2",
    "resolving-conflicts-manually": "3.1",
    "using-a-merge-tool": "3.2",
    "cherry-picking-commits": "3.3",
    "recovering-from-hard-resets": "4.1",
    "reversing-pushed-commits-safely": "4.2",
    "completing-rebase-recovery-sequences": "4.3",
}


def _bank() -> dict[str, dict]:
    return scenario_bank() | extension_scenario_bank()


def _practice_ids(level: str) -> list[str]:
    return [
        case_id
        for scenarios in MODULE_SCENARIO_PLAN[level].values()
        for scenario in scenarios
        for case_id in scenario.variants
    ]


def test_curated_levels_close_with_a_hard_checkpoint():
    assert set(TRANSFER_CHECKPOINTS) == set(LEVEL_NUMBERS)
    for level, checkpoint in TRANSFER_CHECKPOINTS.items():
        authored = _bank()[checkpoint["case_id"]]
        assert authored["difficulty"] == "hard"
        assert authored["scenario_number"].rsplit(".", 1)[0] == LEVEL_NUMBERS[level]
        assert checkpoint["note"].strip()
        assert checkpoint["case_id"] not in _practice_ids(level)


def test_current_checkpoint_objectives_use_action_phrasing():
    """Match the learner-objective convention introduced by ed781e0."""
    verbs = {
        "Create",
        "Keep",
        "Restore",
        "Preserve",
        "Remove",
        "Finish",
        "Complete",
        "Record",
        "Update",
        "Leave",
        "Publish",
        "Base",
        "Exclude",
    }
    for checkpoint in TRANSFER_CHECKPOINTS.values():
        checks = _bank()[checkpoint["case_id"]]["objective_checks"]
        assert checks and all(check.split()[0] in verbs for check in checks), checks


def test_transfer_checkpoints_are_never_placed_in_challenge_gates():
    reserved_ids = {spec["case_id"] for spec in TRANSFER_CHECKPOINTS.values()} | set(
        RETIRED_TRANSFER_CHECKPOINTS
    )
    gate_ids = {
        case_id
        for gate in CHALLENGE_GATES.values()
        for cases in gate["trials"].values()
        for case_id in cases
    }
    assert not reserved_ids & gate_ids


@pytest.mark.parametrize("level", sorted(LEVEL_NUMBERS))
def test_checkpoint_repository_goal_is_distinct_from_practice_and_gates(level):
    """A useful screen; actual decisions are proved by the outcome suite."""
    from curriculum.seed_data.generated.generated_targets import TARGET_STATES
    from curriculum.seed_data.source.challenge_gates import CHALLENGE_GATES
    from curriculum.tests.test_scenario_plan_invariants import _case

    def fingerprint(case_id):
        return state_key(
            SimpleNamespace(
                initial_state=_case(case_id)["initial_state"], target_state=TARGET_STATES[case_id]
            )
        )

    checkpoint = TRANSFER_CHECKPOINTS[level]["case_id"]
    ordinary = [
        case_id for plan_level in MODULE_SCENARIO_PLAN for case_id in _practice_ids(plan_level)
    ] + [
        case_id
        for gate in CHALLENGE_GATES.values()
        for ids in gate["trials"].values()
        for case_id in ids
    ]
    assert fingerprint(checkpoint) not in {fingerprint(case_id) for case_id in ordinary}


@pytest.mark.parametrize("level", sorted(LEVEL_NUMBERS))
def test_a_checkpoint_only_asks_for_moves_already_practised(level):
    """It composes what was taught: nothing in it is new to the learner."""
    from curriculum.tests.test_scenario_plan_invariants import _parts

    # Guaranteed practice, never a union of all future modules or optional
    # variants. The merge-tool case explicitly requires completed manual Hard.
    known = set()
    for taught_level in (level, *TRANSFER_CHECKPOINTS[level].get("prerequisites", ())):
        for scenarios in MODULE_SCENARIO_PLAN[taught_level].values():
            for scenario in scenarios:
                known |= set.intersection(*(set(_parts(case_id)) for case_id in scenario.variants))
    assert set(_parts(TRANSFER_CHECKPOINTS[level]["case_id"])) <= known


@pytest.mark.django_db
def test_seed_reserves_checkpoints_apart_from_practice():
    call_command("seed_curriculum", verbosity=0)
    reserved = AdventureLevelTierScenarioVariant.objects.filter(
        is_transfer=True, is_published=True
    ).select_related("scenario__tier__adventure_level")
    assert {v.slug for v in reserved} == {c["case_id"] for c in TRANSFER_CHECKPOINTS.values()}
    reserved_ids = {c["case_id"] for c in TRANSFER_CHECKPOINTS.values()} | set(
        RETIRED_TRANSFER_CHECKPOINTS
    )
    gate_variants = ChallengeTrialVariant.objects.filter(
        is_published=True,
        trial__challenge_level__chapter__story__slug="arcane-spire",
    )
    gate_ids = {
        case_id
        for gate in CHALLENGE_GATES.values()
        for cases in gate["trials"].values()
        for case_id in cases
    }
    assert set(gate_variants.values_list("case_id", flat=True)) == gate_ids
    assert not gate_variants.filter(case_id__in=reserved_ids).exists()
    assert not gate_variants.filter(slug__in=reserved_ids).exists()
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
