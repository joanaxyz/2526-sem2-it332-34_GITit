from django.db.models import Prefetch

from common.constants import (
    DIFFICULTY_EASY,
    DIFFICULTY_MEDIUM,
    SESSION_MODE_PRIMARY,
    SESSION_STATUS_ABANDONED,
    SESSION_STATUS_COMPLETED,
    SESSION_STATUS_FAILED,
    SESSION_STATUS_STARTED,
)
from scenarios.models import (
    CompletionRecord,
    DifficultyInstance,
    ScenarioSession,
    ScenarioSkillFocus,
)
from simulator.services import is_diagnostic_command


def default_successful_attempts_for_difficulty(difficulty: str) -> int:
    """Fallback attempt requirement for legacy difficulty rows."""
    return 3 if difficulty == "easy" else 2


def required_successful_attempts_for_difficulty(
    difficulty_or_instance: str | DifficultyInstance,
) -> int:
    """Return the data-driven successful attempt requirement for a difficulty."""
    if isinstance(difficulty_or_instance, DifficultyInstance):
        return difficulty_or_instance.required_successful_attempts
    return default_successful_attempts_for_difficulty(difficulty_or_instance)


def command_accuracy_rate(
    *,
    status: str,
    counted_action_total: int,
    minimum_counted_commands: int,
) -> int | None:
    if status == SESSION_STATUS_STARTED:
        return None
    if status in {SESSION_STATUS_FAILED, SESSION_STATUS_ABANDONED}:
        return 0
    if counted_action_total <= minimum_counted_commands:
        return 100
    if minimum_counted_commands == 0:
        return 0
    return round((minimum_counted_commands / counted_action_total) * 100)


def latest_attempt_payload(*, user, difficulty_instance: DifficultyInstance) -> dict | None:
    session = (
        ScenarioSession.objects.filter(
            user=user,
            difficulty_instance=difficulty_instance,
        )
        .order_by("-id")
        .first()
    )
    if not session:
        return None

    return latest_attempt_payload_from_session(
        session=session,
        difficulty_instance=difficulty_instance,
    )


def latest_attempt_payload_from_session(
    *,
    session: ScenarioSession,
    difficulty_instance: DifficultyInstance,
) -> dict:
    minimum_counted_commands = difficulty_instance.command_policy.min_counted_commands
    command_accurate = (
        session.status == "completed"
        and session.counted_action_total <= minimum_counted_commands
    )
    accuracy_rate = command_accuracy_rate(
        status=session.status,
        counted_action_total=session.counted_action_total,
        minimum_counted_commands=minimum_counted_commands,
    )

    return {
        "id": session.id,
        "status": session.status,
        "accuracy_rate": accuracy_rate,
        "command_accurate": command_accurate if session.status == "completed" else None,
        "counted_action_total": session.counted_action_total,
        "total_attempts": session.total_attempts,
        "completed_at": session.completed_at,
        "ended_at": session.ended_at,
    }


def session_is_command_accurate(
    *,
    session: ScenarioSession | None,
    difficulty_instance: DifficultyInstance,
) -> bool:
    if not session or session.status != SESSION_STATUS_COMPLETED:
        return False
    return session.counted_action_total <= difficulty_instance.command_policy.min_counted_commands


def accuracy_display_session(
    *,
    completion: CompletionRecord | None,
    latest_session: ScenarioSession | None,
) -> ScenarioSession | None:
    return latest_session or (completion.session if completion else None)


def _published_difficulty_queryset():
    return (
        DifficultyInstance.objects.filter(is_published=True)
        .select_related("command_policy")
        .only(
            "id",
            "scenario_id",
            "difficulty",
            "completion_type",
            "required_successful_attempts",
            "command_policy__id",
            "command_policy__min_counted_commands",
            "command_policy__max_counted_commands",
            "command_policy__non_counted_patterns",
        )
    )


