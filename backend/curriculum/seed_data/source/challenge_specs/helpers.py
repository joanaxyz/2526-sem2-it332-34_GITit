"""Shared helpers for authored challenge seed specs."""

from __future__ import annotations

from typing import Any

from curriculum.seed_data.blueprint_overlay import BLUEPRINT_CHALLENGE_SPECS
from curriculum.seed_data.generated.generated_targets import TARGET_STATES
from curriculum.seed_data.source.challenge_fixtures import (
    BRANCH_BASE,
    BRANCH_LONG,
    CLONE_REMOTE,
    CONFLICT_HISTORY,
    MERGE_BASE,
    PATCH_HISTORY,
    PRECONFLICT,
    RECOVERY_HISTORY,
    REMOTE_BASE,
    REMOTE_DIVERGED,
    REMOTE_FIXTURE_AHEAD,
    SNAPSHOT_BASE,
    SNAPSHOT_WITH_SECRET,
)
from curriculum.seed_data.spec_helpers import commit, ev, meta_equals, repo, uninitialized

DIFFICULTY_ORDER = {"easy": 1, "medium": 2, "hard": 3}

def _contract(
    state_requirements: dict[str, Any],
    *,
    required: list[str] | None = None,
    forbidden: list[str] | None = None,
    graph: dict[str, Any] | None = None,
    concepts: list[str] | None = None,
    engine_notes: list[str] | None = None,
) -> dict[str, Any]:
    spec = ev(state_requirements, required=required, forbidden=forbidden)
    spec["curriculum_contract"] = {
        "schema_version": 1,
        "challenge_type": "scenario_graph_transition",
        "dag_transition": graph or {},
        "concepts_used": concepts or [],
        "engine_notes": engine_notes or [],
    }
    return spec

def _with_context_notes(story: str, *, before: str, current: str | None, risk: str | None) -> str:
    rows = [story, f"You open the repository and find {before}."]
    if current:
        rows.append(current)
    if risk:
        rows.append(f"This matters because {_lower_first(risk)}")
    return " ".join(row for row in rows if row)

def _with_target_notes(task: str, *, after: str, task_notes: list[str] | None) -> str:
    notes = [task, f"The handoff is done when the repository reaches this state: {after}."]
    notes.extend(
        task_notes
        or [
            "Use the repository diagram and status clues before acting.",
            "The final answer is the repository state, not a memorized command string.",
        ]
    )
    return " ".join(note for note in notes if note)

def _lower_first(value: str) -> str:
    return value[:1].lower() + value[1:] if value else value

def _scenario(
    story: str,
    task: str,
    *,
    before: str,
    after: str,
    current: str | None = None,
    risk: str | None = None,
    task_notes: list[str] | None = None,
    details: list | None = None,
) -> dict[str, Any]:
    context = {
        "schema_version": 3,
        "story": _with_context_notes(story, before=before, current=current, risk=risk),
        "task": _with_target_notes(task, after=after, task_notes=task_notes),
    }
    if details:
        # The frontend shows only copyable values; the story/task prose says
        # what each value is for. Accept bare strings (preferred) or legacy
        # {label, value} dicts.
        context["details"] = [
            entry
            if isinstance(entry, dict)
            else {"label": "", "value": str(entry)}
            for entry in details
        ]
    return context

def variant(
    case_id: str,
    label: str,
    *,
    story: str,
    task: str,
    before: str,
    after: str,
    initial: dict[str, Any],
    solution: list[str],
    evaluation: dict[str, Any],
    current: str | None = None,
    risk: str | None = None,
    workspace_files: list[dict[str, Any]] | None = None,
    details: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    return {
        "case_id": case_id,
        "slug_template": case_id,
        "label_template": label,
        "initial_state_template": initial,
        # `.get` (not `[case_id]`) so the seed imports before targets exist; the
        # `generate_targets` command reads these specs to compute the targets. A
        # genuinely missing target is rejected downstream (empty target_state).
        "target_state_template": TARGET_STATES.get(case_id, {}),
        "solution_commands_template": solution,
        "solution_workspace_files_template": workspace_files or [],
        "evaluation_spec_template": evaluation,
        "scenario_context_template": _scenario(
            story,
            task,
            before=before,
            after=after,
            current=current,
            risk=risk,
            details=details,
        ),
        "scaffold_policy_template": {
            "diagram": "primary",
        },
    }

# First-completion GitCoin payout per trial difficulty (override via `reward`).
TRIAL_REWARD_DEFAULTS = {"easy": 40, "medium": 80, "hard": 140}


def level(
    difficulty: str,
    *,
    story: str,
    task: str,
    before: str,
    after: str,
    variants: list[dict[str, Any]],
    uses_adventure_levels: list[str],
    current: str | None = None,
    risk: str | None = None,
    min_counted_commands: int = 1,
    max_counted_commands: int = 8,
    reward: int | None = None,
) -> dict[str, Any]:
    scenario = _scenario(
        story,
        task,
        before=before,
        after=after,
        current=current,
        risk=risk,
    )
    return {
        "difficulty": difficulty,
        "min_counted_commands": min_counted_commands,
        "max_counted_commands": max_counted_commands,
        "reward_coins": TRIAL_REWARD_DEFAULTS.get(difficulty, 40) if reward is None else reward,
        "uses_adventure_levels": uses_adventure_levels,
        "scenario_context": scenario,
        "variants": variants,
    }

def challenge(
    module: str,
    slug: str,
    title: str,
    summary: str,
    narrative: str,
    levels: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "module": module,
        "slug": slug,
        "title": title,
        "summary": summary,
        "narrative": narrative,
        "levels": levels,
    }


__all__ = [name for name in globals() if not name.startswith("__")]
