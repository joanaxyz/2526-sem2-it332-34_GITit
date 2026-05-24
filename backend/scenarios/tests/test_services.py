import json

import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.utils import timezone

from common.constants import (
    COMMAND_COUNTED,
    COMMAND_DIAGNOSTIC,
    COMMAND_UNPROCESSABLE,
    COMPLETION_INSPECTION,
    RESULT_INVALID,
    SESSION_MODE_REVIEW,
    SESSION_STATUS_COMPLETED,
    SESSION_STATUS_FAILED,
    SESSION_STATUS_STARTED,
)
from common.exceptions import Locked
from learning.models import Lesson, OrientationProgress
from progress.models import StreakRecord, StudentProgress
from review.services import ReviewModeService
from scenarios.builders import RuntimeScenarioBuilder
from scenarios.models import (
    CompletionRecord,
    DifficultyInstance,
    GitCommandContent,
    ScenarioGenerationBlueprint,
    ScenarioSession,
    ScenarioSkillFocus,
    ScenarioVariant,
)
from scenarios.selectors import scenario_status_payload, scenario_status_payloads
from scenarios.serializers import session_payload
from scenarios.services import (
    CommandCountClassifier,
    CommandProcessingService,
    InspectionAnswerSubmissionService,
    ScenarioSessionService,
)


@pytest.fixture()
def seeded_content(db):
    call_command("seed_starter_content")


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
        source_entry_point="lesson",
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
        scenario__slug="form-clean-commit",
        difficulty="easy",
    )

    session = ScenarioSessionService().start_session(
        user=user,
        difficulty_instance=difficulty,
        source_entry_point="lesson",
    )

    assert session.status == "started"
    assert session.orientation_complete_at_start is False


def test_diagnostic_commands_are_logged_but_not_counted(student):
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="form-clean-commit",
        difficulty="easy",
    )
    session = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="lesson",
    )

    assert session.variant.difficulty_instance_id == difficulty.id

    response = CommandProcessingService().submit_command(session=session, command="git status")

    session.refresh_from_db()
    assert response["command_classification"] == COMMAND_DIAGNOSTIC
    assert "On branch" in response["terminal_output"]
    assert "Only simulated" not in response["terminal_output"]
    assert session.counted_action_total == 0
    assert session.non_counted_diagnostic_total == 1


def test_state_based_completion_creates_completion_record(student):
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="form-clean-commit",
        difficulty="easy",
    )
    session = complete_required_accurate_sessions(user=student, difficulty=difficulty)

    session.refresh_from_db()
    completion = CompletionRecord.objects.get(user=student, difficulty_instance=difficulty)
    assert session.status == "completed"
    assert completion.counted_action_total == 2


def test_session_payload_includes_completion_when_record_exists(student):
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="form-clean-commit",
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
        scenario__slug="form-clean-commit",
        difficulty="easy",
    )
    session = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="lesson",
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
    hard_variant = RuntimeScenarioBuilder().generate_variant(
        user=student,
        difficulty_instance=hard,
    )
    hard_session = ScenarioSession.objects.create(
        user=student,
        learning_unit=hard.scenario.learning_unit,
        scenario=hard.scenario,
        difficulty_instance=hard,
        variant=hard_variant,
        source_entry_point="lesson",
        command_policy_snapshot=hard.command_policy.snapshot(),
        repository_state=hard_variant.initial_state,
    )

    hard_payload = session_payload(hard_session, include_steps=False)

    assert hard_payload["scaffolding"]["expected_state"] is False
    assert hard_payload["expected_state"] is None


def test_starting_session_creates_persisted_generated_variant_with_student_context(student):
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="form-clean-commit",
        difficulty="easy",
    )
    before_count = ScenarioVariant.objects.filter(
        difficulty_instance=difficulty,
        is_generated=True,
    ).count()

    session = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="lesson",
    )
    variant = session.variant
    payload = session_payload(session, include_steps=False)
    serialized_payload = json.dumps(payload)

    assert (
        ScenarioVariant.objects.filter(
            difficulty_instance=difficulty,
            is_generated=True,
        ).count()
        == before_count + 1
    )
    assert variant.is_generated is True
    assert variant.generated_from_blueprint is not None
    assert variant.parameter_context
    assert variant.student_context
    assert variant.initial_state
    assert variant.target_rule
    assert variant.target_state
    assert variant.expected_state_diagram
    assert variant.solution_commands
    assert payload["student_context"] == variant.student_context
    assert payload["scenario"]["student_context"] == variant.student_context
    for command in variant.solution_commands:
        assert command not in serialized_payload