def scenario_queryset(*, include_variants: bool = True):
    queryset = (
        ScenarioSkillFocus.objects.filter(
            is_published=True,
            learning_unit__is_published=True,
            lesson__is_published=True,
        )
        .select_related("learning_unit", "lesson")
        .prefetch_related(Prefetch("difficulty_instances", queryset=_published_difficulty_queryset()))
    )
    if include_variants:
        queryset = queryset.prefetch_related("difficulty_instances__variants")
    return queryset


def scenario_list_queryset():
    return (
        ScenarioSkillFocus.objects.filter(
            is_published=True,
            learning_unit__is_published=True,
            lesson__is_published=True,
        )
        .prefetch_related(Prefetch("difficulty_instances", queryset=_published_difficulty_queryset()))
        .only(
            "id",
            "learning_unit_id",
            "lesson_id",
            "slug",
            "title",
            "focus",
            "summary",
            "skill_focus_type",
            "primary_focus_commands",
            "is_published",
            "sort_order",
        )
        .order_by("learning_unit_id", "lesson_id", "sort_order", "id")
    )


def scenario_status_payload(*, user, scenario: ScenarioSkillFocus) -> dict:
    return scenario_status_payloads(user=user, scenarios=[scenario])[0]


def scenario_status_payloads(*, user, scenarios, include_preview: bool = True) -> list[dict]:
    scenarios = list(scenarios)
    difficulty_instances = [
        instance
        for scenario in scenarios
        for instance in scenario.difficulty_instances.all()
    ]
    difficulty_ids = [instance.id for instance in difficulty_instances]
    required_map = {
        instance.id: required_successful_attempts_for_difficulty(instance)
        for instance in difficulty_instances
    }
    difficulty_by_key = {
        (instance.scenario_id, instance.difficulty): instance
        for instance in difficulty_instances
    }
    completions = _completion_map(user=user, difficulty_ids=difficulty_ids)
    accurate_counts = _accurate_completion_counts(user=user, difficulty_ids=difficulty_ids)
    successful_attempts = _progress_map(
        difficulty_ids=difficulty_ids,
        required_map=required_map,
        accurate_counts=accurate_counts,
        count_key="count",
    )
    mastery_progress_map = _progress_map(
        difficulty_ids=difficulty_ids,
        required_map=required_map,
        accurate_counts=accurate_counts,
        count_key="mastered",
    )
    completed_ids = _completed_difficulty_ids(user=user, difficulty_ids=difficulty_ids)
    active_sessions, latest_sessions, retryable_sessions = _session_state_maps(
        user=user,
        difficulty_ids=difficulty_ids,
    )

    return [
        _scenario_status_payload_from_maps(
            scenario=scenario,
            completions=completions,
            active_sessions=active_sessions,
            latest_sessions=latest_sessions,
            retryable_sessions=retryable_sessions,
            difficulty_by_key=difficulty_by_key,
            completed_ids=completed_ids,
            mastery_progress_map=mastery_progress_map,
            successful_attempts=successful_attempts,
            include_preview=include_preview,
        )
        for scenario in scenarios
    ]


