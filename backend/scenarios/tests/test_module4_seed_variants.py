import json

from django.core.management import call_command
from django.test import override_settings

from learning.models import LearningUnit
from scenarios.models import DifficultyInstance, ScenarioSkillFocus, ScenarioVariant
from simulator.git_commands import GitCommandParser, GitCommandRegistry


def _example_command(command: str) -> str:
    replacements = {
        "<branch>": "main",
        "<target>": "HEAD@{1}",
        "<remote>": "origin",
        "<commit>": "c1",
    }
    example = command
    for placeholder, value in replacements.items():
        example = example.replace(placeholder, value)
    return example


@override_settings(DEBUG=True)
def test_module_four_seed_creates_advanced_recovery_variants(db):
    call_command("seed_module4_scenarios", "--reset", "--confirm", "--validate-build")

    unit = LearningUnit.objects.get(slug="advanced-recovery-history")
    assert unit.number == 4
    assert (
        list(
            ScenarioSkillFocus.objects.filter(learning_unit=unit, is_published=True)
            .order_by("sort_order", "slug")
            .values_list("slug", flat=True)
        )
        == [
            "recover-from-hard-reset-incident",
            "reverse-pushed-commit-safely",
            "complete-rebase-recovery-sequence",
        ]
    )
    assert DifficultyInstance.objects.filter(scenario__learning_unit=unit, is_published=True).count() == 9
    assert ScenarioVariant.objects.filter(scenario__learning_unit=unit, is_published=True).count() == 45

    recovery = ScenarioSkillFocus.objects.get(learning_unit=unit, slug="recover-from-hard-reset-incident")
    assert "git reflog" in recovery.primary_focus_commands
    assert "git switch" in recovery.primary_focus_commands

    rollback = ScenarioSkillFocus.objects.get(learning_unit=unit, slug="reverse-pushed-commit-safely")
    assert rollback.primary_focus_commands == ["git revert", "git push"]

    rebase = ScenarioSkillFocus.objects.get(learning_unit=unit, slug="complete-rebase-recovery-sequence")
    assert "git rebase" in rebase.primary_focus_commands
    assert "git merge-base" in rebase.supporting_diagnostic_commands


@override_settings(DEBUG=True)
def test_module_four_seeded_solutions_are_state_based_and_command_supported(db):
    call_command("seed_module4_scenarios", "--reset", "--confirm", "--validate-build")
    parser = GitCommandParser()
    registry = GitCommandRegistry()

    for variant in ScenarioVariant.objects.filter(
        scenario__learning_unit__slug="advanced-recovery-history",
        is_published=True,
    ):
        assert variant.target_rule
        assert variant.target_state
        assert variant.expected_state_diagram
        assert variant.student_context
        assert variant.solution_commands
        context = json.dumps(variant.student_context).lower()
        for command in variant.solution_commands:
            assert command.lower() not in context
            parsed = parser.parse(command)
            spec = registry.get(parsed.subcommand)
            assert spec is not None, command
            assert spec.validate(parsed) is None, command


@override_settings(DEBUG=True)
def test_module_four_easy_variants_use_distinct_student_briefs(db):
    call_command("seed_module4_scenarios", "--reset", "--confirm", "--validate-build")
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="recover-from-hard-reset-incident",
        difficulty="easy",
        is_published=True,
    )
    variants = list(difficulty.variants.filter(is_published=True).order_by("semantic_key", "id"))
    stories = [((variant.student_context or {}).get("story") or "").strip() for variant in variants]

    assert len(variants) >= 3
    assert all(stories)
    assert len(set(stories)) == len(stories)

    for scenario in ScenarioSkillFocus.objects.filter(
        learning_unit__slug="advanced-recovery-history",
        is_published=True,
    ):
        preview = scenario.command_preview_config
        for ref in preview.get("command_refs", []):
            command = ref.get("command")
            if not command:
                continue
            parsed = parser.parse(_example_command(command))
            spec = registry.get(parsed.subcommand)
            assert spec is not None, command
            assert spec.validate(parsed) is None, command