def test_session_payload_falls_back_for_old_variants_without_student_context(student):
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="form-clean-commit",
        difficulty="easy",
    )
    session = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="lesson",
    )
    session.variant.student_context = {}
    session.variant.save(update_fields=["student_context"])
    session.refresh_from_db()

    payload = session_payload(session, include_steps=False)

    assert payload["student_context"]["story"] == session.difficulty_instance.narrative
    assert payload["student_context"]["requirements"] == [session.difficulty_instance.task_prompt]


def test_active_session_payload_and_command_submit_do_not_regenerate_variant(student):
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="form-clean-commit",
        difficulty="easy",
    )
    session = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="lesson",
    )
    variant_id = session.variant_id
    generated_count = ScenarioVariant.objects.filter(
        difficulty_instance=difficulty,
        is_generated=True,
    ).count()

    assert session_payload(session, include_steps=False)["variant"]["id"] == variant_id
    CommandProcessingService().submit_command(session=session, command="git status")
    session.refresh_from_db()

    assert session.variant_id == variant_id
    assert (
        ScenarioVariant.objects.filter(
            difficulty_instance=difficulty,
            is_generated=True,
        ).count()
        == generated_count
    )


def test_generated_context_exposes_checked_values_without_solution_commands(student):
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="form-clean-commit",
        difficulty="easy",
    )
    session = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="lesson",
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


def test_generated_context_exposes_excluded_files_and_remote_values(student):
    ignore_difficulty = DifficultyInstance.objects.get(
        scenario__slug="configure-gitignore-rules",
        difficulty="easy",
    )
    ignore_session = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=ignore_difficulty,
        source_entry_point="lesson",
    )
    ignore_context = json.dumps(ignore_session.variant.student_context).lower()
    for path in ignore_session.variant.target_rule["latest_commit"]["excludes_paths"]:
        assert path.lower() in ignore_context

    clone_difficulty = DifficultyInstance.objects.get(
        scenario__slug="clone-project-and-inspect",
        difficulty="easy",
    )
    clone_session = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=clone_difficulty,
        source_entry_point="lesson",
    )
    clone_context = json.dumps(clone_session.variant.student_context).lower()
    for remote, url in clone_session.variant.target_rule["remote_url_matches"].items():
        assert remote.lower() in clone_context
        assert url.lower() in clone_context


def test_partial_staging_requires_the_selected_file_scope(student):
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="stage-selected-changes",
        difficulty="easy",
    )
    session = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="lesson",
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
        scenario__slug="form-clean-commit",
        difficulty="easy",
    )
    prior = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="lesson",
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
    assert retry.variant.variant_fingerprint != prior.variant.variant_fingerprint
    assert retry.variant.parameter_context != prior.variant.parameter_context
    assert retry.variant.blueprint_signature == prior.variant.blueprint_signature
    assert retry.changed_variant is True
    assert retry.rta_eligible is True


def test_retry_from_active_session_requires_exit_first(student):
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="form-clean-commit",
        difficulty="easy",
    )
    prior = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="lesson",
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


def test_starting_active_difficulty_requires_exit_first(student):
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="form-clean-commit",
        difficulty="easy",
    )
    active = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="lesson",
    )

    with pytest.raises(Locked, match="Exit the current scenario"):
        ScenarioSessionService().start_session(
            user=student,
            difficulty_instance=difficulty,
            source_entry_point="unit_card",
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
        scenario__slug="form-clean-commit",
        difficulty="easy",
    )
    complete_required_accurate_sessions(user=student, difficulty=difficulty)
    completion = CompletionRecord.objects.get(user=student, difficulty_instance=difficulty)
    generated_count = ScenarioVariant.objects.filter(
        difficulty_instance=difficulty,
        is_generated=True,
    ).count()

    review_session = ReviewModeService().start_review_session(
        user=student, difficulty_instance=difficulty
    )

    assert review_session.mode == SESSION_MODE_REVIEW
    assert review_session.variant_id == completion.session.variant_id
    assert (
        ScenarioVariant.objects.filter(
            difficulty_instance=difficulty,
            is_generated=True,
        ).count()
        == generated_count
    )
    assert (
        CompletionRecord.objects.filter(user=student, difficulty_instance=difficulty).count() == 1
    )
    assert ScenarioSession.objects.filter(user=student, mode=SESSION_MODE_REVIEW).count() == 1