def _scenario_status_payload_from_maps(
    *,
    scenario: ScenarioSkillFocus,
    completions: dict[int, CompletionRecord],
    active_sessions: dict[int, ScenarioSession],
    latest_sessions: dict[int, ScenarioSession],
    retryable_sessions: dict[int, ScenarioSession],
    difficulty_by_key: dict[tuple[int, str], DifficultyInstance],
    completed_ids: set[int],
    mastery_progress_map: dict[int, dict],
    successful_attempts: dict[int, dict],
    include_preview: bool,
) -> dict:
    difficulties = []
    for instance in scenario.difficulty_instances.all():
        completion = completions.get(instance.id)
        in_progress = active_sessions.get(instance.id)
        retryable_session = retryable_sessions.get(instance.id)
        latest_session = latest_sessions.get(instance.id)
        display_session = accuracy_display_session(
            completion=completion,
            latest_session=latest_session,
        )
        progress = successful_attempts.get(
            instance.id,
            {"count": 0, "required": required_successful_attempts_for_difficulty(instance)},
        )
        mastery = mastery_progress_map.get(
            instance.id,
            {"mastered": 0, "required": required_successful_attempts_for_difficulty(instance)},
        )
        latest_attempt = (
            latest_attempt_payload_from_session(
                session=display_session,
                difficulty_instance=instance,
            )
            if display_session
            else None
        )
        latest_is_accurate = (latest_attempt or {}).get("accuracy_rate") == 100
        successful_enough = progress["count"] >= progress["required"]
        can_review = completion is not None and successful_enough and latest_is_accurate
        can_retry = retryable_session is not None and not can_review
        difficulties.append(
            {
                "id": instance.id,
                "difficulty": instance.difficulty,
                "completion_type": instance.completion_type,
                "status": _difficulty_status(
                    instance=instance,
                    completions=completions,
                    active_sessions=active_sessions,
                    retryable_sessions=retryable_sessions,
                    difficulty_by_key=difficulty_by_key,
                    completed_ids=completed_ids,
                ),
                "review_available": can_review,
                "mastery_progress": mastery,
                "mastered_records": mastery,
                "successful_attempts": progress,
                "completion": {
                    "first_attempt_star": completion.first_attempt_star if completion else False,
                    "counted_action_total": completion.counted_action_total if completion else None,
                    "completed_at": completion.completed_at if completion else None,
                }
                if completion
                else None,
                "latest_attempt": latest_attempt,
                "active_session_id": in_progress.id if in_progress else None,
                "retry_session_id": retryable_session.id if can_retry else None,
                "policy": _policy_payload(instance=instance, include_preview=include_preview),
            }
        )
    order = {"easy": 0, "medium": 1, "hard": 2}
    difficulties.sort(key=lambda item: order[item["difficulty"]])
    payload = {
        "id": scenario.id,
        "slug": scenario.slug,
        "title": scenario.title,
        "focus": scenario.focus,
        "summary": scenario.summary,
        "skill_focus_type": scenario.skill_focus_type,
        "primary_focus_commands": scenario.primary_focus_commands,
        "learning_unit_id": scenario.learning_unit_id,
        "module_id": scenario.learning_unit_id,
        "lesson_id": scenario.lesson_id,
        "difficulties": difficulties,
    }

    if include_preview:
        payload.update(
            {
                "short_explanation": scenario.short_explanation,
                "supporting_inspection_commands": scenario.supporting_inspection_commands,
                "safe_demo_commands": scenario.safe_demo_commands,
                "demo_repository_state": scenario.demo_repository_state,
                "demo_dag_config": scenario.demo_dag_config,
                "demo_explanation_steps": scenario.demo_explanation_steps,
                "related_git_concepts": scenario.related_git_concepts,
                "command_preview": _command_preview_payload(scenario),
            }
        )
        return payload

    return payload


def _command_preview_payload(scenario: ScenarioSkillFocus) -> dict:
    commands = _unique_commands(
        [
            *list(scenario.primary_focus_commands or []),
            *list(scenario.supporting_inspection_commands or []),
            *list(scenario.safe_demo_commands or []),
        ]
    )
    demo_steps = scenario.demo_explanation_steps or []
    before_state = scenario.demo_repository_state or {}
    after_state = demo_steps[-1].get("repository_state") if demo_steps and isinstance(demo_steps[-1], dict) else before_state
    return {
        "title": "Command preview",
        "command_title": scenario.title,
        "syntax_examples": [
            example
            for command in commands
            for example in _syntax_examples(command)
        ],
        "supported_demo_commands": scenario.safe_demo_commands or commands,
        "demo_steps": demo_steps,
        "before_state": before_state,
        "after_state": after_state,
        "short_explanation": scenario.short_explanation,
        "common_mistakes": _common_mistakes(commands),
        "diagnostic": commands and all(is_diagnostic_command(command) for command in commands if command.startswith("git")),
        "counted": any(not is_diagnostic_command(command) for command in commands if command.startswith("git")),
    }


def _unique_commands(commands: list[str]) -> list[str]:
    seen = set()
    unique = []
    for command in commands:
        normalized = " ".join(str(command).split()).lower()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        unique.append(command)
    return unique


