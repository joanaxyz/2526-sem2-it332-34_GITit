import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import override_settings

from learning.models import Lesson
from scenarios.command_content import GIT_COMMAND_CONTENT_LIBRARY
from scenarios.models import (
    CommandCountPolicy,
    DifficultyInstance,
    GitCommandContent,
    ScenarioGenerationBlueprint,
    ScenarioSkillFocus,
    ScenarioVariant,
)
from simulator.git_commands import GitCommandParser, GitCommandRegistry


def _example_command(command: str) -> str:
    replacements = {
        "<path>": "demo.txt",
        "<directory>": "demo-repo",
        "<url>": "https://example.test/repo.git",
        "<folder>": "repo-copy",
        "<branch>": "feature",
        "<name>": "origin",
        "<old>": "origin",
        "<new>": "upstream",
        "<commit>": "c1",
        "<number>": "2",
    }
    example = command
    for placeholder, value in replacements.items():
        example = example.replace(placeholder, value)
    return example


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

    assert (
        Lesson.objects.filter(unit__slug="local-repository-foundations", is_published=True).count()
        == 9
    )
    assert (
        list(
            ScenarioSkillFocus.objects.filter(
                learning_unit__slug="local-repository-foundations",
                is_published=True,
            )
            .order_by("sort_order")
            .values_list("slug", flat=True)
        )
        == expected_slugs
    )
    assert (
        DifficultyInstance.objects.filter(
            scenario__learning_unit__slug="local-repository-foundations",
            is_published=True,
        ).count()
        == 24
    )
    assert (
        CommandCountPolicy.objects.filter(
            difficulty_instance__scenario__learning_unit__slug="local-repository-foundations",
        ).count()
        == 24
    )
    assert (
        ScenarioGenerationBlueprint.objects.filter(
            difficulty_instance__scenario__learning_unit__slug="local-repository-foundations",
            is_published=True,
        ).count()
        >= 24
    )
    assert (
        ScenarioVariant.objects.filter(
            scenario__learning_unit__slug="local-repository-foundations",
        ).count()
        == 0
    )


@override_settings(DEBUG=True)
def test_module_one_seed_uses_authored_cases_and_preview_only_diagnostics(db):
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
        if (
            difficulty.scenario.slug == "initialize-local-repository"
            and difficulty.difficulty == "easy"
        ):
            assert difficulty.required_successful_attempts == 1
        else:
            assert difficulty.required_successful_attempts == (
                3 if difficulty.difficulty == "easy" else 2
            )

    preview = ScenarioSkillFocus.objects.get(slug="inspect-repository-state")
    assert preview.difficulty_instances.filter(is_published=True).count() == 0
    assert preview.command_preview_config["diagnostic"] is True
    assert not DifficultyInstance.objects.filter(completion_type="inspection").exists()


@override_settings(DEBUG=True)
def test_clone_blueprints_cover_branch_depth_and_destination_forms(db):
    call_command("seed_module1_scenarios", "--reset", "--confirm", "--validate-build")

    commands = []
    cases = []
    for blueprint in ScenarioGenerationBlueprint.objects.filter(
        difficulty_instance__scenario__slug="clone-remote-repository",
        is_published=True,
    ):
        cases.extend(blueprint.parameter_pools["cases"])
        commands.extend(case["solution_command"] for case in blueprint.parameter_pools["cases"])

    assert any(command == "git clone https://example.test/training/docs-portal.git" for command in commands)
    assert any(command.endswith(" api-workshop") for command in commands)
    assert any("git@example.test:" in command for command in commands)
    assert any(command.startswith("git clone -b starter ") for command in commands)
    assert any(command.startswith("git clone --branch starter ") for command in commands)
    assert any(command.startswith("git clone --depth 1 ") for command in commands)
    assert any(case["selected_branch"] != "main" for case in cases)
    assert any(case["clone_shallow"] is True and case["clone_depth"] == 1 for case in cases)


