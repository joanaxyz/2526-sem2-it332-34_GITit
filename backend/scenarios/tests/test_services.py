import json
import logging
import time

import pytest
from django.contrib.auth import get_user_model
from django.test import override_settings
from django.core.management import call_command
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.utils import timezone
from rest_framework.test import APIRequestFactory, force_authenticate

from common.constants import (
    COMMAND_COUNTED,
    COMMAND_DIAGNOSTIC,
    COMMAND_UNPROCESSABLE,
    RESULT_INVALID,
    SESSION_MODE_REVIEW,
    SESSION_STATUS_COMPLETED,
    SESSION_STATUS_FAILED,
    SESSION_STATUS_STARTED,
)
from common.exceptions import Locked
from learning.models import Lesson, OrientationProgress
from progress.models import StreakRecord, StudentProgress
from retries.services import VariantSelectionService
from review.services import ReviewModeService
from scenarios.builders import ScenarioVariantBuildError
from scenarios.models import (
    CompletionRecord,
    DifficultyInstance,
    GitCommandContent,
    ScenarioSession,
    ScenarioSkillFocus,
    ScenarioVariant,
    StepLog,
)
from scenarios.selectors import scenario_status_payload, scenario_status_payloads
from scenarios.serializers import prefetch_session_payload_context, session_payload
from scenarios.services import (
    CommandCountClassifier,
    CommandProcessingService,
    ScenarioSessionService,
)
from scenarios.views import (
    CommandSubmitAPIView,
    ScenarioRetryAPIView,
    SkillFocusDemoCommandAPIView,
    SkillFocusDetailAPIView,
    WorkspaceFileCreateAPIView,
)


@pytest.fixture()
def seeded_content(db):
    call_command("seed_module1_scenarios")


@pytest.fixture()
def student(db, seeded_content):
    user = get_user_model().objects.create_user(
        username="student@example.com",
        email="student@example.com",
        password="Password123!",
        first_name="Student",
    )
    StudentProgress.objects.create(user=user)
    StreakRecord.objects.create(user=user)
    for lesson in Lesson.objects.filter(unit__is_orientation=True):
        OrientationProgress.objects.create(
            user=user, lesson=lesson, completed_at="2026-05-18T00:00:00Z"
        )
    return user


def complete_accurate_session(*, user, difficulty):
    session = ScenarioSessionService().start_session(
        user=user,
        difficulty_instance=difficulty,
        source_entry_point="module_card",
    )
    for command in session.variant.solution_commands:
        CommandProcessingService().submit_command(session=session, command=command)
        session.refresh_from_db()
        if session.status == SESSION_STATUS_COMPLETED:
            break
    return session


def complete_required_accurate_sessions(*, user, difficulty):
    sessions = [
        complete_accurate_session(user=user, difficulty=difficulty)
        for _ in range(difficulty.required_successful_attempts)
    ]
    return sessions[-1]


def test_primary_session_can_start_before_orientation_completion(db, seeded_content):
    user = get_user_model().objects.create_user(
        username="new@example.com",
        email="new@example.com",
        password="Password123!",
        first_name="New",
    )
    StudentProgress.objects.create(user=user)
    StreakRecord.objects.create(user=user)
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="stage-and-commit-basic-workflow",
        difficulty="easy",
    )

    session = ScenarioSessionService().start_session(
        user=user,
        difficulty_instance=difficulty,
        source_entry_point="module_card",
    )

    assert session.status == "started"
    assert session.orientation_complete_at_start is False


def test_git_status_command_response_omits_project_tree(student):
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="stage-and-commit-basic-workflow",
        difficulty="easy",
    )
    session = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="module_card",
    )

    response = CommandProcessingService().submit_command(session=session, command="git status")

    assert "project_tree" not in response["repository_state"]
    assert "visible_tree" not in response["repository_state"]
    assert response["repository_state"]["commits"]


def test_git_status_command_submit_completes_within_performance_budget(student):
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="stage-and-commit-basic-workflow",
        difficulty="easy",
    )
    session = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="module_card",
    )
    service = CommandProcessingService()

    start = time.perf_counter()
    service.submit_command(session=session, command="git status")
    elapsed_ms = (time.perf_counter() - start) * 1000

    assert elapsed_ms < 750, f"git status submit took {elapsed_ms:.1f}ms"


COMMAND_SUBMIT_TIMING_SPANS = (
    "scenario.command.repository_state_clone",
    "scenario.command.parse_execute",
    "scenario.command.repository_state_normalize",
    "scenario.command.state_hash",
    "scenario.command.expected_state_hash",
    "scenario.command.evaluation",
    "scenario.command.repository_snapshot",
)


def test_command_submit_emits_performance_timing_spans(student, caplog):
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="stage-and-commit-basic-workflow",
        difficulty="easy",
    )
    session = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="module_card",
    )

    with override_settings(PERFORMANCE_TIMING_ENABLED=True):
        with caplog.at_level(logging.INFO, logger="git_it.performance"):
            CommandProcessingService().submit_command(session=session, command="git status")
            session.refresh_from_db()
            CommandProcessingService().submit_command(session=session, command="git add .")

    messages = "\n".join(record.message for record in caplog.records)
    for span in COMMAND_SUBMIT_TIMING_SPANS:
        assert span in messages, f"missing timing span: {span}"


def test_module4_git_status_command_submit_completes_within_performance_budget(student):
    call_command("seed_module4_scenarios", "--reset", "--confirm", "--validate-build")
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="recover-from-hard-reset-incident",
        difficulty="easy",
    )
    session = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="module_card",
    )
    service = CommandProcessingService()

    start = time.perf_counter()
    service.submit_command(session=session, command="git status")
    elapsed_ms = (time.perf_counter() - start) * 1000

    assert elapsed_ms < 1500, f"module 4 git status submit took {elapsed_ms:.1f}ms"


def test_diagnostic_commands_are_logged_but_not_counted(student):
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="stage-and-commit-basic-workflow",
        difficulty="easy",
    )
    session = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="module_card",
    )

    assert session.variant.difficulty_instance_id == difficulty.id

    response = CommandProcessingService().submit_command(session=session, command="git status")

    session.refresh_from_db()
    assert response["command_classification"] == COMMAND_DIAGNOSTIC
    assert "On branch" in response["terminal_output"]
    assert "Only simulated" not in response["terminal_output"]
    assert session.counted_action_total == 0
    assert session.non_counted_diagnostic_total == 1