def test_scenario_payload_includes_latest_attempt_accuracy(student):
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="form-clean-commit",
        difficulty="easy",
    )
    session = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="lesson",
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
    scenario = ScenarioSkillFocus.objects.get(slug="form-clean-commit", is_published=True)

    payload = scenario_status_payload(user=student, scenario=scenario)
    list_payload = scenario_status_payloads(
        user=student, scenarios=[scenario], include_preview=False
    )[0]

    assert "demo_repository_state" in payload
    assert "safe_demo_commands" in payload
    assert payload["command_preview"]["supported_demo_commands"]
    assert "demo_repository_state" not in list_payload
    assert "demo_explanation_steps" not in list_payload
    assert "command_preview" not in list_payload


def test_command_preview_resolves_reusable_command_content(student):
    scenario = ScenarioSkillFocus.objects.get(slug="form-clean-commit", is_published=True)

    payload = scenario_status_payload(user=student, scenario=scenario)
    preview = payload["command_preview"]
    status_command = next(
        command for command in preview["commands"] if command["key"] == "git-status"
    )

    assert GitCommandContent.objects.filter(key="git-status").count() == 1
    assert preview["schema_version"] == 2
    assert preview["command_refs"]
    assert status_command["command"] == "git status"
    assert status_command["pages"][0]["blocks"][0]["type"] == "paragraph"
    assert status_command["demo_steps"][0]["repository_state"]
    assert any(command["key"] == "scenario-context" for command in preview["commands"])


def test_command_preview_applies_scenario_page_customization(student):
    scenario = ScenarioSkillFocus.objects.get(slug="form-clean-commit", is_published=True)
    scenario.command_preview_config = {
        **scenario.command_preview_config,
        "command_refs": [
            {
                "key": "git-status",
                "command": "git status",
                "include_page_ids": ["overview"],
                "append_pages": [
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
        "page_overrides": {
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


def test_latest_attempt_accuracy_reflects_extra_counted_actions(student):
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="form-clean-commit",
        difficulty="easy",
    )
    session = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="lesson",
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
        scenario__slug="form-clean-commit",
        difficulty="easy",
    )
    session = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="lesson",
    )
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


def test_abandoned_retry_becomes_latest_zero_mastery(student):
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="form-clean-commit",
        difficulty="easy",
    )
    session = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="lesson",
    )
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
        scenario__slug="form-clean-commit",
        difficulty="easy",
    )
    difficulty.required_successful_attempts = 1
    difficulty.save(update_fields=["required_successful_attempts"])
    first = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="lesson",
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
        scenario__slug="form-clean-commit",
        difficulty="easy",
    )
    primary = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="lesson",
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
    assert DifficultyInstance.objects.filter(is_published=True).count() == 27
    assert ScenarioGenerationBlueprint.objects.filter(is_published=True).count() == 27
    assert ScenarioVariant.objects.filter(is_published=True, is_generated=False).count() == 0
    assert all(
        len(scenario.primary_focus_commands) == 1
        or scenario.slug in {"inspect-repository-state", "read-repository-state"}
        for scenario in ScenarioSkillFocus.objects.filter(is_published=True)
    )


def test_module_one_scenarios_have_all_difficulties_and_generation_blueprints(seeded_content):
    expected_difficulties = {"easy", "medium", "hard"}
    for scenario in ScenarioSkillFocus.objects.filter(
        learning_unit__slug="local-repository-foundations",
        is_published=True,
    ):
        difficulties = {
            instance.difficulty: instance
            for instance in scenario.difficulty_instances.filter(is_published=True)
        }
        assert set(difficulties) == expected_difficulties
        for instance in difficulties.values():
            blueprint = instance.generation_blueprints.get(is_published=True)
            assert blueprint.generation_count >= 1
            assert blueprint.parameter_pools
            assert blueprint.initial_state_template
            assert blueprint.target_rule_template
            assert blueprint.solution_commands_template
            assert blueprint.student_context_template


def test_module_one_required_attempt_counts_come_from_curriculum(seeded_content):
    hard_review = DifficultyInstance.objects.get(
        scenario__slug="integrate-local-workflow",
        difficulty="hard",
    )
    easy_partial = DifficultyInstance.objects.get(
        scenario__slug="stage-selected-changes",
        difficulty="easy",
    )

    assert hard_review.required_successful_attempts == 3
    assert easy_partial.required_successful_attempts == 2


