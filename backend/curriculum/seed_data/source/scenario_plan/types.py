"""The shape of a planned scenario; see CONTENT_AUTHORING_GUIDE.md."""

from __future__ import annotations

from dataclasses import dataclass

DEBUT = "debut"
PRACTICE = "practice"
COMPOSE = "compose"
SPIRAL = "spiral"
TRANSFER = "transfer"
ROLES = (DEBUT, PRACTICE, COMPOSE, SPIRAL, TRANSFER)


@dataclass(frozen=True)
class ScenarioSpec:
    """One designed scenario of a tier.

    ``slug`` is stable across reseeds: learners' ``cleared_scenario_slugs`` name it.
    ``variants`` are Variant IDs in authored order, so the first is the one a
    first-time learner gets; a retry rotates within the same scenario.
    """

    slug: str
    title: str
    role: str
    variants: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.role not in ROLES:
            raise ValueError(f"Scenario {self.slug!r} has unknown role {self.role!r}.")


# level slug -> difficulty -> scenarios in play order
LevelScenarios = dict[str, tuple[ScenarioSpec, ...]]
ModuleScenarios = dict[str, LevelScenarios]
