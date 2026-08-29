"""Adventure scoring — unified 3-star model.

  ★   cleared (solved)
  ★★  cleared within command budget (counted_commands <= min_counted_commands)
  ★★★ first-try within budget (retry_index == 0, within budget)

Returns 0 when not solved.
"""


def stars(*, solved: bool, counted_commands: int, budget: int, first_try: bool) -> int:
    if not solved:
        return 0
    within_budget = counted_commands <= budget
    return 1 + int(within_budget) + int(within_budget and first_try)


def apply_library_penalty(*, stars: int, library_opened: bool) -> int:
    if not library_opened or stars <= 0:
        return stars
    return max(1, stars - 1)
