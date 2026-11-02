"""Mastery-unit KPI arithmetic shared by live reports and frozen studies."""

from collections import defaultdict
from datetime import timedelta

from django.db.models import Count, Max, Q
from django.utils import timezone

from adventures.models import AdventureLevelTierRun
from common.constants import (
    COMMAND_DIAGNOSTIC,
    SESSION_STATUS_ABANDONED,
    SESSION_STATUS_COMPLETED,
    SESSION_STATUS_FAILED,
)
from progress.models import AdventureLevelTierCompletion, KpiCheckpoint, KpiExposure

# car_first is CAR's starting point for learners, not an evaluated KPI.
KEYS = ("scr", "car", "car_first", "hlcr", "arc", "rta", "retry_success_rate")
TERMINAL = (SESSION_STATUS_COMPLETED, SESSION_STATUS_FAILED, SESSION_STATUS_ABANDONED)
# An open run whose last command is this old counts as left, like an abandonment.
STALE_AFTER = timedelta(days=7)


def rate(n, d, *, average=False, unit=None):
    result = {
        "value": round(n / d * (1 if average else 100), 2 if average else 1) if d else None,
        "numerator": round(n, 4),
        "denominator": d,
    }
    if unit:
        result["unit"] = unit
    return result


def car_score(*, passed, target, actual):
    if target is None or target <= 0 or actual is None or passed is None:
        return None
    return 100 * int(passed) * min(1, target / max(1, actual))


def rates(records):
    observed = [
        r
        for r in records
        if not r.get("mastery_missing", False) and not r.get("in_progress", False)
    ]
    hard = [r for r in observed if r["difficulty"] == "hard"]
    mastered = [r for r in observed if r["mastered"]]
    car = [s for r in records for s in r["car_scores"]]
    car_first = [s for r in records for s in r["car_first_scores"]]
    transfer = [r["transfer"] for r in records if r["transfer"] is not None]
    retry_total = sum(r.get("retry_total", 0) for r in records)
    result = {
        "scr": rate(len(mastered), len(observed)),
        "car": rate(sum(car), len(car), average=True),
        "car_first": rate(sum(car_first), len(car_first), average=True),
        "hlcr": rate(sum(r["mastered"] for r in hard), len(hard)),
        "arc": rate(sum(r["failures"] for r in mastered), len(mastered), average=True),
        "rta": rate(sum(transfer), len(transfer)),
        "retry_success_rate": rate(sum(r.get("retry_wins", 0) for r in records), retry_total),
    }
    result["rtr"] = result["retry_success_rate"]
    return result


def balanced(records, *, cohort=False):
    if not cohort:
        return rates(records)
    players = defaultdict(list)
    for row in records:
        players[row["player_id"]].append(row)
    per_player = [rates(rows) for rows in players.values()]
    result = {}
    for key in KEYS:
        values = [p[key]["value"] for p in per_player if p[key]["value"] is not None]
        result[key] = rate(sum(values), len(values), average=True, unit="participants")
    result["rtr"] = result["retry_success_rate"]
    return result


def content_key(semantic_key, variant_id):
    return semantic_key or f"id:{variant_id}"


def scenario_car(clears):
    """Each scenario's first and latest score, plus its count of unscored ones.

    ``clears`` maps a scenario to the scores (``None`` without a reference) of the
    learner's clears of content they had not cleared before, oldest first.
    """
    first, latest, missing = [], [], 0
    for scores in clears.values():
        scored = [s for s in scores if s is not None]
        if scored:
            first.append(scored[0])
            latest.append(scored[-1])
        else:
            missing += 1
    return first, latest, missing


