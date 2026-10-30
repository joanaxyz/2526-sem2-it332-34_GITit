"""Versioned scoring snapshots shared by both gameplay surfaces."""

from common.runtime.star_targets import counted_command_total

SCORING_POLICY_VERSION = 2


def thresholds(efficient, maximum, generous=None):
    efficient = max(1, int(efficient))
    maximum = max(int(maximum), efficient + 2)
    generous = efficient + (maximum - efficient + 1) // 2 if generous is None else int(generous)
    if not efficient < generous < maximum:
        raise ValueError("Targets must satisfy efficient < generous < maximum.")
    return efficient, generous, maximum


def run_scoring_snapshot(variant, *, efficient, maximum):
    from curriculum.services.solution_audit import verified_route_cost
    from curriculum.services.techniques import required_techniques

    params = variant.parameter_context or {}
    efficient = max(
        efficient,
        int(params.get("minimum_counted_commands", 0)),
        counted_command_total(variant.solution_commands),
        verified_route_cost(variant.case_id),
    )
    maximum = int(params.get("maximum_counted_commands", maximum))
    efficient, generous, maximum = thresholds(
        efficient,
        maximum,
        params.get(
            "generous_counted_commands",
            getattr(
                getattr(variant, "scenario", None) or getattr(variant, "trial", None),
                "generous_counted_commands",
                None,
            ),
        ),
    )
    return {
        "min_counted_commands": efficient,
        "generous_counted_commands": generous,
        "max_counted_commands": maximum,
        "scoring_policy_version": SCORING_POLICY_VERSION,
        "example_counted_commands": counted_command_total(variant.solution_commands),
        "required_techniques": params.get(
            "required_techniques", required_techniques(variant.case_id)
        ),
    }


def command_comparison(run):
    if run.status != "completed" or getattr(run, "is_transfer", False):
        return None
    example = run.example_counted_commands
    if example is None:
        return None
    learner = run.counted_action_total
    return {
        "learner_count": learner,
        "example_count": example,
        "relation": "fewer" if learner < example else "equal" if learner == example else "more",
    }