def test_command_submit_response_uses_lightweight_in_progress_payload(student):
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="stage-and-commit-basic-workflow",
        difficulty="easy",
    )
    session = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="module_card",
    )
    request = APIRequestFactory().post(
        f"/api/scenarios/sessions/{session.id}/commands/",
        {"command": "git status"},
        format="json",
    )
    force_authenticate(request, user=student)

    response = CommandSubmitAPIView.as_view()(request, session_id=session.id)

    assert response.status_code == 200
    payload = response.data["session"]
    assert payload["id"] == session.id
    assert payload["status"] == SESSION_STATUS_STARTED
    assert payload["repository_state"]["branches"] == session.repository_state["branches"]
    assert payload["counts"]["non_counted_diagnostic_total"] == 1
    assert response.data["step"]["command_text"] == "git status"
    assert response.data["step"]["contextual_feedback"]
    assert "scenario" not in payload
    assert "module" not in payload
    assert "unit" not in payload
    assert "expected_state" not in payload
    assert "steps" not in payload
    assert "policy" not in payload
    assert "scaffolding" not in payload
    assert "next_difficulty" not in payload
    assert "completion" not in payload


def test_workspace_file_create_response_updates_project_tree_without_counting(student):
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="stage-and-commit-basic-workflow",
        difficulty="easy",
    )
    session = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="module_card",
    )
    request = APIRequestFactory().post(
        f"/api/scenarios/sessions/{session.id}/files/",
        {"path": "src/generated.py", "content": "print('hello')\n"},
        format="json",
    )
    force_authenticate(request, user=student)

    response = WorkspaceFileCreateAPIView.as_view()(request, session_id=session.id)

    assert response.status_code == 200
    session.refresh_from_db()
    assert session.repository_state["working_tree"]["src/generated.py"] == {
        "status": "untracked",
        "content": "print('hello')\n",
    }
    assert response.data["repository_state"]["project_tree"]["src/generated.py"] == {
        "status": "untracked",
        "source": "working_tree",
        "content": "print('hello')\n",
    }
    assert response.data["counts"]["total_attempts"] == 0
    assert response.data["steps"] == []


def test_workspace_file_write_response_updates_project_tree_without_counting(student):
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="stage-and-commit-basic-workflow",
        difficulty="easy",
    )
    session = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="module_card",
    )
    request = APIRequestFactory().patch(
        f"/api/scenarios/sessions/{session.id}/files/",
        {"path": "README.md", "content": "readme-v2\n"},
        format="json",
    )
    force_authenticate(request, user=student)

    response = WorkspaceFileCreateAPIView.as_view()(request, session_id=session.id)

    assert response.status_code == 200
    session.refresh_from_db()
    assert session.repository_state["working_tree"]["README.md"] == {
        "status": "modified",
        "content": "readme-v2\n",
    }
    assert response.data["repository_state"]["project_tree"]["README.md"] == {
        "status": "modified",
        "source": "working_tree",
        "content": "readme-v2\n",
    }
    assert response.data["counts"]["total_attempts"] == 0
    assert response.data["steps"] == []


def test_command_submit_in_progress_query_count_is_bounded(student):
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="stage-and-commit-basic-workflow",
        difficulty="easy",
    )
    session = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="module_card",
    )
    request = APIRequestFactory().post(
        f"/api/scenarios/sessions/{session.id}/commands/",
        {"command": "git status"},
        format="json",
    )
    force_authenticate(request, user=student)

    with CaptureQueriesContext(connection) as captured:
        response = CommandSubmitAPIView.as_view()(request, session_id=session.id)

    assert response.status_code == 200
    assert len(captured) <= 10


def test_command_submit_completion_payload_keeps_progress_without_full_metadata(student):
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="stage-and-commit-basic-workflow",
        difficulty="easy",
    )
    session = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="module_card",
    )
    response = None
    for command in session.variant.solution_commands:
        request = APIRequestFactory().post(
            f"/api/scenarios/sessions/{session.id}/commands/",
            {"command": command},
            format="json",
        )
        force_authenticate(request, user=student)
        response = CommandSubmitAPIView.as_view()(request, session_id=session.id)
        session.refresh_from_db()
        if response.data["session"]["status"] == SESSION_STATUS_COMPLETED:
            break

    assert response is not None
    payload = response.data["session"]
    assert payload["status"] == SESSION_STATUS_COMPLETED
    assert payload["mastery_progress"]["required"] == difficulty.required_successful_attempts
    assert "completion" in payload
    assert "next_difficulty" in payload
    assert "scenario" not in payload
    assert "module" not in payload
    assert "expected_state" not in payload
    assert "steps" not in payload


def test_diagnostic_command_preview_does_not_create_playable_records(student):
    preview = ScenarioSkillFocus.objects.get(slug="inspect-repository-state")
    assert preview.difficulty_instances.filter(is_published=True).count() == 0

    request = APIRequestFactory().post(
        "/api/scenarios/inspect-repository-state/demo-command/",
        {"command": "git status"},
        format="json",
    )
    force_authenticate(request, user=student)
    response = SkillFocusDemoCommandAPIView.as_view()(request, slug=preview.slug)

    assert response.status_code == 200
    assert response.data["command_classification"] == "diagnostic"
    assert ScenarioSession.objects.filter(user=student).count() == 0
    assert CompletionRecord.objects.filter(user=student).count() == 0
    assert StepLog.objects.count() == 0


def test_state_based_completion_creates_completion_record(student):
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="stage-and-commit-basic-workflow",
        difficulty="easy",
    )
    session = complete_required_accurate_sessions(user=student, difficulty=difficulty)

    session.refresh_from_db()
    completion = CompletionRecord.objects.get(user=student, difficulty_instance=difficulty)
    assert session.status == "completed"
    assert completion.counted_action_total == 2


def test_session_payload_includes_completion_when_record_exists(student):
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="stage-and-commit-basic-workflow",
        difficulty="easy",
    )
    session = complete_required_accurate_sessions(user=student, difficulty=difficulty)

    session.refresh_from_db()
    payload = session_payload(session, include_steps=False)
    assert "completion" in payload and payload["completion"] is not None
    assert payload["completion"]["counted_action_total"] == 2
    assert payload["completion"]["first_attempt_star"] in (True, False)
    assert payload["completion"]["completed_at"] is not None


def test_session_payload_expected_state_uses_rich_snapshot_and_scaffolding(student):
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="stage-and-commit-basic-workflow",
        difficulty="easy",
    )
    session = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="module_card",
    )

    payload = session_payload(session, include_steps=False)
    latest_commit = payload["expected_state"]["commits"][-1]

    assert payload["scaffolding"]["expected_state"] is True
    assert latest_commit["message"]
    assert "tree" in latest_commit
    assert "changes" in latest_commit

    hard = DifficultyInstance.objects.get(
        scenario=difficulty.scenario,
        difficulty="hard",
    )
    hard_variant = hard.variants.filter(is_published=True).first()
    hard_session = ScenarioSession.objects.create(
        user=student,
        learning_unit=hard.scenario.learning_unit,
        scenario=hard.scenario,
        difficulty_instance=hard,
        variant=hard_variant,
        source_entry_point="module_card",
        command_policy_snapshot=hard.command_policy.snapshot(),
        repository_state=hard_variant.initial_state,
    )

    hard_payload = session_payload(hard_session, include_steps=False)

    assert hard_payload["scaffolding"]["expected_state"] is False
    assert hard_payload["expected_state"] is None


