"""Resolve and normalize the canonical adventure wave-plan owners."""

from __future__ import annotations

from curriculum.seed_data.blueprint_overlay import BLUEPRINT_ADVENTURE_LEVELS


def _level(slug: str, title: str, *, waves: list[str], reuse: list[str] | None = None) -> dict:
    return {
        "slug": slug,
        "title": title,
        "wave_slugs": list(waves),
        "reuse_usages": list(reuse or []),
    }

def adventure_levels_for(adventure_slug: str, problems: list[dict]) -> list[dict]:
    """Ordered level groups for one adventure.

    ``problems`` are the ``q()`` specs that resolved to ``adventure_slug`` (in
    authoring order). An explicit plan groups them into multi-wave levels;
    everything else degrades to one single-wave level per problem.
    """
    from curriculum.seed_data.adventures import ADVENTURE_WAVE_PLANS

    plan = _wave_plan_levels(ADVENTURE_WAVE_PLANS.get(adventure_slug, []))
    if not plan:
        return [
            {
                "slug": spec["slug"],
                "title": spec["title"],
                "waves": [spec],
                "reuse_usages": [],
            }
            for spec in problems
        ]
    available = {spec["slug"]: spec for spec in problems}
    planned_slugs = {slug for level in plan for slug in level["wave_slugs"]}
    levels = []
    for level in plan:
        waves = [available[slug] for slug in level["wave_slugs"] if slug in available]
        if not waves:
            continue
        levels.append(
            {
                "slug": level["slug"],
                "title": level["title"],
                "waves": waves,
                "reuse_usages": level["reuse_usages"],
            }
        )
    # Any problem the plan forgot still ships as its own single-wave level so no
    # authored content silently disappears. Blueprint-owned adventures are the
    # exception: the pack is the contract, so older stray problem slugs are not
    # appended after the explicit ledger.
    if adventure_slug not in BLUEPRINT_ADVENTURE_LEVELS:
        for spec in problems:
            if spec["slug"] not in planned_slugs:
                levels.append(
                    {
                        "slug": spec["slug"],
                        "title": spec["title"],
                        "waves": [spec],
                        "reuse_usages": [],
                    }
                )
    return levels

def _wave_plan_levels(plan: list[dict]) -> list[dict]:
    """Normalize ``adventures.py`` wave plans into the local level-plan shape."""
    levels = []
    for level in plan:
        wave_slugs = []
        for wave in level.get("waves", []):
            # ``adventures.py`` stores each wave as a list for historical support
            # of multi-slot waves. The current runtime maps one authored problem
            # to one wave, so flatten the authored singleton lists in order.
            if isinstance(wave, dict):
                wave_slugs.append(str(wave["slug"]))
            else:
                wave_slugs.extend(wave)
        levels.append(
            _level(
                str(level["slug"]),
                str(level["title"]),
                waves=wave_slugs,
                reuse=list(level.get("reuse_usages", [])),
            )
        )
    return levels

__all__ = ["adventure_levels_for"]
