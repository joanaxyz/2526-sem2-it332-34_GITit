from common.constants import SESSION_STATUS_STARTED
from adventures.services import ordered_problems_for
from practice.context import StudentContextNormalizer
from adventures.models import AdventureProblemAttempt, AdventureRun
from simulator.services import RepositorySnapshotService

_snapshotter = RepositorySnapshotService()


def attempt_payload(attempt: AdventureProblemAttempt) -> dict:
    problem = attempt.adventure_problem
    variant = attempt.selected_variant
    context = StudentContextNormalizer().normalize(
        variant.student_context or problem.student_context,
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
            "summary": problem.summary,
            "is_required": problem.is_required,
        },
        "variant": {"id": variant.id, "label": variant.label},
        "student_context": context,
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
            "min_counted_commands": variant.min_counted_commands,
            "max_counted_commands": variant.max_counted_commands,
            "ideal_counted_commands": variant.ideal_counted_commands,
        },
        "counts": {
            "command_count": attempt.command_count,
            "counted_command_count": attempt.counted_command_count,
            "hint_count": attempt.hint_count,
        },
        "repository_state": _snapshotter.snapshot(
            attempt.repository_state, already_normalized=True
        ),
    }


def attempt_result_payload(attempt: AdventureProblemAttempt) -> dict:
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
    attempts = list(run.attempts.select_related("adventure_problem", "selected_variant"))
    current = next(
        (a for a in attempts if a.status == SESSION_STATUS_STARTED), None
    )
    total_problems = len(ordered_problems_for(run.command_adventure))
    return {
        "id": run.id,
        "status": run.status,
        "command_adventure": {
            "id": run.command_adventure_id,
            "slug": run.command_adventure.slug,
            "title": run.command_adventure.title,
            "description": run.command_adventure.description,
        },
        "current_problem_index": run.current_problem_index,
        "total_problems": total_problems,
        "total_score": run.total_score,
        "mastery_progress_gained": run.mastery_progress_gained,
        "completed_at": run.completed_at,
        "current_attempt": attempt_payload(current) if current else None,
        "results": [attempt_result_payload(a) for a in attempts],
        "progress": {
            "completed": sum(1 for a in attempts if a.status != SESSION_STATUS_STARTED),
            "total": total_problems,
        },
    }
