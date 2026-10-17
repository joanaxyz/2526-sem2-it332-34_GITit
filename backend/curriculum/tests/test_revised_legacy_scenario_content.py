from __future__ import annotations

import pytest
from django.core.management import call_command

from adventures.models import AdventureLevelTierWaveVariant
from curriculum.management.commands.seed_legacy_modules import LEGACY_MODULE_LEVELS
from curriculum.seed_data.revised_legacy_scenarios import revised_legacy_scenarios


def _legacy_cases() -> list[dict]:
    return [
        case
        for level in LEGACY_MODULE_LEVELS
        for tier in level.get("tiers", {}).values()
        for case in tier["cases"]
    ]


def test_revised_bank_covers_every_legacy_variant_once():
    cases = _legacy_cases()
    content = revised_legacy_scenarios()

    assert len(cases) == len(content) == 265
    assert set(content) == {case["case_id"] for case in cases}
    assert len({item["source_case_id"] for item in content.values()}) == 265


def test_revised_bank_has_complete_learner_facing_content_without_staff_sections():
    for case_id, item in revised_legacy_scenarios().items():
        assert item["label"].strip(), case_id
        assert item["story"].strip(), case_id
        assert item["real_world_context"].strip(), case_id
        assert item["task"].strip(), case_id
        flattened = " ".join(
            [
                item["label"],
                item["story"],
                item["real_world_context"],
                item["task"],
                *(value["value"] for value in item["required_values"]),
            ]
        ).lower()
        assert "staff only" not in flattened, case_id
        assert "answer key" not in flattened, case_id
        assert "accepted alternatives" not in flattened, case_id
        assert "evaluation" not in flattened, case_id


def test_revised_bank_exposes_required_resolved_files_as_copy_values():
    content = revised_legacy_scenarios()

    manual = content["manual-easy-auth-copy"]
    assert manual["required_values"] == [
        {
            "label": "Required file: src/auth.js",
            "value": "timeout=5000\nretry=enabled",
        }
    ]


def test_revised_variant_task_replaces_the_generic_tier_task():
    invoice = revised_legacy_scenarios()["init-easy-invoice"]

    assert invoice["label"] == "Initialize invoice-tracker"
    assert invoice["task"] == (
        "Create a new invoice-tracker folder that is a Git repository, with main as its "
        "first branch."
    )


@pytest.mark.django_db
def test_legacy_seed_persists_revised_variant_content():
    call_command("seed_legacy_modules", verbosity=0)

    variant = AdventureLevelTierWaveVariant.objects.get(case_id="init-easy-invoice")
    assert variant.label == "Initialize invoice-tracker"
    assert variant.scenario_context["task"] == (
        "Create a new invoice-tracker folder that is a Git repository, with main as its "
        "first branch."
    )
    assert variant.scenario_context["real_world_context"].startswith(
        "A client project can grow beyond its first brief."
    )
    assert variant.scenario_context["details"][0]["label"] == ""
    assert "Starting point:" in variant.scenario_context["details"][0]["value"]

    conflict = AdventureLevelTierWaveVariant.objects.get(case_id="manual-easy-auth-copy")
    assert conflict.scenario_context["details"][1] == {
        "label": "Required file: src/auth.js",
        "value": "timeout=5000\nretry=enabled",
    }
