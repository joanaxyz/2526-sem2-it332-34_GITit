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
    SESSION_STATUS_FAILED,
    SESSION_STATUS_STARTED,
)
from common.exceptions import Locked
from learning.models import Lesson, OrientationProgress
from progress.models import StreakRecord, StudentProgress
from review.services import ReviewModeService
from scenarios.models import (
    CompletionRecord,
    DifficultyInstance,
    ScenarioSession,
    ScenarioSkillFocus,
    ScenarioVariant,
)
from scenarios.selectors import scenario_status_payload
from scenarios.serializers import session_payload
from scenarios.services import (
    CommandCountClassifier,
    CommandProcessingService,
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
    assert session.counted_action_total == 0
    assert session.non_counted_diagnostic_total == 1


def test_state_based_completion_creates_completion_record(student):
    difficulty = DifficultyInstance.objects.get(
        scenario__slug="form-clean-commit",
        difficulty="easy",
    )
    session = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="lesson",
    )

    CommandProcessingService().submit_command(session=session, command="git add .")
    CommandProcessingService().submit_command(
        session=session, command='git commit -m "starter snapshot"'
    )

    session.refresh_from_db()
    completion = CompletionRecord.objects.get(user=student, difficulty_instance=difficulty)
    assert session.status == "completed"
    assert completion.counted_action_total == 2


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

    CommandProcessingService().submit_command(
        session=retry, command=retry.variant.solution_commands[0]
    )

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
    assert retry.variant.difficulty_instance_id == difficulty.id
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
    session = ScenarioSessionService().start_session(
        user=student,
        difficulty_instance=difficulty,
        source_entry_point="lesson",
    )
    CommandProcessingService().submit_command(session=session, command="git add .")
    CommandProcessingService().submit_command(
        session=session, command='git commit -m "starter snapshot"'
    )

    review_session = ReviewModeService().start_review_session(
        user=student, difficulty_instance=difficulty
    )

    assert review_session.mode == SESSION_MODE_REVIEW
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
    CommandProcessingService().submit_command(session=session, command="git add .")
    CommandProcessingService().submit_command(
        session=session, command='git commit -m "starter snapshot"'
    )

    payload = scenario_status_payload(user=student, scenario=difficulty.scenario)
    easy = next(item for item in payload["difficulties"] if item["difficulty"] == "easy")

    assert easy["latest_attempt"]["status"] == "completed"
    assert easy["latest_attempt"]["id"] == session.id
    assert easy["latest_attempt"]["accuracy_rate"] == 100
    assert easy["latest_attempt"]["command_accurate"] is True
    assert session_payload(session)["next_difficulty"]["difficulty"] == "medium"


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


def test_seeded_curriculum_has_full_variant_set_and_one_primary_focus(seeded_content):
    assert ScenarioSkillFocus.objects.filter(is_published=True).count() == 27
    assert DifficultyInstance.objects.filter(is_published=True).count() == 81
    assert ScenarioVariant.objects.filter(is_published=True).count() == 405
    assert all(
        len(scenario.primary_focus_commands) == 1
        for scenario in ScenarioSkillFocus.objects.filter(is_published=True)
    )


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
    assert classifier.classify(command="git diff --staged", policy_snapshot=policy, processed=True) == (
        COMMAND_DIAGNOSTIC,
        0,
    )
    assert classifier.classify(command="git branch -v", policy_snapshot=policy, processed=True) == (
        COMMAND_DIAGNOSTIC,
        0,
    )
    assert classifier.classify(command="git branch -d stale", policy_snapshot=policy, processed=True) == (
        COMMAND_COUNTED,
        1,
    )
    assert classifier.classify(command="git restore scratch.md", policy_snapshot=policy, processed=True) == (
        COMMAND_COUNTED,
        1,
    )
    assert classifier.classify(command="git status --wat", policy_snapshot=policy, processed=False) == (
        COMMAND_COUNTED,
        1,
    )
    assert classifier.classify(command="git rebase main", policy_snapshot=policy, processed=False) == (
        COMMAND_COUNTED,
        1,
    )
    assert classifier.classify(command="python cleanup.py", policy_snapshot=policy, processed=False) == (
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

    response = CommandProcessingService().submit_command(session=session, command="git status --wat")

    session.refresh_from_db()
    assert response["command_classification"] == COMMAND_COUNTED
    assert response["evaluation_result"] == RESULT_INVALID
    assert session.counted_action_total == 1
    assert response["remaining_counted_commands"] == session.command_policy_snapshot["max_counted_commands"] - 1


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
    assert difficulty.completion_type == COMPLETION_INSPECTION
    assert response["command_classification"] == COMMAND_DIAGNOSTIC
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
    assert payload["counts"]["remaining_counted_commands"] == next_retry.command_policy_snapshot["max_counted_commands"]


def test_seeded_variants_do_not_contain_unresolved_target_placeholders(seeded_content):
    serialized = [
        {
            "target_rule": variant.target_rule,
            "expected_observations": variant.expected_observations,
            "solution_commands": variant.solution_commands,
        }
        for variant in ScenarioVariant.objects.filter(is_published=True)
    ]

    assert "<" not in str(serialized)


def test_seeded_state_based_variants_require_focus_commands_and_hide_task_answers(seeded_content):
    for difficulty in DifficultyInstance.objects.select_related("scenario").filter(is_published=True):
        task_prompt = difficulty.task_prompt.lower()
        assert "git " not in task_prompt.replace("git repository", "repository")
        for focus_command in difficulty.scenario.primary_focus_commands:
            assert focus_command.lower() not in task_prompt

        if difficulty.completion_type == COMPLETION_INSPECTION:
            continue

        focus_commands = set(difficulty.scenario.primary_focus_commands)
        for variant in difficulty.variants.filter(is_published=True):
            assert focus_commands.issubset(set(variant.target_rule.get("required_commands", [])))

            if difficulty.scenario.focus in {"git clone", "git remote"}:
                assert variant.target_rule.get("remote_url_matches", {}).get("origin")