def test_starting_session_uses_seeded_authored_variant_with_student_context(student):
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="stage-and-commit-basic-workflow",
        difficulty="easy",
    )
    before_count = ScenarioVariant.objects.filter(difficulty_instance=difficulty).count()

    session = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="module_card",
    )
    variant = session.variant
    payload = session_payload(session, include_steps=False)
    serialized_payload = json.dumps(payload)

    assert (
        ScenarioVariant.objects.filter(difficulty_instance=difficulty).count()
        == before_count
    )
    assert variant.case_id
    assert variant.semantic_key
    assert variant.parameter_context
    assert variant.student_context
    assert variant.initial_state
    assert variant.target_rule
    assert variant.target_state
    assert variant.expected_state_diagram
    assert variant.solution_commands
    assert payload["student_context"] == variant.student_context
    assert payload["scenario"]["student_context"] == variant.student_context
    assert "task_prompt" not in payload["scenario"]
    assert "success_conditions" not in serialized_payload
    for command in variant.solution_commands:
        assert command not in serialized_payload


def test_session_payload_falls_back_for_old_variants_without_student_context(student):
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="stage-and-commit-basic-workflow",
        difficulty="easy",
    )
    session = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="module_card",
    )
    session.variant.student_context = {}
    session.variant.save(update_fields=["student_context"])
    session.refresh_from_db()

    payload = session_payload(session, include_steps=False)

    assert payload["student_context"]["story"] == session.difficulty_instance.narrative
    assert "situation" not in payload["student_context"]
    assert "task_prompt" not in payload["scenario"]


def test_new_session_payload_stays_within_query_budget(student):
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="stage-and-commit-basic-workflow",
        difficulty="easy",
    )
    session = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="module_card",
    )
    prefetch_session_payload_context(session)

    with CaptureQueriesContext() as context:
        payload = session_payload(session, include_steps=False)

    assert payload["variant"]["looped_variant"] is False
    assert payload["reviewable_difficulties"] == []
    assert len(context.captured_queries) <= 1


def test_active_session_payload_and_command_submit_do_not_create_variant(student):
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="stage-and-commit-basic-workflow",
        difficulty="easy",
    )
    session = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="module_card",
    )
    variant_id = session.variant_id
    variant_count = ScenarioVariant.objects.filter(difficulty_instance=difficulty).count()

    assert session_payload(session, include_steps=False)["variant"]["id"] == variant_id
    CommandProcessingService().submit_command(session=session, command="git status")
    session.refresh_from_db()

    assert session.variant_id == variant_id
    assert (
        ScenarioVariant.objects.filter(difficulty_instance=difficulty).count()
        == variant_count
    )


def test_authored_context_exposes_checked_values_without_solution_commands(student):
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="stage-and-commit-basic-workflow",
        difficulty="easy",
    )
    session = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="module_card",
    )
    variant = session.variant
    context_text = json.dumps(variant.student_context).lower()
    latest_commit_rule = variant.target_rule["latest_commit"]

    for message in latest_commit_rule["message_contains"]:
        assert message.lower() in context_text
    for path in latest_commit_rule["contains_paths"]:
        assert path.lower() in context_text
    for path in latest_commit_rule.get("excludes_paths", []):
        assert path.lower() in context_text
    assert variant.target_rule["head_branch"] in context_text
    for command in variant.solution_commands:
        assert command.lower() not in context_text


def test_authored_context_exposes_excluded_files_and_remote_values(student):
    ignore_difficulty = DifficultyInstance.objects.get(
        scenario__slug="configure-gitignore-rules",
        difficulty="easy",
    )
    ignore_session = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=ignore_difficulty,
        source_entry_point="module_card",
    )
    ignore_context = json.dumps(ignore_session.variant.student_context).lower()
    for path in ignore_session.variant.target_rule["latest_commit"]["excludes_paths"]:
        assert path.lower() in ignore_context

    clone_difficulty = DifficultyInstance.objects.get(
        scenario__slug="clone-remote-repository",
        difficulty="easy",
    )
    clone_session = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=clone_difficulty,
        source_entry_point="module_card",
    )
    clone_context = json.dumps(clone_session.variant.student_context).lower()
    for remote, url in clone_session.variant.target_rule["remote_url_matches"].items():
        assert remote.lower() in clone_context
        assert url.lower() in clone_context


def test_partial_staging_requires_the_selected_file_scope(student):
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="partial-staging-add-p",
        difficulty="easy",
    )
    session = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="module_card",
    )

    CommandProcessingService().submit_command(session=session, command="git add .")

    session.refresh_from_db()
    assert session.status == "started"
    assert not CompletionRecord.objects.filter(
        user=student, difficulty_instance=difficulty
    ).exists()

    ScenarioSessionService().abandon(session=session)
    retry = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="retry",
        prior_session=session,
    )

    for command in retry.variant.solution_commands:
        CommandProcessingService().submit_command(session=retry, command=command)
        retry.refresh_from_db()
        if retry.status == SESSION_STATUS_COMPLETED:
            break

    retry.refresh_from_db()
    assert retry.status == "completed"


def test_retry_after_failure_uses_changed_variant_when_available(student):
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="stage-and-commit-basic-workflow",
        difficulty="easy",
    )
    variant_count = ScenarioVariant.objects.filter(difficulty_instance=difficulty).count()
    prior = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="module_card",
    )
    prior.status = SESSION_STATUS_FAILED
    prior.save(update_fields=["status"])

    retry = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="retry",
        prior_session=prior,
    )

    assert retry.variant_id != prior.variant_id
    assert retry.variant.scenario_id == prior.variant.scenario_id == difficulty.scenario_id
    assert retry.variant.difficulty_instance_id == difficulty.id
    assert (
        retry.variant.scenario.primary_focus_commands
        == prior.variant.scenario.primary_focus_commands
    )
    assert retry.variant.semantic_key != prior.variant.semantic_key
    assert retry.variant.case_id != prior.variant.case_id
    assert retry.changed_variant is True
    assert retry.rta_eligible is True
    assert ScenarioVariant.objects.filter(difficulty_instance=difficulty).count() == variant_count


def test_retry_repeats_deterministically_when_only_one_authored_variant_is_available(student):
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="stage-and-commit-basic-workflow",
        difficulty="easy",
    )
    kept_variant = difficulty.variants.filter(is_published=True).order_by("id").first()
    difficulty.variants.exclude(id=kept_variant.id).update(is_published=False)
    prior = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="module_card",
    )
    prior.status = SESSION_STATUS_FAILED
    prior.save(update_fields=["status"])

    retry = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="retry",
        prior_session=prior,
    )

    assert retry.variant_id == prior.variant_id == kept_variant.id
    assert retry.changed_variant is False
    assert retry.rta_eligible is False


