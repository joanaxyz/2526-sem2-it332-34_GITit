from django.core.management import call_command

from learning.models import FoundationTopic, LearningModule
from scenarios.context import StudentContextNormalizer
from scenarios.models import (
    CommandDrill,
    CommandTopic,
    PracticeKind,
    PracticeSession,
    WorkflowScenario,
    WorkflowScenarioLevel,
)
from scenarios.selectors import module_content_page
from scenarios.services import CommandProcessingService, PracticeSessionService
from scenarios.visualization import RepositoryVisualizationService


def make_user(django_user_model, username: str = "student"):
    return django_user_model.objects.create_user(
        username=username,
        email=f"{username}@example.com",
        password="pass12345",
    )


def test_seed_curriculum_v2_creates_foundations_and_separate_problem_types(db):
    call_command("seed_curriculum_v2")

    assert FoundationTopic.objects.count() >= 2
    assert not LearningModule.objects.filter(number=0).exists()
    assert CommandTopic.objects.filter(base_command="git add").exists()
    assert CommandDrill.objects.filter(usage__usage_form="git add <file>").exists()
    scenario = WorkflowScenario.objects.get(slug="stage-commit-switch")
    assert set(scenario.levels.values_list("difficulty", flat=True)) == {"easy", "medium", "hard"}


def test_command_drill_sessions_do_not_use_difficulty(db, django_user_model):
    call_command("seed_curriculum_v2")
    user = make_user(django_user_model)
    drill = CommandDrill.objects.get(slug="read-status")

    session = PracticeSessionService().start_session(
        user=user,
        problem=drill,
        source_entry_point="module_page",
    )

    assert session.practice_kind == PracticeKind.COMMAND_DRILL
    assert session.difficulty == ""
    assert session.command_drill == drill


def test_workflow_scenario_sessions_use_levels(db, django_user_model):
    call_command("seed_curriculum_v2")
    user = make_user(django_user_model)
    level = WorkflowScenarioLevel.objects.get(scenario__slug="stage-commit-switch", difficulty="easy")

    session = PracticeSessionService().start_session(
        user=user,
        problem=level,
        source_entry_point="module_page",
    )

    assert session.practice_kind == PracticeKind.WORKFLOW_SCENARIO
    assert session.difficulty == "easy"
    assert session.workflow_level == level


def test_module_content_is_paginated_by_section(db, django_user_model):
    call_command("seed_curriculum_v2")
    user = make_user(django_user_model)
    module = LearningModule.objects.get(slug="creating-inspecting-repositories")

    first_page = module_content_page(
        user=user,
        module_id=module.id,
        section="command_topics",
        limit=2,
    )

    assert first_page["results"]
    assert first_page["results"][0]["item_type"] == "command_topic"
    assert first_page["next_cursor"] is not None


def test_student_context_normalizer_strips_answers_and_evaluator_internals():
    context = StudentContextNormalizer().normalize(
        {
            "schema_version": 2,
            "brief": {"story": "Reach the target."},
            "objective": {
                "required_details": [{"label": "File", "value": "app.py"}],
            },
            "solution_commands": ["git add app.py"],
            "required_commands": ["git add"],
            "evaluation_spec": {"state_requirements": {"staging_contains": ["app.py"]}},
        }
    )

    flattened = str(context).lower()
    assert "git add" not in flattened
    assert "evaluation_spec" not in flattened
    assert context["objective"]["required_details"] == [{"label": "File", "value": "app.py"}]


def test_visualization_state_lens_and_delta_work_without_new_commits():
    before = {
        "repository_initialized": True,
        "commits": [{"id": "c0", "message": "Base", "parents": [], "tree": {"app.py": "old"}}],
        "branches": {"main": "c0"},
        "head": {"type": "branch", "name": "main"},
        "working_tree": {"app.py": "new"},
        "staging": {},
        "conflicts": [],
    }
    after = {
        **before,
        "working_tree": {},
        "staging": {"app.py": "new"},
    }

    payload = RepositoryVisualizationService().snapshot(after, previous_state=before)

    assert [commit["id"] for commit in payload["commit_dag"]["commits"]] == ["c0"]
    assert payload["state_lens"]["staging_area"][0]["path"] == "app.py"
    assert payload["command_effect_delta"]["files_staged"] == ["app.py"]
    assert payload["command_effect_delta"]["commits_created"] == []


def test_status_drill_completes_with_explicit_process_requirement(db, django_user_model):
    call_command("seed_curriculum_v2")
    user = make_user(django_user_model)
    drill = CommandDrill.objects.get(slug="read-status")
    session = PracticeSessionService().start_session(
        user=user,
        problem=drill,
        source_entry_point="module_page",
    )

    result = CommandProcessingService().submit_command(session=session, command="git status")

    session.refresh_from_db()
    assert result["evaluation_result"] == "TargetMatched"
    assert session.status == "completed"
    assert PracticeSession.objects.filter(user=user, command_drill=drill).count() == 1
