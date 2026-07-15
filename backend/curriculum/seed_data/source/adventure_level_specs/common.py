"""Shared helpers for authored adventure level specs."""

from __future__ import annotations

import copy

from curriculum.seed_data.blueprint_overlay import BLUEPRINT_ADVENTURE_LEVELS
from curriculum.seed_data.generated.generated_targets import TARGET_STATES
from curriculum.seed_data.source.adventure_fixtures import (
    BASE,
    BASE_TREE,
    REMOTE_FIXTURE_HISTORY,
    REMOTE_FIXTURE_MAIN,
    REMOTE_FIXTURE_STARTER,
    THREE_COMMITS,
    TWO_COMMITS,
)
from curriculum.seed_data.source.command_routing import adventure_for_usage
from curriculum.seed_data.spec_helpers import commit, ev, meta_equals, repo, uninitialized


def _adventure_for_usage(usage: str) -> str:
    return adventure_for_usage(usage)

def _command_from_usage(usage: str) -> str:
    """Return the command family a level is meant to train.

    Objective checks are shared by every variant of a level, so they must stay
    variant-safe. Specific files, branches, and commit IDs belong in the
    per-variant evaluation_spec; the checklist only verifies the intended Git
    move was used.
    """
    family = usage.split("/", 1)[0]
    if usage.startswith(("git-checkout/create-and-switch", "git-checkout/legacy-create")):
        return "git switch"
    if usage.startswith("git-checkout/"):
        return "git checkout"
    command_map = {
        "git-cherry-pick": "git cherry-pick",
        "git-checkout-conflict": "git checkout",
        "git-diff-conflict": "git diff",
        "git-ls-files": "git ls-files",
        "git-merge-base": "git merge-base",
        "git-rev-list": "git rev-list",
    }
    if family in command_map:
        return command_map[family]
    if family.startswith("git-"):
        return "git " + family[4:]
    return family.replace("-", " ")

def _modular_checks(checks: list[dict] | None) -> list[dict]:
    """Keep authored objective checks as a modular, variant-safe checklist.

    Each authored check must carry a human ``label`` plus a non-empty
    ``requirement`` expressed in the evaluation_spec vocabulary. They are used
    verbatim - one checklist row per real sub-goal of the scenario - so the
    learner sees granular progress instead of a single bashed-together objective.

    Contract (the author is responsible for this): every requirement must be
    variant-safe (identical truth across all of a wave's variants) and an
    end-state outcome (false before the step is done, true after). A requirement
    that names a specific file/branch/commit belongs in the per-variant
    evaluation_spec, not here.
    """
    result: list[dict] = []
    for check in checks or []:
        if not isinstance(check, dict):
            continue
        label = str(check.get("label", "")).strip()
        requirement = check.get("requirement") or {}
        if not label:
            raise ValueError("Workflow objective check is missing a label.")
        if not requirement:
            raise ValueError(f"Workflow objective check {label!r} has an empty requirement.")
        result.append({"label": label, "requirement": requirement})
    if not result:
        raise ValueError("Workflow level declared no objective checks.")
    return result

def _variant_safe_checks(usage: str, checks: list[dict] | None) -> list[dict]:
    command = _command_from_usage(usage)
    first_label = None
    for check in checks or []:
        label = str(check.get("label", "")).strip()
        if label:
            first_label = label
            break
    return [
        {
            "label": first_label or f"Use {command} for the requested Git move.",
            "requirement": {"required_commands": [command]},
        }
    ]

def _text(value) -> str:
    if value in (None, ""):
        return ""
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, dict):
        return ", ".join(f"{key}: {_text(item)}" for key, item in value.items() if _text(item))
    if isinstance(value, (list, tuple, set)):
        return ", ".join(_text(item) for item in value if _text(item))
    return str(value).strip()

def _normalize_detail(entry) -> tuple[str, str]:
    """Accept either a plain copyable value or a legacy {label, value} dict.

    The frontend renders only the value (plus a copy button); the story/task
    prose is responsible for saying what each value is for, so new content
    authors bare strings.
    """
    if isinstance(entry, dict):
        return str(entry.get("label", "") or ""), _text(entry.get("value"))
    return "", _text(entry)

def _add_detail(details: list[dict], seen: set[str], entry) -> None:
    label, text = _normalize_detail(entry)
    if not text:
        return
    key = text.lower()
    if key in seen:
        return
    seen.add(key)
    details.append({"label": label, "value": text})

