"""The shape of a planned wave (docs/goals/curriculum-waves-and-repetition/WAVE_MAP.md)."""

from __future__ import annotations

from dataclasses import dataclass

DEBUT = "debut"
PRACTICE = "practice"
COMPOSE = "compose"
SPIRAL = "spiral"
TRANSFER = "transfer"
ROLES = (DEBUT, PRACTICE, COMPOSE, SPIRAL, TRANSFER)


@dataclass(frozen=True)
class WaveSpec:
    """One designed wave of a tier.

    ``slug`` is stable across reseeds: learners' ``cleared_wave_slugs`` name it.
    ``variants`` are Variant IDs in authored order, so the first is the one a
    first-time learner gets; a retry rotates within the same wave.
    """

    slug: str
    title: str
    role: str
    variants: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.role not in ROLES:
            raise ValueError(f"Wave {self.slug!r} has unknown role {self.role!r}.")


# level slug -> difficulty -> waves in play order
LevelWaves = dict[str, tuple[WaveSpec, ...]]
ModuleWaves = dict[str, LevelWaves]
