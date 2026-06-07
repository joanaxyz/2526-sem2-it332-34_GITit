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
from scenarios.selectors import module_content_page, storey_content_page
from scenarios.serializers import session_payload
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
        limit=1,
    )

    assert first_page["results"]
    assert first_page["results"][0]["item_type"] == "command_topic"
    assert first_page["next_cursor"] is not None


def test_storey_content_page_returns_command_adventures(db, django_user_model):
    call_command("seed_curriculum_v2")
    user = make_user(django_user_model)
    storey = LearningModule.objects.get(slug="creating-inspecting-repositories")

    page = storey_content_page(
        user=user,
        storey_id=storey.id,
        section="command_adventures",
    )

    assert page["results"]
    assert page["results"][0]["item_type"] == "command_drill_adventure"


def test_module_content_exposes_command_drill_adventure_levels_not_public_command_cards(db, django_user_model):
    call_command("seed_curriculum_v2")
    user = make_user(django_user_model)
    module = LearningModule.objects.get(slug="tracking-changes-snapshots")

    page = module_content_page(
        user=user,
        module_id=module.id,
        section="command_adventures",
        limit=8,
    )

    assert page["results"]
    adventure = page["results"][0]
    assert adventure["item_type"] == "command_drill_adventure"
    assert adventure["title"] == "Preparing File Changes"
    assert [level["label"] for level in adventure["levels"]] == ["Level 1", "Level 2"]
    assert all("difficulty" not in level for level in adventure["levels"])
    assert all("base_command" not in level for level in adventure["levels"])
    assert adventure["levels"][0]["usage_count"] > 0
    assert adventure["levels"][0]["next_practice"]["practice_kind"] == PracticeKind.COMMAND_DRILL


def test_every_published_module_has_command_drill_adventure(db, django_user_model):
    call_command("seed_curriculum_v2")
    user = make_user(django_user_model)

    for module in LearningModule.objects.filter(is_published=True):
        page = module_content_page(
            user=user,
            module_id=module.id,
            section="command_adventures",
        )
        assert page["results"], module.slug
        assert page["results"][0]["levels"], module.slug


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


def test_visualization_payload_keeps_commit_dag_without_extra_lenses():
    state = {
        "repository_initialized": True,
        "commits": [{"id": "c0", "message": "Base", "parents": [], "tree": {"app.py": "old"}}],
        "branches": {"main": "c0"},
        "head": {"type": "branch", "name": "main"},
        "working_tree": {},
        "staging": {"app.py": "new"},
        "conflicts": [],
    }

    payload = RepositoryVisualizationService().snapshot(state)

    assert payload["schema_version"] == 2
    assert [commit["id"] for commit in payload["commit_dag"]["commits"]] == ["c0"]


def test_command_drill_payload_exposes_target_diagram(db, django_user_model):
    call_command("seed_curriculum_v2")
    user = make_user(django_user_model)
    drill = CommandDrill.objects.get(slug="stage-one-file")
    session = PracticeSessionService().start_session(
        user=user,
        problem=drill,
        source_entry_point="module_page",
    )

    payload = session_payload(session)

    assert payload["scaffolding"]["live_dag"] is True
    assert payload["scaffolding"]["expected_state"] is True
    assert payload["expected_state"] is not None
    assert "target_state" not in payload["scaffolding"]
    assert payload["difficulty"] is None


def test_workflow_hard_payload_hides_expected_state(db, django_user_model):
    call_command("seed_curriculum_v2")
    user = make_user(django_user_model)
    level = WorkflowScenarioLevel.objects.get(scenario__slug="stage-commit-switch", difficulty="hard")
    variant = level.variants.get(is_published=True)
    session = PracticeSession.objects.create(
        user=user,
        module=level.module,
        practice_kind=PracticeKind.WORKFLOW_SCENARIO,
        workflow_scenario=level.scenario,
        workflow_level=level,
        variant=variant,
        source_entry_point="module_page",
        difficulty=level.difficulty,
        command_budget_snapshot={
            "min_counted_commands": level.min_counted_commands,
            "max_counted_commands": level.max_counted_commands,
        },
        repository_state=variant.initial_state,
    )

    payload = session_payload(session)

    assert payload["scaffolding"]["expected_state"] is False
    assert payload["expected_state"] is None


def test_unsupported_command_levels_are_not_published(db):
    call_command("seed_curriculum_v2")

    published_commands = set(
        CommandTopic.objects.filter(is_published=True).values_list("base_command", flat=True)
    )

    assert published_commands == {"git init", "git status", "git add", "git commit", "git switch"}
    assert not LearningModule.objects.filter(slug="integrated-workflows", is_published=True).exists()
    assert not CommandTopic.objects.filter(base_command="git clone", is_published=True).exists()


def test_seed_curriculum_v2_validate_passes_for_published_content(db):
    call_command("seed_curriculum_v2", validate=True)


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
