import json

import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import IntegrityError, transaction
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APIClient

from learning.models import LearningUnit, Lesson
from scenarios.command_content import GIT_COMMAND_CONTENT_LIBRARY
from scenarios.models import (
    CommandCountPolicy,
    DifficultyInstance,
    GitCommandContent,
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
def test_module_one_authored_variant_seed_matches_v3_contract(db):
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
    anchor_html = "\n".join(
        Lesson.objects.filter(unit__slug="local-repository-foundations", is_published=True)
        .order_by("sort_order")
        .values_list("content_html", flat=True)
    ).lower()
    assert "internal scenario anchor" in anchor_html
    assert "overview explains" not in anchor_html
    assert "start a generated" not in anchor_html
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
        ScenarioVariant.objects.filter(
            scenario__learning_unit__slug="local-repository-foundations",
            is_published=True,
        ).count()
        >= 65
    )
    assert not ScenarioVariant.objects.filter(
        scenario__learning_unit__slug="local-repository-foundations",
        case_id="",
    ).exists()
    assert not ScenarioVariant.objects.filter(
        scenario__learning_unit__slug="local-repository-foundations",
        semantic_key="",
    ).exists()


@override_settings(DEBUG=True)
def test_module_one_seed_uses_authored_cases_and_preview_only_diagnostics(db):
    call_command("seed_module1_scenarios", "--reset", "--confirm")

    for difficulty in DifficultyInstance.objects.filter(
        scenario__learning_unit__slug="local-repository-foundations",
        is_published=True,
    ):
        variants = list(difficulty.variants.filter(is_published=True))
        assert variants
        assert len({variant.case_id for variant in variants}) == len(variants)
        assert len({variant.semantic_key for variant in variants}) == len(variants)
        assert all(variant.student_context for variant in variants)
        assert all(variant.solution_commands for variant in variants)

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
def test_clone_authored_variants_cover_branch_depth_and_destination_forms(db):
    call_command("seed_module1_scenarios", "--reset", "--confirm", "--validate-build")

    commands = []
    cases = []
    for variant in ScenarioVariant.objects.filter(
        difficulty_instance__scenario__slug="clone-remote-repository",
        is_published=True,
    ):
        cases.append(variant.parameter_context)
        commands.extend(variant.solution_commands)

    assert any(command == "git clone https://example.test/training/docs-portal.git" for command in commands)
    assert any(command.endswith(" api-workshop") for command in commands)
    assert any("git@example.test:" in command for command in commands)
    assert any(command.startswith("git clone -b starter ") for command in commands)
    assert any(command.startswith("git clone --branch starter ") for command in commands)
    assert any(command.startswith("git clone --depth 1 ") for command in commands)
    assert any(case["selected_branch"] != "main" for case in cases)
    assert any(case["clone_shallow"] is True and case["clone_depth"] == 1 for case in cases)


@override_settings(DEBUG=True)
def test_gitignore_variants_require_creating_gitignore_file(db):
    call_command("seed_module1_scenarios", "--reset", "--confirm", "--validate-build")

    variants = ScenarioVariant.objects.filter(
        difficulty_instance__scenario__slug="configure-gitignore-rules",
        is_published=True,
    )

    assert variants
    assert all(".gitignore" not in variant.initial_state["working_tree"] for variant in variants)
    assert all(variant.solution_commands[0].startswith("printf ") for variant in variants)
    assert all(
        any(rule.get("type") == "gitignore_matches_paths" for rule in variant.target_rule["rules"])
        for variant in variants
    )
    preview_payload = json.dumps(
        ScenarioSkillFocus.objects.get(slug="configure-gitignore-rules").command_preview_config
    )
    assert "printf" in preview_payload
    assert "<content>" in preview_payload
    assert all(variant.solution_commands[0] not in preview_payload for variant in variants)