def _syntax_examples(command: str) -> list[str]:
    normalized = " ".join(command.split()).lower()
    examples = {
        "git status": ["git status"],
        "git log --oneline": ["git log --oneline", "git log --oneline --graph --all"],
        "git diff": ["git diff", "git diff --staged"],
        "git diff --staged": ["git diff --staged", "git diff --cached"],
        "git show": ["git show", "git show <commit>"],
        "git branch": ["git branch", "git branch -v"],
        "git remote -v": ["git remote", "git remote -v"],
        "git reflog": ["git reflog"],
        "git init": ["git init", "git init <directory>"],
        "git clone": ["git clone <url>", "git clone <url> <folder>"],
        "git add": ["git add <path>", "git add .", "git add -A", "git add -p <path>"],
        "git add -p": ["git add -p <path>"],
        "git commit": ['git commit -m "message"'],
        "git commit --amend": ["git commit --amend", 'git commit --amend -m "message"'],
        "git restore": ["git restore <path>", "git restore --staged <path>"],
        "git rm --cached": ["git rm --cached <path>"],
    }
    for prefix, syntax in examples.items():
        if normalized.startswith(prefix):
            return syntax
    return [command]


def _common_mistakes(commands: list[str]) -> list[str]:
    mistakes = []
    normalized = " ".join(commands).lower()
    if "git diff" in normalized:
        mistakes.append("Confusing unstaged diff output with staged diff output.")
    if "git add" in normalized:
        mistakes.append("Staging unrelated files instead of the requested path or hunk.")
    if "git restore" in normalized:
        mistakes.append("Using working-tree restore when you meant to unstage with --staged.")
    if "git commit --amend" in normalized:
        mistakes.append("Creating a new follow-up commit instead of replacing the latest local commit.")
    if not mistakes:
        mistakes.append("Skipping read-only inspection before choosing an action.")
    return mistakes[:3]


def _policy_payload(*, instance: DifficultyInstance, include_preview: bool) -> dict:
    policy = instance.command_policy
    payload = {
        "id": policy.id,
        "min_counted_commands": policy.min_counted_commands,
        "max_counted_commands": policy.max_counted_commands,
    }
    if include_preview:
        payload["non_counted_patterns"] = policy.non_counted_patterns
    return payload


def _completion_map(*, user, difficulty_ids: list[int]) -> dict[int, CompletionRecord]:
    if not difficulty_ids:
        return {}
    return {
        completion.difficulty_instance_id: completion
        for completion in CompletionRecord.objects.filter(
            user=user,
            difficulty_instance_id__in=difficulty_ids,
        )
        .select_related("session")
        .only(
            "difficulty_instance_id",
            "first_attempt_star",
            "counted_action_total",
            "completed_at",
            "session__id",
            "session__status",
            "session__counted_action_total",
            "session__total_attempts",
            "session__completed_at",
            "session__ended_at",
            "session__mode",
        )
    }


def _progress_map(
    *,
    difficulty_ids: list[int],
    required_map: dict[int, int],
    accurate_counts: dict[int, int],
    count_key: str,
) -> dict[int, dict]:
    if not difficulty_ids:
        return {}
    return {
        difficulty_id: {
            count_key: min(
                accurate_counts.get(difficulty_id, 0),
                required_map.get(difficulty_id, default_successful_attempts_for_difficulty("medium")),
            ),
            "required": required_map.get(
                difficulty_id,
                default_successful_attempts_for_difficulty("medium"),
            ),
        }
        for difficulty_id in difficulty_ids
    }


def _completed_difficulty_ids(*, user, difficulty_ids: list[int]) -> set[int]:
    if not difficulty_ids:
        return set()
    return set(
        ScenarioSession.objects.filter(
            user=user,
            mode=SESSION_MODE_PRIMARY,
            status=SESSION_STATUS_COMPLETED,
            difficulty_instance_id__in=difficulty_ids,
        ).values_list("difficulty_instance_id", flat=True)
    )


