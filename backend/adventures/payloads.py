from django.db.models import Prefetch

from adventures.models import AdventureRun, SkillMastery
from adventures.services import (
    form_solve_targets,
    ordered_levels_for,
)
from common.constants import SESSION_STATUS_STARTED
from curriculum.models import CommandForm
from curriculum.stage_config import merged_battle_stage, stage_payload
from evaluation.checklist import ObjectiveChecklistEvaluator
from practice.models import CommandStep
from practice.services.context import ScenarioContextNormalizer
from progress.selectors import completed_adventure_level_count
from simulator.services import RepositorySnapshotService

_snapshotter = RepositorySnapshotService()


def _live_objective_checks(
    attempt: AdventureRun,
    *,
    executed_commands: list[str] | None = None,
) -> list:
    checks = attempt.current_wave.objective_checks if attempt.current_wave_id else []
    if not checks:
        return []
    if executed_commands is None:
        executed_commands = [step.command_text for step in attempt.steps.all()]
    return ObjectiveChecklistEvaluator().evaluate(
        checks,
        state=attempt.repository_state,
        initial_state=attempt.selected_variant.initial_state,
        executed_commands=executed_commands,
        state_already_normalized=True,
    )


def _mastery_payload(run: AdventureRun) -> dict:
    form_ids = (
        set(run.level.command_forms.values_list("id", flat=True))
        if run.level_id
        else set()
    )
    rows = {
        mastery.command_form_id: mastery
        for mastery in SkillMastery.objects.filter(
            player_id=run.player_id,
            command_form_id__in=form_ids,
        )
    }
    targets = form_solve_targets(form_ids)
    forms = (
        CommandForm.objects.filter(id__in=form_ids)
        .select_related("command_skill")
        .order_by("command_skill__sort_order", "sort_order", "id")
    )
    commands = []
    mastered = 0
    for form in forms:
        row = rows.get(form.id)
        solves = row.solves if row else 0
        target = targets.get(form.id, 1)
        is_mastered = bool(row and row.mastered)
        mastered += int(is_mastered)
        commands.append(
            {
                "slug": form.slug,
                "form_id": form.id,
                "form_slug": form.slug,
                "skill_slug": form.command_skill.slug,
                "title": form.label,
                "strength": solves,
                "mastered_bar": target,
                "introduced": bool(row and (row.solves > 0 or row.learned_at)),
                "mastered": is_mastered,
            }
        )
    total = len(form_ids)
    return {
        "commands": commands,
        "commands_mastered": mastered,
        "total_commands": total,
        "total_achievable": total,
        "passed": run.passed_at is not None,
    }


def _wave_context(wave) -> dict:
    if wave is None:
        return {"schema_version": 3, "story": "", "task": ""}
    return {
        "schema_version": 3,
        "story": wave.story,
        "task": wave.task,
    }


def _wave_index_for(attempt: AdventureRun) -> int:
    """0-based index of the active wave within its level."""
    wave = attempt.current_wave
    if wave is None:
        return 0
    return list(
        attempt.level.waves.filter(is_published=True)
        .order_by("sort_order", "id")
        .values_list("id", flat=True)
    ).index(wave.id) if attempt.level_id else 0


