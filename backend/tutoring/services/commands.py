"""Observe the existing verified terminal path without changing its accounting."""

from simulator.trajectory import describe_transition, route_position
from tutoring.models import PendingCommandIntroduction
from tutoring.services.anatomy import anatomy
from tutoring.services.guide_privacy import safe_guide
from tutoring.services.introductions import context_hash

# Marks a feedback row that has not been read yet (``None`` means there is none).
UNREAD = object()


def stored_feedback(run):
    # The command submission joins the row onto its locked run read.
    if type(run).pendingcommandintroduction.is_cached(run):
        return getattr(run, "pendingcommandintroduction", None)
    return PendingCommandIntroduction.objects.filter(run=run).first()


def current_feedback(run, stored=UNREAD):
    pending = stored_feedback(run) if stored is UNREAD else stored
    if (
        pending
        and pending.revision == run.total_attempts
        and pending.context_hash == context_hash(run)
    ):
        return pending
    return None


def used_introduced_form(candidate, execution) -> bool:
    result = execution.result
    return bool(
        candidate is not None
        and result.processed
        and not result.exit_code
        and candidate.form.used_by(result.normalized_command)
    )


def record_command_feedback(run, candidate, execution, previous_feedback=None, stored=UNREAD):
    """Record feedback for the command that ran while ``candidate`` was introduced.

    ``candidate`` is the introduction planned *before* the command ran, and
    ``stored`` the run's feedback row read before it ran. Returns the run's
    feedback row afterwards, or ``None``.
    """

    used_form = used_introduced_form(candidate, execution)
    if previous_feedback is not None:
        # Reading feedback must not race the next terminal submission. Keep the
        # same lesson until acknowledged; refresh its binding after every command.
        if not (used_form and candidate.teaching_key == previous_feedback.teaching_key):
            previous_feedback.payload = safe_guide(previous_feedback.payload)
            previous_feedback.revision = run.total_attempts
            previous_feedback.context_hash = context_hash(run)
            previous_feedback.save(update_fields=["revision", "context_hash", "payload"])
            return previous_feedback
    if stored is not None:
        PendingCommandIntroduction.objects.filter(run=run).delete()
    if candidate is None:
        return None
    result = execution.result
    if used_form:
        changes = describe_transition(execution.previous_state, execution.next_state)
        verdict = "correct"
        # Off the authored route is not necessarily wrong (another order or name
        # may still solve it), so only the on-route case makes a claim.
        explanation = (
            "That's the right command."
            if _advanced_route(run, candidate, execution)
            else "That worked. Check the task for your next step."
        )
    elif execution.state_mutated:
        # A different route changed what is useful next. The planner decides
        # afresh from the new repository; never reveal an obsolete example.
        return None
    elif result.processed and not result.exit_code and result.diagnostic:
        # Looking around (status, log, diff) is always fine.
        return None
    else:
        verdict = "incorrect"
        explanation = "That wasn't the command this step needs."
        changes = []
    return PendingCommandIntroduction.objects.create(
        run=run,
        teaching_key=candidate.teaching_key,
        revision=run.total_attempts,
        context_hash=context_hash(run),
        payload={
            **introduction_copy(candidate),
            "changes": changes,
            "verdict": verdict,
            "explanation": explanation,
        },
    )


def introduction_copy(candidate) -> dict:
    form = candidate.form
    return safe_guide(
        {
            "title": form.label or form.usage_form,
            # What the repository needs from this move, as structured changes.
            "needs": [dict(change) for change in candidate.step_effect if isinstance(change, dict)],
            "command_form": form.payload(),
            "anatomy": anatomy(form.usage_form),
        }
    )


def _advanced_route(run, candidate, execution) -> bool:
    from adventures.services.tier_history import TierCommandHistoryCache

    history = [*TierCommandHistoryCache().history_for(run=run)]
    if not history or history[-1] != execution.result.normalized_command:
        history.append(execution.result.normalized_command)
    position = route_position(
        run.selected_variant.solution_trajectory, execution.next_state, history
    )
    return position is not None and position > candidate.last_step_index
