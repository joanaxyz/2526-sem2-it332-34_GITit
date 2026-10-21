BOOK_BLOCK_TYPES = {
    "paragraph",
    "bullet_list",
    "list",
    "command",
    "code",
    "callout",
    "warning",
    "terminal_output",
    "diagram",
    "image",
}


def content_levels(definition: dict) -> list[dict]:
    levels = definition.get("levels")
    if isinstance(levels, list):
        return [level for level in levels if isinstance(level, dict)]
    level = definition.get("level")
    return [level] if isinstance(level, dict) else []


def _level_as_problem(level: dict) -> dict:
    """A flat (pre-scenario) authored level IS a single problem: its scenario fields
    (slug/solution_commands/initial_state/.../variants) describe one playable
    scenario or trial."""
    problem = dict(level)
    problem.setdefault("slug", level.get("slug"))
    return problem


def level_scenarios(level: dict) -> list[dict]:
    """Ordered playable problems (scenarios) inside an authored adventure level.

    New content nests ``scenarios: [...]``; legacy flat content (no ``scenarios``) is
    treated as one scenario so old definitions keep compiling."""
    scenarios = level.get("scenarios")
    if isinstance(scenarios, list) and any(isinstance(scenario, dict) for scenario in scenarios):
        return [scenario for scenario in scenarios if isinstance(scenario, dict)]
    return [_level_as_problem(level)]


def level_trials(level: dict) -> list[dict]:
    """Ordered difficulty trials inside an authored challenge level.

    New content nests ``trials: [...]``; legacy flat content (one ``difficulty``
    per authored level) is treated as a single trial."""
    trials = level.get("trials")
    if isinstance(trials, list) and any(isinstance(trial, dict) for trial in trials):
        return [trial for trial in trials if isinstance(trial, dict)]
    return [_level_as_problem(level)]


def challenge_is_nested(definition: dict) -> bool:
    """True when the authored challenge uses the nested ``levels[].trials[]``
    shape. Legacy flat ``levels[]`` (each a difficulty) is collapsed into one
    ChallengeLevel to preserve existing content."""
    return any("trials" in level for level in content_levels(definition))
