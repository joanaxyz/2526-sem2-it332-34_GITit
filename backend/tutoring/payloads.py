from tutoring.models import PendingCommandIntroduction
from tutoring.services.commands import UNREAD, introduction_copy
from tutoring.services.guide_privacy import safe_guide
from tutoring.services.introductions import context_hash, issue_help_token, issue_token
from tutoring.services.planner import PlannerReads, plan_introduction
from tutoring.services.teaching import guide_key


def tutor_payload(run, *, reads: PlannerReads | None = None, pending=UNREAD):
    """``reads`` and ``pending`` (the run's feedback row, or ``None``) let a
    command submission reuse what it already loaded."""

    if pending is UNREAD:
        pending = PendingCommandIntroduction.objects.filter(run=run).first()
    if pending and "needs" not in pending.payload:
        # Feedback written in an older payload shape; replan instead.
        pending.delete()
        pending = None
    reads = reads or PlannerReads(run.player_id)
    context_id = context_hash(run)
    if (
        pending
        and pending.revision == run.total_attempts
        and pending.context_hash == context_id
        and pending.teaching_key not in reads.introduced
    ):
        safe = safe_guide(pending.payload)
        return {
            "context_id": f"{context_id}:{guide_key(pending.teaching_key)}:feedback",
            "teaching_key": guide_key(pending.teaching_key),
            "run_revision": run.total_attempts,
            "phase": "feedback",
            "anatomy": [],
            "concepts": [],
            **safe,
            "help_token": issue_help_token(
                run, pending.teaching_key, safe["command_form"]["usage_form"]
            ),
            "completion_token": issue_token(run, pending.teaching_key, "feedback"),
        }
    candidate = plan_introduction(run, reads)
    if candidate is None:
        return None
    safe = introduction_copy(candidate)
    return {
        "context_id": f"{context_id}:{guide_key(candidate.teaching_key)}:introduction",
        "teaching_key": guide_key(candidate.teaching_key),
        "run_revision": run.total_attempts,
        "phase": "introduction",
        **safe,
        "help_token": issue_help_token(
            run, candidate.teaching_key, safe["command_form"]["usage_form"]
        ),
        "changes": [],
        "verdict": None,
        "explanation": None,
        "completion_token": None,
    }