def test_retry_loops_after_all_available_variants_are_seen(student):
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="stage-and-commit-basic-workflow",
        difficulty="easy",
    )
    published = list(difficulty.variants.filter(is_published=True).order_by("semantic_key", "id"))
    keep_ids = [variant.id for variant in published[:2]]
    difficulty.variants.exclude(id__in=keep_ids).update(is_published=False)

    first = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="module_card",
    )
    first.status = SESSION_STATUS_FAILED
    first.ended_at = timezone.now()
    first.save(update_fields=["status", "ended_at"])

    second = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="retry",
        prior_session=first,
    )
    second.status = SESSION_STATUS_FAILED
    second.ended_at = timezone.now()
    second.save(update_fields=["status", "ended_at"])

    third = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="retry",
        prior_session=second,
    )

    assert second.variant_id != first.variant_id
    assert third.variant_id == first.variant_id
    assert third.variant_id != second.variant_id


def test_session_payload_marks_looped_variant_after_exhaustion(student):
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="stage-and-commit-basic-workflow",
        difficulty="easy",
    )
    published = list(difficulty.variants.filter(is_published=True).order_by("semantic_key", "id"))
    keep_ids = [variant.id for variant in published[:2]]
    difficulty.variants.exclude(id__in=keep_ids).update(is_published=False)

    first = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="module_card",
    )
    first.status = SESSION_STATUS_FAILED
    first.ended_at = timezone.now()
    first.save(update_fields=["status", "ended_at"])

    second = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="retry",
        prior_session=first,
    )
    second.status = SESSION_STATUS_FAILED
    second.ended_at = timezone.now()
    second.save(update_fields=["status", "ended_at"])

    third = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="retry",
        prior_session=second,
    )

    assert session_payload(second, include_steps=False)["variant"]["looped_variant"] is False
    assert session_payload(third, include_steps=False)["variant"]["looped_variant"] is True


def test_starting_session_without_authored_variants_fails_clearly(student):
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="stage-and-commit-basic-workflow",
        difficulty="easy",
    )
    difficulty.variants.update(is_published=False)

    with pytest.raises(ScenarioVariantBuildError, match="no published authored variants"):
        ScenarioSessionService().start_session(
            user=student,
            difficulty_instance=difficulty,
            source_entry_point="module_card",
        )


def test_semantic_variant_identity_uses_authored_case_key(student):
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="stage-and-commit-basic-workflow",
        difficulty="easy",
    )
    first = difficulty.variants.filter(is_published=True).first()
    same_case = ScenarioVariant(
        scenario=first.scenario,
        difficulty_instance=first.difficulty_instance,
        slug=f"{first.slug}-copy",
        label=first.label,
        structure_signature=first.structure_signature,
        initial_state=first.initial_state,
        target_state=first.target_state,
        target_rule=first.target_rule,
        expected_state_diagram=first.expected_state_diagram,
        solution_commands=first.solution_commands,
        case_id=first.case_id,
        semantic_key=first.semantic_key,
        parameter_context={**first.parameter_context, "index": 999},
        student_context=first.student_context,
        is_published=True,
    )

    assert (
        VariantSelectionService().changed_between(prior=first, current=same_case)
        is False
    )


def test_retry_from_active_session_requires_exit_first(student):
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="stage-and-commit-basic-workflow",
        difficulty="easy",
    )
    prior = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="module_card",
    )

    with pytest.raises(Locked, match="Exit the current scenario"):
        ScenarioSessionService().start_session(
            user=student,
            difficulty_instance=difficulty,
            source_entry_point="retry",
            prior_session=prior,
        )

    prior.refresh_from_db()
    assert prior.status == SESSION_STATUS_STARTED
    assert prior.ended_at is None
    assert (
        ScenarioSession.objects.filter(
            user=student,
            difficulty_instance=difficulty,
            status=SESSION_STATUS_STARTED,
        ).count()
        == 1
    )


def test_retry_does_not_create_duplicate_active_session(student):
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="stage-and-commit-basic-workflow",
        difficulty="easy",
    )
    prior = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="module_card",
    )
    prior.status = SESSION_STATUS_FAILED
    prior.ended_at = timezone.now()
    prior.save(update_fields=["status", "ended_at"])
    active = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="retry",
        prior_session=prior,
    )

    with pytest.raises(Locked, match="Exit the current scenario"):
        ScenarioSessionService().start_session(
            user=student,
            difficulty_instance=difficulty,
            source_entry_point="retry",
            prior_session=prior,
        )

    active.refresh_from_db()
    assert active.status == SESSION_STATUS_STARTED
    assert (
        ScenarioSession.objects.filter(
            user=student,
            difficulty_instance=difficulty,
            status=SESSION_STATUS_STARTED,
        ).count()
        == 1
    )


def test_retry_endpoint_starts_new_attempt_from_ended_session(student):
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="stage-and-commit-basic-workflow",
        difficulty="easy",
    )
    prior = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="module_card",
    )
    prior.status = SESSION_STATUS_FAILED
    prior.ended_at = timezone.now()
    prior.save(update_fields=["status", "ended_at"])
    request = APIRequestFactory().post(
        f"/api/scenarios/sessions/{prior.id}/retry/",
        format="json",
    )
    force_authenticate(request, user=student)

    response = ScenarioRetryAPIView.as_view()(request, session_id=prior.id)

    assert response.status_code == 201
    session = ScenarioSession.objects.get(id=response.data["id"])
    assert session.prior_session_id == prior.id
    assert session.status == SESSION_STATUS_STARTED
    assert session.source_entry_point == "retry"


def test_starting_active_difficulty_requires_exit_first(student):
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="stage-and-commit-basic-workflow",
        difficulty="easy",
    )
    active = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="module_card",
    )

    with pytest.raises(Locked, match="Exit the current scenario"):
        ScenarioSessionService().start_session(
            user=student,
            difficulty_instance=difficulty,
            source_entry_point="module_card",
        )

    active.refresh_from_db()
    assert active.status == SESSION_STATUS_STARTED
    assert (
        ScenarioSession.objects.filter(
            user=student,
            difficulty_instance=difficulty,
            status=SESSION_STATUS_STARTED,
        ).count()
        == 1
    )


def test_review_mode_logs_separately_without_new_completion(student):
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="stage-and-commit-basic-workflow",
        difficulty="easy",
    )
    complete_required_accurate_sessions(user=student, difficulty=difficulty)
    completion = CompletionRecord.objects.get(user=student, difficulty_instance=difficulty)
    variant_count = ScenarioVariant.objects.filter(difficulty_instance=difficulty).count()

    review_session = ReviewModeService().start_review_session(
        user=student, difficulty_instance=difficulty
    )

    assert review_session.mode == SESSION_MODE_REVIEW
    assert review_session.variant_id == completion.session.variant_id
    assert (
        ScenarioVariant.objects.filter(difficulty_instance=difficulty).count()
        == variant_count
    )
    assert (
        CompletionRecord.objects.filter(user=student, difficulty_instance=difficulty).count() == 1
    )
    assert ScenarioSession.objects.filter(user=student, mode=SESSION_MODE_REVIEW).count() == 1


