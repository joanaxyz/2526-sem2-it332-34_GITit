"""Read-only activity counts over the same learner/tier records as live KPIs."""

from .mastery_metrics import samples


def module_activity(records, module_numbers):
    """Count participants independently of metric eligibility.

    live_records supplies one record per learner/tier, excluding staff, replays,
    transfers and optional levels in the admin scope. Participants include open
    tiers; attempted/mastered use the existing samples definitions unchanged.
    Counts are not a sequential funnel: learners can visit multiple modules.
    """
    result = []
    for number in module_numbers:
        scoped = [record for record in records if record["module"] == number]
        difficulties = []
        for difficulty in ("easy", "medium", "hard"):
            counts = samples([record for record in scoped if record["difficulty"] == difficulty])
            difficulties.append({
                "difficulty": difficulty,
                "attempted_tiers": counts["attempted_tiers"],
                "mastered_tiers": counts["mastered_tiers"],
                "in_progress_tiers": counts["in_progress_tiers"],
            })
        result.append({
            "number": number,
            "participants": len({record["player_id"] for record in scoped}),
            "difficulties": difficulties,
        })
    return result