@override_settings(DEBUG=True)
def test_authored_variant_semantic_key_is_unique_per_difficulty(db):
    call_command("seed_module1_scenarios", "--reset", "--confirm")
    variant = ScenarioVariant.objects.filter(is_published=True).first()

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            ScenarioVariant.objects.create(
                scenario=variant.scenario,
                difficulty_instance=variant.difficulty_instance,
                slug=f"{variant.slug}-copy",
                label=variant.label,
                structure_signature=variant.structure_signature,
                initial_state=variant.initial_state,
                target_state=variant.target_state,
                target_rule=variant.target_rule,
                expected_state_diagram=variant.expected_state_diagram,
                solution_commands=variant.solution_commands,
                case_id=variant.case_id,
                semantic_key=variant.semantic_key,
                parameter_context=variant.parameter_context,
                student_context=variant.student_context,
                is_published=True,
            )


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
    first_ref = first.command_preview_config["command_refs"][0]
    assert first_ref["id"].startswith("git-status")
    assert first_ref["key"] == "git-status"
    assert first_ref["command"] == "git status"
    assert "overview" in first_ref["include_page_ids"]
    ref_keys = [ref["key"] for ref in first.command_preview_config["command_refs"]]
    assert ref_keys.count("git-log") >= 1
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


@override_settings(DEBUG=True)
def test_lesson_scoped_scenario_route_is_gone_and_module_list_still_works(db):
    call_command("seed_module1_scenarios", "--reset", "--confirm")
    user = get_user_model().objects.create_user(
        username="scenario-list@example.com",
        email="scenario-list@example.com",
        password="Password123!",
    )
    client = APIClient()
    client.force_authenticate(user)
    unit = LearningUnit.objects.get(slug="local-repository-foundations")
    lesson = Lesson.objects.filter(unit=unit).first()

    lesson_response = client.get(f"/api/scenarios/lessons/{lesson.id}/")
    module_response = client.get(f"/api/scenarios/modules/{unit.id}/")

    assert lesson_response.status_code == status.HTTP_404_NOT_FOUND
    assert module_response.status_code == status.HTTP_200_OK
    assert len(module_response.data) == 9
    assert module_response.data[0]["learning_unit_id"] == unit.id


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
                    "templates": [
                            {
                                "slug": "dupe",
                                "initial_state_template": {
                                    "repository_initialized": True,
                                    "commits": [],
                                    "branches": {"main": None},
                                    "head": {"type": "branch", "name": "main"},
                                    "working_tree": {},
                                    "staging": {},
                                    "conflicts": [],
                                },
                                "target_rule_template": {"repository_state_unchanged": True},
                                "cases": [
                                    {"case_id": "one", "answer_anchor": "one"},
                                    {"case_id": "two", "answer_anchor": "two"},
                            ],
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
                    "templates": [
                        {
                            "slug": "missing",
                            "slug_template": "missing-{{case_id}}",
                            "label_template": "Missing {{missing_value}}",
                            "structure_key": "missing",
                            "cases": [{"case_id": "one", "answer_anchor": "one"}],
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
                    "templates": [
                        {
                            "slug": "unused",
                            "slug_template": "unused-{{case_id}}",
                            "label_template": "Unused {{case_id}}",
                            "structure_key": "unused",
                            "cases": [
                                {
                                    "case_id": "one",
                                    "answer_anchor": "one",
                                    "dead_metadata": "not referenced",
                                }
                            ],
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


@override_settings(DEBUG=True)
def test_module_one_seed_rejects_empty_target_rules(db):
    command = __import__(
        "learning.management.commands.seed_module1_scenarios",
        fromlist=["Command"],
    ).Command()
    specs = [
        {
            "slug": "empty-target-rule-demo",
            "difficulties": {
                "easy": {
                    "templates": [
                        {
                            "slug": "empty-rule",
                            "slug_template": "empty-rule-{{case_id}}",
                            "label_template": "Empty rule {{case_id}}",
                            "structure_key": "empty-rule",
                            "cases": [{"case_id": "one", "answer_anchor": "one"}],
                            "initial_state_template": {"repository_initialized": True},
                            "target_rule_template": {},
                            "solution_commands_template": ["git status"],
                            "student_context_template": {"summary": "Inspect status."},
                        }
                    ]
                }
            },
        }
    ]

    with pytest.raises(CommandError, match="authored variant has no target_rule"):
        command._validate_seed_specs(specs)