def attempt_payload(
    attempt: AdventureRun,
    *,
    executed_commands: list[str] | None = None,
    include_steps: bool = True,
) -> dict:
    level = attempt.level
    wave = attempt.current_wave
    variant = attempt.selected_variant
    raw_context = _merged_scenario_context(_wave_context(wave), variant.scenario_context or {})
    context = ScenarioContextNormalizer().normalize(
        raw_context,
        fallback_story="Reach the requested repository outcome cleanly.",
    )
    budget_owner = wave if wave is not None else None
    return {
        "id": attempt.id,
        "order": 0,
        "wave": _wave_index_for(attempt),
        "position": 0,
        "status": attempt.status,
        "level": {
            "id": level.id,
            "slug": level.slug,
            "title": level.title,
            "is_required": level.is_required,
            "reward_coins": level.reward_coins,
        },
        "wave_problem": None
        if wave is None
        else {
            "id": wave.id,
            "slug": wave.slug,
            "title": wave.title,
            "sort_order": wave.sort_order,
        },
        "variant": {"id": variant.id, "label": variant.label},
        "scenario_context": context,
        "objective_checks": _live_objective_checks(
            attempt,
            executed_commands=executed_commands
            if executed_commands is not None or include_steps
            else [],
        ),
        "scaffolding": {
            "live_dag": bool((variant.scaffold_policy or {}).get("live_dag", False)),
            "expected_state": False,
            "contextual_feedback": bool(
                (variant.scaffold_policy or {}).get("contextual_feedback", False)
            ),
        },
        "command_budget": {
            "min_counted_commands": budget_owner.min_counted_commands if budget_owner else 1,
            "max_counted_commands": budget_owner.max_counted_commands if budget_owner else 4,
        },
        "counts": {
            "command_count": attempt.command_count,
            "counted_command_count": attempt.counted_command_count,
        },
        "repository_state": _snapshotter.snapshot(
            attempt.repository_state,
            already_normalized=True,
        ),
        "steps": [
            {
                "id": step.id,
                "command_text": step.command_text,
                "terminal_output": step.terminal_output,
                "result_category": step.result_category,
            }
            for step in (attempt.steps.all() if include_steps else [])
        ],
    }


def _merged_scenario_context(level_context: dict, variant_context: dict) -> dict:
    if not level_context:
        return variant_context or {}
    if not variant_context:
        return level_context or {}
    level = ScenarioContextNormalizer().normalize(level_context, fallback_story="")
    variant = ScenarioContextNormalizer().normalize(variant_context, fallback_story="")
    merged = {
        "schema_version": 3,
        "story": variant.get("story") or level.get("story", ""),
        "task": variant.get("task") or level.get("task", ""),
        "details": _dedupe_details(
            [*(level.get("details") or []), *(variant.get("details") or [])]
        ),
    }
    return {key: value for key, value in merged.items() if value not in ("", [], {}, None)}


def _dedupe_details(details: list[dict]) -> list[dict]:
    seen = set()
    unique = []
    for detail in details:
        label = str(detail.get("label") or "").strip()
        value = str(detail.get("value") or "").strip()
        if not label or not value:
            continue
        key = (label.lower(), value.lower())
        if key in seen:
            continue
        seen.add(key)
        unique.append({"label": label, "value": value})
    return unique


def attempt_result_payload(attempt: AdventureRun) -> dict:
    return {
        "id": attempt.id,
        "order": 0,
        "status": attempt.status,
        "stars": attempt.stars,
        "counted_command_count": attempt.counted_command_count,
    }


def _level_ref(level) -> dict:
    return {
        "id": level.id,
        "slug": level.slug,
        "title": level.title,
        "is_required": level.is_required,
        "reward_coins": level.reward_coins,
    }


def _level_progress_payload(run: AdventureRun) -> dict:
    levels = ordered_levels_for(run.level) if run.level_id else []
    level_ids = [level.id for level in levels]
    if not level_ids:
        return {
            "current_level_index": 0,
            "total_levels": 0,
            "next_level": None,
            "progress": {"completed": 0, "total": 0},
        }

    current_index = level_ids.index(run.level_id) if run.level_id in level_ids else 0
    completed_count = completed_adventure_level_count(
        player_id=run.player_id,
        adventure_level_ids=level_ids,
    )
    next_level = levels[current_index + 1] if current_index + 1 < len(levels) else None
    return {
        "current_level_index": current_index + 1,
        "total_levels": len(levels),
        "next_level": _level_ref(next_level) if next_level is not None else None,
        "progress": {
            "completed": completed_count,
            "total": len(levels),
        },
    }