def test_scenario_payload_includes_latest_attempt_accuracy(student):
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="stage-and-commit-basic-workflow",
        difficulty="easy",
    )
    session = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="module_card",
    )
    for command in session.variant.solution_commands:
        CommandProcessingService().submit_command(session=session, command=command)
        session.refresh_from_db()
        if session.status == SESSION_STATUS_COMPLETED:
            break

    payload = scenario_status_payload(user=student, scenario=difficulty.scenario)
    easy = next(item for item in payload["difficulties"] if item["difficulty"] == "easy")

    assert easy["latest_attempt"]["status"] == "completed"
    assert easy["latest_attempt"]["id"] == session.id
    assert easy["latest_attempt"]["accuracy_rate"] == 100
    assert easy["latest_attempt"]["command_accurate"] is True
    assert easy["mastery_progress"] == {"mastered": 1, "required": 3}
    assert session_payload(session)["next_difficulty"] is None


def test_scenario_summary_payload_excludes_heavy_preview_fields(student):
    scenario = ScenarioSkillFocus.objects.get(slug="stage-and-commit-basic-workflow", is_published=True)

    payload = scenario_status_payload(user=student, scenario=scenario)
    list_payload = scenario_status_payloads(
        user=student, scenarios=[scenario], include_preview=False
    )[0]

    assert "demo_repository_state" not in payload
    assert "safe_demo_commands" not in payload
    assert payload["command_preview"]["supported_demo_commands"]
    assert payload["command_preview"]["demo_repository_state"]
    assert "demo_repository_state" not in list_payload
    assert "demo_explanation_steps" not in list_payload
    assert "command_preview" not in list_payload


def test_command_preview_detail_paginates_heavy_command_content(student):
    scenario = ScenarioSkillFocus.objects.get(slug="inspect-repository-state", is_published=True)
    full_payload = scenario_status_payload(user=student, scenario=scenario)
    full_commands = full_payload["command_preview"]["commands"]

    paged_payload = scenario_status_payload(
        user=student,
        scenario=scenario,
        preview_command_index=1,
    )
    preview = paged_payload["command_preview"]

    assert len(full_commands) > 1
    assert preview["navigation"]["current_index"] == 1
    assert preview["navigation"]["total_count"] == len(full_commands)
    assert len(preview["commands"]) == len(full_commands)
    assert preview["commands"][0]["pages"] == []
    assert "page_count" in preview["commands"][0]
    assert preview["commands"][1]["pages"] == full_commands[1]["pages"]


def test_skill_focus_detail_uses_requested_preview_command_page(student):
    scenario = ScenarioSkillFocus.objects.get(slug="inspect-repository-state", is_published=True)
    request = APIRequestFactory().get(
        f"/api/scenarios/skill-focus/{scenario.slug}/?command_index=1"
    )
    force_authenticate(request, user=student)

    response = SkillFocusDetailAPIView.as_view()(request, slug=scenario.slug)
    preview = response.data["command_preview"]

    assert response.status_code == 200
    assert preview["navigation"]["current_index"] == 1
    assert preview["commands"][0]["pages"] == []
    assert preview["commands"][1]["pages"]


def test_command_preview_resolves_reusable_command_content(student):
    scenario = ScenarioSkillFocus.objects.get(slug="stage-and-commit-basic-workflow", is_published=True)

    payload = scenario_status_payload(user=student, scenario=scenario)
    preview = payload["command_preview"]
    status_command = next(
        command for command in preview["commands"] if command["key"] == "git-status"
    )

    assert GitCommandContent.objects.filter(key="git-status").count() == 1
    assert preview["schema_version"] == 2
    assert preview["command_refs"]
    assert status_command["base_command"] == "git status"
    assert status_command["command"] == "git status"
    assert status_command["sections"][0]["type"] == "overview"
    assert status_command["sections"][1]["type"] == "syntax"
    assert status_command["pages"][0]["blocks"][0]["type"] == "paragraph"
    assert status_command["demo_steps"][0]["repository_state"]


def test_command_preview_applies_scenario_page_customization(student):
    scenario = ScenarioSkillFocus.objects.get(slug="stage-and-commit-basic-workflow", is_published=True)
    scenario.command_preview_config = {
        **scenario.command_preview_config,
        "command_refs": [
            {
                "key": "git-status",
                "command": "git status",
                "include_section_ids": ["overview"],
                "append_content": [
                    {
                        "id": "scenario-note",
                        "title": "Scenario note",
                        "blocks": [
                            {
                                "type": "callout",
                                "body": "Use status to read this scenario before acting.",
                            }
                        ],
                    }
                ],
            }
        ],
        "section_overrides": {
            "git-status": {
                "overview": {"title": "Status in this scenario"},
            }
        },
    }
    scenario.save(update_fields=["command_preview_config"])

    payload = scenario_status_payload(user=student, scenario=scenario)
    status_command = payload["command_preview"]["commands"][0]

    assert [page["id"] for page in status_command["pages"]] == [
        "overview",
        "scenario-note",
    ]
    assert status_command["pages"][0]["title"] == "Status in this scenario"
    assert status_command["pages"][1]["blocks"][0]["body"] == (
        "Use status to read this scenario before acting."
    )


def test_command_preview_deduplicates_variant_refs_under_one_command(student):
    scenario = ScenarioSkillFocus.objects.get(slug="stage-and-commit-basic-workflow", is_published=True)
    scenario.command_preview_config = {
        **scenario.command_preview_config,
        "command_refs": [
            {
                "key": "git-log",
                "command": "git log --oneline",
            },
            {
                "key": "git-log",
                "command": "git log --oneline --graph --all",
            },
        ],
    }
    scenario.save(update_fields=["command_preview_config"])

    payload = scenario_status_payload(user=student, scenario=scenario)
    log_commands = [
        command
        for command in payload["command_preview"]["commands"]
        if command["key"] == "git-log"
    ]

    assert len(log_commands) == 1
    assert log_commands[0]["base_command"] == "git log"
    assert log_commands[0]["command"] == "git log"
    assert [
        page["title"]
        for page in log_commands[0]["pages"]
        if page["title"] in {"Compact History", "Visual Branch History"}
    ] == ["Compact History", "Visual Branch History"]


def test_latest_attempt_accuracy_reflects_extra_counted_actions(student):
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="stage-and-commit-basic-workflow",
        difficulty="easy",
    )
    session = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="module_card",
    )
    session.status = "completed"
    session.counted_action_total = 3
    session.completed_at = timezone.now()
    session.ended_at = session.completed_at
    session.save(update_fields=["status", "counted_action_total", "completed_at", "ended_at"])

    payload = scenario_status_payload(user=student, scenario=difficulty.scenario)
    easy = next(item for item in payload["difficulties"] if item["difficulty"] == "easy")

    assert easy["latest_attempt"]["accuracy_rate"] == 67
    assert easy["latest_attempt"]["command_accurate"] is False


