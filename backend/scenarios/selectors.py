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
from scenarios.command_content import (
    base_command_for_command,
    command_content_key_for_command,
    normalize_command_text,
    pages_from_command_sections,
)
from scenarios.models import (
    CompletionRecord,
    DifficultyInstance,
    GitCommandContent,
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
    config = scenario.command_preview_config or {}
    if config:
        return _normalized_command_preview_config(scenario, config)

    commands = _unique_commands(
        [
            *list(scenario.primary_focus_commands or []),
            *list(scenario.supporting_inspection_commands or []),
            *list(scenario.safe_demo_commands or []),
        ]
    )
    demo_steps = scenario.demo_explanation_steps or []
    before_state = scenario.demo_repository_state or {}
    preview_commands = _resolved_preview_commands(
        scenario=scenario,
        config={},
        commands=commands,
        before_state=before_state,
        sections=[],
    )
    if not demo_steps:
        demo_steps = [
            step
            for preview_command in preview_commands
            for step in preview_command.get("demo_steps", [])
            if isinstance(step, dict)
        ]
    after_state = demo_steps[-1].get("repository_state") if demo_steps and isinstance(demo_steps[-1], dict) else before_state
    return {
        "schema_version": 2,
        "title": "Command preview",
        "command_title": scenario.title,
        "commands": preview_commands,
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


def _normalized_command_preview_config(scenario: ScenarioSkillFocus, config: dict) -> dict:
    sections = [
        section
        for section in config.get("sections", [])
        if isinstance(section, dict)
    ]
    supported_commands = config.get("supported_demo_commands") or scenario.safe_demo_commands or []
    demo_steps = []
    for section in sections:
        demo_steps.extend(
            step
            for step in section.get("demo_steps", [])
            if isinstance(step, dict)
        )
    if not demo_steps:
        demo_steps = scenario.demo_explanation_steps or []
    before_state = config.get("demo_repository_state") or scenario.demo_repository_state or {}
    commands = _unique_commands(
        [
            *list(scenario.primary_focus_commands or []),
            *list(scenario.supporting_inspection_commands or []),
            *list(supported_commands),
        ]
    )
    preview_commands = _resolved_preview_commands(
        scenario=scenario,
        config=config,
        commands=commands,
        before_state=before_state,
        sections=sections,
    )
    if not demo_steps:
        demo_steps = [
            step
            for preview_command in preview_commands
            for step in preview_command.get("demo_steps", [])
            if isinstance(step, dict)
        ]
    after_state = demo_steps[-1].get("repository_state") if demo_steps and isinstance(demo_steps[-1], dict) else before_state
    return {
        "schema_version": config.get("schema_version") or 2,
        "title": config.get("title") or "Command preview",
        "intro": config.get("intro") or scenario.short_explanation,
        "purpose": config.get("purpose") or scenario.summary,
        "focus_label": config.get("focus_label") or scenario.focus,
        "command_title": config.get("command_title") or scenario.title,
        "commands": preview_commands,
        "custom_pages": _normalize_preview_pages(config.get("custom_pages") or []),
        "command_refs": config.get("command_refs") or [],
        "sections": sections,
        "syntax_examples": config.get("syntax_examples")
        or _syntax_examples_from_preview_commands(preview_commands)
        or _section_syntax_examples(sections),
        "supported_demo_commands": supported_commands or commands,
        "demo_steps": demo_steps,
        "demo_repository_state": before_state,
        "demo_dag_config": config.get("demo_dag_config") or scenario.demo_dag_config or {},
        "before_state": before_state,
        "after_state": after_state,
        "short_explanation": config.get("short_explanation") or scenario.short_explanation,
        "what_changes": config.get("what_changes") or [],
        "what_does_not_change": config.get("what_does_not_change") or [],
        "common_mistakes": config.get("common_mistakes") or _common_mistakes(commands),
        "readiness_notes": config.get("readiness_notes") or [],
        "diagnostic": config.get("diagnostic")
        if "diagnostic" in config
        else commands and all(is_diagnostic_command(command) for command in commands if command.startswith("git")),
        "counted": config.get("counted")
        if "counted" in config
        else any(not is_diagnostic_command(command) for command in commands if command.startswith("git")),
    }


def _resolved_preview_commands(
    *,
    scenario: ScenarioSkillFocus,
    config: dict,
    commands: list[str],
    before_state: dict,
    sections: list[dict],
) -> list[dict]:
    lookup = _command_content_lookup()
    direct_commands = config.get("commands")
    if isinstance(direct_commands, list) and direct_commands:
        return [
            _direct_preview_command(
                command=item,
                index=index,
                scenario=scenario,
                before_state=before_state,
            )
            for index, item in enumerate(direct_commands)
            if isinstance(item, dict)
        ]

    refs = config.get("command_refs") or []
    if refs:
        preview_commands = [
            _preview_command_from_ref(
                ref=_normalize_command_ref(ref),
                index=index,
                scenario=scenario,
                config=config,
                lookup=lookup,
                before_state=before_state,
            )
            for index, ref in enumerate(refs)
        ]
    elif sections:
        preview_commands = [
            _legacy_section_preview_command(
                section=section,
                index=index,
                before_state=before_state,
            )
            for index, section in enumerate(sections)
        ]
    else:
        preview_commands = [
            _preview_command_from_ref(
                ref={"command": command, "key": command_content_key_for_command(command)},
                index=index,
                scenario=scenario,
                config=config,
                lookup=lookup,
                before_state=before_state,
            )
            for index, command in enumerate(commands)
        ]

    preview_commands = _dedupe_preview_commands(preview_commands)

    custom_pages = _normalize_preview_pages(config.get("custom_pages") or [])
    if custom_pages:
        preview_commands.append(
            {
                "id": "scenario-context",
                "key": "scenario-context",
                "title": config.get("custom_pages_title") or "Scenario context",
                "command": "",
                "canonical_command": "",
                "aliases": [],
                "summary": config.get("purpose") or scenario.summary,
                "tags": ["scenario"],
                "pages": custom_pages,
                "demo_steps": [],
            }
        )
    return [command for command in preview_commands if command.get("pages")]


def _dedupe_preview_commands(preview_commands: list[dict]) -> list[dict]:
    deduped: list[dict] = []
    index_by_key: dict[str, int] = {}
    for command in preview_commands:
        if not isinstance(command, dict):
            continue
        dedupe_key = command.get("key") or command.get("base_command") or command.get("command") or command.get("title")
        dedupe_key = normalize_command_text(str(dedupe_key))
        if not dedupe_key:
            deduped.append(command)
            continue
        if dedupe_key not in index_by_key:
            index_by_key[dedupe_key] = len(deduped)
            deduped.append(command)
            continue

        existing = deduped[index_by_key[dedupe_key]]
        existing["demo_steps"] = _merge_unique_by_fields(
            existing.get("demo_steps") or [],
            command.get("demo_steps") or [],
            ("command", "title"),
        )
        existing["sections"] = _merge_unique_by_fields(
            existing.get("sections") or [],
            command.get("sections") or [],
            ("id", "title"),
        )
        existing["pages"] = _merge_unique_by_fields(
            existing.get("pages") or [],
            command.get("pages") or [],
            ("id", "title"),
        )
    return deduped


def _merge_unique_by_fields(existing: list, incoming: list, fields: tuple[str, ...]) -> list:
    merged = list(existing)
    seen = {
        tuple(str(item.get(field, "")) for field in fields)
        for item in merged
        if isinstance(item, dict)
    }
    for item in incoming:
        if not isinstance(item, dict):
            continue
        identity = tuple(str(item.get(field, "")) for field in fields)
        if identity in seen:
            continue
        seen.add(identity)
        merged.append(item)
    return merged


def _command_content_lookup() -> dict[str, GitCommandContent]:
    lookup = {}
    for content in GitCommandContent.objects.filter(is_active=True):
        lookup[content.key] = content
        lookup[normalize_command_text(content.canonical_command)] = content
        for alias in content.aliases or []:
            lookup[normalize_command_text(alias)] = content
    return lookup


def _normalize_command_ref(ref: str | dict) -> dict:
    if isinstance(ref, str):
        return {"key": command_content_key_for_command(ref), "command": ref}
    if isinstance(ref, dict):
        command = ref.get("command") or ref.get("canonical_command") or ""
        key = ref.get("key") or command_content_key_for_command(command)
        return {**ref, "key": key}
    return {"key": "", "command": ""}


def _preview_command_from_ref(
    *,
    ref: dict,
    index: int,
    scenario: ScenarioSkillFocus,
    config: dict,
    lookup: dict[str, GitCommandContent],
    before_state: dict,
) -> dict:
    ref_command = ref.get("command") or ref.get("canonical_command") or ""
    command = ref_command
    key = ref.get("key") or command_content_key_for_command(command)
    content = lookup.get(key) or lookup.get(normalize_command_text(command))
    title = ref.get("title") or ref.get("display_name")
    summary = ref.get("summary")
    if content:
        demo_command = command or content.canonical_command
        command = content.canonical_command
        title = title or content.display_name
        summary = summary or content.summary
        aliases = content.aliases or []
        tags = content.tags or []
        base_command = content.base_command or base_command_for_command(command)
        sections = _resolved_content_sections(content=content, ref=ref, config=config)
        pages = _resolved_content_pages(
            content=content,
            ref=ref,
            config=config,
        )
    else:
        title = title or command or "Command"
        summary = summary or "Use this preview command before starting the generated scenario."
        aliases = []
        tags = []
        base_command = base_command_for_command(command)
        sections = []
        pages = _fallback_command_pages(command=command, title=title, summary=summary)
        demo_command = command

    return {
        "id": ref.get("id") or key or f"command-{index}",
        "key": key,
        "base_command": ref.get("base_command") or base_command,
        "title": title,
        "display_name": content.display_name if content else title,
        "command": command,
        "canonical_command": content.canonical_command if content else command,
        "aliases": aliases,
        "summary": summary,
        "tags": tags,
        "sections": sections,
        "pages": pages,
        "demo_steps": _demo_steps_for_preview_command(
            scenario=scenario,
            ref=ref,
            command=demo_command,
            title=title,
            summary=summary,
            before_state=before_state,
        ),
    }


def _resolved_content_pages(
    *,
    content: GitCommandContent,
    ref: dict,
    config: dict,
) -> list[dict]:
    section_pages = pages_from_command_sections(_normalize_command_sections(content.sections or []))
    pages = _normalize_preview_pages(section_pages or content.pages or [])
    include_ids = _included_page_ids(config=config, ref=ref, key=content.key)
    if include_ids:
        include_set = {str(page_id) for page_id in include_ids}
        pages = [page for page in pages if str(page.get("id")) in include_set]

    overrides = _page_override_map(_command_page_overrides(config=config, ref=ref, key=content.key))
    if overrides:
        pages = [_merge_page_override(page, overrides.get(str(page.get("id")))) for page in pages]

    if ref.get("replace_pages"):
        pages = _normalize_preview_pages(ref.get("pages") or [])

    prepend_pages = _normalize_preview_pages(ref.get("prepend_pages") or [])
    append_pages = _normalize_preview_pages(
        ref.get("append_pages") or ref.get("custom_pages") or []
    )
    return [*prepend_pages, *pages, *append_pages]


def _resolved_content_sections(
    *,
    content: GitCommandContent,
    ref: dict,
    config: dict,
) -> list[dict]:
    sections = _normalize_command_sections(content.sections or [])
    include_ids = _included_page_ids(config=config, ref=ref, key=content.key)
    if include_ids:
        include_set = {str(section_id) for section_id in include_ids}
        sections = [section for section in sections if str(section.get("id")) in include_set]
    if ref.get("replace_sections"):
        sections = _normalize_command_sections(ref.get("sections") or [])
    append_sections = _normalize_command_sections(
        ref.get("append_sections") or ref.get("custom_sections") or []
    )
    return [*sections, *append_sections]


def _included_page_ids(*, config: dict, ref: dict, key: str) -> list[str]:
    raw = (
        ref.get("include_page_ids")
        or ref.get("included_page_ids")
        or config.get("include_page_ids")
        or config.get("included_page_ids")
    )
    if isinstance(raw, dict):
        raw = raw.get(key)
    return raw if isinstance(raw, list) else []


def _command_page_overrides(*, config: dict, ref: dict, key: str):
    raw = ref.get("page_overrides")
    if raw:
        return raw
    raw = config.get("page_overrides") or {}
    if isinstance(raw, dict) and key in raw:
        return raw[key]
    return raw


def _page_override_map(raw) -> dict[str, dict]:
    if isinstance(raw, list):
        return {
            str(item.get("id")): item
            for item in raw
            if isinstance(item, dict) and item.get("id")
        }
    if isinstance(raw, dict):
        if all(isinstance(value, dict) for value in raw.values()):
            return {str(key): value for key, value in raw.items()}
        if raw.get("id"):
            return {str(raw["id"]): raw}
    return {}


def _merge_page_override(page: dict, override: dict | None) -> dict:
    if not override:
        return page
    merged = {**page, **override}
    if "blocks" in override:
        merged["blocks"] = _normalize_preview_blocks(override["blocks"])
    return merged


def _direct_preview_command(
    *,
    command: dict,
    index: int,
    scenario: ScenarioSkillFocus,
    before_state: dict,
) -> dict:
    command_text = command.get("command") or command.get("canonical_command") or ""
    title = command.get("title") or command.get("display_name") or command_text or "Command"
    summary = command.get("summary") or ""
    sections = _normalize_command_sections(command.get("sections") or [])
    section_pages = pages_from_command_sections(sections)
    pages = _normalize_preview_pages(command.get("pages") or section_pages)
    return {
        "id": command.get("id") or command.get("key") or f"command-{index}",
        "key": command.get("key") or command_content_key_for_command(command_text),
        "base_command": command.get("base_command") or base_command_for_command(command_text),
        "title": title,
        "display_name": command.get("display_name") or title,
        "command": command_text,
        "canonical_command": command.get("canonical_command") or command_text,
        "aliases": command.get("aliases") or [],
        "summary": summary,
        "tags": command.get("tags") or [],
        "sections": sections,
        "pages": pages,
        "demo_steps": _demo_steps_for_preview_command(
            scenario=scenario,
            ref=command,
            command=command_text,
            title=title,
            summary=summary,
            before_state=before_state,
        ),
    }


def _legacy_section_preview_command(
    *,
    section: dict,
    index: int,
    before_state: dict,
) -> dict:
    command = section.get("command") or section.get("title") or ""
    title = section.get("title") or command or "Command"
    pages = _normalize_preview_pages(section.get("pages") or [])
    if not pages:
        pages = _fallback_command_pages(
            command=command,
            title=title,
            summary=section.get("explanation") or "",
            syntax_examples=section.get("syntax_examples") or [],
        )
    demo_steps = _normalize_demo_steps(
        section.get("demo_steps") or [],
        fallback_snapshot=before_state,
        fallback_command=command,
        fallback_title=title,
        fallback_explanation=section.get("explanation") or "",
    )
    return {
        "id": section.get("id") or command_content_key_for_command(command) or f"section-{index}",
        "key": command_content_key_for_command(command),
        "base_command": base_command_for_command(command),
        "title": title,
        "display_name": title,
        "command": command,
        "canonical_command": command,
        "aliases": [],
        "summary": section.get("explanation") or "",
        "tags": [],
        "sections": [],
        "pages": pages,
        "demo_steps": demo_steps,
    }


def _normalize_command_sections(value) -> list[dict]:
    if not isinstance(value, list):
        return []
    sections = []
    allowed_types = {
        "overview",
        "form",
        "option",
        "argument",
        "effect",
        "mistake",
        "practice_note",
    }
    for index, section in enumerate(value, start=1):
        if not isinstance(section, dict):
            continue
        section_type = section.get("type") or "overview"
        if section_type not in allowed_types:
            section_type = "overview"
        title = section.get("title") or f"Section {index}"
        normalized = {
            "id": section.get("id") or f"section-{index}",
            "type": section_type,
            "title": title,
            "content": _normalize_preview_blocks(section.get("content") or []),
        }
        if section.get("command"):
            normalized["command"] = section["command"]
        if section.get("token"):
            normalized["token"] = section["token"]
        sections.append(normalized)
    return sections


def _normalize_preview_pages(value) -> list[dict]:
    if not isinstance(value, list):
        return []
    pages = []
    for index, page in enumerate(value, start=1):
        if not isinstance(page, dict):
            continue
        title = page.get("title") or page.get("heading") or f"Page {index}"
        normalized = {
            key: page[key]
            for key in (
                "id",
                "title",
                "subtitle",
                "eyebrow",
                "heading",
                "body",
                "demo_steps",
                "section_type",
            )
            if key in page
        }
        normalized["id"] = normalized.get("id") or f"page-{index}"
        normalized["title"] = title
        normalized["blocks"] = _normalize_preview_blocks(page.get("blocks") or [])
        pages.append(normalized)
    return pages


def _normalize_preview_blocks(value) -> list[dict]:
    if not isinstance(value, list):
        return []
    blocks = []
    for block in value:
        if not isinstance(block, dict):
            continue
        normalized = dict(block)
        if normalized.get("type") == "list":
            normalized["type"] = "bullet_list"
        blocks.append(normalized)
    return blocks


def _fallback_command_pages(
    *,
    command: str,
    title: str,
    summary: str,
    syntax_examples: list[str] | None = None,
) -> list[dict]:
    syntax = syntax_examples or _syntax_examples(command)
    return [
        {
            "id": "overview",
            "title": "Overview",
            "blocks": [
                {"type": "paragraph", "body": summary},
                {"type": "command", "title": "Command forms", "items": syntax},
            ],
        },
        {
            "id": "readiness",
            "title": "Readiness",
            "blocks": [
                {
                    "type": "callout",
                    "title": title,
                    "body": "Use this preview content before starting the generated scenario.",
                }
            ],
        },
    ]


def _demo_steps_for_preview_command(
    *,
    scenario: ScenarioSkillFocus,
    ref: dict,
    command: str,
    title: str,
    summary: str,
    before_state: dict,
) -> list[dict]:
    explicit_steps = _normalize_demo_steps(
        ref.get("demo_steps") or [],
        fallback_snapshot=before_state,
        fallback_command=command,
        fallback_title=title,
        fallback_explanation=summary,
    )
    if explicit_steps:
        return explicit_steps

    normalized_command = normalize_command_text(command)
    scenario_steps = _normalize_demo_steps(
        scenario.demo_explanation_steps or [],
        fallback_snapshot=before_state,
        fallback_command=command,
        fallback_title=title,
        fallback_explanation=summary,
    )
    matching_steps = [
        step
        for step in scenario_steps
        if normalize_command_text(step.get("command", "")) == normalized_command
    ]
    if matching_steps:
        return matching_steps
    if not command:
        return []

    diagnostic = command.startswith("git ") and is_diagnostic_command(command)
    return [
        {
            "command": command,
            "title": title or command,
            "explanation": summary,
            "repository_state": before_state,
            "common_mistake": "",
            "diagnostic": diagnostic,
            "counted": command.startswith("git ") and not diagnostic,
        }
    ]


def _normalize_demo_steps(
    value,
    *,
    fallback_snapshot: dict,
    fallback_command: str,
    fallback_title: str,
    fallback_explanation: str,
) -> list[dict]:
    if not isinstance(value, list):
        return []
    steps = []
    for index, step in enumerate(value, start=1):
        if not isinstance(step, dict):
            continue
        command = step.get("command") or fallback_command or f"Demo step {index}"
        title = step.get("title") or fallback_title or command
        explanation = step.get("explanation") or fallback_explanation
        diagnostic = step.get("diagnostic")
        if diagnostic is None:
            diagnostic = command.startswith("git ") and is_diagnostic_command(command)
        steps.append(
            {
                "command": command,
                "title": title,
                "explanation": explanation,
                "repository_state": step.get("repository_state") or fallback_snapshot,
                "common_mistake": step.get("common_mistake") or "",
                "diagnostic": diagnostic,
                "counted": step.get("counted")
                if "counted" in step
                else command.startswith("git ") and not diagnostic,
            }
        )
    return steps


def _syntax_examples_from_preview_commands(preview_commands: list[dict]) -> list[str]:
    examples = []
    for command in preview_commands:
        for page in command.get("pages", []):
            for block in page.get("blocks", []):
                if block.get("type") in {"command", "code"}:
                    examples.extend(block.get("items") or [])
    return _unique_commands(examples)


def _section_syntax_examples(sections: list[dict]) -> list[str]:
    examples = []
    for section in sections:
        if not isinstance(section, dict):
            continue
        examples.extend(section.get("syntax_examples", []))
    return examples


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
        "git diff --staged": ["git diff --staged", "git diff --cached"],
        "git diff": ["git diff", "git diff --staged"],
        "git show": ["git show", "git show <commit>"],
        "git branch": ["git branch", "git branch -v"],
        "git remote -v": ["git remote", "git remote -v"],
        "git reflog": ["git reflog"],
        "git init": ["git init", "git init <directory>"],
        "git clone": ["git clone <url>", "git clone <url> <folder>"],
        "git add -p": ["git add -p <path>"],
        "git add": ["git add <path>", "git add .", "git add -A", "git add -p <path>"],
        "git commit --amend": ["git commit --amend", 'git commit --amend -m "message"'],
        "git commit": ['git commit -m "message"'],
        "git restore --staged": ["git restore --staged <path>"],
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
