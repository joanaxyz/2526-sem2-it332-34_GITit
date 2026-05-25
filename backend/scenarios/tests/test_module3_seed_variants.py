import json

from django.core.management import call_command
from django.test import override_settings

from learning.models import LearningUnit
from scenarios.models import DifficultyInstance, ScenarioSkillFocus, ScenarioVariant
from simulator.git_commands import GitCommandParser, GitCommandRegistry


def _example_command(command: str) -> str:
    replacements = {
        "<branch>": "feature/auth-timeout",
        "<tool>": "vscode",
        "<key>": "merge.tool",
        "<value>": "vscode",
        "<remote>": "origin",
        "<commit>": "c1",
        "<path>": "src/auth.js",
    }
    example = command
    for placeholder, value in replacements.items():
        example = example.replace(placeholder, value)
    return example


@override_settings(DEBUG=True)
def test_module_three_seed_creates_conflict_resolution_variants(db):
    call_command("seed_module3_scenarios", "--reset", "--confirm", "--validate-build")

    unit = LearningUnit.objects.get(slug="conflict-resolution")
    assert unit.number == 3
    assert (
        list(
            ScenarioSkillFocus.objects.filter(learning_unit=unit, is_published=True)
            .order_by("sort_order", "slug")
            .values_list("slug", flat=True)
        )
        == [
            "diagnose-conflict-state",
            "identify-merge-conflict-state",
            "accept-conflict-side",
            "abort-conflicted-merge",
            "resolve-conflicts-manually",
            "use-merge-tool-workflow",
            "prevent-stale-conflict-merge",
            "cherry-pick-selected-commit",
            "module3-integrated-conflict-workflow",
        ]
    )
    assert DifficultyInstance.objects.filter(scenario__learning_unit=unit, is_published=True).count() == 27
    assert ScenarioVariant.objects.filter(scenario__learning_unit=unit, is_published=True).count() == 60

    mergetool = ScenarioSkillFocus.objects.get(learning_unit=unit, slug="use-merge-tool-workflow")
    assert mergetool.primary_focus_commands == [
        "git config",
        "git merge",
        "git mergetool",
        "git add",
        "git commit",
    ]
    assert "git mergetool" in json.dumps(mergetool.command_preview_config)

    side = ScenarioSkillFocus.objects.get(learning_unit=unit, slug="accept-conflict-side")
    assert "git checkout" in side.primary_focus_commands
    assert "git checkout --ours" in json.dumps(side.command_preview_config)

    abort = ScenarioSkillFocus.objects.get(learning_unit=unit, slug="abort-conflicted-merge")
    assert abort.focus == "git merge --abort"

    diagnostics = ScenarioSkillFocus.objects.get(learning_unit=unit, slug="diagnose-conflict-state")
    assert diagnostics.skill_focus_type == ScenarioSkillFocus.SkillFocusType.CONCEPT_SPECIFIC
    assert "git ls-files" in diagnostics.primary_focus_commands
    assert "git diff --check" in diagnostics.supporting_diagnostic_commands

    capstone = ScenarioSkillFocus.objects.get(
        learning_unit=unit,
        slug="module3-integrated-conflict-workflow",
    )
    assert capstone.primary_focus_commands == [
        "git fetch",
        "git merge",
        "git mergetool",
        "git cherry-pick",
    ]


@override_settings(DEBUG=True)
def test_module_three_seeded_solutions_are_state_based_and_command_supported(db):
    call_command("seed_module3_scenarios", "--reset", "--confirm", "--validate-build")
    parser = GitCommandParser()
    registry = GitCommandRegistry()

    for variant in ScenarioVariant.objects.filter(
        scenario__learning_unit__slug="conflict-resolution",
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

    for scenario in ScenarioSkillFocus.objects.filter(
        learning_unit__slug="conflict-resolution",
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