def adventure_run_payload(run: AdventureRun, *, include_current_steps: bool = True) -> dict:
    if include_current_steps:
        run = (
            AdventureRun.objects.select_related(
                "level",
                "level__chapter",
                "level__chapter__story",
                "level__source_content_definition",
                "current_wave",
                "selected_variant",
            )
            .prefetch_related(
                "level__command_forms",
                "level__waves",
                Prefetch("steps", queryset=CommandStep.objects.order_by("id")),
            )
            .get(id=run.id)
        )
    current = run if run.status == SESSION_STATUS_STARTED else None
    stage_chapter = run.level.chapter if run.level_id else None
    stage_config = (
        merged_battle_stage(chapter=stage_chapter, content_owner=run.level)
        if run.level_id
        else {}
    )
    total_waves = max(
        1, run.level.waves.filter(is_published=True).count() if run.level_id else 1
    )
    current_wave_number = (_wave_index_for(run) + 1) if run.status == SESSION_STATUS_STARTED else total_waves
    level_progress = _level_progress_payload(run)
    return {
        "id": run.id,
        "status": run.status,
        "replay": run.is_replay,
        "is_passed": bool(run.passed_at),
        "selected_level": None
        if run.level_id is None
        else {
            "id": run.level_id,
            "slug": run.level.slug,
            "title": run.level.title,
            "is_required": run.level.is_required,
            "reward_coins": run.level.reward_coins,
        },
        "story": None
        if not (run.level_id and run.level.chapter.story_id)
        else {
            "id": run.level.chapter.story_id,
            "slug": run.level.chapter.story.slug,
            "title": run.level.chapter.story.title,
            "world_slug": run.level.chapter.story.world_slug,
        },
        "chapter_id": stage_chapter.id if stage_chapter else None,
        "battle_stage": stage_payload(stage_config),
        "current_level_index": level_progress["current_level_index"],
        "total_levels": level_progress["total_levels"],
        "next_level": level_progress["next_level"],
        "current_wave": current_wave_number,
        "total_waves": total_waves,
        "stars": run.stars,
        "library_opened": run.library_opened,
        "passed": run.passed_at is not None,
        "mastery": _mastery_payload(run),
        "completed_at": run.completed_at,
        "current_attempt": attempt_payload(run, include_steps=include_current_steps)
        if current
        else None,
        "results": [] if current else [attempt_result_payload(run)],
        "progress": level_progress["progress"],
    }


def adventure_level_library_payload(run: AdventureRun) -> dict | None:
    from curriculum.library import library_key_for_command
    from curriculum.selectors import chapter_book

    if not run.level_id:
        return None
    book = chapter_book(chapter_id=run.level.chapter_id)
    if book is None:
        return None

    commands = []
    skill_ids = {
        form.command_skill_id
        for form in run.current_wave.command_forms.all()
        if form.command_skill_id is not None
    } if run.current_wave_id else set()
    if skill_ids:
        commands = [command for command in book["commands"] if command["id"] in skill_ids]

    solution_keys = {
        library_key_for_command(command)
        for command in (run.selected_variant.solution_commands or [])
        if str(command or "").strip()
    }
    if not commands and solution_keys:
        commands = [
            command
            for command in book["commands"]
            if library_key_for_command(command["base_command"]) in solution_keys
        ]

    if not commands:
        skill_ids = {
            form.command_skill_id
            for form in run.level.command_forms.all()
            if form.command_skill_id is not None
        }
        commands = [command for command in book["commands"] if command["id"] in skill_ids]

    return {
        **book,
        "command_count": len(commands),
        "commands": commands,
        "lesson_count": 0,
        "lessons": [],
    }


def adventure_command_payload(
    run: AdventureRun,
    *,
    attempt: AdventureRun,
    repository_state: dict | None = None,
    executed_commands: list[str] | None = None,
) -> dict:
    return {
        "partial": True,
        "id": run.id,
        "status": run.status,
        "current_attempt": {
            "id": attempt.id,
            "counts": {
                "command_count": attempt.command_count,
                "counted_command_count": attempt.counted_command_count,
            },
            "repository_state": repository_state
            if repository_state is not None
            else _snapshotter.snapshot(attempt.repository_state, already_normalized=True),
            "objective_checks": _live_objective_checks(
                attempt,
                executed_commands=executed_commands,
            ),
        },
    }