def test_completed_scenario_remains_retryable_until_three_mastered_instances(student):
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="stage-and-commit-basic-workflow",
        difficulty="easy",
    )
    session = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="module_card",
    )
    session.command_policy_snapshot = {
        **session.command_policy_snapshot,
        "max_counted_commands": 10,
    }
    session.save(update_fields=["command_policy_snapshot"])
    CommandProcessingService().submit_command(session=session, command="git status --wat")
    for command in session.variant.solution_commands:
        CommandProcessingService().submit_command(session=session, command=command)
        session.refresh_from_db()
        if session.status == SESSION_STATUS_COMPLETED:
            break
    session.refresh_from_db()

    payload = scenario_status_payload(user=student, scenario=difficulty.scenario)
    easy = next(item for item in payload["difficulties"] if item["difficulty"] == "easy")

    assert session.status == SESSION_STATUS_COMPLETED
    assert easy["review_available"] is False
    assert easy["retry_session_id"] == session.id
    assert easy["latest_attempt"]["accuracy_rate"] == 67

    retry = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="retry",
        prior_session=session,
    )
    for command in retry.variant.solution_commands:
        CommandProcessingService().submit_command(session=retry, command=command)
        retry.refresh_from_db()
        if retry.status == SESSION_STATUS_COMPLETED:
            break

    payload = scenario_status_payload(user=student, scenario=difficulty.scenario)
    easy = next(item for item in payload["difficulties"] if item["difficulty"] == "easy")
    completion = CompletionRecord.objects.filter(
        user=student,
        difficulty_instance=difficulty,
    ).first()

    assert retry.status == SESSION_STATUS_COMPLETED
    assert completion is None
    assert easy["review_available"] is False
    assert easy["retry_session_id"] == retry.id
    assert easy["latest_attempt"]["id"] == retry.id
    assert easy["latest_attempt"]["accuracy_rate"] == 100
    assert easy["mastery_progress"] == {"mastered": 1, "required": 3}


def test_accept_conflict_side_fails_at_max_when_wrong_side_committed(student):
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="accept-conflict-side",
        difficulty="medium",
    )
    session = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="module_card",
    )
    session.command_policy_snapshot = {
        **session.command_policy_snapshot,
        "max_counted_commands": 4,
    }
    session.save(update_fields=["command_policy_snapshot"])
    service = CommandProcessingService()
    for command in (
        "git checkout --ours src/policy.yml",
        "git add src/policy.yml",
        'git commit -m "Accept incoming branch version"',
        "git status --wat",
    ):
        service.submit_command(session=session, command=command)
        session.refresh_from_db()

    assert session.status == SESSION_STATUS_FAILED
    assert session.counted_action_total == 4
    assert (
        session.failure_reason
        == "Action limit reached before the target repository state was reached."
    )


def test_completed_scenario_at_seventy_five_percent_counts_progress_without_forced_retry(student):
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="stage-and-commit-basic-workflow",
        difficulty="easy",
    )
    min_counted = difficulty.command_policy.min_counted_commands
    session = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="module_card",
    )
    session.status = SESSION_STATUS_COMPLETED
    session.counted_action_total = min_counted + 1
    session.completed_at = timezone.now()
    session.ended_at = session.completed_at
    session.save(
        update_fields=["status", "counted_action_total", "completed_at", "ended_at"]
    )

    payload = scenario_status_payload(user=student, scenario=difficulty.scenario)
    easy = next(item for item in payload["difficulties"] if item["difficulty"] == "easy")
    expected = round((min_counted / (min_counted + 1)) * 100)

    assert expected >= 70
    assert easy["latest_attempt"]["accuracy_rate"] == expected
    assert easy["latest_attempt"]["command_accurate"] is False
    assert easy["retry_session_id"] is None
    assert easy["mastery_progress"]["mastered"] == 1


def test_abandoned_retry_becomes_latest_zero_mastery(student):
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="stage-and-commit-basic-workflow",
        difficulty="easy",
    )
    session = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="module_card",
    )
    session.command_policy_snapshot = {
        **session.command_policy_snapshot,
        "max_counted_commands": 10,
    }
    session.save(update_fields=["command_policy_snapshot"])
    CommandProcessingService().submit_command(session=session, command="git status --wat")
    for command in session.variant.solution_commands:
        CommandProcessingService().submit_command(session=session, command=command)
        session.refresh_from_db()
        if session.status == SESSION_STATUS_COMPLETED:
            break
    session.refresh_from_db()
    retry = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="retry",
        prior_session=session,
    )
    ScenarioSessionService().abandon(session=retry)

    payload = scenario_status_payload(user=student, scenario=difficulty.scenario)
    easy = next(item for item in payload["difficulties"] if item["difficulty"] == "easy")

    assert session.status == SESSION_STATUS_COMPLETED
    assert easy["status"] == "completed"
    assert easy["review_available"] is False
    assert easy["retry_session_id"] == retry.id
    assert easy["latest_attempt"]["id"] == retry.id
    assert easy["latest_attempt"]["accuracy_rate"] == 0


def test_later_completed_retry_replaces_prior_mastery_even_when_worse(student):
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="stage-and-commit-basic-workflow",
        difficulty="easy",
    )
    difficulty.required_successful_attempts = 1
    difficulty.save(update_fields=["required_successful_attempts"])
    first = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="module_card",
    )
    for command in first.variant.solution_commands:
        CommandProcessingService().submit_command(session=first, command=command)
        first.refresh_from_db()
        if first.status == SESSION_STATUS_COMPLETED:
            break
    first.refresh_from_db()

    retry = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="retry",
        prior_session=first,
    )
    retry.status = SESSION_STATUS_COMPLETED
    retry.counted_action_total = 4
    retry.completed_at = timezone.now()
    retry.ended_at = retry.completed_at
    retry.save(update_fields=["status", "counted_action_total", "completed_at", "ended_at"])
    CommandProcessingService()._complete_session(retry)

    payload = scenario_status_payload(user=student, scenario=difficulty.scenario)
    easy = next(item for item in payload["difficulties"] if item["difficulty"] == "easy")
    completion = CompletionRecord.objects.get(user=student, difficulty_instance=difficulty)

    assert completion.session_id == retry.id
    assert completion.counted_action_total == 4
    assert easy["latest_attempt"]["id"] == retry.id
    assert easy["latest_attempt"]["accuracy_rate"] == 50
    assert easy["review_available"] is False
    assert easy["retry_session_id"] == retry.id


