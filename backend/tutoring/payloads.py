from tutoring.models import PendingCommandIntroduction
from tutoring.services.commands import UNREAD, introduction_copy
from tutoring.services.forms import usage_for_teaching_key
from tutoring.services.guide_privacy import safe_guide
from tutoring.services.introductions import context_hash, issue_help_token, issue_token
from tutoring.services.planner import PlannerReads, plan_move
from tutoring.services.teaching import guide_key


def teaching_payload(run, *, reads: PlannerReads | None = None, pending=UNREAD) -> dict:
    """What a tier run teaches: the open command guide (``tutor``), the guides
    this scenario already taught (to read again), where the next move's command
    is taught when that is another scenario, and tips.

    ``reads`` and ``pending`` (the run's feedback row, or ``None``) let a
    command submission reuse what it already loaded.
    """

    if run.is_transfer:
        return {"tutor": None, "command_guides": [], "guide_elsewhere": None, "tips": []}
    reads = reads or PlannerReads(run.player_id)
    plan = plan_move(run, reads)
    elsewhere = plan.elsewhere if plan else None
    return {
        "tutor": _open_guide(run, plan.guide if plan else None, reads, pending),
        "command_guides": [
            _reference_guide(run, key, usage_for_teaching_key(key))
            for key in reads.homes_in(run.current_scenario_id)
            if key in reads.introduced
        ],
        "guide_elsewhere": (
            {
                "guide": _reference_guide(
                    run, elsewhere.form.teaching_key, elsewhere.form.usage_form
                ),
                "home": _home(elsewhere.home),
            }
            if elsewhere
            else None
        ),
        "tips": [tip.payload() for tip in plan.tips] if plan else [],
    }


def _open_guide(run, candidate, reads: PlannerReads, pending) -> dict | None:
    if pending is UNREAD:
        pending = PendingCommandIntroduction.objects.filter(run=run).first()
    if pending and "needs" not in pending.payload:
        # Feedback written in an older payload shape; replan instead.
        pending.delete()
        pending = None
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
            **safe,
            "help_token": issue_help_token(
                run, pending.teaching_key, safe["command_form"]["usage_form"]
            ),
            "completion_token": issue_token(run, pending.teaching_key, "feedback"),
        }
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


def _reference_guide(run, teaching_key: str, usage_form: str) -> dict:
    """A command guide to read, not tied to the next move: no repository
    changes and nothing to complete."""

    safe = safe_guide({"command_form": {"teaching_key": teaching_key, "usage_form": usage_form}})
    return {
        "context_id": f"{guide_key(teaching_key)}:reference",
        "teaching_key": guide_key(teaching_key),
        "run_revision": run.total_attempts,
        "phase": "introduction",
        **safe,
        "help_token": issue_help_token(run, teaching_key, safe["command_form"]["usage_form"]),
        "completion_token": None,
    }


def _home(home) -> dict:
    scenario = home.scenario
    level = scenario.tier.adventure_level
    return {
        "chapter_number": level.chapter.number,
        "level_title": level.title,
        "difficulty": scenario.tier.difficulty,
        "scenario_title": scenario.title,
    }
