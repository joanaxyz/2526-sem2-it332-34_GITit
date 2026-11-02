"""Validated command references. See KPI_METHODOLOGY.md for Let definitions."""

import hashlib
import json

from django.core.exceptions import ValidationError

from adventures.services.tier_budget import command_budget
from common.constants import RESULT_TARGET_MATCHED
from common.git.shell_commands import shell_program
from curriculum.services.solution_replay import replay_solutions
from evaluation.completion import CompletionEvaluationContext, PracticeCompletionEvaluator
from simulator.services import RepositoryStateSimulator
from simulator.trajectory import RepositoryFingerprinter

POLICY = 1


def digest(value) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def ref_hash(variant) -> str:
    return digest(
        {
            "policy": POLICY,
            "initial": variant.initial_state,
            "target": variant.target_state,
            "spec": variant.evaluation_spec,
            "commands": variant.solution_commands,
            "files": variant.solution_workspace_files,
            "diagnostics": variant.assess_diag,
            "action_limit": command_budget(variant)[1],
        }
    )


def valid_ref(variant) -> int | None:
    return (
        variant.ref_count if variant.ref_count and variant.ref_hash == ref_hash(variant) else None
    )


def state_key(variant) -> str:
    """Ignore generated commit IDs, messages and presentation bookkeeping."""
    fingerprinter = RepositoryFingerprinter()
    return digest(
        [
            fingerprinter.fingerprints(variant.initial_state)["coarse"],
            fingerprinter.fingerprints(variant.target_state)["coarse"],
        ]
    )


def validate_refs(variants, *, allow_unscored=False) -> dict[int, int]:
    """Replay first, evaluate the actual goal, then atomically persist references.

    Neither processability nor a matching star budget proves a valid solution.
    """
    variants = list(variants)
    cases = {
        str(v.id): {
            "initial_state": v.initial_state,
            "solution_commands": v.solution_commands,
            "workspace_files": v.solution_workspace_files,
            "max_counted_commands": command_budget(v)[1],
        }
        for v in variants
    }
    targets, replays = replay_solutions(cases)
    routes = {v.id: (targets[str(v.id)], replays[str(v.id)]["steps"]) for v in variants}
    return _save_refs(variants, routes, allow_unscored=allow_unscored)


def seed_refs(variants) -> dict[int, int]:
    """Persist references from the committed replay, so seeding needs no Node.

    ``generate_targets`` stores the browser engine's replay as each variant's
    target state and solution trajectory, and CI proves both match a fresh
    replay. A variant without a stored route stays unscored.
    """
    variants = list(variants)
    routes = {
        v.id: (v.target_state, steps)
        for v in variants
        if (steps := (v.solution_trajectory or {}).get("steps"))
    }
    return _save_refs(variants, routes, allow_unscored=True)


def _save_refs(variants, routes, *, allow_unscored) -> dict[int, int]:
    counts = {}
    tools = RepositoryStateSimulator()
    evaluator = PracticeCompletionEvaluator()
    for variant in variants:
        if variant.id not in routes:
            continue
        final, steps = routes[variant.id]
        result = evaluator.evaluate(
            CompletionEvaluationContext(
                variant=variant,
                next_state=final,
                executed_commands=variant.solution_commands,
                next_state_hash=tools.state_hash(final),
                expected_state_hash=tools.state_hash(variant.target_state),
            )
        )
        if result.result_category != RESULT_TARGET_MATCHED:
            raise ValidationError(f"Reference for {variant.slug} does not solve its objective.")
        count = sum(
            1
            for step in steps
            if not shell_program(step["command"])
            and (not step["diagnostic"] or variant.assess_diag)
        )
        if not count:
            if allow_unscored:
                continue
            raise ValidationError(
                f"{variant.slug} has no counted commands; explicitly assess diagnostics if appropriate."
            )
        counts[variant.id] = count
    for variant in variants:
        variant.ref_count = counts.get(variant.id)
        variant.ref_hash = ref_hash(variant) if variant.ref_count else ""
    if variants:
        type(variants[0]).objects.bulk_update(
            variants, ["ref_count", "ref_hash", "assess_diag"], batch_size=200
        )
    return counts
