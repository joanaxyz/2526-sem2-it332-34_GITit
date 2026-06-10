from django.db.models import Prefetch

from adventures.models import AdventureMastery, AdventureQuestAttempt, AdventureRun
from adventures.scheduler import pass_bar_for, total_achievable
from adventures.services import ordered_problems_for
from common.constants import SESSION_STATUS_STARTED
from evaluation.checklist import ObjectiveChecklistEvaluator
from practice.context import ScenarioContextNormalizer
from practice.models import CommandStep
from simulator.services import RepositorySnapshotService

_snapshotter = RepositorySnapshotService()


def _live_objective_checks(attempt: AdventureQuestAttempt) -> list:
    """Evaluate the adventure-only objective checklist against the attempt's
    current repository state. Shared by the full attempt payload and the slim
    per-command payload so the checklist ticks off identically on both paths.
    Checks are authored on the problem (`objective_checks`); their server-side
    requirements never leave the backend — only {label, satisfied} rows do."""
    return ObjectiveChecklistEvaluator().evaluate(
        attempt.adventure_quest.objective_checks,
        state=attempt.repository_state,
        initial_state=attempt.selected_variant.initial_state,
    )


def _mastery_payload(run: AdventureRun, problems: list) -> dict:
    """Per-command Leitner state for the adventure, plus the session's pass-bar
    progress. Drives the mastery UI (boxes, commands mastered, score vs bar).
    `problems` is passed in so the ordered-problems join runs once per request."""
    rows = {
        m.adventure_quest_id: m
        for m in AdventureMastery.objects.filter(
            user_id=run.user_id, adventure_quest__in=[p.id for p in problems]
        )
    }
    commands = []
    mastered = 0
    for problem in problems:
        row = rows.get(problem.id)
        strength = row.strength if row else 0
        ceiling = problem.required_successful_attempts
        is_mastered = strength >= ceiling
        mastered += int(is_mastered)
        commands.append(
            {
                "slug": problem.slug,
                "title": problem.title,
                "strength": strength,
                "mastered_bar": ceiling,
                "introduced": bool(row and row.introduced),
                "mastered": is_mastered,
            }
        )
    return {
        "commands": commands,
        "commands_mastered": mastered,
        "total_commands": len(problems),
        "session_score": run.session_score,
        "pass_bar": round(pass_bar_for(run.command_adventure, problems=problems)),
        "total_achievable": total_achievable(run.command_adventure, problems=problems),
        "passed": run.passed_at is not None,
    }


def attempt_payload(attempt: AdventureQuestAttempt) -> dict:
    problem = attempt.adventure_quest
    variant = attempt.selected_variant
    # The narrative is authored on the problem and shared across its variants;
    # the variant only carries a generated fallback, so the problem's authored
    # context wins.
    raw_context = problem.scenario_context or variant.scenario_context or {}
    context = ScenarioContextNormalizer().normalize(
        raw_context,
        fallback_story="Reach the requested repository outcome cleanly.",
    )
    return {
        "id": attempt.id,
        "order": attempt.order,
        "status": attempt.status,
        "problem": {
            "id": problem.id,
            "slug": problem.slug,
            "title": problem.title,
            "is_required": problem.is_required,
        },
        "variant": {"id": variant.id, "label": variant.label},
        "scenario_context": context,
        # The objective checklist is adventure-only and ticks off live: each
        # authored check's server-side requirement is evaluated against the
        # current attempt state. Display-only — completion is still governed by
        # evaluation_spec. Same shape as the per-command patch field.
        "objective_checks": _live_objective_checks(attempt),
        # Adventure scaffolding is deliberately minimal: hints only, no
        # expected-state reveal, no contextual panel by default. A variant may
        # opt into a richer panel via scaffold_policy, but expected_state is
        # always forced off so the answer never leaks in adventure mode.
        "scaffolding": {
            "live_dag": bool((variant.scaffold_policy or {}).get("live_dag", False)),
            "expected_state": False,
            "contextual_feedback": bool(
                (variant.scaffold_policy or {}).get("contextual_feedback", False)
            ),
            "hints": True,
        },
        "available_hints": len(variant.hint_set or []),
        "command_budget": {
            "min_counted_commands": problem.min_counted_commands,
            "max_counted_commands": problem.max_counted_commands,
        },
        "counts": {
            "command_count": attempt.command_count,
            "counted_command_count": attempt.counted_command_count,
            "hint_count": attempt.hint_count,
        },
        "repository_state": _snapshotter.snapshot(
            attempt.repository_state, already_normalized=True
        ),
        # Command history for the terminal. Mirrors the challenge `steps` payload
        # so the frontend can derive terminal lines from cached server state
        # (and rehydrate on refresh) instead of ephemeral component state. Only
        # the live attempt is serialized through here, so this stays bounded.
        "steps": [
            {
                "id": step.id,
                "command_text": step.command_text,
                "terminal_output": step.terminal_output,
                "result_category": step.result_category,
            }
            for step in attempt.steps.all()
        ],
    }


