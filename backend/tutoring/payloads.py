from tutoring.models import PendingCommandIntroduction, PlayerCommandIntroduction
from tutoring.services.commands import introduction_copy
from tutoring.services.introductions import context_hash, issue_token
from tutoring.services.planner import plan_introduction


def tutor_payload(run):
    pending = PendingCommandIntroduction.objects.filter(run=run).first()
    if pending and "needs" not in pending.payload:
        # Feedback written in an older payload shape; replan instead.
        pending.delete()
        pending = None
    context_id = context_hash(run)
    if (pending and pending.revision == run.total_attempts
            and pending.context_hash == context_id
            and not PlayerCommandIntroduction.objects.filter(
                player_id=run.player_id, teaching_key=pending.teaching_key,
            ).exists()):
        return {
            "context_id": f"{context_id}:{pending.teaching_key}:feedback",
            "teaching_key": pending.teaching_key,
            "run_revision": run.total_attempts,
            "phase": "feedback",
            **pending.payload,
            "completion_token": issue_token(run, pending.teaching_key, "feedback"),
        }
    candidate = plan_introduction(run)
    if candidate is None:
        return None
    return {
        "context_id": f"{context_id}:{candidate.teaching_key}:introduction",
        "teaching_key": candidate.teaching_key,
        "run_revision": run.total_attempts,
        "phase": "introduction",
        **introduction_copy(candidate),
        "changes": [],
        "verdict": None,
        "explanation": None,
        "example_command": None,
        "completion_token": None,
    }
