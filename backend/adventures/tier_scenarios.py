"""Ordered scenarios inside an adventure difficulty tier.

A tier holds one or more published scenarios, played in ``sort_order``. A run
plays the learner's next uncleared scenario; one solve clears a scenario, and the
tier completes when every published scenario is cleared.
"""

from __future__ import annotations

from adventures.models import AdventureLevelTierRun, AdventureLevelTierScenario


def published_scenarios(tier) -> list[AdventureLevelTierScenario]:
    return list(tier.scenarios.filter(is_published=True).order_by("sort_order", "id"))


def cleared_slugs(progress) -> list[str]:
    return list(progress.cleared_scenario_slugs or []) if progress is not None else []


def next_scenario(
    scenarios: list[AdventureLevelTierScenario], progress
) -> AdventureLevelTierScenario | None:
    """The first published scenario the learner has not cleared, or None."""
    cleared = set(cleared_slugs(progress))
    return next((scenario for scenario in scenarios if scenario.slug not in cleared), None)


def scenario_progress(
    scenarios: list[AdventureLevelTierScenario], progress, *, tier_completed: bool = False
) -> dict:
    """Cleared scenarios toward the tier, and the next one to play.

    A completed tier is fully cleared even when its completion predates
    per-scenario tracking or a reseed replaced its scenarios.
    """
    total = len(scenarios)
    if tier_completed:
        return {"completed": total, "total": total, "cleared": True, "next_scenario": None}
    cleared = set(cleared_slugs(progress))
    completed = sum(1 for scenario in scenarios if scenario.slug in cleared)
    upcoming = next(
        (
            {"index": index, "slug": scenario.slug, "title": scenario.title}
            for index, scenario in enumerate(scenarios, start=1)
            if scenario.slug not in cleared
        ),
        None,
    )
    return {
        "completed": completed,
        "total": total,
        "cleared": bool(scenarios) and upcoming is None,
        "next_scenario": upcoming,
    }


def replay_scenario(
    *, player, tier, scenarios: list[AdventureLevelTierScenario]
) -> AdventureLevelTierScenario:
    """Free play cycles the tier's scenarios, starting after the last replayed one."""
    latest = (
        AdventureLevelTierRun.objects.filter(player=player, tier=tier, is_replay=True)
        .order_by("-started_at", "-id")
        .values_list("current_scenario_id", flat=True)
        .first()
    )
    ids = [scenario.id for scenario in scenarios]
    if latest not in ids:
        return scenarios[0]
    return scenarios[(ids.index(latest) + 1) % len(scenarios)]