@override_settings(DEBUG=True)
def test_diagnostic_command_preview_is_first_module_one_scenario(db):
    call_command("seed_module1_scenarios", "--reset", "--confirm")

    first = (
        ScenarioSkillFocus.objects.filter(
            learning_unit__slug="local-repository-foundations",
            is_published=True,
        )
        .order_by("sort_order")
        .first()
    )

    assert first.slug == "inspect-repository-state"
    assert first.difficulty_instances.filter(is_published=True).count() == 0
    assert first.safe_demo_commands[:7] == [
        "git status",
        "git log --oneline",
        "git diff",
        "git diff --staged",
        "git show",
        "git branch",
        "git remote -v",
    ]
    assert first.command_preview_config["focus_label"] == "diagnostic commands"
    assert GitCommandContent.objects.filter(key="git-status", is_active=True).exists()
    assert len(first.command_preview_config["command_refs"]) >= 7
    assert first.command_preview_config["command_refs"][0] == {
        "id": "git-status",
        "key": "git-status",
        "command": "git status",
    }
    ref_keys = [ref["key"] for ref in first.command_preview_config["command_refs"]]
    assert ref_keys.count("git-log") == 1
    assert "git log --oneline" in first.safe_demo_commands
    assert "git log --oneline --graph --all" in first.safe_demo_commands
    status_content = GitCommandContent.objects.get(key="git-status", is_active=True)
    log_content = GitCommandContent.objects.get(key="git-log", is_active=True)
    assert status_content.base_command == "git status"
    assert status_content.sections[0]["type"] == "overview"
    assert any(section["type"] == "option" for section in status_content.sections)
    assert log_content.base_command == "git log"
    assert [section["title"] for section in log_content.sections[:4]] == [
        "Overview",
        "Reading History",
        "Compact History",
        "Visual Branch History",
    ]
    assert any(
        section["type"] == "option" and section["token"] == "--oneline"
        for section in log_content.sections
    )
    assert "sections" not in first.command_preview_config


def test_command_content_documents_only_simulator_supported_forms():
    parser = GitCommandParser()
    registry = GitCommandRegistry()

    for definition in GIT_COMMAND_CONTENT_LIBRARY:
        for section in definition["sections"]:
            command = section.get("command")
            if command and str(command).startswith("git "):
                parsed = parser.parse(_example_command(command))
                spec = registry.get(parsed.subcommand)
                assert spec is not None, command
                assert spec.validate(parsed) is None, command
            for block in section.get("content", []):
                if block.get("type") != "command":
                    continue
                for command in block.get("items", []):
                    if not str(command).startswith("git "):
                        continue
                    parsed = parser.parse(_example_command(command))
                    spec = registry.get(parsed.subcommand)
                    assert spec is not None, command
                    assert spec.validate(parsed) is None, command


@override_settings(DEBUG=True)
def test_module_one_preview_commands_are_supported_by_simulator(db):
    call_command("seed_module1_scenarios", "--reset", "--confirm")
    parser = GitCommandParser()
    registry = GitCommandRegistry()

    for scenario in ScenarioSkillFocus.objects.filter(
        learning_unit__slug="local-repository-foundations",
        is_published=True,
    ):
        preview = scenario.command_preview_config or {}
        commands = [
            *preview.get("supported_demo_commands", []),
            *[
                ref.get("command")
                for ref in preview.get("command_refs", [])
                if isinstance(ref, dict) and ref.get("command")
            ],
        ]
        for command in commands:
            parsed = parser.parse(_example_command(command))
            spec = registry.get(parsed.subcommand)
            assert spec is not None, command
            assert spec.validate(parsed) is None, command


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


@override_settings(DEBUG=True)
def test_module_one_seed_rejects_missing_placeholders(db):
    command = __import__(
        "learning.management.commands.seed_module1_scenarios",
        fromlist=["Command"],
    ).Command()
    specs = [
        {
            "slug": "missing-placeholder-demo",
            "difficulties": {
                "easy": {
                    "blueprints": [
                        {
                            "slug": "missing",
                            "slug_template": "missing-{{case_id}}",
                            "label_template": "Missing {{missing_value}}",
                            "subtemplate_signature": "missing",
                            "parameter_pools": {
                                "cases": [{"case_id": "one", "answer_anchor": "one"}]
                            },
                            "initial_state_template": {},
                            "target_rule_template": {},
                            "solution_commands_template": ["git status"],
                            "student_context_template": {},
                        }
                    ]
                }
            },
        }
    ]

    with pytest.raises(CommandError, match="missing case fields"):
        command._validate_seed_specs(specs)


@override_settings(DEBUG=True)
def test_module_one_seed_rejects_unused_case_fields(db):
    command = __import__(
        "learning.management.commands.seed_module1_scenarios",
        fromlist=["Command"],
    ).Command()
    specs = [
        {
            "slug": "unused-field-demo",
            "difficulties": {
                "easy": {
                    "blueprints": [
                        {
                            "slug": "unused",
                            "slug_template": "unused-{{case_id}}",
                            "label_template": "Unused {{case_id}}",
                            "subtemplate_signature": "unused",
                            "parameter_pools": {
                                "cases": [
                                    {
                                        "case_id": "one",
                                        "answer_anchor": "one",
                                        "dead_metadata": "not referenced",
                                    }
                                ]
                            },
                            "initial_state_template": {},
                            "target_rule_template": {},
                            "solution_commands_template": ["git status"],
                            "student_context_template": {},
                        }
                    ]
                }
            },
        }
    ]

    with pytest.raises(CommandError, match="unused case fields"):
        command._validate_seed_specs(specs)
