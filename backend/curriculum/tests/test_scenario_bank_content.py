from __future__ import annotations

import pytest
from django.core.management import call_command

from adventures.models import AdventureLevelTierWaveVariant
from curriculum.management.commands.seed_curriculum import MODULE_LEVELS
from curriculum.seed_data.generated.generated_targets import TARGET_STATES
from curriculum.seed_data.scenario_bank import scenario_bank
from curriculum.seed_data.scenario_runtime import DISPLACED_REVISED_CASE_IDS
from evaluation.services.state_based import StateBasedEvaluator


def _curriculum_cases() -> list[dict]:
    return [
        case
        for level in MODULE_LEVELS
        for tier in level.get("tiers", {}).values()
        for case in tier["cases"]
    ]


def test_revised_bank_uses_every_authored_variant_id_once():
    cases = _curriculum_cases()
    content = scenario_bank()

    assert len(cases) == len(content) == 265
    assert len({case["case_id"] for case in cases}) == 265
    assert set(content) == {case["case_id"] for case in cases}
    assert {item["difficulty"] for item in content.values()} == {"easy", "medium", "hard"}
    assert all("source_case_id" not in item for item in content.values())


def test_revised_bank_has_complete_learner_facing_content_without_staff_sections():
    for case_id, item in scenario_bank().items():
        for field in (
            "label",
            "story",
            "starting_point",
            "real_world_context",
            "task",
            "expected_result",
        ):
            assert item[field].strip(), (case_id, field)
        assert item["objective_checks"], case_id

        flattened = " ".join(
            [
                item["label"],
                item["story"],
                item["starting_point"],
                item["real_world_context"],
                item["task"],
                item["expected_result"],
                *item["objective_checks"],
                *(file["content"] for file in item["required_files"]),
            ]
        ).lower()
        assert "staff only" not in flattened, case_id
        assert "answer key" not in flattened, case_id
        assert "accepted alternatives" not in flattened, case_id


def test_revised_bank_preserves_required_resolved_files_and_answer_order():
    manual = scenario_bank()["manual-easy-auth-copy"]

    assert manual["required_files"] == [
        {"path": "src/auth.js", "content": "timeout=5000\nretry=enabled"}
    ]
    assert manual["solution_commands"] == [
        "git merge feature/auth-timeout",
        "git add src/auth.js",
        "git commit --no-edit",
    ]
    assert manual["solution_workspace_files"] == [
        {
            "mode": "write",
            "path": "src/auth.js",
            "content": "timeout=5000\nretry=enabled",
            "after_command_index": 1,
        }
    ]


def test_every_revised_answer_key_satisfies_its_runtime_evaluation():
    evaluator = StateBasedEvaluator()
    failures = []

    for case in _curriculum_cases():
        outcome = evaluator.evaluate(
            TARGET_STATES[case["case_id"]],
            case["state_requirements"],
            initial_state=case["initial_state"],
            executed_commands=case["solution_commands"],
        )
        if not outcome.target_matched:
            failures.append((case["case_id"], [rule["reason"] for rule in outcome.failed_rules]))

    assert failures == []


@pytest.mark.django_db
def test_curriculum_seed_persists_the_complete_scenario_contract():
    call_command("seed_curriculum", verbosity=0)

    variant = AdventureLevelTierWaveVariant.objects.get(case_id="init-easy-invoice")
    authored = scenario_bank()["init-easy-invoice"]
    assert variant.label == authored["label"]
    assert variant.solution_commands == authored["solution_commands"]
    assert variant.scenario_context == {
        "schema_version": 3,
        "story": authored["story"],
        "starting_point": authored["starting_point"],
        "real_world_context": authored["real_world_context"],
        "task": authored["task"],
        "objective_checks": authored["objective_checks"],
        "expected_result": authored["expected_result"],
        "details": [],
    }
    assert (
        variant.parameter_context["minimum_counted_commands"]
        == authored["minimum_counted_commands"]
    )
    assert (
        variant.parameter_context["maximum_counted_commands"]
        == authored["maximum_counted_commands"]
    )

    conflict = AdventureLevelTierWaveVariant.objects.get(case_id="manual-easy-auth-copy")
    assert conflict.scenario_context["details"][0] == {
        "label": "Required file: src/auth.js",
        "value": "timeout=5000\nretry=enabled",
    }
    assert AdventureLevelTierWaveVariant.objects.filter(is_published=True).count() == 265


@pytest.mark.django_db
def test_reseed_unpublishes_all_displaced_revised_ids():
    call_command("seed_curriculum", verbosity=0)

    for displaced_id, replacement_id in DISPLACED_REVISED_CASE_IDS.items():
        replacement = AdventureLevelTierWaveVariant.objects.get(case_id=replacement_id)
        AdventureLevelTierWaveVariant.objects.create(
            wave=replacement.wave,
            slug=displaced_id,
            label=f"Retired {displaced_id}",
            initial_state=replacement.initial_state,
            target_state=replacement.target_state,
            evaluation_spec=replacement.evaluation_spec,
            solution_commands=replacement.solution_commands,
            solution_workspace_files=replacement.solution_workspace_files,
            solution_trajectory=replacement.solution_trajectory,
            case_id=displaced_id,
            semantic_key=displaced_id,
            parameter_context={},
            scenario_context=replacement.scenario_context,
            is_published=True,
        )

    call_command("seed_curriculum", verbosity=0)

    displaced = AdventureLevelTierWaveVariant.objects.filter(case_id__in=DISPLACED_REVISED_CASE_IDS)
    assert displaced.count() == len(DISPLACED_REVISED_CASE_IDS)
    assert not displaced.filter(is_published=True).exists()