def test_primary_focus_is_not_polluted_by_supporting_workflow_commands(seeded_content):
    scenario = ScenarioSkillFocus.objects.get(slug="form-clean-commit", is_published=True)

    assert scenario.primary_focus_commands == ["git commit"]
    assert "git status" in scenario.supporting_inspection_commands
    assert "git diff" in scenario.supporting_inspection_commands
    assert "git add" not in scenario.primary_focus_commands


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
        scenario__slug="form-clean-commit",
        difficulty="easy",
    )
    session = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="lesson",
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
        scenario__slug="form-clean-commit",
        difficulty="easy",
    )
    session = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="lesson",
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
    assert session.failure_reason == "Action limit reached."
    assert payload["status"] == SESSION_STATUS_FAILED
    assert payload["counts"]["counted_action_total"] == 1
    assert payload["counts"]["minimum_counted_commands"] == 1
    assert payload["counts"]["maximum_counted_commands"] == 1
    assert payload["counts"]["remaining_counted_commands"] == 0
    assert payload["counts"]["max_reached"] is True


def test_failed_session_blocks_further_commands(student):
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="form-clean-commit",
        difficulty="easy",
    )
    session = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="lesson",
    )
    session.status = SESSION_STATUS_FAILED
    session.ended_at = timezone.now()
    session.failure_reason = "Action limit reached."
    session.save(update_fields=["status", "ended_at", "failure_reason"])

    with pytest.raises(Locked):
        CommandProcessingService().submit_command(session=session, command="git status")


def test_inspection_scenario_completes_without_fake_state_changes(student):
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="read-repository-state",
        difficulty="easy",
    )
    session = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="lesson",
    )
    initial_state = session.repository_state

    response = CommandProcessingService().submit_command(session=session, command="git status")
    session.refresh_from_db()
    assert session.status == SESSION_STATUS_STARTED

    answer_response = InspectionAnswerSubmissionService().submit_answer(
        session=session,
        answer=session.variant.expected_observations["expected_answer"],
    )

    session.refresh_from_db()
    assert difficulty.completion_type == COMPLETION_INSPECTION
    assert response["command_classification"] == COMMAND_DIAGNOSTIC
    assert answer_response["evaluation"].target_matched is True
    assert session.status == "completed"
    assert session.counted_action_total == 0
    assert session.repository_state == initial_state
    assert "completion_type" in session.variant.target_rule


def test_init_scenario_does_not_complete_by_cloning_after_init(student):
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="initialize-project-and-first-commit",
        difficulty="easy",
    )
    session = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="lesson",
    )

    CommandProcessingService().submit_command(session=session, command="git init")
    response = CommandProcessingService().submit_command(
        session=session,
        command="git clone https://example.test/auth.git auth-project",
    )

    session.refresh_from_db()
    assert response["command_classification"] == COMMAND_COUNTED
    assert session.status == "started"
    assert session.repository_state["repository_initialized"] is True
    assert session.repository_state["working_tree"]
    assert not CompletionRecord.objects.filter(
        user=student, difficulty_instance=difficulty
    ).exists()


def test_init_scenario_does_not_complete_by_cloning_first(student):
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="initialize-project-and-first-commit",
        difficulty="easy",
    )
    session = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="lesson",
    )

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
        scenario__slug="clone-project-and-inspect",
        difficulty="easy",
    )
    session = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="lesson",
    )

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
        scenario__slug="form-clean-commit",
        difficulty="easy",
    )
    first = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="lesson",
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


def test_generated_variants_do_not_contain_unresolved_target_placeholders(student):
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="form-clean-commit",
        difficulty="easy",
    )
    session = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="lesson",
    )
    variant = session.variant
    serialized = {
        "target_rule": variant.target_rule,
        "expected_observations": variant.expected_observations,
        "solution_commands": variant.solution_commands,
        "student_context": variant.student_context,
    }

    assert "<" not in str(serialized)
    assert "{{" not in str(serialized)


def test_generated_state_based_variants_require_focus_commands_and_hide_task_answers(student):
    for difficulty in DifficultyInstance.objects.select_related("scenario").filter(
        is_published=True
    ):
        task_prompt = difficulty.task_prompt.lower()
        assert "git " not in task_prompt.replace("git repository", "repository")
        for focus_command in difficulty.scenario.primary_focus_commands:
            assert focus_command.lower() not in task_prompt

        if difficulty.completion_type == COMPLETION_INSPECTION:
            continue

        focus_commands = set(difficulty.scenario.primary_focus_commands)
        variant = RuntimeScenarioBuilder().generate_variant(
            user=student,
            difficulty_instance=difficulty,
        )
        assert focus_commands.issubset(set(variant.target_rule.get("required_commands", [])))

        if difficulty.scenario.focus in {"git clone", "git remote"}:
            assert variant.target_rule.get("remote_url_matches", {}).get("origin")