def test_review_sessions_do_not_replace_primary_accuracy(student):
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="stage-and-commit-basic-workflow",
        difficulty="easy",
    )
    primary = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="module_card",
    )
    primary.status = SESSION_STATUS_COMPLETED
    primary.counted_action_total = 3
    primary.completed_at = timezone.now()
    primary.ended_at = primary.completed_at
    primary.save(update_fields=["status", "counted_action_total", "completed_at", "ended_at"])
    CompletionRecord.objects.create(
        user=student,
        scenario=difficulty.scenario,
        difficulty_instance=difficulty,
        session=primary,
        first_attempt_star=False,
        counted_action_total=3,
    )
    review_session = ReviewModeService().start_review_session(
        user=student,
        difficulty_instance=difficulty,
    )
    review_session.status = SESSION_STATUS_COMPLETED
    review_session.counted_action_total = 2
    review_session.completed_at = timezone.now()
    review_session.ended_at = review_session.completed_at
    review_session.save(
        update_fields=["status", "counted_action_total", "completed_at", "ended_at"]
    )

    payload = scenario_status_payload(user=student, scenario=difficulty.scenario)
    easy = next(item for item in payload["difficulties"] if item["difficulty"] == "easy")

    assert easy["latest_attempt"]["id"] == primary.id
    assert easy["latest_attempt"]["accuracy_rate"] == 67
    assert easy["review_available"] is False
    assert easy["retry_session_id"] == primary.id


def test_seeded_curriculum_has_full_variant_set_and_one_primary_focus(seeded_content):
    assert (
        Lesson.objects.filter(unit__slug="local-repository-foundations", is_published=True).count()
        == 9
    )
    assert ScenarioSkillFocus.objects.filter(is_published=True).count() == 9
    assert DifficultyInstance.objects.filter(is_published=True).count() == 24
    assert ScenarioVariant.objects.filter(is_published=True).count() >= 65
    assert ScenarioVariant.objects.filter(is_published=True, semantic_key="").count() == 0
    assert all(
        scenario.primary_focus_commands
        for scenario in ScenarioSkillFocus.objects.filter(is_published=True)
    )


def test_module_one_scenarios_have_all_difficulties_and_authored_variants(seeded_content):
    expected_difficulties = {"easy", "medium", "hard"}
    for scenario in ScenarioSkillFocus.objects.filter(
        learning_unit__slug="local-repository-foundations",
        is_published=True,
    ):
        difficulties = {
            instance.difficulty: instance
            for instance in scenario.difficulty_instances.filter(is_published=True)
        }
        if scenario.slug == "inspect-repository-state":
            assert difficulties == {}
            continue
        assert set(difficulties) == expected_difficulties
        for instance in difficulties.values():
            variants = instance.variants.filter(is_published=True)
            assert variants.exists()
            assert all(variant.case_id for variant in variants)
            assert all(variant.semantic_key for variant in variants)
            assert all(variant.initial_state for variant in variants)
            assert all(variant.target_rule for variant in variants)
            assert all(variant.solution_commands for variant in variants)
            assert all(variant.student_context for variant in variants)


def test_module_one_required_attempt_counts_come_from_curriculum(seeded_content):
    hard_review = DifficultyInstance.objects.get(
        scenario__slug="module1-integrated-local-workflow",
        difficulty="hard",
    )
    easy_partial = DifficultyInstance.objects.get(
        scenario__slug="partial-staging-add-p",
        difficulty="easy",
    )

    assert hard_review.required_successful_attempts == 2
    assert easy_partial.required_successful_attempts == 3


def test_primary_focus_is_not_polluted_by_supporting_workflow_commands(seeded_content):
    scenario = ScenarioSkillFocus.objects.get(slug="stage-and-commit-basic-workflow", is_published=True)

    assert scenario.primary_focus_commands == ["git add", "git commit"]
    assert "git status" in scenario.supporting_diagnostic_commands
    assert "git diff" in scenario.supporting_diagnostic_commands
    assert "git status" not in scenario.primary_focus_commands
    assert "git diff" not in scenario.primary_focus_commands


def test_command_classifier_keeps_diagnostics_free_and_actions_counted():
    classifier = CommandCountClassifier()
    policy = {"non_counted_patterns": []}

    assert classifier.classify(command="git status", policy_snapshot=policy, processed=True) == (
        COMMAND_DIAGNOSTIC,
        0,
    )
    assert classifier.classify(
        command="git diff --staged", policy_snapshot=policy, processed=True
    ) == (
        COMMAND_DIAGNOSTIC,
        0,
    )
    assert classifier.classify(command="git branch -v", policy_snapshot=policy, processed=True) == (
        COMMAND_DIAGNOSTIC,
        0,
    )
    assert classifier.classify(
        command="git branch -d stale", policy_snapshot=policy, processed=True
    ) == (
        COMMAND_COUNTED,
        1,
    )
    assert classifier.classify(
        command="git restore scratch.md", policy_snapshot=policy, processed=True
    ) == (
        COMMAND_COUNTED,
        1,
    )
    assert classifier.classify(
        command="git status --wat", policy_snapshot=policy, processed=False
    ) == (
        COMMAND_COUNTED,
        1,
    )
    assert classifier.classify(
        command="git rebase main", policy_snapshot=policy, processed=False
    ) == (
        COMMAND_COUNTED,
        1,
    )
    assert classifier.classify(
        command="python cleanup.py", policy_snapshot=policy, processed=False
    ) == (
        COMMAND_UNPROCESSABLE,
        0,
    )


def test_invalid_git_syntax_consumes_action_budget(student):
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="stage-and-commit-basic-workflow",
        difficulty="easy",
    )
    session = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="module_card",
    )

    response = CommandProcessingService().submit_command(
        session=session, command="git status --wat"
    )

    session.refresh_from_db()
    assert response["command_classification"] == COMMAND_COUNTED
    assert response["evaluation_result"] == RESULT_INVALID
    assert "error: unknown option" in response["terminal_output"]
    assert session.counted_action_total == 1
    assert (
        response["remaining_counted_commands"]
        == session.command_policy_snapshot["max_counted_commands"] - 1
    )


def test_counted_command_reaching_max_limit_fails_session(student):
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="stage-and-commit-basic-workflow",
        difficulty="easy",
    )
    session = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="module_card",
    )
    session.command_policy_snapshot = {
        **session.command_policy_snapshot,
        "min_counted_commands": 1,
        "max_counted_commands": 1,
    }
    session.save(update_fields=["command_policy_snapshot"])

    response = CommandProcessingService().submit_command(
        session=session, command="git status --wat"
    )

    session.refresh_from_db()
    payload = session_payload(session)
    assert response["command_classification"] == COMMAND_COUNTED
    assert session.status == SESSION_STATUS_FAILED
    assert (
        session.failure_reason
        == "Action limit reached before the target repository state was reached."
    )
    assert payload["status"] == SESSION_STATUS_FAILED
    assert payload["counts"]["counted_action_total"] == 1
    assert payload["counts"]["minimum_counted_commands"] == 1
    assert payload["counts"]["maximum_counted_commands"] == 1
    assert payload["counts"]["remaining_counted_commands"] == 0
    assert payload["counts"]["max_reached"] is True


