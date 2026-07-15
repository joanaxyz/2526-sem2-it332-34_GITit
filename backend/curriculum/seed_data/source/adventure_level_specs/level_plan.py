"""Adventure level grouping plan."""

from __future__ import annotations

from curriculum.seed_data.blueprint_overlay import BLUEPRINT_ADVENTURE_LEVELS


def _level(slug: str, title: str, *, waves: list[str], reuse: list[str] | None = None,
           brief: str = "") -> dict:
    return {
        "slug": slug,
        "title": title,
        "brief": brief,
        "wave_slugs": list(waves),
        "reuse_usages": list(reuse or []),
    }

ADVENTURE_LEVEL_PLAN = {
    "repository-foundations": [
        _level(
            "initialize-a-repository",
            "Initialize a repository",
            brief="Turn a plain folder into a Git repository and save the first commit.",
            waves=["init-current-folder", "init-named-folder", "init-with-initial-branch"],
            reuse=["git-add/dot", "git-commit/message"],
        ),
        _level(
            "clone-existing-repositories",
            "Clone existing repositories",
            brief="Copy a remote project down to your machine.",
            waves=[
                "clone-default-folder",
                "clone-into-named-folder",
                "clone-specific-branch",
                "clone-shallow-history",
            ],
            reuse=["git-status/plain"],
        ),
        _level(
            "read-repository-status",
            "Read repository status",
            brief="See what Git thinks changed before you act.",
            waves=[
                "inspect-status",
                "inspect-short-status",
                "inspect-porcelain-status",
                "inspect-ignored-status",
            ],
            reuse=["git-init/current-directory"],
        ),
        _level(
            "stage-and-commit",
            "Stage and commit your first save",
            brief="Stage exactly what you mean, then seal the snapshot.",
            waves=["stage-one-file", "stage-visible-folder-work", "commit-staged-snapshot"],
            reuse=["git-status/plain"],
        ),
        _level(
            "inspect-changes-with-diff",
            "Inspect changes with diff",
            brief="Review working and staged content, then save what you confirmed.",
            waves=["inspect-working-diff", "inspect-staged-diff"],
            reuse=["git-add/file", "git-commit/message", "git-status/plain"],
        ),
        _level(
            "read-your-history",
            "Read your history",
            brief="Investigate the commit history at every level of detail, then record what you found.",
            waves=[
                "inspect-compact-history",
                "inspect-graph-history",
                "inspect-named-commit",
            ],
            reuse=[
                "git-log/limit",
                "git-log/stat",
                "git-log/patch",
                "git-show/head",
                "git-show/name-only",
                "git-add/file",
                "git-commit/message",
            ],
        ),
        _level(
            "configure-and-ignore",
            "Configure and ignore",
            brief="Set up your identity, add a shortcut, and keep noise out of your commits.",
            waves=[
                "set-global-user-name",
                "set-global-user-email",
                "set-global-alias",
                "explain-ignore-rule",
            ],
            reuse=["git-config/list", "git-add/file", "git-commit/message"],
        ),
    ],
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
        plan = ADVENTURE_LEVEL_PLAN.get(adventure_slug)
    if not plan:
        return [
            {
                "slug": spec["slug"],
                "title": spec["title"],
                "brief": spec.get("scenario_context", {}).get("story", ""),
                "narrative_brief": spec.get("narrative_brief", {}),
                "level_type": spec.get("level_type", "guided_workflow"),
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
                "brief": level["brief"],
                "narrative_brief": level.get("narrative_brief", waves[0].get("narrative_brief", {})),
                "level_type": level.get("level_type", waves[0].get("level_type", "guided_workflow")),
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
                        "brief": "",
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
                brief=str(level.get("brief", "")),
                reuse=list(level.get("reuse_usages", [])),
            )
        )
    return levels

__all__ = ["ADVENTURE_LEVEL_PLAN", "adventure_levels_for"]
