import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import override_settings

from common.constants import COMPLETION_INSPECTION
from learning.models import Lesson
from scenarios.models import (
    CommandCountPolicy,
    DifficultyInstance,
    ScenarioGenerationBlueprint,
    ScenarioSkillFocus,
    ScenarioVariant,
)


@override_settings(DEBUG=True)
def test_module_one_blueprint_seed_matches_v3_contract(db):
    call_command("seed_module1_scenarios", "--reset", "--confirm", "--validate-build")

    expected_slugs = [
        "inspect-repository-state",
        "initialize-local-repository",
        "clone-remote-repository",
        "stage-and-commit-basic-workflow",
        "configure-gitignore-rules",
        "partial-staging-add-p",
        "amend-latest-commit",
        "unstage-and-discard-changes",
        "module1-integrated-local-workflow",
    ]

    assert Lesson.objects.filter(unit__slug="local-repository-foundations", is_published=True).count() == 9
    assert list(
        ScenarioSkillFocus.objects.filter(
            learning_unit__slug="local-repository-foundations",
            is_published=True,
        ).order_by("sort_order").values_list("slug", flat=True)
    ) == expected_slugs
    assert DifficultyInstance.objects.filter(
        scenario__learning_unit__slug="local-repository-foundations",
        is_published=True,
    ).count() == 27
    assert CommandCountPolicy.objects.filter(
        difficulty_instance__scenario__learning_unit__slug="local-repository-foundations",
    ).count() == 27
    assert ScenarioGenerationBlueprint.objects.filter(
        difficulty_instance__scenario__learning_unit__slug="local-repository-foundations",
        is_published=True,
    ).count() >= 27
    assert ScenarioVariant.objects.filter(
        scenario__learning_unit__slug="local-repository-foundations",
    ).count() == 0


@override_settings(DEBUG=True)
def test_module_one_seed_uses_authored_cases_and_inspection_policy(db):
    call_command("seed_module1_scenarios", "--reset", "--confirm")

    for blueprint in ScenarioGenerationBlueprint.objects.filter(
        difficulty_instance__scenario__learning_unit__slug="local-repository-foundations",
        is_published=True,
    ):
        cases = blueprint.parameter_pools["cases"]
        assert cases
        assert blueprint.generation_count == len(cases)
        assert blueprint.max_combinations == len(cases)
        assert len({case["case_id"] for case in cases}) == len(cases)
        assert len({case["answer_anchor"] for case in cases}) == len(cases)

    for difficulty in DifficultyInstance.objects.filter(
        scenario__learning_unit__slug="local-repository-foundations",
    ):
        if difficulty.scenario.slug == "initialize-local-repository" and difficulty.difficulty == "easy":
            assert difficulty.required_successful_attempts == 1
        else:
            assert difficulty.required_successful_attempts == (
                3 if difficulty.difficulty == "easy" else 2
            )

    inspection = DifficultyInstance.objects.get(
        scenario__slug="inspect-repository-state",
        difficulty="easy",
    )
    assert inspection.completion_type == COMPLETION_INSPECTION
    assert inspection.command_policy.min_counted_commands == 0
    assert inspection.command_policy.max_counted_commands == 0
    assert "inspection_answer_matches" in str(
        inspection.generation_blueprints.get().target_rule_template
    )


@override_settings(DEBUG=True)
def test_diagnostic_command_preview_is_first_module_one_scenario(db):
    call_command("seed_module1_scenarios", "--reset", "--confirm")

    first = ScenarioSkillFocus.objects.filter(
        learning_unit__slug="local-repository-foundations",
        is_published=True,
    ).order_by("sort_order").first()

    assert first.slug == "inspect-repository-state"
    assert first.safe_demo_commands[:7] == [
        "git status",
        "git log --oneline",
        "git diff",
        "git diff --staged",
        "git show",
        "git branch",
        "git remote -v",
    ]


@override_settings(DEBUG=True)
def test_module_one_seed_rejects_duplicate_solutions_without_waiver(db):
    command = __import__(
        "learning.management.commands.seed_module1_scenarios",
        fromlist=["Command"],
    ).Command()
    specs = [
        {
            "slug": "duplicate-demo",
            "difficulties": {
                "easy": {
                    "blueprints": [
                        {
                            "slug": "dupe",
                            "parameter_pools": {
                                "cases": [
                                    {"case_id": "one", "answer_anchor": "one"},
                                    {"case_id": "two", "answer_anchor": "two"},
                                ]
                            },
                            "solution_commands_template": ["git status"],
                        }
                    ]
                }
            },
        }
    ]

    with pytest.raises(CommandError, match="duplicate solution sequence"):
        command._validate_seed_specs(specs)