def fresh_clears(runs, *, players, end_before=None):
    """Scores of clears of content each learner had not cleared before.

    Replays count, so a learner who replays a tier and meets an unsolved variant
    can raise or lower that scenario's CAR. Repeating solved content never
    counts. Novelty reads the learner's whole history; scores come from ``runs``.
    """
    history = AdventureLevelTierRun.objects.filter(
        player_id__in=players,
        is_transfer=False,
        status=SESSION_STATUS_COMPLETED,
        ended_at__isnull=False,
    )
    if end_before:
        history = history.filter(ended_at__lt=end_before)
    scoped = set(
        runs.filter(
            tier__adventure_level__is_required=True,
            is_transfer=False,
            status=SESSION_STATUS_COMPLETED,
        ).values_list("id", flat=True)
    )
    rows = (
        history.annotate(
            diagnostics=Count(
                "steps",
                filter=Q(
                    steps__command_classification=COMMAND_DIAGNOSTIC,
                    steps__normalized_command__startswith="git ",
                ),
            )
        )
        .order_by("ended_at", "id")
        .values(
            "id",
            "player_id",
            "tier_id",
            "selected_variant_id",
            "selected_variant__semantic_key",
            "selected_variant__scenario_id",
            "ref_count",
            "counted_action_total",
            "assess_diag",
            "diagnostics",
        )
    )
    cleared = defaultdict(set)
    clears = defaultdict(lambda: defaultdict(list))
    for r in rows:
        key = content_key(r["selected_variant__semantic_key"], r["selected_variant_id"])
        if key in cleared[r["player_id"]]:
            continue
        cleared[r["player_id"]].add(key)
        if r["id"] in scoped:
            actual = r["counted_action_total"] + (r["diagnostics"] if r["assess_diag"] else 0)
            clears[r["player_id"], r["tier_id"]][r["selected_variant__scenario_id"]].append(
                car_score(passed=True, target=r["ref_count"], actual=actual)
            )
    return clears


