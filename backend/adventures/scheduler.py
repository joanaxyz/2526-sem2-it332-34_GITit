"""Spaced-repetition (Leitner) scheduler for Command Adventure.

Turns an adventure into an interleaved mastery session: an *introduction front*
(new commands, in curriculum order, gated by prerequisites) running alongside a
*review pool* (introduced-but-unmastered commands, resurfaced when due, weakest
first). Spacing is measured in encounters, not wall-clock time.

Mastery is a Leitner box 0..N per (user, problem), where N is the problem's
`required_successful_attempts`. A passing solve advances a box; a failure demotes.
Each command's box decides how long it rests before it is due again.
"""

from __future__ import annotations

import random

from adventures.models import AdventureMastery, AdventureQuest, AdventureQuestAttempt

# --- tunables --------------------------------------------------------------
BOX_VALUE = 10               # mastery points awarded per box advanced
PASS_BAR_FRACTION = 0.60     # default share of achievable points needed to pass
WARMUP_K = 2                 # introduced commands before review interleaving starts
FLOOR_STRENGTH = 1           # every command must reach this box before a pass counts
PREREQ_STRENGTH = 1          # a prerequisite must be at least this box to unlock a dependent
# Encounters a command rests before it is due again, indexed by its current box.
# Clamped: boxes beyond the list reuse the last interval.
_INTERVALS = [1, 3, 6]


def interval_for(strength: int) -> int:
    return _INTERVALS[min(strength, len(_INTERVALS) - 1)]


def encounter_index(*, user, adventure) -> int:
    """The user's running encounter count for this adventure (across runs)."""
    return AdventureQuestAttempt.objects.filter(
        run__user=user, run__command_adventure=adventure
    ).count()


def _ordered_problems(adventure, *, with_prerequisites: bool = False) -> list[AdventureQuest]:
    # Imported lazily to avoid a services <-> scheduler import cycle.
    from adventures.services import ordered_problems_for

    return ordered_problems_for(adventure, with_prerequisites=with_prerequisites)


class AdventureScheduler:
    """Stateless picker; all state lives in AdventureMastery rows."""

    def _mastery_map(self, *, user, problems: list[AdventureQuest]) -> dict[int, AdventureMastery]:
        rows = AdventureMastery.objects.filter(
            user=user, adventure_quest__in=[p.id for p in problems]
        )
        return {row.adventure_quest_id: row for row in rows}

    def next_problem(
        self, *, user, adventure, problems: list[AdventureQuest] | None = None
    ) -> AdventureQuest | None:
        """Pick the next command-problem to serve, or None when the session is
        complete (every command mastered / nothing left to introduce). Callers
        that already resolved the ordered problems (with prerequisites) pass them
        in so the join runs once per request."""
        if problems is None:
            problems = _ordered_problems(adventure, with_prerequisites=True)
        if not problems:
            return None
        mastery = self._mastery_map(user=user, problems=problems)
        idx = encounter_index(user=user, adventure=adventure)

        def strength(p):
            row = mastery.get(p.id)
            return row.strength if row else 0

        def introduced(p):
            row = mastery.get(p.id)
            return bool(row and row.introduced)

        def last_seen(p):
            row = mastery.get(p.id)
            return row.last_seen_seq if row else 0

        def mastered(p):
            return strength(p) >= p.required_successful_attempts

        def prereqs_met(p):
            return all(strength(pre) >= PREREQ_STRENGTH for pre in p.prerequisites.all())

        introduced_problems = [p for p in problems if introduced(p)]
        pool = [p for p in introduced_problems if not mastered(p)]
        new = [p for p in problems if not introduced(p) and prereqs_met(p)]
        due = [p for p in pool if idx - last_seen(p) >= interval_for(strength(p))]

        # Warm-up: introduce sequentially until there is enough to interleave.
        if len(introduced_problems) < WARMUP_K and new:
            return new[0]
        if due:
            return self._weakest(due, idx=idx, strength=strength, last_seen=last_seen)
        if new:
            return new[0]
        if pool:
            return self._weakest(pool, idx=idx, strength=strength, last_seen=last_seen)
        return None

    def _weakest(self, items, *, idx, strength, last_seen) -> AdventureQuest:
        """Lowest box first, then most overdue, with a random tie-break."""
        best = min((strength(p), -(idx - last_seen(p))) for p in items)
        tied = [p for p in items if (strength(p), -(idx - last_seen(p))) == best]
        return random.choice(tied)

    def select_variant(self, *, user, problem):
        """Least-recently-used published variant for this user+problem; cycles when
        fewer variants exist than needed (graceful degradation)."""
        variants = list(problem.variants.filter(is_published=True).order_by("semantic_key", "id"))
        if not variants:
            return None
        recent = (
            AdventureQuestAttempt.objects.filter(run__user=user, adventure_quest=problem)
            .order_by("-id")
            .values_list("selected_variant_id", flat=True)
        )
        recency: dict[int, int] = {}
        for rank, vid in enumerate(recent):
            recency.setdefault(vid, rank)

        def sort_key(v):
            r = recency.get(v.id)
            if r is None:
                return (0, v.id)        # never used -> highest priority
            return (1, -r)              # used -> least-recently-used first

        variants.sort(key=sort_key)
        return variants[0]

    def mark_served(self, *, user, problem, idx: int) -> AdventureMastery:
        row, _ = AdventureMastery.objects.get_or_create(user=user, adventure_quest=problem)
        row.introduced = True
        row.last_seen_seq = idx
        row.save(update_fields=["introduced", "last_seen_seq", "updated_at"])
        return row

    def apply_result(self, *, user, problem, passed: bool, solved: bool) -> bool:
        """Update the Leitner box after an attempt. Returns whether a box advanced
        (which is what earns mastery points)."""
        row, _ = AdventureMastery.objects.get_or_create(user=user, adventure_quest=problem)
        ceiling = problem.required_successful_attempts
        box_advanced = False
        if passed and row.strength < ceiling:
            row.strength += 1
            box_advanced = True
        elif not solved and row.strength > 0:
            row.strength -= 1
        row.save(update_fields=["strength", "updated_at"])
        return box_advanced


# --- pass-bar helpers ------------------------------------------------------

def total_achievable(adventure, *, problems=None) -> int:
    problems = problems if problems is not None else _ordered_problems(adventure)
    return sum(p.required_successful_attempts * BOX_VALUE for p in problems)


def pass_bar_for(adventure, *, problems=None) -> float:
    fraction = adventure.pass_bar_fraction or PASS_BAR_FRACTION
    return total_achievable(adventure, problems=problems) * fraction


def floor_met(*, user, adventure, problems=None) -> bool:
    """Every command in the adventure has been solved at least once (box >= floor)."""
    problems = problems if problems is not None else _ordered_problems(adventure)
    strengths = dict(
        AdventureMastery.objects.filter(
            user=user, adventure_quest__in=[p.id for p in problems]
        ).values_list("adventure_quest_id", "strength")
    )
    return all(strengths.get(p.id, 0) >= FLOOR_STRENGTH for p in problems)


def is_passed(*, user, adventure, session_score: int, problems=None) -> bool:
    problems = problems if problems is not None else _ordered_problems(adventure)
    return session_score >= pass_bar_for(adventure, problems=problems) and floor_met(
        user=user, adventure=adventure, problems=problems
    )