def test_failed_session_blocks_further_commands(student):
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="stage-and-commit-basic-workflow",
        difficulty="easy",
    )
    session = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="module_card",
    )
    session.status = SESSION_STATUS_FAILED
    session.ended_at = timezone.now()
    session.failure_reason = "Action limit reached."
    session.save(update_fields=["status", "ended_at", "failure_reason"])

    with pytest.raises(Locked):
        CommandProcessingService().submit_command(session=session, command="git status")


def test_diagnostic_commands_remain_non_counted_inside_state_based_sessions(student):
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="stage-and-commit-basic-workflow",
        difficulty="easy",
    )
    session = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="module_card",
    )
    initial_state = json.loads(json.dumps(session.repository_state))

    response = CommandProcessingService().submit_command(session=session, command="git status")
    session.refresh_from_db()

    assert response["command_classification"] == COMMAND_DIAGNOSTIC
    assert response["step"].command_classification == COMMAND_DIAGNOSTIC
    assert session.status == SESSION_STATUS_STARTED
    assert session.counted_action_total == 0
    assert session.non_counted_diagnostic_total == 1
    assert session.repository_state == initial_state


def test_init_scenario_does_not_complete_by_cloning_after_init(student):
    easy = DifficultyInstance.objects.get(
        scenario__slug="initialize-local-repository",
        difficulty="easy",
    )
    complete_required_accurate_sessions(user=student, difficulty=easy)
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="initialize-local-repository",
        difficulty="medium",
    )
    session = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="module_card",
    )
    session.command_policy_snapshot = {
        **session.command_policy_snapshot,
        "max_counted_commands": 3,
    }
    session.save(update_fields=["command_policy_snapshot"])

    CommandProcessingService().submit_command(session=session, command="git init")
    response = CommandProcessingService().submit_command(
        session=session,
        command="git clone https://example.test/auth.git auth-project",
    )

    session.refresh_from_db()
    assert response["command_classification"] == COMMAND_COUNTED
    assert session.status == "started"
    assert session.repository_state["repository_initialized"] is True
    assert not CompletionRecord.objects.filter(
        user=student, difficulty_instance=difficulty
    ).exists()


def test_init_scenario_does_not_complete_by_cloning_first(student):
    easy = DifficultyInstance.objects.get(
        scenario__slug="initialize-local-repository",
        difficulty="easy",
    )
    complete_required_accurate_sessions(user=student, difficulty=easy)
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="initialize-local-repository",
        difficulty="medium",
    )
    session = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="module_card",
    )
    session.command_policy_snapshot = {
        **session.command_policy_snapshot,
        "max_counted_commands": 3,
    }
    session.save(update_fields=["command_policy_snapshot"])

    response = CommandProcessingService().submit_command(
        session=session,
        command="git clone https://example.test/auth.git auth-project",
    )

    session.refresh_from_db()
    assert response["command_classification"] == COMMAND_COUNTED
    assert session.status == "started"
    assert not CompletionRecord.objects.filter(
        user=student, difficulty_instance=difficulty
    ).exists()


def test_clone_scenario_does_not_complete_by_initializing_folder(student):
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="clone-remote-repository",
        difficulty="easy",
    )
    session = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="module_card",
    )
    session.command_policy_snapshot = {
        **session.command_policy_snapshot,
        "max_counted_commands": 3,
    }
    session.save(update_fields=["command_policy_snapshot"])

    response = CommandProcessingService().submit_command(session=session, command="git init")

    session.refresh_from_db()
    assert response["command_classification"] == COMMAND_COUNTED
    assert session.status == "started"
    assert session.repository_state["repository_initialized"] is True
    assert session.repository_state["remotes"] == {}
    assert not CompletionRecord.objects.filter(
        user=student, difficulty_instance=difficulty
    ).exists()


def test_retry_after_failed_retry_resets_action_budget(student):
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="stage-and-commit-basic-workflow",
        difficulty="easy",
    )
    first = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="module_card",
    )
    first.status = SESSION_STATUS_FAILED
    first.counted_action_total = first.command_policy_snapshot["max_counted_commands"]
    first.ended_at = timezone.now()
    first.save(update_fields=["status", "counted_action_total", "ended_at"])

    retry = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="retry",
        prior_session=first,
    )
    retry.status = SESSION_STATUS_FAILED
    retry.counted_action_total = retry.command_policy_snapshot["max_counted_commands"]
    retry.ended_at = timezone.now()
    retry.save(update_fields=["status", "counted_action_total", "ended_at"])

    next_retry = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="retry",
        prior_session=retry,
    )
    payload = session_payload(next_retry)

    assert next_retry.counted_action_total == 0
    assert (
        payload["counts"]["remaining_counted_commands"]
        == next_retry.command_policy_snapshot["max_counted_commands"]
    )


def test_authored_variants_do_not_contain_unresolved_target_placeholders(student):
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="stage-and-commit-basic-workflow",
        difficulty="easy",
    )
    session = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="module_card",
    )
    variant = session.variant
    serialized = {
        "target_rule": variant.target_rule,
        "solution_commands": variant.solution_commands,
        "student_context": variant.student_context,
    }

    assert "<" not in str(serialized)
    assert "{{" not in str(serialized)


def test_module4_hard_reset_can_complete_without_required_command_sequence(student):
    call_command("seed_module4_scenarios", "--reset", "--confirm", "--validate-build")
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="recover-from-hard-reset-incident",
        difficulty="easy",
    )
    session = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="module_card",
    )
    recovery_branch = session.variant.parameter_context["recovery_branch"]
    recovery_target = session.variant.parameter_context["recovery_target"]

    CommandProcessingService().submit_command(
        session=session,
        command=f"git switch -c {recovery_branch} {recovery_target}",
    )
    session.refresh_from_db()

    assert session.status == SESSION_STATUS_COMPLETED


def test_authored_state_based_variants_require_focus_commands_and_hide_task_answers(student):
    for difficulty in DifficultyInstance.objects.select_related("scenario").filter(
        is_published=True
    ):
        task_prompt = difficulty.task_prompt.lower()
        assert "git " not in task_prompt.replace("git repository", "repository")
        for focus_command in difficulty.scenario.primary_focus_commands:
            assert focus_command.lower() not in task_prompt

        focus_commands = set(difficulty.scenario.primary_focus_commands)
        for variant in difficulty.variants.filter(is_published=True):
            assert focus_commands.issubset(set(variant.target_rule.get("required_commands", [])))

            if difficulty.scenario.focus in {"git clone", "git remote"}:
                assert variant.target_rule.get("remote_url_matches", {}).get("origin")
