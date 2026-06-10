"""Per-check evaluation for the adventure objective checklist.

The objective checklist is a learner-facing, gitmastery-style list of end-state
outcomes. Each authored check carries a human `label` plus a machine
`requirement` expressed in the same vocabulary as `evaluation_spec`
`state_requirements`. This evaluator runs each requirement against the current
repository state so the UI can tick checks off live.

This is display-only: whether a problem is *solved* is still decided wholesale by
the variant's `evaluation_spec` via the EvaluationEngine. The checklist only
narrates progress toward that goal.
"""

from evaluation.services import StateBasedEvaluator


class ObjectiveChecklistEvaluator:
    def evaluate(
        self,
        checks: list | None,
        *,
        state: dict,
        initial_state: dict | None = None,
        executed_commands: list[str] | None = None,
    ) -> list[dict]:
        evaluator = StateBasedEvaluator()
        results: list[dict] = []
        for check in checks or []:
            if not isinstance(check, dict):
                continue
            label = str(check.get("label", "")).strip()
            requirement = check.get("requirement") or {}
            if not label:
                continue
            # An empty requirement would match vacuously (no rules → no failures),
            # so a check with no requirement is reported unsatisfied rather than
            # silently always-green. Authoring validation forbids this case.
            satisfied = bool(
                requirement
                and evaluator.evaluate(
                    state,
                    requirement,
                    initial_state=initial_state,
                    executed_commands=executed_commands or [],
                ).target_matched
            )
            results.append({"label": label, "satisfied": satisfied})
        return results
