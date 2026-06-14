"""Spaced-repetition (Leitner) scheduler for Command Adventure.

Turns an adventure into an interleaved mastery session: an *introduction front*
(new commands, in curriculum order, gated by prerequisites) running alongside a
*review pool* (introduced-but-unmastered commands, resurfaced when due, weakest
first). Spacing is measured in encounters, not wall-clock time.

Mastery is a Leitner box 0..N per (user, level), where N is the level's
`required_successful_attempts`. A passing solve advances a box; a failure demotes.
Each command's box decides how long it rests before it is due again.
"""

from __future__ import annotations

import random

from command_adventures.models import AdventureLevel, AdventureLevelAttempt, AdventureMastery

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
    return AdventureLevelAttempt.objects.filter(
        run__user=user, run__command_adventure=adventure
    ).count()


def _ordered_levels(adventure, *, with_prerequisites: bool = False) -> list[AdventureLevel]:
    # Imported lazily to avoid a services <-> scheduler import cycle.
    from command_adventures.services import ordered_levels_for

    return ordered_levels_for(adventure, with_prerequisites=with_prerequisites)


class AdventureScheduler:
    """Stateless picker; all state lives in AdventureMastery rows."""

    def _mastery_map(self, *, user, levels: list[AdventureLevel]) -> dict[int, AdventureMastery]:
        rows = AdventureMastery.objects.filter(
            user=user, adventure_level__in=[q.id for q in levels]
        )
        return {row.adventure_level_id: row for row in rows}

    def next_level(
        self, *, user, adventure, levels: list[AdventureLevel] | None = None
    ) -> AdventureLevel | None:
        """Pick the next command-level to serve, or None when the session is
        complete (every command mastered / nothing left to introduce). Callers
        that already resolved the ordered levels (with prerequisites) pass them
        in so the join runs once per request."""
        if levels is None:
            levels = _ordered_levels(adventure, with_prerequisites=True)
        if not levels:
            return None
        mastery = self._mastery_map(user=user, levels=levels)
        idx = encounter_index(user=user, adventure=adventure)

        def strength(q):
            row = mastery.get(q.id)
            return row.strength if row else 0

        def introduced(q):
            row = mastery.get(q.id)
            return bool(row and row.introduced)

        def last_seen(q):
            row = mastery.get(q.id)
            return row.last_seen_seq if row else 0

        def mastered(q):
            return strength(q) >= q.required_successful_attempts

        def prereqs_met(q):
            return all(strength(pre) >= PREREQ_STRENGTH for pre in q.prerequisites.all())

        introduced_levels = [q for q in levels if introduced(q)]
        pool = [q for q in introduced_levels if not mastered(q)]
        new = [q for q in levels if not introduced(q) and prereqs_met(q)]
        due = [q for q in pool if idx - last_seen(q) >= interval_for(strength(q))]

        # Warm-up: introduce sequentially until there is enough to interleave.
        if len(introduced_levels) < WARMUP_K and new:
            return new[0]
        if due:
            return self._weakest(due, idx=idx, strength=strength, last_seen=last_seen)
        if new:
            return new[0]
        if pool:
            return self._weakest(pool, idx=idx, strength=strength, last_seen=last_seen)
        return None

    def _weakest(self, items, *, idx, strength, last_seen) -> AdventureLevel:
        """Lowest box first, then most overdue, with a random tie-break."""
        best = min((strength(q), -(idx - last_seen(q))) for q in items)
        tied = [q for q in items if (strength(q), -(idx - last_seen(q))) == best]
        return random.choice(tied)

    def select_variant(self, *, user, level):
        """Least-recently-used published variant for this user+level; cycles when
        fewer variants exist than needed (graceful degradation)."""
        variants = list(level.adventure_variants.filter(is_published=True).order_by("semantic_key", "id"))
        if not variants:
            return None
        recent = (
            AdventureLevelAttempt.objects.filter(run__user=user, adventure_level=level)
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

    def mark_served(self, *, user, level, idx: int) -> AdventureMastery:
        row, _ = AdventureMastery.objects.get_or_create(user=user, adventure_level=level)
        row.introduced = True
        row.last_seen_seq = idx
        row.save(update_fields=["introduced", "last_seen_seq", "updated_at"])
        return row

    def apply_result(self, *, user, level, passed: bool, solved: bool) -> bool:
        """Update the Leitner box after an attempt. Returns whether a box advanced
        (which is what earns mastery points)."""
        row, _ = AdventureMastery.objects.get_or_create(user=user, adventure_level=level)
        ceiling = level.required_successful_attempts
        box_advanced = False
        if passed and row.strength < ceiling:
            row.strength += 1
            box_advanced = True
        elif not solved and row.strength > 0:
            row.strength -= 1
        row.save(update_fields=["strength", "updated_at"])
        return box_advanced


# --- pass-bar helpers ------------------------------------------------------

def total_achievable(adventure, *, levels=None) -> int:
    levels = levels if levels is not None else _ordered_levels(adventure)
    return sum(q.required_successful_attempts * BOX_VALUE for q in levels)


def pass_bar_for(adventure, *, levels=None) -> float:
    fraction = adventure.pass_bar_fraction or PASS_BAR_FRACTION
    return total_achievable(adventure, levels=levels) * fraction


def floor_met(*, user, adventure, levels=None) -> bool:
    """Every command in the adventure has been solved at least once (box >= floor)."""
    levels = levels if levels is not None else _ordered_levels(adventure)
    strengths = dict(
        AdventureMastery.objects.filter(
            user=user, adventure_level__in=[q.id for q in levels]
        ).values_list("adventure_level_id", "strength")
    )
    return all(strengths.get(q.id, 0) >= FLOOR_STRENGTH for q in levels)


def is_passed(*, user, adventure, session_score: int, levels=None) -> bool:
    levels = levels if levels is not None else _ordered_levels(adventure)
    return session_score >= pass_bar_for(adventure, levels=levels) and floor_met(
        user=user, adventure=adventure, levels=levels
    )