def _accurate_completion_counts(*, user, difficulty_ids: list[int]) -> dict[int, int]:
    if not difficulty_ids:
        return {}

    counts = {difficulty_id: 0 for difficulty_id in difficulty_ids}
    # Expected query shape: one session scan with command policy joined for all
    # visible difficulties; callers already have required attempt counts from
    # the prefetched DifficultyInstance rows.
    rows = (
        ScenarioSession.objects.filter(
            user=user,
            mode=SESSION_MODE_PRIMARY,
            status=SESSION_STATUS_COMPLETED,
            difficulty_instance_id__in=difficulty_ids,
        )
        .select_related("difficulty_instance__command_policy")
        .only(
            "difficulty_instance_id",
            "counted_action_total",
            "difficulty_instance__command_policy__min_counted_commands",
        )
    )
    for session in rows:
        if session.counted_action_total <= session.difficulty_instance.command_policy.min_counted_commands:
            counts[session.difficulty_instance_id] = counts.get(session.difficulty_instance_id, 0) + 1
    return counts


def _session_state_maps(
    *,
    user,
    difficulty_ids: list[int],
) -> tuple[dict[int, ScenarioSession], dict[int, ScenarioSession], dict[int, ScenarioSession]]:
    if not difficulty_ids:
        return {}, {}, {}
    active_sessions: dict[int, ScenarioSession] = {}
    latest_sessions: dict[int, ScenarioSession] = {}
    retryable_sessions: dict[int, ScenarioSession] = {}
    for session in (
        ScenarioSession.objects.filter(
            user=user,
            difficulty_instance_id__in=difficulty_ids,
        )
        .only(
            "id",
            "difficulty_instance_id",
            "status",
            "counted_action_total",
            "total_attempts",
            "completed_at",
            "ended_at",
            "mode",
        )
        .order_by("difficulty_instance_id", "-id")
    ):
        if session.mode != SESSION_MODE_PRIMARY:
            continue
        latest_sessions.setdefault(session.difficulty_instance_id, session)
        if session.status == SESSION_STATUS_STARTED:
            active_sessions.setdefault(session.difficulty_instance_id, session)
        elif session.status in {
            SESSION_STATUS_FAILED,
            SESSION_STATUS_ABANDONED,
            SESSION_STATUS_COMPLETED,
        }:
            retryable_sessions.setdefault(session.difficulty_instance_id, session)
    return active_sessions, latest_sessions, retryable_sessions


def _difficulty_status(
    *,
    instance: DifficultyInstance,
    completions: dict[int, CompletionRecord],
    active_sessions: dict[int, ScenarioSession],
    retryable_sessions: dict[int, ScenarioSession],
    difficulty_by_key: dict[tuple[int, str], DifficultyInstance],
    completed_ids: set[int],
) -> str:
    if instance.id in completed_ids:
        return "completed"
    if instance.id in active_sessions:
        return "in_progress"

    unlocked = _is_unlocked(
        instance=instance,
        difficulty_by_key=difficulty_by_key,
        completed_ids=completed_ids,
    )
    retryable_session = retryable_sessions.get(instance.id)
    if retryable_session and unlocked:
        return retryable_session.status
    if unlocked:
        return "not_started"
    return "locked"


def _is_unlocked(
    *,
    instance: DifficultyInstance,
    difficulty_by_key: dict[tuple[int, str], DifficultyInstance],
    completed_ids: set[int],
) -> bool:
    if instance.difficulty == DIFFICULTY_EASY:
        return True
    previous = DIFFICULTY_EASY if instance.difficulty == DIFFICULTY_MEDIUM else DIFFICULTY_MEDIUM
    previous_instance = difficulty_by_key.get((instance.scenario_id, previous))
    return bool(previous_instance and previous_instance.id in completed_ids)


def get_difficulty_instance(instance_id: int) -> DifficultyInstance:
    return (
        DifficultyInstance.objects.select_related(
            "scenario",
            "scenario__learning_unit",
            "command_policy",
            "target_rule",
        )
        .prefetch_related("variants")
        .get(
            id=instance_id,
            is_published=True,
            scenario__is_published=True,
            scenario__learning_unit__is_published=True,
            scenario__lesson__is_published=True,
        )
    )
