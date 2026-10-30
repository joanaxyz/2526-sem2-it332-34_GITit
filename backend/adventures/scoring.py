"""Adventure scoring — unified 3-star model.

  ★   cleared (solved)
  ★★  cleared within command budget (counted_commands <= min_counted_commands)
  ★★★ within budget with at most one retry

Returns 0 when not solved.
"""

from common.constants import SESSION_STATUS_COMPLETED, SESSION_STATUS_STARTED


def stars(*, solved: bool, counted_commands: int, budget: int, retry_count: int) -> int:
    if not solved:
        return 0
    within_budget = counted_commands <= budget
    return 1 + int(within_budget) + int(within_budget and retry_count <= 1)


def star_breakdown(run) -> dict | None:
    """Explain the saved grade or live eligibility using the same grading rule.

    Each criterion adds one star in order. An ended, unsolved run cannot earn
    bonuses; transfer checkpoints are deliberately ungraded.
    """
    if getattr(run, "is_transfer", False):
        return None
    active = run.status == SESSION_STATUS_STARTED
    solved = run.status == SESSION_STATUS_COMPLETED
    awarded = run.stars if solved else 0
    current_grade = stars(
        solved=True,
        counted_commands=run.counted_action_total,
        budget=run.min_counted_commands,
        retry_count=run.retry_index,
    )
    previous_rules = solved and awarded != current_grade
    available = current_grade if active else awarded
    criteria = []
    for value, key in enumerate(("clear", "command_target", "retry_allowance"), start=1):
        state = "earned" if value <= awarded else "pending" if value <= available else "missed"
        reason = None
        if state == "missed":
            if previous_rules:
                reason = "previous_scoring_rules"
            elif not active and not solved:
                reason = "not_cleared"
            elif run.counted_action_total > run.min_counted_commands:
                reason = "command_target_exceeded"
            elif key == "retry_allowance":
                reason = "retry_allowance_exceeded"
        criteria.append({"key": key, "state": state, "reason": reason})
    return {
        "stars": awarded,
        "available_stars": available,
        "counted_commands": run.counted_action_total,
        "command_target": run.min_counted_commands,
        "retry_count": run.retry_index,
        "graded_under_previous_rules": previous_rules,
        "criteria": criteria,
    }


def apply_library_penalty(*, stars: int, library_opened: bool) -> int:
    if not library_opened or stars <= 0:
        return stars
    return max(1, stars - 1)