def attempt_result_payload(attempt: AdventureQuestAttempt) -> dict:
    return {
        "id": attempt.id,
        "order": attempt.order,
        "status": attempt.status,
        "correctness_score": attempt.correctness_score,
        "efficiency_score": attempt.efficiency_score,
        "independence_score": attempt.independence_score,
        "final_score": attempt.final_score,
        "mastery_gain": attempt.mastery_gain,
        "hint_count": attempt.hint_count,
        "counted_command_count": attempt.counted_command_count,
    }


def adventure_run_payload(run: AdventureRun) -> dict:
    # The ordered-problems join is shared by total_problems, the mastery panel,
    # and the pass-bar math; resolve it once per request instead of 4x.
    problems = ordered_problems_for(run.command_adventure)
    attempts = list(
        run.attempts.select_related("adventure_quest", "selected_variant").prefetch_related(
            Prefetch("steps", queryset=CommandStep.objects.order_by("id"))
        )
    )
    current = next(
        (a for a in attempts if a.status == SESSION_STATUS_STARTED), None
    )
    total_problems = len(problems)
    return {
        "id": run.id,
        "status": run.status,
        "mode": run.mode,
        # Stable across re-runs: a replay never clears this, so the outcome UI and
        # challenge gate can rely on it instead of the latest run's status.
        "is_passed": run.command_adventure.runs.filter(
            user_id=run.user_id, passed_at__isnull=False
        ).exists(),
        "command_adventure": {
            "id": run.command_adventure_id,
            "slug": run.command_adventure.slug,
            "title": run.command_adventure.title,
            "description": run.command_adventure.description,
        },
        # The adventure's storey (module) is its OneToOne owner; surfaced so the
        # completion modal's "Back to Tower" lands on the right storey.
        "storey_id": run.command_adventure.module_id,
        "current_problem_index": run.current_problem_index,
        "total_problems": total_problems,
        "session_score": run.session_score,
        "passed": run.passed_at is not None,
        "mastery_progress_gained": run.mastery_progress_gained,
        "mastery": _mastery_payload(run, problems),
        "completed_at": run.completed_at,
        "current_attempt": attempt_payload(current) if current else None,
        "results": [attempt_result_payload(a) for a in attempts],
        "progress": {
            "completed": sum(1 for a in attempts if a.status != SESSION_STATUS_STARTED),
            "total": total_problems,
        },
    }


def adventure_command_payload(run: AdventureRun, *, attempt: AdventureQuestAttempt) -> dict:
    """Lightweight per-command payload, returned while an attempt is still in
    progress. Mirrors the challenge `command_run_payload` split: mid-attempt only
    the live attempt state changes (repository, counts, objective checklist), so
    the mastery panel, results list, problem text, and scenario normalization are
    all skipped. The full `adventure_run_payload` is sent only when the attempt
    transitions (solved / budget spent) — which is when mastery and the next
    problem actually change. The frontend merges this patch into the cached run."""
    return {
        "partial": True,
        "id": run.id,
        "status": run.status,
        "current_attempt": {
            "id": attempt.id,
            "counts": {
                "command_count": attempt.command_count,
                "counted_command_count": attempt.counted_command_count,
                "hint_count": attempt.hint_count,
            },
            "repository_state": _snapshotter.snapshot(
                attempt.repository_state, already_normalized=True
            ),
            "objective_checks": _live_objective_checks(attempt),
        },
    }
