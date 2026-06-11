"""Spaced-repetition (Leitner) scheduler for Command Adventure.

Turns an adventure into an interleaved mastery session: an *introduction front*
(new commands, in curriculum order, gated by prerequisites) running alongside a
*review pool* (introduced-but-unmastered commands, resurfaced when due, weakest
first). Spacing is measured in encounters, not wall-clock time.

Mastery is a Leitner box 0..N per (user, quest), where N is the quest's
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


def _ordered_quests(adventure, *, with_prerequisites: bool = False) -> list[AdventureQuest]:
    # Imported lazily to avoid a services <-> scheduler import cycle.
    from adventures.services import ordered_quests_for

    return ordered_quests_for(adventure, with_prerequisites=with_prerequisites)


class AdventureScheduler:
    """Stateless picker; all state lives in AdventureMastery rows."""

    def _mastery_map(self, *, user, quests: list[AdventureQuest]) -> dict[int, AdventureMastery]:
        rows = AdventureMastery.objects.filter(
            user=user, adventure_quest__in=[q.id for q in quests]
        )
        return {row.adventure_quest_id: row for row in rows}

    def next_quest(
        self, *, user, adventure, quests: list[AdventureQuest] | None = None
    ) -> AdventureQuest | None:
        """Pick the next command-quest to serve, or None when the session is
        complete (every command mastered / nothing left to introduce). Callers
        that already resolved the ordered quests (with prerequisites) pass them
        in so the join runs once per request."""
        if quests is None:
            quests = _ordered_quests(adventure, with_prerequisites=True)
        if not quests:
            return None
        mastery = self._mastery_map(user=user, quests=quests)
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

        introduced_quests = [q for q in quests if introduced(q)]
        pool = [q for q in introduced_quests if not mastered(q)]
        new = [q for q in quests if not introduced(q) and prereqs_met(q)]
        due = [q for q in pool if idx - last_seen(q) >= interval_for(strength(q))]

        # Warm-up: introduce sequentially until there is enough to interleave.
        if len(introduced_quests) < WARMUP_K and new:
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
        best = min((strength(q), -(idx - last_seen(q))) for q in items)
        tied = [q for q in items if (strength(q), -(idx - last_seen(q))) == best]
        return random.choice(tied)

    def select_variant(self, *, user, quest):
        """Least-recently-used published variant for this user+quest; cycles when
        fewer variants exist than needed (graceful degradation)."""
        variants = list(quest.adventure_variants.filter(is_published=True).order_by("semantic_key", "id"))
        if not variants:
            return None
        recent = (
            AdventureQuestAttempt.objects.filter(run__user=user, adventure_quest=quest)
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

    def mark_served(self, *, user, quest, idx: int) -> AdventureMastery:
        row, _ = AdventureMastery.objects.get_or_create(user=user, adventure_quest=quest)
        row.introduced = True
        row.last_seen_seq = idx
        row.save(update_fields=["introduced", "last_seen_seq", "updated_at"])
        return row

    def apply_result(self, *, user, quest, passed: bool, solved: bool) -> bool:
        """Update the Leitner box after an attempt. Returns whether a box advanced
        (which is what earns mastery points)."""
        row, _ = AdventureMastery.objects.get_or_create(user=user, adventure_quest=quest)
        ceiling = quest.required_successful_attempts
        box_advanced = False
        if passed and row.strength < ceiling:
            row.strength += 1
            box_advanced = True
        elif not solved and row.strength > 0:
            row.strength -= 1
        row.save(update_fields=["strength", "updated_at"])
        return box_advanced


# --- pass-bar helpers ------------------------------------------------------

def total_achievable(adventure, *, quests=None) -> int:
    quests = quests if quests is not None else _ordered_quests(adventure)
    return sum(q.required_successful_attempts * BOX_VALUE for q in quests)


def pass_bar_for(adventure, *, quests=None) -> float:
    fraction = adventure.pass_bar_fraction or PASS_BAR_FRACTION
    return total_achievable(adventure, quests=quests) * fraction


def floor_met(*, user, adventure, quests=None) -> bool:
    """Every command in the adventure has been solved at least once (box >= floor)."""
    quests = quests if quests is not None else _ordered_quests(adventure)
    strengths = dict(
        AdventureMastery.objects.filter(
            user=user, adventure_quest__in=[q.id for q in quests]
        ).values_list("adventure_quest_id", "strength")
    )
    return all(strengths.get(q.id, 0) >= FLOOR_STRENGTH for q in quests)


def is_passed(*, user, adventure, session_score: int, quests=None) -> bool:
    quests = quests if quests is not None else _ordered_quests(adventure)
    return session_score >= pass_bar_for(adventure, quests=quests) and floor_met(
        user=user, adventure=adventure, quests=quests
    )