def live_records(runs, *, end_before=None):
    """Read each learner/tier once; mastery is dated by its first clear.

    ``runs`` may include replays: only CAR reads them (see ``fresh_clears``).
    A better replay moves ``completed_at`` forward, so it cannot date mastery.
    A tier enters SCR/HLCR once it has an outcome: mastery, a concluded run, or
    an open run with commands idle for ``STALE_AFTER``. Opening a tier without
    typing anything is not an attempt; such tiers are reported as in progress.
    """
    as_of = min(timezone.now(), end_before) if end_before else timezone.now()
    rows = list(
        runs.filter(tier__adventure_level__is_required=True, is_transfer=False, is_replay=False)
        .annotate(last_step_at=Max("steps__created_at"))
        .values(
            "id",
            "player_id",
            "tier_id",
            "status",
            "started_at",
            "ended_at",
            "last_step_at",
            "tier__difficulty",
            "tier__adventure_level__slug",
            "tier__adventure_level__chapter__number",
            "prior_run__status",
        )
    )
    players = {r["player_id"] for r in rows}
    tiers = {r["tier_id"] for r in rows}
    clears = fresh_clears(runs, players=players, end_before=end_before)
    completions = AdventureLevelTierCompletion.objects.filter(
        player_id__in=players, tier_id__in=tiers
    )
    checkpoints = KpiCheckpoint.objects.filter(
        player_id__in=players, tier_id__in=tiers
    ).select_related("variant__scenario")
    if end_before:
        checkpoints = checkpoints.filter(assigned_at__lt=end_before)
    points = {(c.player_id, c.tier_id, c.kind): c for c in checkpoints}
    # Every non-replay clear precedes mastery (later launches are replays), so
    # without a first-mastery checkpoint the latest one is the mastering run.
    last_clear = {}
    for r in rows:
        if r["status"] == SESSION_STATUS_COMPLETED and r["ended_at"]:
            key = r["player_id"], r["tier_id"]
            last_clear[key] = max(r["ended_at"], last_clear.get(key, r["ended_at"]))
    mastery = {}
    for c in completions:
        key = c.player_id, c.tier_id
        car = points.get((*key, "car"))
        at = car.ended_at if car and car.ended_at else last_clear.get(key, c.completed_at)
        if not end_before or at < end_before:
            mastery[key] = at
    from .checkpoints import transfer_ready as checkpoint_ready

    seen = defaultdict(set)
    if any(p.kind == "transfer" and p.ended_at is None for p in points.values()):
        for player_id, key in KpiExposure.objects.filter(player_id__in=players).values_list(
            "player_id", "state_key"
        ):
            seen[player_id].add(key)
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["player_id"], row["tier_id"]].append(row)
    records = []
    for (player_id, tier_id), attempts in grouped.items():
        row = attempts[0]
        at = mastery.get((player_id, tier_id))
        car = points.get((player_id, tier_id, "car"))
        transfer = points.get((player_id, tier_id, "transfer"))
        car_ready = car and (not end_before or (car.ended_at and car.ended_at < end_before))
        transfer_ready = (
            transfer and transfer.ended_at and (not end_before or transfer.ended_at < end_before)
        )
        retries = [
            r
            for r in attempts
            if r["prior_run__status"] == SESSION_STATUS_FAILED
            and r["status"] in TERMINAL
            and (not end_before or (r["ended_at"] and r["ended_at"] < end_before))
        ]
        concluded = any(
            (
                r["status"] in TERMINAL
                and (r["ended_at"] < as_of if r["ended_at"] else end_before is None)
            )
            or (r["last_step_at"] and r["last_step_at"] <= as_of - STALE_AFTER)
            for r in attempts
        )
        car_first, car_latest, car_missing = scenario_car(clears[player_id, tier_id])
        records.append(
            {
                "player_id": player_id,
                "tier_id": tier_id,
                "module": row["tier__adventure_level__chapter__number"],
                "slug": row["tier__adventure_level__slug"],
                "difficulty": row["tier__difficulty"],
                "mastered": at is not None,
                "in_progress": at is None and not concluded,
                "failures": car.retries
                if car_ready
                else sum(
                    r["ended_at"] is not None
                    and r["ended_at"] <= at
                    and (
                        r["status"] == SESSION_STATUS_FAILED
                        or (
                            r["status"] == SESSION_STATUS_ABANDONED
                            and r["last_step_at"] is not None
                        )
                    )
                    for r in attempts
                )
                if at
                else 0,
                "car_scores": car_latest,
                "car_first_scores": car_first,
                "car_missing": car_missing,
                "transfer": int(transfer.passed)
                if transfer_ready and transfer.passed is not None
                else None,
                "transfer_assigned": bool(transfer),
                "transfer_missing": bool(transfer_ready and transfer.passed is None)
                or bool(
                    transfer
                    and transfer.ended_at is None
                    and not checkpoint_ready(transfer, seen=seen[player_id])
                )
                or bool(
                    row["tier__adventure_level__chapter__number"] in (3, 4) and at and not transfer
                ),
                "retry_total": len(retries),
                "retry_wins": sum(r["status"] == SESSION_STATUS_COMPLETED for r in retries),
            }
        )
    return records


def samples(records):
    return {
        "participants": len({r["player_id"] for r in records}),
        "attempted_tiers": sum(
            r.get("attempted", True) and not r.get("in_progress", False) for r in records
        ),
        "in_progress_tiers": sum(r.get("in_progress", False) for r in records),
        "mastered_tiers": sum(r["mastered"] for r in records),
        "mastery_missing": sum(r.get("mastery_missing", False) for r in records),
        "car_scored": sum(len(r["car_scores"]) for r in records),
        "car_missing": sum(r["car_missing"] for r in records),
        "transfer_assigned": sum(r.get("transfer_assigned", False) for r in records),
        "transfer_pending": sum(
            r.get("transfer_assigned", False)
            and r["transfer"] is None
            and not r.get("transfer_missing", False)
            for r in records
        ),
        "transfer_missing": sum(
            r.get(
                "transfer_missing",
                r["module"] in (3, 4) and r["mastered"] and not r.get("transfer_assigned", False),
            )
            for r in records
        ),
    }