def _task_with_notes(task: str, task_notes: list[str] | None) -> str:
    notes = [_text(item) for item in task_notes or [] if _text(item)]
    if not notes:
        return task
    note_text = " ".join(notes)
    return f"{task} {note_text}" if task else note_text

def _variant_with_context(
    variant: dict,
    *,
    story: str,
    task: str,
    details: list[dict] | None,
    task_notes: list[str] | None,
) -> dict:
    enriched = copy.deepcopy(variant)
    # Details are an *authored* slot only - a short list of hard-to-retype literals
    # the learner genuinely needs (remote URLs, exact branch/commit refs). We no
    # longer auto-derive details from the solution commands or the repo state:
    # that leaked the answer (it printed the exact tokens to type) and read like a
    # spec sheet. Everything narrative belongs in `story`/`task` instead.
    #
    # `story`/`task`/level-`details` are shared by every variant; per-variant
    # literals (the URL/branch/commit THIS variant uses, which differ for the
    # anti-memorization rotation) come from the variant's own `details`.
    variant_details = enriched.pop("detail_overrides", None) or []
    merged_details: list[dict] = []
    seen: set[str] = set()
    for detail in list(details or []) + list(variant_details):
        _add_detail(merged_details, seen, detail)
    # Hard guard against the old bloat: copy details are only a few literals.
    if len(merged_details) > 4:
        raise ValueError(
            f"Level copy details list {len(merged_details)} values; keep it to <=4 hard-to-retype "
            "literals (URLs/refs) and move the rest into the story/task."
        )

    enriched["scenario_context_template"] = {
        "schema_version": 3,
        "story": story,
        "task": _task_with_notes(task, task_notes),
        "details": merged_details,
    }
    return enriched

def v(
    case_id: str,
    label: str,
    initial: dict,
    solution: list[str],
    evaluation: dict,
    *,
    hints: list[str] | None = None,
    details: list[dict] | None = None,
    workspace_files: list[dict] | None = None,
) -> dict:
    return {
        "case_id": case_id,
        "slug_template": case_id,
        "label_template": label,
        "initial_state_template": initial,
        # `.get` (not `[case_id]`) so the seed imports before targets exist - the
        # `generate_targets` command imports these specs to read initial_state +
        # solution_commands, then computes the targets. A genuinely missing target
        # is caught downstream (builders + seed_curriculum reject an empty target).
        "target_state_template": TARGET_STATES.get(case_id, {}),
        "solution_commands_template": solution,
        "solution_workspace_files_template": workspace_files or [],
        "evaluation_spec_template": evaluation,
        "scaffold_policy_template": {},
        # Consumed by `_variant_with_context` (popped, never persisted): the
        # hard-to-retype literals unique to this variant (URL/branch/commit).
        "detail_overrides": details or [],
    }

def q(
    usage: str,
    slug: str,
    title: str,
    story: str,
    task: str,
    variants: list[dict],
    *,
    checks: list[dict],
    prerequisites: list[str] | None = None,
    min_counted_commands: int = 1,
    max_counted_commands: int = 4,
    details: list[dict] | None = None,
    task_notes: list[str] | None = None,
    command_forms: list[str] | None = None,
    adventure: str | None = None,
    workflow: bool = False,
    level_type: str = "guided_workflow",
    narrative_brief: dict | None = None,
) -> dict:
    # `workflow=True` opts a level into the modular objective checklist: the
    # authored `checks` are used verbatim, so each step of the scenario is its own
    # variant-safe, end-state objective (ticks off only when that step is truly
    # done). Legacy single-move levels (workflow=False) collapse to one
    # "the move was used" check via _variant_safe_checks until they are re-authored.
    objective_checks = _modular_checks(checks) if workflow else _variant_safe_checks(usage, checks)
    return {
        "usage": usage,
        "adventure": adventure or _adventure_for_usage(usage),
        "slug": slug,
        "title": title,
        "min_counted_commands": min_counted_commands,
        "max_counted_commands": max_counted_commands,
        "scenario_context": {
            "schema_version": 3,
            "story": story,
            "task": _task_with_notes(task, task_notes),
            "details": [
                {"label": label, "value": value}
                for label, value in (_normalize_detail(entry) for entry in details or [])
                if value
            ],
        },
        "objective_checks": objective_checks,
        "command_forms": command_forms or [],
        "prerequisites": prerequisites or [],
        "level_type": level_type,
        "narrative_brief": narrative_brief or {},
        "variants": [
            _variant_with_context(
                variant,
                story=story,
                task=task,
                details=details,
                task_notes=task_notes,
            )
            for variant in variants
        ],
    }


__all__ = [name for name in globals() if not name.startswith("__")]
