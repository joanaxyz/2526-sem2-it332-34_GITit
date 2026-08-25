"""Compatibility wrapper for composed adventure level specs."""

from __future__ import annotations

from curriculum.seed_data.source.adventure_level_specs import (
    ADVENTURE_LEVELS,
    SPEC_BY_SLUG,
    adventure_levels_for,
)

__all__ = ["ADVENTURE_LEVELS", "SPEC_BY_SLUG", "adventure_levels_for"]
